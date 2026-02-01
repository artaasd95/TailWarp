#include "survival_probability.h"
#include <cmath>
#include <iostream>
#include <algorithm>

namespace tailwarp {
namespace risk_metrics {

// ============================================================================
// CUDA Kernels
// ============================================================================

namespace cuda_kernels {

/**
 * @brief Device function to compute standard normal CDF
 * 
 * Approximation using error function for use on GPU
 */
__device__ inline float device_normal_cdf(float x) {
    return 0.5f * (1.0f + erff(x / sqrtf(2.0f)));
}

/**
 * @brief Device function to compute cumulative hazard
 * 
 * For hazard-integrated model: ∫₀ᵗ γ(s)ds
 * Approximation: cumulative_hazard = -mean_return * t / (volatility²)
 * with jump adjustment: (σ²·t + λ²)
 */
__device__ inline float compute_cumulative_hazard(float mean_return,
                                                   float volatility,
                                                   float time_horizon,
                                                   float jump_intensity) {
    if (volatility < 1e-10f) return 0.0f;
    
    // Base cumulative variance
    float var_t = volatility * volatility * time_horizon;
    
    // Add jump intensity squared
    float cumulative_var = var_t + jump_intensity * jump_intensity;
    
    // Cumulative hazard: loss intensity integrated over time
    // Approximation: -drift/volatility²
    float hazard = -mean_return * time_horizon / (volatility * volatility + 1e-10f);
    
    // Clamp to non-negative
    return fmaxf(0.0f, -hazard);
}

/**
 * @brief Device function for structural barrier survival calculation
 * 
 * S(t) = N(-A_t/2 + log(d)/A_t) - d·N(-A_t/2 - log(d)/A_t)
 * 
 * Where:
 *   A_t² = σ²·t + λ²
 *   d = V₀/B (distance to default)
 */
__device__ inline float compute_structural_survival(float distance_to_default,
                                                    float volatility,
                                                    float time_horizon,
                                                    float jump_intensity) {
    if (distance_to_default <= 0.0f) return 0.0f;
    if (volatility < 1e-10f) return (distance_to_default > 1.0f) ? 1.0f : 0.0f;
    
    // Compute A_t = sqrt(σ²·t + λ²)
    float var_component = volatility * volatility * time_horizon;
    float jump_component = jump_intensity * jump_intensity;
    float A_t = sqrtf(var_component + jump_component + 1e-10f);
    
    // Avoid division by zero
    if (A_t < 1e-10f) return (distance_to_default > 1.0f) ? 1.0f : 0.0f;
    
    // log(d)
    float log_d = logf(distance_to_default + 1e-10f);
    
    // First term: N(-A_t/2 + log(d)/A_t)
    float arg1 = -A_t / 2.0f + log_d / A_t;
    float term1 = device_normal_cdf(arg1);
    
    // Second term: d·N(-A_t/2 - log(d)/A_t)
    float arg2 = -A_t / 2.0f - log_d / A_t;
    float term2 = distance_to_default * device_normal_cdf(arg2);
    
    // S(t) = term1 - term2
    float survival = term1 - term2;
    
    // Clamp to [0, 1]
    return fmaxf(0.0f, fminf(1.0f, survival));
}

/**
 * @brief Device function for Information Ratio survival
 * 
 * P(α > 0) = Φ(IR) where IR = E[α]/σ_α
 */
__device__ inline float compute_information_ratio_survival(float mean_residual,
                                                           float residual_volatility) {
    if (residual_volatility < 1e-10f) {
        return (mean_residual > 0.0f) ? 1.0f : 0.0f;
    }
    
    float IR = mean_residual / (residual_volatility + 1e-10f);
    return device_normal_cdf(IR);
}

/**
 * @brief Device function for heavy-tailed (Lindy Effect) survival
 * 
 * P(X > x) = L(x)x^(-α)
 * Survival with age: S(age) = age^(-α) / age_max^(-α)
 */
__device__ inline float compute_lindy_survival(float current_level,
                                               float barrier_level,
                                               float tail_exponent,
                                               float time_horizon) {
    if (current_level <= barrier_level || tail_exponent <= 0.0f) return 0.0f;
    
    float relative_level = current_level / (barrier_level + 1e-10f);
    if (relative_level < 1.0f) return 0.0f;
    
    // Lindy effect: older age increases survival odds
    // S(t) approximates as exp(-λ·t^(-α)) where λ depends on tail exponent
    float age_factor = powf(time_horizon, -tail_exponent);
    
    return fminf(1.0f, expf(-0.5f * age_factor) * relative_level);
}

/**
 * @brief Device function for ruin theory survival
 * 
 * Capital dynamics: dU_t = c·dt - dN_t (where dN_t = claim jump)
 * Survival: S(t) = 1 - ψ(u) where ψ is ruin probability
 */
__device__ inline float compute_ruin_theory_survival(float current_capital,
                                                     float claim_frequency,
                                                     float average_claim,
                                                     float premium_inflow) {
    if (current_capital <= 0.0f) return 0.0f;
    
    // Net profit condition: premium_inflow > claim_frequency * average_claim
    float expected_loss = claim_frequency * average_claim;
    if (premium_inflow <= expected_loss) return 0.0f;
    
    // Lundberg adjustment coefficient
    float positive_drift = premium_inflow - expected_loss;
    float R = 2.0f * positive_drift / (claim_frequency * average_claim * average_claim + 1e-10f);
    
    // Ruin probability: ψ = exp(-R·u)
    float ruin_prob = expf(-R * current_capital);
    
    return 1.0f - fminf(1.0f, ruin_prob);
}

/**
 * @brief CUDA kernel for batch survival probability calculation
 * 
 * Each thread processes one scenario independently.
 * Supports multiple model types and computes comprehensive survival metrics.
 */
__global__ void survival_probability_kernel(const SurvivalProbabilityParameters* d_params,
                                            SurvivalProbabilityResult* d_results,
                                            size_t count) {
    
    unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x;
    
    if (idx >= count) return;
    
    const SurvivalProbabilityParameters& params = d_params[idx];
    SurvivalProbabilityResult& result = d_results[idx];
    
    // Initialize result
    result.distance_to_barrier = params.current_level / (params.barrier_level + 1e-10f);
    
    // Route to appropriate model
    float survival = 0.0f;
    
    switch (params.model_type) {
        
        case SurvivalModelType::HAZARD_INTEGRATED: {
            // Integrate hazard rate over time
            result.cumulative_hazard = compute_cumulative_hazard(
                params.mean_return,
                params.volatility,
                params.time_horizon,
                params.jump_intensity
            );
            
            // S(t) = exp(-cumulative_hazard)
            survival = expf(-result.cumulative_hazard);
            result.hazard_rate = result.cumulative_hazard / (params.time_horizon + 1e-10f);
            break;
        }
        
        case SurvivalModelType::STRUCTURAL_BARRIER: {
            // Merton-style barrier crossing
            survival = compute_structural_survival(
                result.distance_to_barrier,
                params.volatility,
                params.time_horizon,
                params.jump_intensity
            );
            
            float var_t = params.volatility * params.volatility * params.time_horizon;
            result.cumulative_hazard = -logf(fmaxf(1e-10f, survival));
            result.hazard_rate = result.cumulative_hazard / (params.time_horizon + 1e-10f);
            break;
        }
        
        case SurvivalModelType::INFORMATION_RATIO: {
            // Normal CDF of IR
            survival = compute_information_ratio_survival(
                params.mean_residual_return,
                params.residual_volatility
            );
            result.hazard_rate = 0.0f;
            result.cumulative_hazard = 0.0f;
            break;
        }
        
        case SurvivalModelType::HEAVY_TAILED: {
            // Lindy effect
            survival = compute_lindy_survival(
                params.current_level,
                params.barrier_level,
                params.tail_exponent,
                params.time_horizon
            );
            result.hazard_rate = -logf(fmaxf(1e-10f, survival)) / (params.time_horizon + 1e-10f);
            result.cumulative_hazard = -logf(fmaxf(1e-10f, survival));
            break;
        }
        
        case SurvivalModelType::RUIN_THEORY: {
            // Cramér-Lundberg model
            survival = compute_ruin_theory_survival(
                params.current_level,
                params.claim_frequency,
                params.average_claim_size,
                params.premium_inflow
            );
            result.hazard_rate = 0.0f;
            result.cumulative_hazard = 0.0f;
            break;
        }
        
        default:
            survival = 0.5f;  // Default fallback
    }
    
    // Clamp survival probability to [0, 1]
    survival = fmaxf(0.0f, fminf(1.0f, survival));
    
    result.survival_probability = survival;
    result.ruin_probability = 1.0f - survival;
    
    // Expected time to ruin (approximate)
    // For exponential survival decay: E[τ] ≈ -log(0.5) / hazard_rate
    if (result.hazard_rate > 1e-10f) {
        result.expected_time_to_ruin = logf(2.0f) / result.hazard_rate;
    } else if (result.hazard_rate < -1e-10f) {
        result.expected_time_to_ruin = 1e10f;  // Very large (quasi-infinite)
    } else {
        result.expected_time_to_ruin = params.time_horizon;
    }
    
    // Sustainability check (threshold: 0.95 = 95% survival at time horizon)
    float sustainability_threshold = 0.95f;
    result.is_sustainable = (survival >= sustainability_threshold);
    result.confidence_margin = survival - sustainability_threshold;
}

} // namespace cuda_kernels

// ============================================================================
// SurvivalProbabilityMetric Class Implementation
// ============================================================================

SurvivalProbabilityMetric::SurvivalProbabilityMetric() {
    // Initialize CUDA device if available
    int device_count;
    cudaGetDeviceCount(&device_count);
    if (device_count > 0) {
        cudaSetDevice(0);
    }
}

SurvivalProbabilityMetric::~SurvivalProbabilityMetric() {
    // Cleanup if needed
}

/**
 * @brief CPU implementation of survival probability calculation
 * 
 * Reference implementation. GPU version should produce identical results
 * within floating-point precision.
 */
SurvivalProbabilityResult SurvivalProbabilityMetric::calculate_cpu(
    const SurvivalProbabilityParameters& params) const {
    
    SurvivalProbabilityResult result = {};
    
    result.distance_to_barrier = params.current_level / (params.barrier_level + 1e-10f);
    
    float survival = 0.0f;
    
    // Normal CDF approximation for CPU
    auto normal_cdf = [](float x) -> float {
        return 0.5f * (1.0f + std::erf(x / std::sqrt(2.0f)));
    };
    
    switch (params.model_type) {
        
        case SurvivalModelType::HAZARD_INTEGRATED: {
            // Cumulative hazard over time
            if (params.volatility < 1e-10f) {
                result.cumulative_hazard = 0.0f;
            } else {
                float var_t = params.volatility * params.volatility * params.time_horizon;
                float jump_var = params.jump_intensity * params.jump_intensity;
                result.cumulative_hazard = -params.mean_return * params.time_horizon / 
                                          (params.volatility * params.volatility + 1e-10f);
                result.cumulative_hazard = std::max(0.0f, -result.cumulative_hazard);
            }
            
            survival = std::exp(-result.cumulative_hazard);
            result.hazard_rate = result.cumulative_hazard / (params.time_horizon + 1e-10f);
            break;
        }
        
        case SurvivalModelType::STRUCTURAL_BARRIER: {
            // Merton barrier model
            if (result.distance_to_barrier <= 0.0f) {
                survival = 0.0f;
            } else if (params.volatility < 1e-10f) {
                survival = (result.distance_to_barrier > 1.0f) ? 1.0f : 0.0f;
            } else {
                float var_component = params.volatility * params.volatility * params.time_horizon;
                float jump_component = params.jump_intensity * params.jump_intensity;
                float A_t = std::sqrt(var_component + jump_component + 1e-10f);
                
                float log_d = std::log(result.distance_to_barrier + 1e-10f);
                
                float arg1 = -A_t / 2.0f + log_d / A_t;
                float term1 = normal_cdf(arg1);
                
                float arg2 = -A_t / 2.0f - log_d / A_t;
                float term2 = result.distance_to_barrier * normal_cdf(arg2);
                
                survival = std::max(0.0f, std::min(1.0f, term1 - term2));
            }
            
            result.cumulative_hazard = -std::log(std::max(1e-10f, survival));
            result.hazard_rate = result.cumulative_hazard / (params.time_horizon + 1e-10f);
            break;
        }
        
        case SurvivalModelType::INFORMATION_RATIO: {
            // IR-based survival
            if (params.residual_volatility < 1e-10f) {
                survival = (params.mean_residual_return > 0.0f) ? 1.0f : 0.0f;
            } else {
                float IR = params.mean_residual_return / params.residual_volatility;
                survival = normal_cdf(IR);
            }
            result.hazard_rate = 0.0f;
            result.cumulative_hazard = 0.0f;
            break;
        }
        
        case SurvivalModelType::HEAVY_TAILED: {
            // Lindy effect
            if (result.distance_to_barrier <= 1.0f || params.tail_exponent <= 0.0f) {
                survival = 0.0f;
            } else {
                float age_factor = std::pow(params.time_horizon, -params.tail_exponent);
                survival = std::min(1.0f, std::exp(-0.5f * age_factor) * result.distance_to_barrier);
            }
            result.hazard_rate = -std::log(std::max(1e-10f, survival)) / (params.time_horizon + 1e-10f);
            result.cumulative_hazard = -std::log(std::max(1e-10f, survival));
            break;
        }
        
        case SurvivalModelType::RUIN_THEORY: {
            // Cramér-Lundberg model
            if (params.current_level <= 0.0f) {
                survival = 0.0f;
            } else {
                float expected_loss = params.claim_frequency * params.average_claim_size;
                if (params.premium_inflow <= expected_loss) {
                    survival = 0.0f;
                } else {
                    float positive_drift = params.premium_inflow - expected_loss;
                    float R = 2.0f * positive_drift / 
                             (params.claim_frequency * params.average_claim_size * 
                              params.average_claim_size + 1e-10f);
                    float ruin_prob = std::exp(-R * params.current_level);
                    survival = 1.0f - std::min(1.0f, ruin_prob);
                }
            }
            result.hazard_rate = 0.0f;
            result.cumulative_hazard = 0.0f;
            break;
        }
        
        default:
            survival = 0.5f;
    }
    
    result.survival_probability = std::max(0.0f, std::min(1.0f, survival));
    result.ruin_probability = 1.0f - result.survival_probability;
    
    // Expected time to ruin
    if (result.hazard_rate > 1e-10f) {
        result.expected_time_to_ruin = std::log(2.0f) / result.hazard_rate;
    } else if (result.hazard_rate < -1e-10f) {
        result.expected_time_to_ruin = 1e10f;
    } else {
        result.expected_time_to_ruin = params.time_horizon;
    }
    
    // Sustainability assessment
    float sustainability_threshold = 0.95f;
    result.is_sustainable = (result.survival_probability >= sustainability_threshold);
    result.confidence_margin = result.survival_probability - sustainability_threshold;
    
    return result;
}

/**
 * @brief GPU implementation of survival probability calculation
 */
SurvivalProbabilityResult SurvivalProbabilityMetric::calculate_gpu(
    const SurvivalProbabilityParameters& params) const {
    
    SurvivalProbabilityParameters* d_params;
    SurvivalProbabilityResult* d_results;
    SurvivalProbabilityResult h_result = {};
    
    // Allocate device memory
    cudaMalloc(&d_params, sizeof(SurvivalProbabilityParameters));
    cudaMalloc(&d_results, sizeof(SurvivalProbabilityResult));
    
    // Copy data to device
    cudaMemcpy(d_params, &params, sizeof(SurvivalProbabilityParameters), 
               cudaMemcpyHostToDevice);
    
    // Launch kernel with 1 block, 1 thread
    cuda_kernels::survival_probability_kernel<<<1, 1>>>(d_params, d_results, 1);
    
    // Copy result back to host
    cudaMemcpy(&h_result, d_results, sizeof(SurvivalProbabilityResult), 
               cudaMemcpyDeviceToHost);
    
    // Free device memory
    cudaFree(d_params);
    cudaFree(d_results);
    
    return h_result;
}

/**
 * @brief Batch GPU calculation for multiple scenarios
 */
std::vector<SurvivalProbabilityResult> SurvivalProbabilityMetric::calculate_gpu_batch(
    const SurvivalProbabilityParameters* params_array,
    size_t count) const {
    
    SurvivalProbabilityParameters* d_params;
    SurvivalProbabilityResult* d_results;
    std::vector<SurvivalProbabilityResult> h_results(count);
    
    // Allocate device memory
    cudaMalloc(&d_params, count * sizeof(SurvivalProbabilityParameters));
    cudaMalloc(&d_results, count * sizeof(SurvivalProbabilityResult));
    
    // Copy data to device
    cudaMemcpy(d_params, params_array, count * sizeof(SurvivalProbabilityParameters),
               cudaMemcpyHostToDevice);
    
    // Launch kernel
    int block_size = 256;
    int grid_size = (count + block_size - 1) / block_size;
    cuda_kernels::survival_probability_kernel<<<grid_size, block_size>>>(
        d_params, d_results, count);
    
    // Copy results back
    cudaMemcpy(h_results.data(), d_results, count * sizeof(SurvivalProbabilityResult),
               cudaMemcpyDeviceToHost);
    
    // Free device memory
    cudaFree(d_params);
    cudaFree(d_results);
    
    return h_results;
}

float SurvivalProbabilityMetric::compute_cumulative_hazard(float mean_return,
                                                          float volatility,
                                                          float time_horizon) const {
    if (volatility < 1e-10f) return 0.0f;
    
    float hazard = -mean_return * time_horizon / (volatility * volatility);
    return std::max(0.0f, -hazard);
}

float SurvivalProbabilityMetric::compute_structural_survival(float distance_to_default,
                                                            float volatility,
                                                            float time_horizon) const {
    if (distance_to_default <= 0.0f) return 0.0f;
    if (volatility < 1e-10f) return (distance_to_default > 1.0f) ? 1.0f : 0.0f;
    
    auto normal_cdf = [](float x) -> float {
        return 0.5f * (1.0f + std::erf(x / std::sqrt(2.0f)));
    };
    
    float var_t = volatility * volatility * time_horizon;
    float A_t = std::sqrt(var_t + 1e-10f);
    float log_d = std::log(distance_to_default + 1e-10f);
    
    float arg1 = -A_t / 2.0f + log_d / A_t;
    float term1 = normal_cdf(arg1);
    
    float arg2 = -A_t / 2.0f - log_d / A_t;
    float term2 = distance_to_default * normal_cdf(arg2);
    
    float survival = term1 - term2;
    
    return std::max(0.0f, std::min(1.0f, survival));
}

bool SurvivalProbabilityMetric::validate_sustainability_condition(float mean_return,
                                                                 float drift_premium) const {
    if (mean_return <= 0.0f) return false;
    
    return mean_return > drift_premium;
}

} // namespace risk_metrics
} // namespace tailwarp

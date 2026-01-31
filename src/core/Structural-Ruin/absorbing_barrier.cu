#include "absorbing_barrier.h"
#include <cmath>
#include <algorithm>
#include <iostream>

namespace tailwarp {
namespace risk_metrics {

// ============================================================================
// CUDA Kernels
// ============================================================================

namespace cuda_kernels {

/**
 * @brief Device function to compute stopping time
 * 
 * τ = inf{t > 0; X_t < L}
 * Approximated using Brownian motion first-passage time:
 * For drift-diffusion process: E[τ] ≈ -distance / drift (if drift < 0)
 * With volatility: τ ≈ (distance / |drift|) * sqrt(1 + (σ / |drift|)²)
 */
__device__ inline float compute_stopping_time(float current_distance, 
                                              float drift, 
                                              float volatility) {
    if (current_distance <= 0.0f) return 0.0f;
    
    // If drift is positive (moving away from barrier), stopping time is infinite
    if (drift >= 0.0f) {
        return 1e6f;  // Large value representing "very safe"
    }
    
    // If drift is negative (moving toward barrier)
    // Use first-passage time approximation
    float abs_drift = fabsf(drift);
    if (volatility < 1e-10f) {
        // Deterministic case: τ = distance / |drift|
        return current_distance / abs_drift;
    } else {
        // Stochastic case: adjust for volatility
        float vol_ratio = volatility / abs_drift;
        float adjustment = sqrtf(1.0f + vol_ratio * vol_ratio);
        return (current_distance / abs_drift) * adjustment;
    }
}

/**
 * @brief Device function to compute hazard rate
 * 
 * μ(τ) = -d/dτ log(S(τ))
 * Represents instantaneous probability density of failure at time τ
 * For Weibull-like survival: μ(τ) ≈ (1/scale) * (τ/scale)^(shape-1)
 */
__device__ inline float compute_hazard_rate(float stopping_time, 
                                           float current_distance,
                                           float volatility) {
    if (stopping_time <= 0.0f || current_distance <= 0.0f) return 1.0f;
    
    // Hazard rate increases as we approach stopping time
    // Normalized by stopping time and volatility
    float base_hazard = 1.0f / (stopping_time + 1e-10f);
    
    // Volatility reduces hazard (more buffer/randomness)
    float vol_factor = 1.0f / (1.0f + volatility / (current_distance + 1e-10f));
    
    return base_hazard * vol_factor;
}

/**
 * @brief Device function to compute survival probability
 * 
 * S(τ) = probability of surviving to time τ
 * Using exponential survival model: S(τ) = e^(-∫ μ(t) dt)
 */
__device__ inline float compute_survival_probability(float stopping_time) {
    if (stopping_time < 0.0f) return 0.0f;
    if (stopping_time > 100.0f) return 1.0f;  // Essentially 1.0 for large times
    
    // Approximate integral of hazard rate
    // S(τ) = exp(-τ / characteristic_time)
    return expf(-1.0f / (stopping_time + 1e-10f));
}

/**
 * @brief Device function to detect ergodicity breakdown
 * 
 * Non-ergodic regime: Single tail event > series of expected small losses
 * Metric compares: CVaR (tail impact) vs. accumulated drift (diffusion impact)
 * 
 * ergodicity_metric = min(1.0, (tail_impact) / (drift_impact + 1e-10))
 */
__device__ inline float compute_ergodicity_metric(float cvar_scale, 
                                                 float volatility,
                                                 float loss_frequency,
                                                 float average_loss) {
    // Tail impact: CVaR represents worst-case loss per event
    float tail_impact = cvar_scale;
    
    // Drift impact: expected loss per period
    float drift_impact = loss_frequency * average_loss;
    
    // Ratio: if > 1, tail dominates (non-ergodic)
    if (drift_impact < 1e-10f) return 1.0f;
    
    float ratio = tail_impact / (drift_impact + 1e-10f);
    
    // Normalize to [0, 1] where 1 = maximum non-ergodicity
    // ergodicity_metric = 1 / (1 + ratio)  -- inverted
    // So: high ratio -> low metric (non-ergodic) -> but we want high for non-ergodic
    // Let's use: min(1.0, ratio / (1.0 + ratio))
    return fminf(1.0f, ratio / (1.0f + ratio));
}

/**
 * @brief CUDA kernel for batch Absorbing Barrier calculation
 * 
 * Each thread processes one scenario independently.
 * Thread-block level cooperative load with grid-stride loop for scalability.
 */
__global__ void absorbing_barrier_kernel(const AbsorbingBarrierParameters* d_params,
                                         AbsorbingBarrierResult* d_results,
                                         size_t count) {
    
    unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x;
    
    if (idx >= count) return;
    
    const AbsorbingBarrierParameters& params = d_params[idx];
    AbsorbingBarrierResult& result = d_results[idx];
    
    // ========================================================================
    // Step 1: Distance to Barrier
    // ========================================================================
    // U(t) = current_value - barrier_level (surplus model)
    result.distance_to_barrier = params.current_value - params.barrier_level;
    
    // If already at/below barrier, immediate ruin
    if (result.distance_to_barrier <= 0.0f) {
        result.distance_to_barrier = 0.0f;
        result.distance_in_cvar_units = 0.0f;
        result.stopping_time_estimate = 0.0f;
        result.hazard_rate = 1.0f;
        result.survival_probability = 0.0f;
        result.lindy_expectancy = 0.0f;
        result.ergodicity_metric = 0.5f;
        result.is_ergodic = false;
        result.net_profit_valid = false;
        result.surplus_trajectory = result.distance_to_barrier;
        return;
    }
    
    // ========================================================================
    // Step 2: Distance in CVaR Units
    // ========================================================================
    // How many CVaR-scale losses can we absorb?
    if (params.cvar_scale > 1e-10f) {
        result.distance_in_cvar_units = result.distance_to_barrier / params.cvar_scale;
    } else {
        result.distance_in_cvar_units = 1e6f;
    }
    
    // ========================================================================
    // Step 3: Net Profit Condition
    // ========================================================================
    // Must have: inflow_rate > loss_frequency * average_loss
    // c > λ * μ_loss
    result.net_profit_valid = (params.inflow_rate > 
                              params.loss_frequency * params.average_loss);
    
    // ========================================================================
    // Step 4: Estimate Drift and Volatility for Cramér-Lundberg
    // ========================================================================
    // Drift: net inflow minus expected losses per period
    float drift = params.inflow_rate - 
                 (params.loss_frequency * params.average_loss);
    
    // Volatility: variance of loss process
    // Approximate as sqrt(loss_frequency) * average_loss
    float volatility = sqrtf(params.loss_frequency) * params.average_loss;
    
    // ========================================================================
    // Step 5: Stopping Time Estimate
    // ========================================================================
    // τ = inf{t > 0; X_t < L}
    result.stopping_time_estimate = compute_stopping_time(
        result.distance_to_barrier, 
        drift, 
        volatility
    );
    
    // ========================================================================
    // Step 6: Hazard Rate (Force of Mortality)
    // ========================================================================
    // μ(τ) = instantaneous risk at current state
    result.hazard_rate = compute_hazard_rate(
        result.stopping_time_estimate,
        result.distance_to_barrier,
        volatility
    );
    
    // Clamp to [0, 1]
    result.hazard_rate = fminf(1.0f, fmaxf(0.0f, result.hazard_rate));
    
    // ========================================================================
    // Step 7: Survival Probability
    // ========================================================================
    // S(τ) = Probability of not hitting barrier over time horizon
    result.survival_probability = compute_survival_probability(
        result.stopping_time_estimate
    );
    
    // ========================================================================
    // Step 8: Lindy Expectancy
    // ========================================================================
    // Time already survived (age) is the distance to barrier normalized
    float age = result.stopping_time_estimate > 0.0f ? 
               result.distance_to_barrier / (params.cvar_scale + 1e-10f) : 
               0.0f;
    
    // Lindy Effect: E[remaining_life | age] = age
    // (For power-law distributed lifetimes)
    result.lindy_expectancy = age;
    
    // ========================================================================
    // Step 9: Ergodicity Detection
    // ========================================================================
    // Non-ergodic regime: single tail event threatens survival more than drift
    result.ergodicity_metric = compute_ergodicity_metric(
        params.cvar_scale,
        volatility,
        params.loss_frequency,
        params.average_loss
    );
    
    // If ergodicity_metric is high (> 0.5), system is non-ergodic
    result.is_ergodic = (result.ergodicity_metric < 0.5f);
    
    // ========================================================================
    // Step 10: Surplus Trajectory
    // ========================================================================
    // Expected surplus at horizon: u + c*T - λ*μ_loss*T
    float expected_loss_over_horizon = params.loss_frequency * params.average_loss * 
                                       params.time_horizon;
    result.surplus_trajectory = result.distance_to_barrier + 
                               (params.inflow_rate * params.time_horizon) - 
                               expected_loss_over_horizon;
}

} // namespace cuda_kernels

// ============================================================================
// AbsorbingBarrier Class Implementation
// ============================================================================

AbsorbingBarrier::AbsorbingBarrier() {
    int device_count;
    cudaGetDeviceCount(&device_count);
    if (device_count > 0) {
        cudaSetDevice(0);
    }
}

AbsorbingBarrier::~AbsorbingBarrier() {
    // Cleanup if needed
}

/**
 * @brief CPU implementation (reference)
 */
AbsorbingBarrierResult AbsorbingBarrier::calculate_cpu(
    const AbsorbingBarrierParameters& params) const {
    
    AbsorbingBarrierResult result = {};
    
    // Step 1: Distance to Barrier
    result.distance_to_barrier = params.current_value - params.barrier_level;
    
    if (result.distance_to_barrier <= 0.0f) {
        result.distance_to_barrier = 0.0f;
        result.distance_in_cvar_units = 0.0f;
        result.stopping_time_estimate = 0.0f;
        result.hazard_rate = 1.0f;
        result.survival_probability = 0.0f;
        result.lindy_expectancy = 0.0f;
        result.ergodicity_metric = 0.5f;
        result.is_ergodic = false;
        result.net_profit_valid = false;
        result.surplus_trajectory = result.distance_to_barrier;
        return result;
    }
    
    // Step 2: Distance in CVaR Units
    if (params.cvar_scale > 1e-10f) {
        result.distance_in_cvar_units = result.distance_to_barrier / params.cvar_scale;
    } else {
        result.distance_in_cvar_units = 1e6f;
    }
    
    // Step 3: Net Profit Condition
    result.net_profit_valid = (params.inflow_rate > 
                              params.loss_frequency * params.average_loss);
    
    // Step 4: Estimate Drift and Volatility
    float drift = params.inflow_rate - 
                 (params.loss_frequency * params.average_loss);
    float volatility = std::sqrt(params.loss_frequency) * params.average_loss;
    
    // Step 5: Stopping Time
    result.stopping_time_estimate = estimate_stopping_time(
        result.distance_to_barrier, 
        drift, 
        volatility
    );
    
    // Step 6: Hazard Rate
    if (result.stopping_time_estimate > 0.0f) {
        float base_hazard = 1.0f / (result.stopping_time_estimate + 1e-10f);
        float vol_factor = 1.0f / (1.0f + volatility / (result.distance_to_barrier + 1e-10f));
        result.hazard_rate = std::min(1.0f, std::max(0.0f, base_hazard * vol_factor));
    } else {
        result.hazard_rate = 0.0f;
    }
    
    // Step 7: Survival Probability
    if (result.stopping_time_estimate > 100.0f) {
        result.survival_probability = 1.0f;
    } else if (result.stopping_time_estimate > 0.0f) {
        result.survival_probability = std::exp(-1.0f / (result.stopping_time_estimate + 1e-10f));
    } else {
        result.survival_probability = 0.0f;
    }
    
    // Step 8: Lindy Expectancy
    float age = result.stopping_time_estimate > 0.0f ? 
               result.distance_to_barrier / (params.cvar_scale + 1e-10f) : 
               0.0f;
    result.lindy_expectancy = age;
    
    // Step 9: Ergodicity Detection
    float tail_impact = params.cvar_scale;
    float drift_impact = params.loss_frequency * params.average_loss;
    float ratio = drift_impact > 1e-10f ? tail_impact / drift_impact : 1.0f;
    result.ergodicity_metric = std::min(1.0f, ratio / (1.0f + ratio));
    result.is_ergodic = (result.ergodicity_metric < 0.5f);
    
    // Step 10: Surplus Trajectory
    float expected_loss_over_horizon = params.loss_frequency * params.average_loss * 
                                       params.time_horizon;
    result.surplus_trajectory = result.distance_to_barrier + 
                               (params.inflow_rate * params.time_horizon) - 
                               expected_loss_over_horizon;
    
    return result;
}

/**
 * @brief GPU implementation (single call)
 */
AbsorbingBarrierResult AbsorbingBarrier::calculate_gpu(
    const AbsorbingBarrierParameters& params) const {
    
    AbsorbingBarrierParameters* d_params = nullptr;
    AbsorbingBarrierResult* d_results = nullptr;
    AbsorbingBarrierResult h_result = {};
    
    cudaMalloc(&d_params, sizeof(AbsorbingBarrierParameters));
    cudaMalloc(&d_results, sizeof(AbsorbingBarrierResult));
    
    cudaMemcpy(d_params, &params, sizeof(AbsorbingBarrierParameters), 
               cudaMemcpyHostToDevice);
    
    cuda_kernels::absorbing_barrier_kernel<<<1, 1>>>(d_params, d_results, 1);
    
    cudaMemcpy(&h_result, d_results, sizeof(AbsorbingBarrierResult), 
               cudaMemcpyDeviceToHost);
    
    cudaFree(d_params);
    cudaFree(d_results);
    
    return h_result;
}

/**
 * @brief Batch GPU implementation
 */
std::vector<AbsorbingBarrierResult> AbsorbingBarrier::calculate_gpu_batch(
    const AbsorbingBarrierParameters* params_array, 
    size_t count) const {
    
    AbsorbingBarrierParameters* d_params = nullptr;
    AbsorbingBarrierResult* d_results = nullptr;
    std::vector<AbsorbingBarrierResult> h_results(count);
    
    cudaMalloc(&d_params, count * sizeof(AbsorbingBarrierParameters));
    cudaMalloc(&d_results, count * sizeof(AbsorbingBarrierResult));
    
    cudaMemcpy(d_params, params_array, count * sizeof(AbsorbingBarrierParameters), 
               cudaMemcpyHostToDevice);
    
    int blockSize = 256;
    int gridSize = (count + blockSize - 1) / blockSize;
    
    cuda_kernels::absorbing_barrier_kernel<<<gridSize, blockSize>>>(
        d_params, d_results, count
    );
    
    cudaMemcpy(h_results.data(), d_results, count * sizeof(AbsorbingBarrierResult), 
               cudaMemcpyDeviceToHost);
    
    cudaFree(d_params);
    cudaFree(d_results);
    
    return h_results;
}

/**
 * @brief Validate Net Profit Condition
 */
bool AbsorbingBarrier::validate_net_profit_condition(float inflow_rate, 
                                                     float loss_frequency, 
                                                     float average_loss) const {
    return inflow_rate > loss_frequency * average_loss;
}

/**
 * @brief Estimate Stopping Time
 */
float AbsorbingBarrier::estimate_stopping_time(float current_distance, 
                                               float drift, 
                                               float volatility) const {
    if (current_distance <= 0.0f) return 0.0f;
    if (drift >= 0.0f) return 1e6f;
    
    float abs_drift = std::abs(drift);
    if (volatility < 1e-10f) {
        return current_distance / abs_drift;
    } else {
        float vol_ratio = volatility / abs_drift;
        float adjustment = std::sqrt(1.0f + vol_ratio * vol_ratio);
        return (current_distance / abs_drift) * adjustment;
    }
}

/**
 * @brief Calculate Lindy Expectancy
 */
float AbsorbingBarrier::calculate_lindy_expectancy(float age, 
                                                   float confidence_factor) const {
    if (age <= 0.0f) return 0.0f;
    // Lindy Effect: E[remaining_life | age] = age * confidence_factor
    return age * confidence_factor;
}

} // namespace risk_metrics
} // namespace tailwarp

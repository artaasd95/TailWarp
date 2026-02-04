#include "solvency_distance.h"
#include <cmath>
#include <algorithm>
#include <iostream>
#include <stdexcept>

namespace tailwarp {
namespace risk_metrics {

// ============================================================================
// CUDA Kernels
// ============================================================================

namespace cuda_kernels {

/**
 * @brief Device function to compute solvency distance
 * 
 * Core calculation: distance = (current_equity - barrier) / cvar_scale
 * 
 * @param current_equity Current portfolio value
 * @param absorbing_barrier Ruin threshold
 * @param cvar_scale CVaR magnitude (average tail loss)
 * @return Solvency distance as dimensionless count of tail events
 */
__device__ inline float compute_solvency_distance(float current_equity,
                                                  float absorbing_barrier,
                                                  float cvar_scale) {
    // Calculate capital buffer
    float buffer = current_equity - absorbing_barrier;
    
    // If already at or below barrier, distance is zero
    if (buffer <= 0.0f) {
        return 0.0f;
    }
    
    // If CVaR scale is invalid, return zero (cannot measure distance)
    if (cvar_scale <= 1e-10f) {
        return 0.0f;
    }
    
    // Calculate distance in units of CVaR
    float distance = buffer / cvar_scale;
    
    return distance;
}

/**
 * @brief Device function to compute normalized risk score
 * 
 * Maps distance to [0, 1] where 0 = critical, 1 = safe
 * Uses sigmoid-like function for smooth transitions between zones
 * 
 * Formula: score = 1 / (1 + exp(-k * (distance - midpoint)))
 * where k controls steepness and midpoint is between red and green
 */
__device__ inline float compute_risk_score(float distance,
                                          float red_threshold,
                                          float green_threshold) {
    // If distance is at or below red threshold, score is 0 (critical)
    if (distance <= red_threshold) {
        return 0.0f;
    }
    
    // If distance is at or above green threshold, score is 1 (safe)
    if (distance >= green_threshold) {
        return 1.0f;
    }
    
    // Linear interpolation between red and green thresholds
    float range = green_threshold - red_threshold;
    if (range <= 0.0f) {
        return 0.5f;  // Degenerate case
    }
    
    float normalized = (distance - red_threshold) / range;
    
    // Apply sigmoid for smooth transition
    // Using tanh for smooth S-curve: (tanh(x) + 1) / 2
    float x = (normalized - 0.5f) * 4.0f;  // Scale to [-2, 2] for good sigmoid shape
    float score = (tanhf(x) + 1.0f) * 0.5f;
    
    return score;
}

/**
 * @brief Device function to classify risk level
 * 
 * Determines if portfolio is in green/yellow/red zone based on distance
 * 
 * @param distance Solvency distance
 * @param config Configuration with thresholds
 * @param is_fragile Output: true if in yellow/red zone
 * @param is_critical Output: true if in red zone
 * @param risk_score Output: normalized risk score [0, 1]
 */
__device__ inline void classify_risk_level(float distance,
                                          const SolvencyDistanceConfig* config,
                                          bool& is_fragile,
                                          bool& is_critical,
                                          float& risk_score) {
    // Critical: distance < red threshold (cannot absorb even 1 tail event)
    is_critical = (distance < config->red_threshold);
    
    // Fragile: distance < yellow threshold (can absorb < 3 tail events)
    is_fragile = (distance < config->yellow_threshold);
    
    // Compute continuous risk score
    risk_score = compute_risk_score(distance, 
                                   config->red_threshold, 
                                   config->green_threshold);
}

/**
 * @brief CUDA kernel for batch Solvency Distance calculation
 * 
 * Each thread processes one scenario independently.
 * Thread-block level cooperative load with grid-stride loop for scalability.
 */
__global__ void solvency_distance_kernel(const SolvencyDistanceParameters* d_params,
                                         SolvencyDistanceResult* d_results,
                                         const SolvencyDistanceConfig* d_config,
                                         size_t count) {
    
    unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x;
    
    if (idx >= count) return;
    
    const SolvencyDistanceParameters& params = d_params[idx];
    SolvencyDistanceResult& result = d_results[idx];
    
    // ========================================================================
    // Step 1: Calculate Capital Buffer
    // ========================================================================
    // u = current_equity - absorbing_barrier
    result.current_capital_buffer = params.current_equity - params.absorbing_barrier;
    
    // ========================================================================
    // Step 2: Calculate Solvency Distance
    // ========================================================================
    // Solvency Distance = buffer / CVaR
    result.solvency_distance = compute_solvency_distance(
        params.current_equity,
        params.absorbing_barrier,
        params.cvar_scale
    );
    
    // Alternative representation: same value, explicit naming
    result.cvar_normalized_buffer = result.solvency_distance;
    
    // ========================================================================
    // Step 3: Store Thresholds for Reference
    // ========================================================================
    result.green_threshold = d_config->green_threshold;
    result.yellow_threshold = d_config->yellow_threshold;
    result.red_threshold = d_config->red_threshold;
    
    // ========================================================================
    // Step 4: Risk Classification
    // ========================================================================
    classify_risk_level(
        result.solvency_distance,
        d_config,
        result.is_fragile,
        result.is_critical,
        result.risk_score
    );
    
    // ========================================================================
    // Step 5: Calculate Distance to VaR (Optional Diagnostic)
    // ========================================================================
    if (params.var_threshold > 0.0f) {
        // How many VaR units away from barrier?
        if (params.var_threshold > 1e-10f) {
            result.distance_to_var = result.current_capital_buffer / params.var_threshold;
        } else {
            result.distance_to_var = 0.0f;
        }
    } else {
        result.distance_to_var = 0.0f;
    }
    
    // ========================================================================
    // Step 6: Calculate Relative Buffer Ratio (Optional Diagnostic)
    // ========================================================================
    // What percentage of current equity is the buffer?
    if (params.current_equity > 1e-10f) {
        result.relative_buffer_ratio = result.current_capital_buffer / params.current_equity;
    } else {
        result.relative_buffer_ratio = 0.0f;
    }
}

} // namespace cuda_kernels

// ============================================================================
// SolvencyDistance Class Implementation
// ============================================================================

SolvencyDistance::SolvencyDistance() {
    // Initialize with default configuration
    config_ = SolvencyDistanceConfig();
    
    // Check CUDA availability
    int device_count;
    cudaGetDeviceCount(&device_count);
    if (device_count > 0) {
        cudaSetDevice(0);
    }
}

SolvencyDistance::SolvencyDistance(const SolvencyDistanceConfig& config) 
    : config_(config) {
    // Check CUDA availability
    int device_count;
    cudaGetDeviceCount(&device_count);
    if (device_count > 0) {
        cudaSetDevice(0);
    }
}

SolvencyDistance::~SolvencyDistance() {
    // Cleanup if needed
}

/**
 * @brief Helper method to classify risk
 */
void SolvencyDistance::classify_risk(SolvencyDistanceResult& result, float distance) const {
    result.is_critical = (distance < config_.red_threshold);
    result.is_fragile = (distance < config_.yellow_threshold);
    result.risk_score = calculate_risk_score(distance);
}

/**
 * @brief Helper method to calculate risk score
 */
float SolvencyDistance::calculate_risk_score(float distance) const {
    // If distance is at or below red threshold, score is 0 (critical)
    if (distance <= config_.red_threshold) {
        return 0.0f;
    }
    
    // If distance is at or above green threshold, score is 1 (safe)
    if (distance >= config_.green_threshold) {
        return 1.0f;
    }
    
    // Linear interpolation between red and green thresholds
    float range = config_.green_threshold - config_.red_threshold;
    if (range <= 0.0f) {
        return 0.5f;  // Degenerate case
    }
    
    float normalized = (distance - config_.red_threshold) / range;
    
    // Apply sigmoid for smooth transition
    float x = (normalized - 0.5f) * 4.0f;
    float score = (std::tanh(x) + 1.0f) * 0.5f;
    
    return score;
}

/**
 * @brief CPU implementation
 */
SolvencyDistanceResult SolvencyDistance::calculate_cpu(
    const SolvencyDistanceParameters& params) const {
    
    SolvencyDistanceResult result = {};
    
    // Step 1: Calculate capital buffer
    result.current_capital_buffer = params.current_equity - params.absorbing_barrier;
    
    // Step 2: Calculate solvency distance
    if (result.current_capital_buffer <= 0.0f) {
        // Already at or below barrier
        result.solvency_distance = 0.0f;
        result.cvar_normalized_buffer = 0.0f;
    } else if (params.cvar_scale <= 1e-10f) {
        // Invalid CVaR scale
        result.solvency_distance = 0.0f;
        result.cvar_normalized_buffer = 0.0f;
    } else {
        // Normal case: buffer / CVaR
        result.solvency_distance = result.current_capital_buffer / params.cvar_scale;
        result.cvar_normalized_buffer = result.solvency_distance;
    }
    
    // Step 3: Store thresholds
    result.green_threshold = config_.green_threshold;
    result.yellow_threshold = config_.yellow_threshold;
    result.red_threshold = config_.red_threshold;
    
    // Step 4: Risk classification
    classify_risk(result, result.solvency_distance);
    
    // Step 5: Distance to VaR (optional diagnostic)
    if (params.var_threshold > 1e-10f) {
        result.distance_to_var = result.current_capital_buffer / params.var_threshold;
    } else {
        result.distance_to_var = 0.0f;
    }
    
    // Step 6: Relative buffer ratio
    if (params.current_equity > 1e-10f) {
        result.relative_buffer_ratio = result.current_capital_buffer / params.current_equity;
    } else {
        result.relative_buffer_ratio = 0.0f;
    }
    
    return result;
}

/**
 * @brief GPU implementation (single calculation)
 */
SolvencyDistanceResult SolvencyDistance::calculate_gpu(
    const SolvencyDistanceParameters& params) const {
    
    // Allocate device memory
    SolvencyDistanceParameters* d_params;
    SolvencyDistanceResult* d_results;
    SolvencyDistanceConfig* d_config;
    
    cudaMalloc(&d_params, sizeof(SolvencyDistanceParameters));
    cudaMalloc(&d_results, sizeof(SolvencyDistanceResult));
    cudaMalloc(&d_config, sizeof(SolvencyDistanceConfig));
    
    // Copy input data to device
    cudaMemcpy(d_params, &params, sizeof(SolvencyDistanceParameters), cudaMemcpyHostToDevice);
    cudaMemcpy(d_config, &config_, sizeof(SolvencyDistanceConfig), cudaMemcpyHostToDevice);
    
    // Launch kernel with single thread
    cuda_kernels::solvency_distance_kernel<<<1, 1>>>(d_params, d_results, d_config, 1);
    
    // Copy result back to host
    SolvencyDistanceResult result;
    cudaMemcpy(&result, d_results, sizeof(SolvencyDistanceResult), cudaMemcpyDeviceToHost);
    
    // Cleanup
    cudaFree(d_params);
    cudaFree(d_results);
    cudaFree(d_config);
    
    return result;
}

/**
 * @brief GPU batch implementation
 */
std::vector<SolvencyDistanceResult> SolvencyDistance::calculate_gpu_batch(
    const SolvencyDistanceParameters* params_array,
    size_t count) const {
    
    if (count == 0) {
        return std::vector<SolvencyDistanceResult>();
    }
    
    // Allocate device memory
    SolvencyDistanceParameters* d_params;
    SolvencyDistanceResult* d_results;
    SolvencyDistanceConfig* d_config;
    
    cudaMalloc(&d_params, count * sizeof(SolvencyDistanceParameters));
    cudaMalloc(&d_results, count * sizeof(SolvencyDistanceResult));
    cudaMalloc(&d_config, sizeof(SolvencyDistanceConfig));
    
    // Copy input data to device
    cudaMemcpy(d_params, params_array, count * sizeof(SolvencyDistanceParameters), 
               cudaMemcpyHostToDevice);
    cudaMemcpy(d_config, &config_, sizeof(SolvencyDistanceConfig), cudaMemcpyHostToDevice);
    
    // Launch kernel with appropriate grid/block dimensions
    int threads_per_block = 256;
    int blocks = (count + threads_per_block - 1) / threads_per_block;
    
    cuda_kernels::solvency_distance_kernel<<<blocks, threads_per_block>>>(
        d_params, d_results, d_config, count);
    
    // Copy results back to host
    std::vector<SolvencyDistanceResult> results(count);
    cudaMemcpy(results.data(), d_results, count * sizeof(SolvencyDistanceResult), 
               cudaMemcpyDeviceToHost);
    
    // Cleanup
    cudaFree(d_params);
    cudaFree(d_results);
    cudaFree(d_config);
    
    return results;
}

/**
 * @brief Update configuration
 */
void SolvencyDistance::set_config(const SolvencyDistanceConfig& config) {
    config_ = config;
}

/**
 * @brief Get current configuration
 */
SolvencyDistanceConfig SolvencyDistance::get_config() const {
    return config_;
}

/**
 * @brief Validate input parameters
 */
bool SolvencyDistance::validate_parameters(const SolvencyDistanceParameters& params) {
    // Current equity must be positive
    if (params.current_equity <= 0.0f) {
        return false;
    }
    
    // Absorbing barrier must be less than current equity (otherwise already ruined)
    if (params.absorbing_barrier >= params.current_equity) {
        return false;
    }
    
    // CVaR scale must be positive
    if (params.cvar_scale <= 0.0f) {
        return false;
    }
    
    // Confidence level must be in (0, 1)
    if (params.confidence_level <= 0.0f || params.confidence_level >= 1.0f) {
        return false;
    }
    
    return true;
}

/**
 * @brief Calculate CVaR from loss distribution (helper function)
 * 
 * This is a utility function to compute CVaR from raw loss data.
 * CVaR_α = E[L | L >= VaR_α]
 */
float SolvencyDistance::calculate_cvar_from_losses(const float* losses,
                                                   size_t count,
                                                   float confidence_level) {
    if (count == 0 || losses == nullptr) {
        return 0.0f;
    }
    
    // Copy and sort losses in descending order
    std::vector<float> sorted_losses(losses, losses + count);
    std::sort(sorted_losses.begin(), sorted_losses.end(), std::greater<float>());
    
    // Find VaR threshold index
    size_t var_index = static_cast<size_t>((1.0f - confidence_level) * count);
    if (var_index >= count) {
        var_index = count - 1;
    }
    
    // Calculate average of tail losses (all losses >= VaR)
    float cvar_sum = 0.0f;
    size_t tail_count = var_index + 1;
    
    for (size_t i = 0; i < tail_count; ++i) {
        cvar_sum += sorted_losses[i];
    }
    
    float cvar = cvar_sum / static_cast<float>(tail_count);
    
    return cvar;
}

} // namespace risk_metrics
} // namespace tailwarp

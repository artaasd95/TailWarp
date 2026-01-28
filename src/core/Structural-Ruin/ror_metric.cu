#include "ror_metric.h"
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
 * @brief Device function to compute Lundberg adjustment coefficient
 * 
 * R = 2 * mean_return / variance
 * 
 * This coefficient captures the relative heaviness of tail losses versus profit drift.
 * Higher R indicates a more stable, less risky strategy.
 */
__device__ inline float compute_lundberg_coefficient(float mean_return, float variance) {
    if (variance < 1e-10f) return 0.0f;
    return 2.0f * mean_return / variance;
}

/**
 * @brief Device function to compute ruin probability
 * 
 * ψ = exp(-R * u)
 * 
 * Where:
 *   R: Lundberg adjustment coefficient
 *   u: Current capital (distance to absorbing barrier)
 */
__device__ inline float compute_ruin_probability(float R, float current_capital) {
    if (R <= 0.0f || current_capital <= 0.0f) return 1.0f;
    return expf(-R * current_capital);
}

/**
 * @brief CUDA kernel for batch RoR calculation
 * 
 * Each thread processes one scenario independently.
 * Computes:
 *   1. Lundberg Adjustment Coefficient (R)
 *   2. Ruin Probability (ψ)
 *   3. Survival Score (1 - ψ)
 *   4. Safety check against threshold
 *   5. Solvency distance estimation
 */
__global__ void ror_kernel(const RoRParameters* d_params,
                           RoRResult* d_results,
                           size_t count) {
    
    unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x;
    
    if (idx >= count) return;
    
    const RoRParameters& params = d_params[idx];
    RoRResult& result = d_results[idx];
    
    // Net Profit Condition check: mean_return must be positive
    if (params.mean_return <= 0.0f) {
        result.lundberg_coefficient = 0.0f;
        result.ruin_probability = 1.0f;
        result.survival_score = 0.0f;
        result.is_safe = false;
        result.solvency_distance = 0.0f;
        return;
    }
    
    // Step 1: Calculate Lundberg Adjustment Coefficient
    // R = 2 * mean_return / variance
    result.lundberg_coefficient = compute_lundberg_coefficient(params.mean_return, 
                                                                params.variance);
    
    // Step 2: Calculate Ruin Probability
    // ψ = exp(-R * u)
    result.ruin_probability = compute_ruin_probability(result.lundberg_coefficient, 
                                                        params.current_capital);
    
    // Clamp ruin probability to [0, 1]
    result.ruin_probability = fminf(1.0f, fmaxf(0.0f, result.ruin_probability));
    
    // Step 3: Calculate Survival Score
    // Survival_Score = 1 - ψ
    result.survival_score = 1.0f - result.ruin_probability;
    
    // Step 4: Safety check
    // Trade is safe if ruin_probability < threshold
    result.is_safe = (result.ruin_probability < params.ruin_threshold);
    
    // Step 5: Calculate Solvency Distance
    // How many average losses can be taken before ruin?
    // solvency_distance = current_capital / |expected_loss|
    // where expected_loss is estimated from variance and mean
    if (params.variance > 1e-10f) {
        // Approximate worst-case loss as mean - 2*std_dev
        float std_dev = sqrtf(params.variance);
        float worst_case_loss = fmaxf(std_dev, 0.1f * params.mean_return);
        result.solvency_distance = params.current_capital / worst_case_loss;
    } else {
        result.solvency_distance = __float2int_ru(params.current_capital);
    }
}

} // namespace cuda_kernels

// ============================================================================
// RoRMetric Class Implementation
// ============================================================================

RoRMetric::RoRMetric() {
    // Initialize CUDA device if available
    int device_count;
    cudaGetDeviceCount(&device_count);
    if (device_count > 0) {
        cudaSetDevice(0);
    }
}

RoRMetric::~RoRMetric() {
    // Cleanup if needed
}

/**
 * @brief CPU implementation of RoR calculation
 * 
 * This is the reference implementation. GPU version should produce identical results
 * (within floating-point precision).
 */
RoRResult RoRMetric::calculate_cpu(const RoRParameters& params) const {
    RoRResult result = {};
    
    // Net Profit Condition: mean_return must be positive
    if (params.mean_return <= 0.0f) {
        result.lundberg_coefficient = 0.0f;
        result.ruin_probability = 1.0f;
        result.survival_score = 0.0f;
        result.is_safe = false;
        result.solvency_distance = 0.0f;
        return result;
    }
    
    // Step 1: Calculate Lundberg Adjustment Coefficient
    // R = 2 * mean_return / variance
    if (params.variance < 1e-10f) {
        result.lundberg_coefficient = 0.0f;
        result.ruin_probability = 1.0f;
        result.survival_score = 0.0f;
        result.is_safe = false;
        result.solvency_distance = 0.0f;
        return result;
    }
    
    result.lundberg_coefficient = 2.0f * params.mean_return / params.variance;
    
    // Step 2: Calculate Ruin Probability
    // ψ = exp(-R * u)
    if (result.lundberg_coefficient <= 0.0f || params.current_capital <= 0.0f) {
        result.ruin_probability = 1.0f;
    } else {
        result.ruin_probability = std::exp(-result.lundberg_coefficient * params.current_capital);
    }
    
    // Clamp to [0, 1]
    result.ruin_probability = std::min(1.0f, std::max(0.0f, result.ruin_probability));
    
    // Step 3: Calculate Survival Score
    result.survival_score = 1.0f - result.ruin_probability;
    
    // Step 4: Safety check against threshold
    result.is_safe = (result.ruin_probability < params.ruin_threshold);
    
    // Step 5: Calculate Solvency Distance
    float std_dev = std::sqrt(params.variance);
    float worst_case_loss = std::max(std_dev, 0.1f * params.mean_return);
    result.solvency_distance = params.current_capital / worst_case_loss;
    
    return result;
}

/**
 * @brief GPU implementation of RoR calculation
 */
RoRResult RoRMetric::calculate_gpu(const RoRParameters& params) const {
    RoRParameters* d_params;
    RoRResult* d_results;
    RoRResult h_result = {};
    
    // Allocate device memory
    cudaMalloc(&d_params, sizeof(RoRParameters));
    cudaMalloc(&d_results, sizeof(RoRResult));
    
    // Copy data to device
    cudaMemcpy(d_params, &params, sizeof(RoRParameters), cudaMemcpyHostToDevice);
    
    // Launch kernel with 1 block, 1 thread for single calculation
    cuda_kernels::ror_kernel<<<1, 1>>>(d_params, d_results, 1);
    
    // Copy result back to host
    cudaMemcpy(&h_result, d_results, sizeof(RoRResult), cudaMemcpyDeviceToHost);
    
    // Free device memory
    cudaFree(d_params);
    cudaFree(d_results);
    
    return h_result;
}

/**
 * @brief Batch GPU calculation for multiple scenarios
 * 
 * More efficient than single calculations as it amortizes kernel launch overhead.
 */
std::vector<RoRResult> RoRMetric::calculate_gpu_batch(const RoRParameters* params_array,
                                                      size_t count) const {
    RoRParameters* d_params;
    RoRResult* d_results;
    std::vector<RoRResult> h_results(count);
    
    // Allocate device memory
    cudaMalloc(&d_params, count * sizeof(RoRParameters));
    cudaMalloc(&d_results, count * sizeof(RoRResult));
    
    // Copy data to device
    cudaMemcpy(d_params, params_array, count * sizeof(RoRParameters), 
               cudaMemcpyHostToDevice);
    
    // Launch kernel with enough blocks for all scenarios
    int block_size = 256;
    int grid_size = (count + block_size - 1) / block_size;
    cuda_kernels::ror_kernel<<<grid_size, block_size>>>(d_params, d_results, count);
    
    // Copy results back to host
    cudaMemcpy(h_results.data(), d_results, count * sizeof(RoRResult), 
               cudaMemcpyDeviceToHost);
    
    // Free device memory
    cudaFree(d_params);
    cudaFree(d_results);
    
    return h_results;
}

/**
 * @brief Validate the Net Profit Condition
 * 
 * This is a prerequisite check: if your expected loss rate exceeds your edge,
 * you will eventually go broke with 100% probability, regardless of starting capital.
 * 
 * Condition: mean_return > loss_frequency * average_loss
 */
bool RoRMetric::validate_net_profit_condition(float mean_return,
                                               float loss_frequency,
                                               float average_loss) const {
    if (mean_return <= 0.0f) return false;
    
    float expected_loss_rate = loss_frequency * average_loss;
    return mean_return > expected_loss_rate;
}

} // namespace risk_metrics
} // namespace tailwarp

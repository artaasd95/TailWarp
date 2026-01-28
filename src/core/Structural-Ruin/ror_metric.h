#ifndef TAILWARP_ROR_METRIC_H
#define TAILWARP_ROR_METRIC_H

#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <cmath>
#include <vector>

/**
 * @file ror_metric.h
 * @brief Risk of Ruin (RoR) Metric Implementation
 * 
 * This module implements the Risk of Ruin metric based on the Cramér-Lundberg model.
 * It quantifies the probability of hitting an absorbing barrier (capital = 0) using
 * the Lundberg Inequality approximation.
 * 
 * Mathematical Foundation:
 * - Survival Score = 1 - exp(-2 * mean_return * current_capital / variance)
 * - Lundberg Adjustment Coefficient: R = 2 * mean_return / variance
 * - Ruin Probability: ψ = exp(-R * u)
 */

namespace tailwarp {
namespace risk_metrics {

/**
 * @struct RoRParameters
 * @brief Parameters required for RoR calculation
 */
struct RoRParameters {
    float mean_return;        // μ: Average daily/per-trade PnL
    float variance;           // σ²: Variance of PnL distribution
    float current_capital;    // u: Current account equity (distance to ruin barrier)
    float ruin_threshold;     // Ruin probability threshold for rejection (default: 0.01 = 1%)
};

/**
 * @struct RoRResult
 * @brief Output of RoR calculation
 */
struct RoRResult {
    float lundberg_coefficient;  // R: Adjustment coefficient
    float ruin_probability;      // ψ: Probability of ruin
    float survival_score;        // 1 - ψ: Probability of survival
    bool is_safe;               // Whether ψ < ruin_threshold
    float solvency_distance;    // Number of avg losses before ruin
};

/**
 * @class RoRMetric
 * @brief CPU/GPU Risk of Ruin metric calculator
 * 
 * Provides both CPU and GPU implementations for calculating Risk of Ruin
 * using the Lundberg Inequality approximation.
 */
class RoRMetric {
public:
    RoRMetric();
    ~RoRMetric();
    
    /**
     * @brief Calculate RoR on CPU
     * @param params RoR parameters
     * @return RoRResult containing ruin probability and survival metrics
     */
    RoRResult calculate_cpu(const RoRParameters& params) const;
    
    /**
     * @brief Calculate RoR on GPU (CUDA)
     * @param params RoR parameters
     * @return RoRResult containing ruin probability and survival metrics
     */
    RoRResult calculate_gpu(const RoRParameters& params) const;
    
    /**
     * @brief Batch calculate RoR for multiple scenarios on GPU
     * @param params_array Array of RoR parameters
     * @param count Number of scenarios
     * @return Vector of RoRResult
     */
    std::vector<RoRResult> calculate_gpu_batch(const RoRParameters* params_array, 
                                                 size_t count) const;
    
    /**
     * @brief Validate net profit condition
     * @param mean_return Average return
     * @param loss_frequency λ: Frequency of losses
     * @param average_loss μ_loss: Average magnitude of loss
     * @return true if mean_return > loss_frequency * average_loss
     */
    bool validate_net_profit_condition(float mean_return, 
                                        float loss_frequency, 
                                        float average_loss) const;
};

// CUDA kernel declarations
namespace cuda_kernels {

/**
 * @brief CUDA kernel for single RoR calculation
 */
__global__ void ror_kernel(const RoRParameters* d_params,
                           RoRResult* d_results,
                           size_t count);

/**
 * @brief Helper kernel to compute Lundberg coefficient
 */
__device__ float compute_lundberg_coefficient(float mean_return, float variance);

/**
 * @brief Helper kernel to compute ruin probability
 */
__device__ float compute_ruin_probability(float R, float current_capital);

} // namespace cuda_kernels

} // namespace risk_metrics
} // namespace tailwarp

#endif // TAILWARP_ROR_METRIC_H

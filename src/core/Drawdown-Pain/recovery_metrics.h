#ifndef TAILWARP_RECOVERY_METRICS_H
#define TAILWARP_RECOVERY_METRICS_H

#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <cmath>
#include <vector>
#include <cstddef>

/**
 * @file recovery_metrics.h
 * @brief Recovery and Resilience Metrics Implementation
 *
 * This module provides three complementary metrics for evaluating recovery from losses:
 *
 * 1. **Calmar Ratio**: Annualized return divided by maximum drawdown.
 *    Answers: "How much return am I earning per unit of worst-case loss?"
 *
 * 2. **Recovery Time**: Duration (in periods) for equity to recover from a drawdown.
 *    Answers: "How long am I stuck underwater after a peak?"
 *
 * 3. **Recovery Factor**: Total net profit divided by maximum drawdown.
 *    Answers: "How many times have I earned back my worst loss?"
 *
 * These metrics focus on **capital regeneration** and **persistence of losses**,
 * treating risk as realized loss and time impairment, not volatility.
 */

namespace tailwarp {
namespace risk_metrics {

// ============================================================================
// Calmar Ratio
// ============================================================================

/**
 * @struct CalmarRatioParameters
 * @brief Input parameters for Calmar Ratio calculation
 */
struct CalmarRatioParameters {
    const float* equity_curve;      // Array of equity values over time
    size_t curve_length;            // Number of data points
    float initial_capital;          // Starting equity (V_0)
    float time_years;               // Time period in years for annualization
};

/**
 * @struct CalmarRatioResult
 * @brief Output of Calmar Ratio calculation
 */
struct CalmarRatioResult {
    float annualized_return;        // Annualized return as decimal (e.g., 0.15 for 15%)
    float annualized_return_pct;    // Annualized return as percentage
    float maximum_drawdown;         // Maximum drawdown as percentage
    float calmar_ratio;             // Annualized Return / Maximum Drawdown
    float final_value;              // Final equity value
    size_t peak_index;              // Index of peak before max drawdown
    size_t trough_index;            // Index of trough of max drawdown
};

/**
 * @class CalmarRatio
 * @brief Calculates Calmar Ratio: return efficiency per unit of worst loss
 *
 * Interpretation:
 * - > 2.0: Excellent risk-adjusted performance
 * - 1.0 - 2.0: Acceptable
 * - < 1.0: Insufficient compensation for drawdown risk
 */
class CalmarRatio {
public:
    CalmarRatio();
    ~CalmarRatio();

    /**
     * @brief Calculate Calmar Ratio on CPU
     * @param params Input parameters
     * @return CalmarRatioResult
     */
    CalmarRatioResult calculate_cpu(const CalmarRatioParameters& params) const;

    /**
     * @brief Calculate Calmar Ratio on GPU (CUDA)
     * @param params Input parameters
     * @return CalmarRatioResult
     */
    CalmarRatioResult calculate_gpu(const CalmarRatioParameters& params) const;
};

// ============================================================================
// Recovery Time
// ============================================================================

/**
 * @struct RecoveryTimeParameters
 * @brief Input parameters for Recovery Time calculation
 */
struct RecoveryTimeParameters {
    const float* equity_curve;      // Array of equity values over time
    size_t curve_length;            // Number of data points
};

/**
 * @struct RecoveryTimeResult
 * @brief Output of Recovery Time calculation
 */
struct RecoveryTimeResult {
    float mean_recovery_time;       // Average recovery time across all drawdown events
    float max_recovery_time;        // Longest recovery time observed
    size_t num_drawdown_events;     // Number of distinct drawdown events detected
    size_t longest_recovery_peak_idx;   // Peak index associated with longest recovery
    size_t longest_recovery_trough_idx; // Trough index of longest recovery
    size_t longest_recovery_end_idx;    // End index where recovery completed
};

/**
 * @class RecoveryTime
 * @brief Measures duration of drawdowns and time to recover
 *
 * Evaluates resilience by examining how long capital remains impaired
 * after peaks are reached.
 */
class RecoveryTime {
public:
    RecoveryTime();
    ~RecoveryTime();

    /**
     * @brief Calculate Recovery Time on CPU
     * @param params Input parameters
     * @return RecoveryTimeResult
     */
    RecoveryTimeResult calculate_cpu(const RecoveryTimeParameters& params) const;

    /**
     * @brief Calculate Recovery Time on GPU (CUDA)
     * @param params Input parameters
     * @return RecoveryTimeResult
     */
    RecoveryTimeResult calculate_gpu(const RecoveryTimeParameters& params) const;
};

// ============================================================================
// Recovery Factor
// ============================================================================

/**
 * @struct RecoveryFactorParameters
 * @brief Input parameters for Recovery Factor calculation
 */
struct RecoveryFactorParameters {
    const float* equity_curve;      // Array of equity values over time
    size_t curve_length;            // Number of data points
    float initial_capital;          // Starting equity (V_0)
};

/**
 * @struct RecoveryFactorResult
 * @brief Output of Recovery Factor calculation
 */
struct RecoveryFactorResult {
    float net_profit;               // Total profit (V_T - V_0)
    float net_profit_pct;           // Net profit as percentage
    float maximum_drawdown;         // Maximum drawdown as percentage
    float maximum_drawdown_absolute;// Maximum drawdown in absolute terms
    float recovery_factor;          // Net Profit / Maximum Drawdown (absolute)
    float final_value;              // Final equity value
    size_t peak_index;              // Index of peak before max drawdown
    size_t trough_index;            // Index of trough of max drawdown
};

/**
 * @class RecoveryFactor
 * @brief Calculates Recovery Factor: earning power vs. worst loss
 *
 * Interpretation:
 * - > 3-5: Strong recovery capability
 * - 1-3: Acceptable
 * - < 1: Weak recovery, risk of stagnation
 */
class RecoveryFactor {
public:
    RecoveryFactor();
    ~RecoveryFactor();

    /**
     * @brief Calculate Recovery Factor on CPU
     * @param params Input parameters
     * @return RecoveryFactorResult
     */
    RecoveryFactorResult calculate_cpu(const RecoveryFactorParameters& params) const;

    /**
     * @brief Calculate Recovery Factor on GPU (CUDA)
     * @param params Input parameters
     * @return RecoveryFactorResult
     */
    RecoveryFactorResult calculate_gpu(const RecoveryFactorParameters& params) const;
};

// ============================================================================
// CUDA Kernel Declarations
// ============================================================================

namespace cuda_kernels {

/**
 * @brief CUDA kernel for Calmar Ratio calculation
 */
__global__ void calmar_ratio_kernel(const float* d_equity_curve,
                                    size_t curve_length,
                                    float initial_capital,
                                    float time_years,
                                    CalmarRatioResult* d_result);

/**
 * @brief CUDA kernel for Recovery Time calculation
 */
__global__ void recovery_time_kernel(const float* d_equity_curve,
                                     size_t curve_length,
                                     RecoveryTimeResult* d_result);

/**
 * @brief CUDA kernel for Recovery Factor calculation
 */
__global__ void recovery_factor_kernel(const float* d_equity_curve,
                                       size_t curve_length,
                                       float initial_capital,
                                       RecoveryFactorResult* d_result);

/**
 * @brief Device function to compute maximum drawdown (MDD)
 *
 * Returns MDD percentage, absolute value, and indices
 */
__device__ inline void compute_mdd_device(const float* equity_curve,
                                          size_t curve_length,
                                          float& out_mdd_pct,
                                          float& out_mdd_absolute,
                                          size_t& out_peak_idx,
                                          size_t& out_trough_idx);

/**
 * @brief Device function to find recovery indices after a drawdown
 *
 * Identifies when equity recovers to or above peak value
 */
__device__ inline size_t find_recovery_idx_device(const float* equity_curve,
                                                  size_t curve_length,
                                                  size_t trough_idx,
                                                  float peak_value);

} // namespace cuda_kernels

} // namespace risk_metrics
} // namespace tailwarp

#endif // TAILWARP_RECOVERY_METRICS_H

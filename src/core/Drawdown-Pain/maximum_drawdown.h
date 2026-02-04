#ifndef TAILWARP_MAXIMUM_DRAWDOWN_H
#define TAILWARP_MAXIMUM_DRAWDOWN_H

#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <cmath>
#include <vector>

/**
 * @file maximum_drawdown.h
 * @brief Maximum Drawdown (MDD) Metric Implementation
 * 
 * Maximum Drawdown represents the largest peak-to-trough decline in the value of an equity
 * curve over a specific time horizon. It measures the worst-case scenario an investor could
 * have faced during a given period.
 * 
 * Mathematical Foundation:
 * MDD = max_i(S_i - min_j(S_j | j > i))
 * 
 * Where:
 * - S_i is the peak value at time i
 * - min_j(S_j | j > i) is the lowest trough after that peak
 * 
 * Key Concepts:
 * - Peak-to-Trough Excursion: Measures the deepest hole the equity curve fell into
 * - Fat-Tail Awareness: In real markets, deep drawdowns are more common than Gaussian models predict
 * - Worst-Case Scenario: Represents the absolute worst entry/exit combination for a holding period
 */

namespace tailwarp {
namespace risk_metrics {

/**
 * @struct MaximumDrawdownParameters
 * @brief Input parameters for Maximum Drawdown calculation
 */
struct MaximumDrawdownParameters {
    const float* equity_curve;      // Array of equity values over time
    size_t curve_length;            // Number of data points
    bool use_percentage;            // If true, return MDD as percentage; if false, as absolute value
};

/**
 * @struct MaximumDrawdownResult
 * @brief Output of Maximum Drawdown calculation
 */
struct MaximumDrawdownResult {
    float mdd_value;                // Maximum drawdown (in absolute or percentage terms)
    float mdd_percentage;           // Maximum drawdown as percentage
    size_t peak_index;              // Index of the peak before the drawdown
    size_t trough_index;            // Index of the trough (lowest point)
    float peak_value;               // Equity value at the peak
    float trough_value;             // Equity value at the trough
    
    // Additional diagnostic information
    float recovery_percentage;      // Percentage gain needed to recover from MDD
    size_t time_to_recovery;        // Number of periods from trough to recovery (or max index if not recovered)
    bool fully_recovered;           // Whether equity exceeded peak before end of period
};

/**
 * @class MaximumDrawdown
 * @brief CPU/GPU Maximum Drawdown metric calculator
 * 
 * Implements peak-to-trough analysis with identification of worst-case scenarios.
 */
class MaximumDrawdown {
public:
    MaximumDrawdown();
    ~MaximumDrawdown();
    
    /**
     * @brief Calculate Maximum Drawdown on CPU
     * @param params Input parameters (equity curve and length)
     * @return MaximumDrawdownResult containing MDD value, peak/trough indices, and recovery info
     */
    MaximumDrawdownResult calculate_cpu(const MaximumDrawdownParameters& params) const;
    
    /**
     * @brief Calculate Maximum Drawdown on GPU (CUDA)
     * @param params Input parameters
     * @return MaximumDrawdownResult
     */
    MaximumDrawdownResult calculate_gpu(const MaximumDrawdownParameters& params) const;
    
    /**
     * @brief Batch calculate Maximum Drawdown for multiple equity curves on GPU
     * @param params_array Array of parameter sets (each curve can have different length)
     * @param count Number of curves
     * @return Vector of MaximumDrawdownResult
     */
    std::vector<MaximumDrawdownResult> calculate_gpu_batch(
        const MaximumDrawdownParameters* params_array,
        size_t count) const;
    
    /**
     * @brief Find the recovery index after a drawdown
     * @param equity_curve Array of equity values
     * @param curve_length Length of array
     * @param peak_index Index of peak before drawdown
     * @param peak_value Value at peak
     * @param start_from_index Index to start searching for recovery
     * @return Index where equity recovers to peak value, or curve_length if not recovered
     */
    static size_t find_recovery_index(const float* equity_curve,
                                      size_t curve_length,
                                      size_t peak_index,
                                      float peak_value,
                                      size_t start_from_index);
};

// CUDA kernel declarations
namespace cuda_kernels {

/**
 * @brief CUDA kernel for Maximum Drawdown calculation (single curve)
 * 
 * Each thread block processes one equity curve.
 * Uses parallel reduction to find maximum drawdown efficiently.
 */
__global__ void maximum_drawdown_kernel(const float* d_equity_curve,
                                        size_t curve_length,
                                        MaximumDrawdownResult* d_result,
                                        bool use_percentage);

/**
 * @brief Device function to compute maximum drawdown
 * 
 * Scans through equity curve to find peak-to-trough maximum.
 */
__device__ inline void compute_mdd(const float* equity_curve,
                                   size_t curve_length,
                                   float& out_mdd,
                                   size_t& out_peak_idx,
                                   size_t& out_trough_idx);

} // namespace cuda_kernels

} // namespace risk_metrics
} // namespace tailwarp

#endif // TAILWARP_MAXIMUM_DRAWDOWN_H

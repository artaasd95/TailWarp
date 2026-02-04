#ifndef TAILWARP_ULCER_INDEX_H
#define TAILWARP_ULCER_INDEX_H

#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <cmath>
#include <vector>

/**
 * @file ulcer_index.h
 * @brief Ulcer Index (UI) Metric Implementation
 * 
 * The Ulcer Index is a downside-only risk metric that calculates the Root-Mean-Square (RMS)
 * of percentage drawdowns. Unlike standard deviation (which treats upside and downside equally),
 * UI only penalizes downside moves and disproportionately penalizes deeper, longer-lasting declines.
 * 
 * Mathematical Foundation:
 * UI = sqrt((1/n) * sum(D_i^2))
 * 
 * Where:
 * - D_i is the percentage drawdown at time i
 * - D_i = (Current Value - Running High) / Running High * 100
 * - n is the number of observations
 * 
 * Key Concepts:
 * - Downside-Only: Ignores upside volatility, only measures underwater periods
 * - Psychological Pain: Squaring amplifies the impact of severe declines
 * - Experienced Risk: Aligns mathematical metric with investor psychology
 */

namespace tailwarp {
namespace risk_metrics {

/**
 * @struct UlcerIndexParameters
 * @brief Input parameters for Ulcer Index calculation
 */
struct UlcerIndexParameters {
    const float* equity_curve;      // Array of equity values over time
    size_t curve_length;            // Number of data points
};

/**
 * @struct UlcerIndexResult
 * @brief Output of Ulcer Index calculation
 */
struct UlcerIndexResult {
    float ulcer_index;              // Primary metric: RMS of percentage drawdowns
    float average_drawdown_depth;   // Average percentage drawdown when underwater
    float max_underwater_percentage; // Maximum percentage drawdown reached
    
    // Distribution of underwater states
    size_t observations_in_drawdown;    // Number of periods underwater
    float percentage_time_underwater;   // Fraction of time in drawdown
    
    // Additional statistics
    float std_of_drawdowns;         // Standard deviation of drawdown percentages
    float cumulative_squareddd;     // Sum of squared drawdowns (numerator of UI formula)
    
    // Severity classification
    bool is_high_pain;              // True if UI > 15 (severe chronic stress)
    float pain_intensity_score;     // Normalized score 0-100 based on UI
};

/**
 * @class UlcerIndex
 * @brief CPU/GPU Ulcer Index metric calculator
 * 
 * Implements downside-only risk measurement using RMS of drawdowns.
 */
class UlcerIndex {
public:
    UlcerIndex();
    ~UlcerIndex();
    
    /**
     * @brief Calculate Ulcer Index on CPU
     * @param params Input parameters
     * @return UlcerIndexResult containing UI and related metrics
     */
    UlcerIndexResult calculate_cpu(const UlcerIndexParameters& params) const;
    
    /**
     * @brief Calculate Ulcer Index on GPU (CUDA)
     * @param params Input parameters
     * @return UlcerIndexResult
     */
    UlcerIndexResult calculate_gpu(const UlcerIndexParameters& params) const;
    
    /**
     * @brief Batch calculate Ulcer Index for multiple equity curves on GPU
     * @param params_array Array of parameter sets
     * @param count Number of curves
     * @return Vector of UlcerIndexResult
     */
    std::vector<UlcerIndexResult> calculate_gpu_batch(
        const UlcerIndexParameters* params_array,
        size_t count) const;
    
    /**
     * @brief Calculate percentage drawdown at a specific point
     * @param current_value Current equity value
     * @param running_high Historical maximum to date
     * @return Percentage drawdown (negative value when underwater, 0 otherwise)
     */
    static float calculate_drawdown_percentage(float current_value, float running_high);
};

// CUDA kernel declarations
namespace cuda_kernels {

/**
 * @brief CUDA kernel for Ulcer Index calculation
 * 
 * Each thread block processes one equity curve.
 * Uses cooperative reduction to compute RMS efficiently.
 */
__global__ void ulcer_index_kernel(const float* d_equity_curve,
                                   size_t curve_length,
                                   UlcerIndexResult* d_result);

/**
 * @brief Device function to compute ulcer index
 * 
 * Maintains running high and computes squared drawdowns.
 */
__device__ inline void compute_ulcer_index(const float* equity_curve,
                                          size_t curve_length,
                                          float& out_ui,
                                          float& out_avg_dd,
                                          float& out_max_dd_pct,
                                          size_t& out_underwater_count,
                                          float& out_cumulative_squared_dd);

/**
 * @brief Device function to calculate percentage drawdown
 */
__device__ inline float device_calculate_dd_pct(float current, float running_high);

} // namespace cuda_kernels

} // namespace risk_metrics
} // namespace tailwarp

#endif // TAILWARP_ULCER_INDEX_H

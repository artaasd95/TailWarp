#ifndef TAILWARP_AVERAGE_DRAWDOWN_DURATION_H
#define TAILWARP_AVERAGE_DRAWDOWN_DURATION_H

#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <cmath>
#include <vector>

/**
 * @file average_drawdown_duration.h
 * @brief Average Drawdown & Drawdown Duration Metric Implementation
 * 
 * While Maximum Drawdown measures acute shocks, these metrics measure chronic stress.
 * Average Drawdown is the mean size of all individual declines below a previous high-water mark.
 * Drawdown Duration measures the time spent underwater before recovery.
 * 
 * Key Concepts:
 * - Chronic Stress: Focuses on typical drawdown size and recovery time, not extreme cases
 * - Psychological Impact: Time to recovery often breaks traders more than depth of loss
 * - Multiple Events: Aggregates statistics across all drawdown periods
 */

namespace tailwarp {
namespace risk_metrics {

/**
 * @struct AverageDrawdownDurationParameters
 * @brief Input parameters for Average Drawdown and Duration calculation
 */
struct AverageDrawdownDurationParameters {
    const float* equity_curve;      // Array of equity values over time
    size_t curve_length;            // Number of data points
    bool use_percentage;            // If true, return drawdowns as percentage
};

/**
 * @struct DrawdownEvent
 * @brief Represents a single drawdown event
 */
struct DrawdownEvent {
    size_t peak_index;              // Index of the high-water mark
    size_t trough_index;            // Index of the lowest point
    float peak_value;               // Value at peak
    float trough_value;             // Value at trough
    float drawdown_magnitude;       // Absolute drawdown value
    float drawdown_percentage;      // Percentage drawdown
    size_t duration;                // Time from peak to recovery to previous high
    bool recovered_to_peak;         // Whether it recovered to peak before curve end
};

/**
 * @struct AverageDrawdownDurationResult
 * @brief Output of Average Drawdown and Duration calculation
 */
struct AverageDrawdownDurationResult {
    // Average statistics
    float average_drawdown;         // Mean magnitude of all drawdowns
    float average_drawdown_pct;     // Mean percentage of all drawdowns
    float average_duration;         // Mean recovery time in periods
    
    // Additional statistics
    size_t total_drawdown_events;   // Number of distinct drawdown periods
    float max_drawdown;             // Largest single drawdown (for reference)
    float min_drawdown;             // Smallest drawdown
    float max_duration;             // Longest recovery period
    
    // Cumulative metrics
    size_t total_periods_underwater;    // Total number of periods in any drawdown
    float cumulative_drawdown;          // Sum of all drawdown magnitudes
    float average_recovery_difficulty;  // Average percentage gain needed to recover
    
    // Risk characterization
    float pain_frequency;           // Fraction of time spent in drawdown
    bool frequent_pain;             // True if pain_frequency > 0.3
};

/**
 * @class AverageDrawdownDuration
 * @brief CPU/GPU Average Drawdown and Duration metric calculator
 * 
 * Implements analysis of typical drawdown behavior across multiple events.
 */
class AverageDrawdownDuration {
public:
    AverageDrawdownDuration();
    ~AverageDrawdownDuration();
    
    /**
     * @brief Calculate Average Drawdown and Duration on CPU
     * @param params Input parameters
     * @return AverageDrawdownDurationResult containing averages and statistics
     */
    AverageDrawdownDurationResult calculate_cpu(
        const AverageDrawdownDurationParameters& params) const;
    
    /**
     * @brief Calculate Average Drawdown and Duration on GPU (CUDA)
     * @param params Input parameters
     * @return AverageDrawdownDurationResult
     */
    AverageDrawdownDurationResult calculate_gpu(
        const AverageDrawdownDurationParameters& params) const;
    
    /**
     * @brief Batch calculate on GPU
     * @param params_array Array of parameter sets
     * @param count Number of curves
     * @return Vector of results
     */
    std::vector<AverageDrawdownDurationResult> calculate_gpu_batch(
        const AverageDrawdownDurationParameters* params_array,
        size_t count) const;
    
    /**
     * @brief Identify all drawdown events in an equity curve
     * @param equity_curve Array of equity values
     * @param curve_length Length of array
     * @param use_percentage If true, calculate percentage drawdowns
     * @return Vector of identified DrawdownEvent structures
     */
    static std::vector<DrawdownEvent> identify_drawdown_events(
        const float* equity_curve,
        size_t curve_length,
        bool use_percentage = false);
};

// CUDA kernel declarations
namespace cuda_kernels {

/**
 * @brief CUDA kernel for Average Drawdown and Duration calculation
 * 
 * Scans equity curve to identify all drawdown events and compute statistics.
 */
__global__ void average_drawdown_duration_kernel(
    const float* d_equity_curve,
    size_t curve_length,
    AverageDrawdownDurationResult* d_result,
    bool use_percentage);

/**
 * @brief Device function to compute average drawdown statistics
 */
__device__ inline void compute_average_dd_stats(
    const float* equity_curve,
    size_t curve_length,
    float& out_avg_dd,
    float& out_avg_dd_pct,
    float& out_avg_duration,
    size_t& out_event_count,
    float& out_max_dd,
    float& out_cumulative_dd,
    size_t& out_underwater_periods);

} // namespace cuda_kernels

} // namespace risk_metrics
} // namespace tailwarp

#endif // TAILWARP_AVERAGE_DRAWDOWN_DURATION_H

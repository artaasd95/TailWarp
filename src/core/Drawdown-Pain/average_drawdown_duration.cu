#include "average_drawdown_duration.h"
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
 * @brief Device function to compute average drawdown statistics
 * 
 * Scans through equity curve, identifies each drawdown event,
 * and accumulates statistics.
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
    size_t& out_underwater_periods) {
    
    out_avg_dd = 0.0f;
    out_avg_dd_pct = 0.0f;
    out_avg_duration = 0.0f;
    out_event_count = 0;
    out_max_dd = 0.0f;
    out_cumulative_dd = 0.0f;
    out_underwater_periods = 0;
    
    if (curve_length < 2) {
        return;
    }
    
    float total_dd = 0.0f;
    float total_dd_pct = 0.0f;
    float total_duration = 0.0f;
    size_t event_count = 0;
    
    float running_max = equity_curve[0];
    size_t running_max_idx = 0;
    bool in_drawdown = false;
    size_t drawdown_start = 0;
    
    for (size_t i = 1; i < curve_length; ++i) {
        float current = equity_curve[i];
        
        // Update running maximum
        if (current > running_max) {
            // Check if we were in drawdown before
            if (in_drawdown) {
                // Drawdown ends when we exceed running max
                in_drawdown = false;
                size_t duration = i - drawdown_start;
                total_duration += duration;
            }
            running_max = current;
            running_max_idx = i;
        } else {
            // We're equal or below running max
            if (!in_drawdown) {
                // Start of new drawdown
                in_drawdown = true;
                drawdown_start = i;
            }
            out_underwater_periods++;
        }
    }
    
    // Re-scan to count distinct drawdown events and accumulate magnitudes
    running_max = equity_curve[0];
    in_drawdown = false;
    float max_dd_seen = 0.0f;
    
    for (size_t i = 1; i < curve_length; ++i) {
        float current = equity_curve[i];
        float dd = running_max - current;
        
        if (dd > 1e-10f) {  // In drawdown
            if (!in_drawdown) {
                in_drawdown = true;
                event_count++;
            }
            total_dd += dd;
            if (running_max > 1e-10f) {
                total_dd_pct += (dd / running_max) * 100.0f;
            }
            if (dd > max_dd_seen) {
                max_dd_seen = dd;
            }
        } else {
            in_drawdown = false;
        }
        
        if (current > running_max) {
            running_max = current;
        }
    }
    
    // Compute averages
    if (event_count > 0) {
        out_avg_dd = total_dd / event_count;
        out_avg_dd_pct = total_dd_pct / event_count;
        out_avg_duration = total_duration / (float)event_count;
    }
    
    out_event_count = event_count;
    out_max_dd = max_dd_seen;
    out_cumulative_dd = total_dd;
}

/**
 * @brief CUDA kernel for Average Drawdown and Duration calculation
 */
__global__ void average_drawdown_duration_kernel(
    const float* d_equity_curve,
    size_t curve_length,
    AverageDrawdownDurationResult* d_result,
    bool use_percentage) {
    
    float avg_dd = 0.0f;
    float avg_dd_pct = 0.0f;
    float avg_duration = 0.0f;
    size_t event_count = 0;
    float max_dd = 0.0f;
    float cumulative_dd = 0.0f;
    size_t underwater_periods = 0;
    
    compute_average_dd_stats(d_equity_curve, curve_length,
                            avg_dd, avg_dd_pct, avg_duration,
                            event_count, max_dd, cumulative_dd,
                            underwater_periods);
    
    if (threadIdx.x == 0) {
        AverageDrawdownDurationResult& result = *d_result;
        
        if (use_percentage) {
            result.average_drawdown = avg_dd_pct;
        } else {
            result.average_drawdown = avg_dd;
        }
        result.average_drawdown_pct = avg_dd_pct;
        result.average_duration = avg_duration;
        result.total_drawdown_events = event_count;
        result.max_drawdown = max_dd;
        result.cumulative_drawdown = cumulative_dd;
        result.total_periods_underwater = underwater_periods;
        
        // Pain frequency: fraction of time underwater
        if (curve_length > 0) {
            result.pain_frequency = (float)underwater_periods / (float)curve_length;
        } else {
            result.pain_frequency = 0.0f;
        }
        
        result.frequent_pain = (result.pain_frequency > 0.3f);
        
        // Average recovery difficulty
        if (event_count > 0 && max_dd > 1e-10f) {
            result.average_recovery_difficulty = (max_dd / (1.0f - max_dd / d_equity_curve[0])) * 100.0f;
        } else {
            result.average_recovery_difficulty = 0.0f;
        }
    }
    
    __syncthreads();
}

} // namespace cuda_kernels

// ============================================================================
// AverageDrawdownDuration Class Implementation
// ============================================================================

AverageDrawdownDuration::AverageDrawdownDuration() {
    int device_count;
    cudaGetDeviceCount(&device_count);
    if (device_count > 0) {
        cudaSetDevice(0);
    }
}

AverageDrawdownDuration::~AverageDrawdownDuration() {
    // Cleanup if needed
}

/**
 * @brief CPU implementation
 */
AverageDrawdownDurationResult AverageDrawdownDuration::calculate_cpu(
    const AverageDrawdownDurationParameters& params) const {
    
    AverageDrawdownDurationResult result = {};
    
    if (params.curve_length < 2 || params.equity_curve == nullptr) {
        return result;
    }
    
    // Identify events
    auto events = identify_drawdown_events(params.equity_curve, params.curve_length, 
                                          params.use_percentage);
    
    if (events.empty()) {
        result.total_drawdown_events = 0;
        result.pain_frequency = 0.0f;
        return result;
    }
    
    // Calculate averages from events
    float total_dd = 0.0f;
    float total_duration = 0.0f;
    float max_dd = 0.0f;
    float max_duration = 0.0f;
    float total_recovery_difficulty = 0.0f;
    size_t underwater_periods = 0;
    
    for (const auto& event : events) {
        total_dd += event.drawdown_magnitude;
        total_duration += event.duration;
        if (event.drawdown_magnitude > max_dd) {
            max_dd = event.drawdown_magnitude;
        }
        if (event.duration > max_duration) {
            max_duration = event.duration;
        }
        
        // Recovery difficulty: how much % gain is needed
        if (event.trough_value > 1e-10f) {
            float recovery_pct = ((event.peak_value - event.trough_value) / event.trough_value) * 100.0f;
            total_recovery_difficulty += recovery_pct;
        }
        
        underwater_periods += event.duration;
    }
    
    size_t event_count = events.size();
    
    result.average_drawdown = total_dd / event_count;
    result.average_duration = total_duration / (float)event_count;
    result.total_drawdown_events = event_count;
    result.max_drawdown = max_dd;
    result.max_duration = max_duration;
    result.cumulative_drawdown = total_dd;
    result.total_periods_underwater = underwater_periods;
    result.pain_frequency = (float)underwater_periods / (float)params.curve_length;
    result.frequent_pain = (result.pain_frequency > 0.3f);
    result.average_recovery_difficulty = total_recovery_difficulty / event_count;
    
    // Calculate percentage version
    if (!events.empty()) {
        float total_dd_pct = 0.0f;
        for (const auto& event : events) {
            total_dd_pct += event.drawdown_percentage;
        }
        result.average_drawdown_pct = total_dd_pct / event_count;
    }
    
    return result;
}

/**
 * @brief GPU implementation
 */
AverageDrawdownDurationResult AverageDrawdownDuration::calculate_gpu(
    const AverageDrawdownDurationParameters& params) const {
    
    if (params.curve_length < 2 || params.equity_curve == nullptr) {
        return AverageDrawdownDurationResult();
    }
    
    // Allocate device memory
    float* d_equity_curve;
    AverageDrawdownDurationResult* d_result;
    
    cudaMalloc(&d_equity_curve, params.curve_length * sizeof(float));
    cudaMalloc(&d_result, sizeof(AverageDrawdownDurationResult));
    
    // Copy input data to device
    cudaMemcpy(d_equity_curve, params.equity_curve, params.curve_length * sizeof(float),
               cudaMemcpyHostToDevice);
    
    // Launch kernel
    cuda_kernels::average_drawdown_duration_kernel<<<1, 256>>>(
        d_equity_curve, params.curve_length, d_result, params.use_percentage);
    
    // Copy result back to host
    AverageDrawdownDurationResult result;
    cudaMemcpy(&result, d_result, sizeof(AverageDrawdownDurationResult), cudaMemcpyDeviceToHost);
    
    // Cleanup
    cudaFree(d_equity_curve);
    cudaFree(d_result);
    
    return result;
}

/**
 * @brief GPU batch implementation
 */
std::vector<AverageDrawdownDurationResult> AverageDrawdownDuration::calculate_gpu_batch(
    const AverageDrawdownDurationParameters* params_array,
    size_t count) const {
    
    if (count == 0 || params_array == nullptr) {
        return std::vector<AverageDrawdownDurationResult>();
    }
    
    std::vector<AverageDrawdownDurationResult> results(count);
    
    for (size_t i = 0; i < count; ++i) {
        results[i] = calculate_gpu(params_array[i]);
    }
    
    return results;
}

/**
 * @brief Identify all drawdown events
 */
std::vector<DrawdownEvent> AverageDrawdownDuration::identify_drawdown_events(
    const float* equity_curve,
    size_t curve_length,
    bool use_percentage) {
    
    std::vector<DrawdownEvent> events;
    
    if (curve_length < 2 || equity_curve == nullptr) {
        return events;
    }
    
    float running_max = equity_curve[0];
    size_t running_max_idx = 0;
    bool in_drawdown = false;
    DrawdownEvent current_event = {};
    
    for (size_t i = 1; i < curve_length; ++i) {
        float current = equity_curve[i];
        
        if (current > running_max) {
            // End of drawdown (we've exceeded the running max)
            if (in_drawdown) {
                // Complete the current event
                current_event.recovered_to_peak = true;
                current_event.duration = i - current_event.peak_index;
                events.push_back(current_event);
                in_drawdown = false;
            }
            running_max = current;
            running_max_idx = i;
        } else if (current < running_max && !in_drawdown) {
            // Start of new drawdown
            in_drawdown = true;
            current_event.peak_index = running_max_idx;
            current_event.trough_index = i;
            current_event.peak_value = running_max;
            current_event.trough_value = current;
            current_event.drawdown_magnitude = running_max - current;
            if (running_max > 1e-10f) {
                current_event.drawdown_percentage = (current_event.drawdown_magnitude / running_max) * 100.0f;
            }
        } else if (current < current_event.trough_value && in_drawdown) {
            // Deepen the drawdown
            current_event.trough_index = i;
            current_event.trough_value = current;
            current_event.drawdown_magnitude = running_max - current;
            if (running_max > 1e-10f) {
                current_event.drawdown_percentage = (current_event.drawdown_magnitude / running_max) * 100.0f;
            }
        }
    }
    
    // Handle incomplete drawdown at end of curve
    if (in_drawdown) {
        current_event.recovered_to_peak = false;
        current_event.duration = curve_length - current_event.peak_index;
        events.push_back(current_event);
    }
    
    return events;
}

} // namespace risk_metrics
} // namespace tailwarp

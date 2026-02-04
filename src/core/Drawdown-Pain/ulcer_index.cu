#include "ulcer_index.h"
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
 * @brief Device function to calculate percentage drawdown
 * 
 * @param current Current equity value
 * @param running_high Historical maximum
 * @return Percentage drawdown (0 if not underwater, negative percentage if underwater)
 */
__device__ inline float device_calculate_dd_pct(float current, float running_high) {
    if (running_high <= 1e-10f) {
        return 0.0f;
    }
    
    float drawdown = (current - running_high) / running_high;  // Will be negative when underwater
    return drawdown;
}

/**
 * @brief Device function to compute ulcer index
 * 
 * Maintains a running high water mark and calculates the RMS of all percentage drawdowns.
 */
__device__ inline void compute_ulcer_index(const float* equity_curve,
                                          size_t curve_length,
                                          float& out_ui,
                                          float& out_avg_dd,
                                          float& out_max_dd_pct,
                                          size_t& out_underwater_count,
                                          float& out_cumulative_squared_dd) {
    
    out_ui = 0.0f;
    out_avg_dd = 0.0f;
    out_max_dd_pct = 0.0f;
    out_underwater_count = 0;
    out_cumulative_squared_dd = 0.0f;
    
    if (curve_length == 0) {
        return;
    }
    
    float running_high = equity_curve[0];
    float cumulative_squared = 0.0f;
    float cumulative_drawdown_pct = 0.0f;
    size_t underwater_count = 0;
    float max_dd_pct = 0.0f;
    
    for (size_t i = 1; i < curve_length; ++i) {
        float current = equity_curve[i];
        
        // Update running high
        if (current > running_high) {
            running_high = current;
        }
        
        // Calculate percentage drawdown (negative when underwater)
        float dd_pct = device_calculate_dd_pct(current, running_high);
        
        // If underwater (dd_pct < 0), accumulate
        if (dd_pct < 0.0f) {
            float abs_dd_pct = fabsf(dd_pct);
            cumulative_squared += abs_dd_pct * abs_dd_pct;
            cumulative_drawdown_pct += abs_dd_pct;
            underwater_count++;
            
            if (abs_dd_pct > max_dd_pct) {
                max_dd_pct = abs_dd_pct;
            }
        }
    }
    
    out_cumulative_squared_dd = cumulative_squared;
    
    // Calculate UI: RMS of percentage drawdowns
    if (curve_length > 0) {
        out_ui = sqrtf(cumulative_squared / curve_length);
    }
    
    // Average drawdown
    if (underwater_count > 0) {
        out_avg_dd = cumulative_drawdown_pct / underwater_count;
    }
    
    out_underwater_count = underwater_count;
    out_max_dd_pct = max_dd_pct;
}

/**
 * @brief CUDA kernel for Ulcer Index calculation
 */
__global__ void ulcer_index_kernel(const float* d_equity_curve,
                                   size_t curve_length,
                                   UlcerIndexResult* d_result) {
    
    float ui = 0.0f;
    float avg_dd = 0.0f;
    float max_dd_pct = 0.0f;
    size_t underwater_count = 0;
    float cumulative_squared = 0.0f;
    
    compute_ulcer_index(d_equity_curve, curve_length,
                       ui, avg_dd, max_dd_pct,
                       underwater_count, cumulative_squared);
    
    if (threadIdx.x == 0) {
        UlcerIndexResult& result = *d_result;
        
        result.ulcer_index = ui;
        result.average_drawdown_depth = avg_dd;
        result.max_underwater_percentage = max_dd_pct;
        result.observations_in_drawdown = underwater_count;
        result.cumulative_squareddd = cumulative_squared;
        
        // Percentage time underwater
        if (curve_length > 0) {
            result.percentage_time_underwater = (float)underwater_count / (float)curve_length;
        } else {
            result.percentage_time_underwater = 0.0f;
        }
        
        // Pain intensity score (0-100)
        // UI > 15 is considered severe chronic stress
        if (ui > 15.0f) {
            result.is_high_pain = true;
            result.pain_intensity_score = fminf(100.0f, (ui / 15.0f) * 100.0f);
        } else {
            result.is_high_pain = false;
            result.pain_intensity_score = (ui / 15.0f) * 100.0f;
        }
        
        // Standard deviation of drawdowns
        if (underwater_count > 1) {
            float variance = (cumulative_squared / underwater_count) - 
                           (avg_dd * avg_dd);
            result.std_of_drawdowns = sqrtf(fmaxf(0.0f, variance));
        } else {
            result.std_of_drawdowns = 0.0f;
        }
    }
    
    __syncthreads();
}

} // namespace cuda_kernels

// ============================================================================
// UlcerIndex Class Implementation
// ============================================================================

UlcerIndex::UlcerIndex() {
    int device_count;
    cudaGetDeviceCount(&device_count);
    if (device_count > 0) {
        cudaSetDevice(0);
    }
}

UlcerIndex::~UlcerIndex() {
    // Cleanup if needed
}

/**
 * @brief Helper function to calculate drawdown percentage
 */
float UlcerIndex::calculate_drawdown_percentage(float current_value, float running_high) {
    if (running_high <= 1e-10f) {
        return 0.0f;
    }
    
    float drawdown = (current_value - running_high) / running_high;
    return drawdown;  // Negative when underwater
}

/**
 * @brief CPU implementation
 */
UlcerIndexResult UlcerIndex::calculate_cpu(const UlcerIndexParameters& params) const {
    
    UlcerIndexResult result = {};
    
    if (params.curve_length == 0 || params.equity_curve == nullptr) {
        return result;
    }
    
    float running_high = params.equity_curve[0];
    float cumulative_squared = 0.0f;
    float cumulative_drawdown_pct = 0.0f;
    size_t underwater_count = 0;
    float max_dd_pct = 0.0f;
    
    // Scan through curve
    for (size_t i = 1; i < params.curve_length; ++i) {
        float current = params.equity_curve[i];
        
        // Update running high
        if (current > running_high) {
            running_high = current;
        }
        
        // Calculate percentage drawdown
        float dd_pct = calculate_drawdown_percentage(current, running_high);
        
        // If underwater (dd_pct < 0), accumulate
        if (dd_pct < 0.0f) {
            float abs_dd_pct = std::fabs(dd_pct);
            cumulative_squared += abs_dd_pct * abs_dd_pct;
            cumulative_drawdown_pct += abs_dd_pct;
            underwater_count++;
            
            if (abs_dd_pct > max_dd_pct) {
                max_dd_pct = abs_dd_pct;
            }
        }
    }
    
    result.cumulative_squareddd = cumulative_squared;
    
    // Calculate UI: RMS of percentage drawdowns
    result.ulcer_index = std::sqrt(cumulative_squared / params.curve_length);
    
    // Average drawdown
    if (underwater_count > 0) {
        result.average_drawdown_depth = cumulative_drawdown_pct / underwater_count;
    } else {
        result.average_drawdown_depth = 0.0f;
    }
    
    result.observations_in_drawdown = underwater_count;
    result.max_underwater_percentage = max_dd_pct;
    
    // Percentage time underwater
    result.percentage_time_underwater = (float)underwater_count / (float)params.curve_length;
    
    // Pain intensity score
    if (result.ulcer_index > 15.0f) {
        result.is_high_pain = true;
        result.pain_intensity_score = std::min(100.0f, (result.ulcer_index / 15.0f) * 100.0f);
    } else {
        result.is_high_pain = false;
        result.pain_intensity_score = (result.ulcer_index / 15.0f) * 100.0f;
    }
    
    // Standard deviation of drawdowns
    if (underwater_count > 1) {
        float avg = result.average_drawdown_depth;
        float variance = (cumulative_squared / underwater_count) - (avg * avg);
        result.std_of_drawdowns = std::sqrt(std::max(0.0f, variance));
    } else {
        result.std_of_drawdowns = 0.0f;
    }
    
    return result;
}

/**
 * @brief GPU implementation
 */
UlcerIndexResult UlcerIndex::calculate_gpu(const UlcerIndexParameters& params) const {
    
    if (params.curve_length == 0 || params.equity_curve == nullptr) {
        return UlcerIndexResult();
    }
    
    // Allocate device memory
    float* d_equity_curve;
    UlcerIndexResult* d_result;
    
    cudaMalloc(&d_equity_curve, params.curve_length * sizeof(float));
    cudaMalloc(&d_result, sizeof(UlcerIndexResult));
    
    // Copy input data to device
    cudaMemcpy(d_equity_curve, params.equity_curve, params.curve_length * sizeof(float),
               cudaMemcpyHostToDevice);
    
    // Launch kernel
    cuda_kernels::ulcer_index_kernel<<<1, 256>>>(d_equity_curve, params.curve_length, d_result);
    
    // Copy result back to host
    UlcerIndexResult result;
    cudaMemcpy(&result, d_result, sizeof(UlcerIndexResult), cudaMemcpyDeviceToHost);
    
    // Cleanup
    cudaFree(d_equity_curve);
    cudaFree(d_result);
    
    return result;
}

/**
 * @brief GPU batch implementation
 */
std::vector<UlcerIndexResult> UlcerIndex::calculate_gpu_batch(
    const UlcerIndexParameters* params_array,
    size_t count) const {
    
    if (count == 0 || params_array == nullptr) {
        return std::vector<UlcerIndexResult>();
    }
    
    std::vector<UlcerIndexResult> results(count);
    
    for (size_t i = 0; i < count; ++i) {
        results[i] = calculate_gpu(params_array[i]);
    }
    
    return results;
}

} // namespace risk_metrics
} // namespace tailwarp

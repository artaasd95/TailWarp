#include "maximum_drawdown.h"
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
 * @brief Device function to compute maximum drawdown
 * 
 * Scans through the equity curve once to find the maximum peak-to-trough decline.
 * Maintains a running maximum and compares every subsequent value to it.
 */
__device__ inline void compute_mdd(const float* equity_curve,
                                   size_t curve_length,
                                   float& out_mdd,
                                   size_t& out_peak_idx,
                                   size_t& out_trough_idx) {
    if (curve_length == 0) {
        out_mdd = 0.0f;
        out_peak_idx = 0;
        out_trough_idx = 0;
        return;
    }
    
    out_mdd = 0.0f;
    out_peak_idx = 0;
    out_trough_idx = 0;
    
    float running_max = equity_curve[0];
    size_t running_max_idx = 0;
    
    // Scan through equity curve
    for (size_t i = 1; i < curve_length; ++i) {
        float current_value = equity_curve[i];
        
        // Calculate drawdown from current running maximum
        float drawdown = running_max - current_value;
        
        // Update if this is the largest drawdown so far
        if (drawdown > out_mdd) {
            out_mdd = drawdown;
            out_peak_idx = running_max_idx;
            out_trough_idx = i;
        }
        
        // Update running maximum if current value is higher
        if (current_value > running_max) {
            running_max = current_value;
            running_max_idx = i;
        }
    }
}

/**
 * @brief CUDA kernel for Maximum Drawdown calculation
 * 
 * Each thread block processes one equity curve completely.
 * Uses cooperative reduction for potential multi-block scenarios.
 */
__global__ void maximum_drawdown_kernel(const float* d_equity_curve,
                                        size_t curve_length,
                                        MaximumDrawdownResult* d_result,
                                        bool use_percentage) {
    
    // For simplicity, one block processes one curve
    // Each thread can participate in parallel scanning if needed
    
    float mdd_value = 0.0f;
    size_t peak_idx = 0;
    size_t trough_idx = 0;
    
    // Compute MDD
    compute_mdd(d_equity_curve, curve_length, mdd_value, peak_idx, trough_idx);
    
    // Only thread 0 writes the result
    if (threadIdx.x == 0) {
        float peak_value = d_equity_curve[peak_idx];
        float trough_value = d_equity_curve[trough_idx];
        
        MaximumDrawdownResult& result = *d_result;
        
        result.peak_index = peak_idx;
        result.trough_index = trough_idx;
        result.peak_value = peak_value;
        result.trough_value = trough_value;
        
        // Calculate MDD percentage
        float mdd_pct = 0.0f;
        if (peak_value > 1e-10f) {
            mdd_pct = (mdd_value / peak_value) * 100.0f;
        }
        result.mdd_percentage = mdd_pct;
        
        // Return value in requested format
        if (use_percentage) {
            result.mdd_value = mdd_pct;
        } else {
            result.mdd_value = mdd_value;
        }
        
        // Calculate recovery percentage needed
        if (trough_value > 1e-10f) {
            result.recovery_percentage = ((peak_value - trough_value) / trough_value) * 100.0f;
        } else {
            result.recovery_percentage = 100.0f;  // 100% gain needed if dropped to near zero
        }
        
        // Check for recovery
        result.fully_recovered = false;
        result.time_to_recovery = curve_length - trough_idx;
        
        for (size_t i = trough_idx + 1; i < curve_length; ++i) {
            if (d_equity_curve[i] >= peak_value) {
                result.fully_recovered = true;
                result.time_to_recovery = i - trough_idx;
                break;
            }
        }
    }
    
    __syncthreads();
}

} // namespace cuda_kernels

// ============================================================================
// MaximumDrawdown Class Implementation
// ============================================================================

MaximumDrawdown::MaximumDrawdown() {
    int device_count;
    cudaGetDeviceCount(&device_count);
    if (device_count > 0) {
        cudaSetDevice(0);
    }
}

MaximumDrawdown::~MaximumDrawdown() {
    // Cleanup if needed
}

/**
 * @brief CPU implementation
 */
MaximumDrawdownResult MaximumDrawdown::calculate_cpu(
    const MaximumDrawdownParameters& params) const {
    
    MaximumDrawdownResult result = {};
    
    if (params.curve_length == 0 || params.equity_curve == nullptr) {
        return result;
    }
    
    float mdd_value = 0.0f;
    size_t peak_idx = 0;
    size_t trough_idx = 0;
    
    float running_max = params.equity_curve[0];
    size_t running_max_idx = 0;
    
    // Scan through equity curve
    for (size_t i = 1; i < params.curve_length; ++i) {
        float current_value = params.equity_curve[i];
        
        // Calculate drawdown from current running maximum
        float drawdown = running_max - current_value;
        
        // Update if this is the largest drawdown so far
        if (drawdown > mdd_value) {
            mdd_value = drawdown;
            peak_idx = running_max_idx;
            trough_idx = i;
        }
        
        // Update running maximum if current value is higher
        if (current_value > running_max) {
            running_max = current_value;
            running_max_idx = i;
        }
    }
    
    // Populate result
    result.peak_index = peak_idx;
    result.trough_index = trough_idx;
    result.peak_value = params.equity_curve[peak_idx];
    result.trough_value = params.equity_curve[trough_idx];
    
    // Calculate MDD percentage
    if (result.peak_value > 1e-10f) {
        result.mdd_percentage = (mdd_value / result.peak_value) * 100.0f;
    } else {
        result.mdd_percentage = 0.0f;
    }
    
    // Return value in requested format
    if (params.use_percentage) {
        result.mdd_value = result.mdd_percentage;
    } else {
        result.mdd_value = mdd_value;
    }
    
    // Calculate recovery percentage needed
    if (result.trough_value > 1e-10f) {
        result.recovery_percentage = ((result.peak_value - result.trough_value) / result.trough_value) * 100.0f;
    } else {
        result.recovery_percentage = 100.0f;
    }
    
    // Check for recovery
    result.fully_recovered = false;
    result.time_to_recovery = params.curve_length - trough_idx;
    
    for (size_t i = trough_idx + 1; i < params.curve_length; ++i) {
        if (params.equity_curve[i] >= result.peak_value) {
            result.fully_recovered = true;
            result.time_to_recovery = i - trough_idx;
            break;
        }
    }
    
    return result;
}

/**
 * @brief GPU implementation (single calculation)
 */
MaximumDrawdownResult MaximumDrawdown::calculate_gpu(
    const MaximumDrawdownParameters& params) const {
    
    if (params.curve_length == 0 || params.equity_curve == nullptr) {
        return MaximumDrawdownResult();
    }
    
    // Allocate device memory
    float* d_equity_curve;
    MaximumDrawdownResult* d_result;
    
    cudaMalloc(&d_equity_curve, params.curve_length * sizeof(float));
    cudaMalloc(&d_result, sizeof(MaximumDrawdownResult));
    
    // Copy input data to device
    cudaMemcpy(d_equity_curve, params.equity_curve, params.curve_length * sizeof(float),
               cudaMemcpyHostToDevice);
    
    // Launch kernel
    cuda_kernels::maximum_drawdown_kernel<<<1, 256>>>(d_equity_curve, params.curve_length, 
                                                       d_result, params.use_percentage);
    
    // Copy result back to host
    MaximumDrawdownResult result;
    cudaMemcpy(&result, d_result, sizeof(MaximumDrawdownResult), cudaMemcpyDeviceToHost);
    
    // Cleanup
    cudaFree(d_equity_curve);
    cudaFree(d_result);
    
    return result;
}

/**
 * @brief GPU batch implementation
 */
std::vector<MaximumDrawdownResult> MaximumDrawdown::calculate_gpu_batch(
    const MaximumDrawdownParameters* params_array,
    size_t count) const {
    
    if (count == 0 || params_array == nullptr) {
        return std::vector<MaximumDrawdownResult>();
    }
    
    std::vector<MaximumDrawdownResult> results(count);
    
    // Process each curve independently on GPU
    for (size_t i = 0; i < count; ++i) {
        results[i] = calculate_gpu(params_array[i]);
    }
    
    return results;
}

/**
 * @brief Find recovery index after drawdown
 */
size_t MaximumDrawdown::find_recovery_index(const float* equity_curve,
                                            size_t curve_length,
                                            size_t peak_index,
                                            float peak_value,
                                            size_t start_from_index) {
    if (start_from_index >= curve_length) {
        return curve_length;
    }
    
    for (size_t i = start_from_index; i < curve_length; ++i) {
        if (equity_curve[i] >= peak_value) {
            return i;
        }
    }
    
    return curve_length;
}

} // namespace risk_metrics
} // namespace tailwarp

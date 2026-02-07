#include "recovery_metrics.h"
#include <algorithm>
#include <iostream>
#include <limits>

namespace tailwarp {
namespace risk_metrics {

// ============================================================================
// CUDA Kernels and Device Functions
// ============================================================================

namespace cuda_kernels {

/**
 * @brief Device function to compute maximum drawdown
 *
 * Scans equity curve to find largest peak-to-trough decline.
 */
__device__ inline void compute_mdd_device(const float* equity_curve,
                                          size_t curve_length,
                                          float& out_mdd_pct,
                                          float& out_mdd_absolute,
                                          size_t& out_peak_idx,
                                          size_t& out_trough_idx) {
    if (curve_length == 0) {
        out_mdd_pct = 0.0f;
        out_mdd_absolute = 0.0f;
        out_peak_idx = 0;
        out_trough_idx = 0;
        return;
    }

    out_mdd_absolute = 0.0f;
    out_mdd_pct = 0.0f;
    out_peak_idx = 0;
    out_trough_idx = 0;

    float running_max = equity_curve[0];
    size_t running_max_idx = 0;

    for (size_t i = 1; i < curve_length; ++i) {
        float current_value = equity_curve[i];
        float drawdown = running_max - current_value;

        if (drawdown > out_mdd_absolute) {
            out_mdd_absolute = drawdown;
            out_peak_idx = running_max_idx;
            out_trough_idx = i;
        }

        if (current_value > running_max) {
            running_max = current_value;
            running_max_idx = i;
        }
    }

    // Convert to percentage
    if (running_max > 1e-10f) {
        out_mdd_pct = (out_mdd_absolute / running_max) * 100.0f;
    }
}

/**
 * @brief Device function to find recovery index
 *
 * Scans forward from trough to find when equity recovers to peak
 */
__device__ inline size_t find_recovery_idx_device(const float* equity_curve,
                                                  size_t curve_length,
                                                  size_t trough_idx,
                                                  float peak_value) {
    for (size_t i = trough_idx + 1; i < curve_length; ++i) {
        if (equity_curve[i] >= peak_value) {
            return i;
        }
    }
    return curve_length;
}

/**
 * @brief CUDA kernel for Calmar Ratio calculation
 *
 * Computes annualized return and divides by maximum drawdown percentage.
 */
__global__ void calmar_ratio_kernel(const float* d_equity_curve,
                                    size_t curve_length,
                                    float initial_capital,
                                    float time_years,
                                    CalmarRatioResult* d_result) {
    if (threadIdx.x != 0) {
        return;
    }

    if (curve_length == 0 || time_years <= 0.0f) {
        d_result->calmar_ratio = 0.0f;
        d_result->annualized_return = 0.0f;
        d_result->annualized_return_pct = 0.0f;
        d_result->maximum_drawdown = 0.0f;
        d_result->final_value = initial_capital;
        d_result->peak_index = 0;
        d_result->trough_index = 0;
        return;
    }

    // Get final equity value
    float final_value = d_equity_curve[curve_length - 1];
    d_result->final_value = final_value;

    // Calculate annualized return
    // Annualized Return = (V_T / V_0)^(1/T) - 1
    float ratio = final_value / initial_capital;
    if (ratio <= 0.0f) {
        d_result->annualized_return = -1.0f;  // Total loss
        d_result->annualized_return_pct = -100.0f;
    } else {
        float exponent = 1.0f / time_years;
        float annualized = powf(ratio, exponent) - 1.0f;
        d_result->annualized_return = annualized;
        d_result->annualized_return_pct = annualized * 100.0f;
    }

    // Compute maximum drawdown
    float mdd_pct = 0.0f;
    float mdd_absolute = 0.0f;
    size_t peak_idx = 0;
    size_t trough_idx = 0;

    compute_mdd_device(d_equity_curve, curve_length, mdd_pct, mdd_absolute, peak_idx, trough_idx);

    d_result->maximum_drawdown = mdd_pct;
    d_result->peak_index = peak_idx;
    d_result->trough_index = trough_idx;

    // Calculate Calmar Ratio
    if (mdd_pct > 1e-10f) {
        d_result->calmar_ratio = d_result->annualized_return_pct / mdd_pct;
    } else {
        // No drawdown observed
        d_result->calmar_ratio = (d_result->annualized_return >= 0.0f) ? 1000.0f : -1000.0f;
    }
}

/**
 * @brief CUDA kernel for Recovery Time calculation
 *
 * Identifies drawdown events and calculates mean and max recovery times.
 */
__global__ void recovery_time_kernel(const float* d_equity_curve,
                                     size_t curve_length,
                                     RecoveryTimeResult* d_result) {
    if (threadIdx.x != 0) {
        return;
    }

    if (curve_length < 2) {
        d_result->mean_recovery_time = 0.0f;
        d_result->max_recovery_time = 0.0f;
        d_result->num_drawdown_events = 0;
        d_result->longest_recovery_peak_idx = 0;
        d_result->longest_recovery_trough_idx = 0;
        d_result->longest_recovery_end_idx = 0;
        return;
    }

    float total_recovery_time = 0.0f;
    float max_recovery_time = 0.0f;
    size_t num_events = 0;
    size_t longest_recovery_peak_idx = 0;
    size_t longest_recovery_trough_idx = 0;
    size_t longest_recovery_end_idx = 0;

    float running_max = d_equity_curve[0];
    size_t running_max_idx = 0;
    bool in_drawdown = false;
    size_t peak_idx = 0;

    for (size_t i = 1; i < curve_length; ++i) {
        float current_value = d_equity_curve[i];

        // Update running maximum if we hit a new high
        if (current_value > running_max) {
            running_max = current_value;
            running_max_idx = i;
            in_drawdown = false;
        } else if (current_value < running_max && !in_drawdown) {
            // Starting a new drawdown
            in_drawdown = true;
            peak_idx = running_max_idx;
        }

        // Check for recovery (if in drawdown and current >= running_max)
        if (in_drawdown && current_value >= running_max) {
            size_t recovery_time = i - peak_idx;
            total_recovery_time += static_cast<float>(recovery_time);
            num_events++;

            if (recovery_time > max_recovery_time) {
                max_recovery_time = static_cast<float>(recovery_time);
                longest_recovery_peak_idx = peak_idx;
                longest_recovery_trough_idx = i - 1;  // Approximate trough
                longest_recovery_end_idx = i;
            }

            in_drawdown = false;
            running_max = current_value;
            running_max_idx = i;
        }
    }

    // If currently in drawdown at end of period
    if (in_drawdown) {
        size_t recovery_time = curve_length - 1 - peak_idx;
        total_recovery_time += static_cast<float>(recovery_time);
        num_events++;

        if (recovery_time > max_recovery_time) {
            max_recovery_time = static_cast<float>(recovery_time);
            longest_recovery_peak_idx = peak_idx;
            longest_recovery_trough_idx = curve_length - 1;
            longest_recovery_end_idx = curve_length - 1;
        }
    }

    d_result->num_drawdown_events = num_events;
    d_result->max_recovery_time = max_recovery_time;
    d_result->mean_recovery_time = (num_events > 0) ? (total_recovery_time / num_events) : 0.0f;
    d_result->longest_recovery_peak_idx = longest_recovery_peak_idx;
    d_result->longest_recovery_trough_idx = longest_recovery_trough_idx;
    d_result->longest_recovery_end_idx = longest_recovery_end_idx;
}

/**
 * @brief CUDA kernel for Recovery Factor calculation
 *
 * Computes net profit divided by maximum drawdown absolute value.
 */
__global__ void recovery_factor_kernel(const float* d_equity_curve,
                                       size_t curve_length,
                                       float initial_capital,
                                       RecoveryFactorResult* d_result) {
    if (threadIdx.x != 0) {
        return;
    }

    if (curve_length == 0) {
        d_result->recovery_factor = 0.0f;
        d_result->net_profit = 0.0f;
        d_result->net_profit_pct = 0.0f;
        d_result->maximum_drawdown = 0.0f;
        d_result->maximum_drawdown_absolute = 0.0f;
        d_result->final_value = initial_capital;
        d_result->peak_index = 0;
        d_result->trough_index = 0;
        return;
    }

    // Get final value and calculate net profit
    float final_value = d_equity_curve[curve_length - 1];
    float net_profit = final_value - initial_capital;
    float net_profit_pct = (initial_capital > 1e-10f) ? (net_profit / initial_capital) * 100.0f : 0.0f;

    d_result->final_value = final_value;
    d_result->net_profit = net_profit;
    d_result->net_profit_pct = net_profit_pct;

    // Compute maximum drawdown
    float mdd_pct = 0.0f;
    float mdd_absolute = 0.0f;
    size_t peak_idx = 0;
    size_t trough_idx = 0;

    compute_mdd_device(d_equity_curve, curve_length, mdd_pct, mdd_absolute, peak_idx, trough_idx);

    d_result->maximum_drawdown = mdd_pct;
    d_result->maximum_drawdown_absolute = mdd_absolute;
    d_result->peak_index = peak_idx;
    d_result->trough_index = trough_idx;

    // Calculate Recovery Factor
    // Recovery Factor = Net Profit / Maximum Drawdown (absolute)
    if (mdd_absolute > 1e-10f) {
        d_result->recovery_factor = net_profit / mdd_absolute;
    } else {
        // No drawdown observed
        d_result->recovery_factor = (net_profit >= 0.0f) ? 1000.0f : -1000.0f;
    }
}

} // namespace cuda_kernels

// ============================================================================
// CalmarRatio Implementation
// ============================================================================

CalmarRatio::CalmarRatio() {
    int device_count;
    cudaGetDeviceCount(&device_count);
    if (device_count > 0) {
        cudaSetDevice(0);
    }
}

CalmarRatio::~CalmarRatio() {
}

CalmarRatioResult CalmarRatio::calculate_cpu(const CalmarRatioParameters& params) const {
    CalmarRatioResult result = {};

    if (params.curve_length == 0 || params.time_years <= 0.0f) {
        return result;
    }

    // Calculate annualized return
    float final_value = params.equity_curve[params.curve_length - 1];
    result.final_value = final_value;

    float ratio = final_value / params.initial_capital;
    if (ratio <= 0.0f) {
        result.annualized_return = -1.0f;
        result.annualized_return_pct = -100.0f;
    } else {
        float exponent = 1.0f / params.time_years;
        float annualized = powf(ratio, exponent) - 1.0f;
        result.annualized_return = annualized;
        result.annualized_return_pct = annualized * 100.0f;
    }

    // Compute maximum drawdown
    float running_max = params.equity_curve[0];
    size_t running_max_idx = 0;
    float mdd_absolute = 0.0f;
    size_t peak_idx = 0;
    size_t trough_idx = 0;

    for (size_t i = 1; i < params.curve_length; ++i) {
        float current_value = params.equity_curve[i];
        float drawdown = running_max - current_value;

        if (drawdown > mdd_absolute) {
            mdd_absolute = drawdown;
            peak_idx = running_max_idx;
            trough_idx = i;
        }

        if (current_value > running_max) {
            running_max = current_value;
            running_max_idx = i;
        }
    }

    float mdd_pct = 0.0f;
    if (running_max > 1e-10f) {
        mdd_pct = (mdd_absolute / running_max) * 100.0f;
    }

    result.maximum_drawdown = mdd_pct;
    result.peak_index = peak_idx;
    result.trough_index = trough_idx;

    // Calculate Calmar Ratio
    if (mdd_pct > 1e-10f) {
        result.calmar_ratio = result.annualized_return_pct / mdd_pct;
    } else {
        result.calmar_ratio = (result.annualized_return >= 0.0f) ? 1000.0f : -1000.0f;
    }

    return result;
}

CalmarRatioResult CalmarRatio::calculate_gpu(const CalmarRatioParameters& params) const {
    CalmarRatioResult result = {};

    if (params.curve_length == 0) {
        return result;
    }

    float* d_equity_curve = nullptr;
    CalmarRatioResult* d_result = nullptr;

    // Allocate device memory
    cudaMalloc(&d_equity_curve, params.curve_length * sizeof(float));
    cudaMalloc(&d_result, sizeof(CalmarRatioResult));

    // Copy data to device
    cudaMemcpy(d_equity_curve, params.equity_curve, params.curve_length * sizeof(float), cudaMemcpyHostToDevice);

    // Launch kernel
    cuda_kernels::calmar_ratio_kernel<<<1, 32>>>(d_equity_curve, params.curve_length, params.initial_capital, params.time_years, d_result);

    // Copy result back
    cudaMemcpy(&result, d_result, sizeof(CalmarRatioResult), cudaMemcpyDeviceToHost);

    // Cleanup
    cudaFree(d_equity_curve);
    cudaFree(d_result);

    return result;
}

// ============================================================================
// RecoveryTime Implementation
// ============================================================================

RecoveryTime::RecoveryTime() {
    int device_count;
    cudaGetDeviceCount(&device_count);
    if (device_count > 0) {
        cudaSetDevice(0);
    }
}

RecoveryTime::~RecoveryTime() {
}

RecoveryTimeResult RecoveryTime::calculate_cpu(const RecoveryTimeParameters& params) const {
    RecoveryTimeResult result = {};

    if (params.curve_length < 2) {
        return result;
    }

    float total_recovery_time = 0.0f;
    float max_recovery_time = 0.0f;
    size_t num_events = 0;
    size_t longest_recovery_peak_idx = 0;
    size_t longest_recovery_trough_idx = 0;
    size_t longest_recovery_end_idx = 0;

    float running_max = params.equity_curve[0];
    size_t running_max_idx = 0;
    bool in_drawdown = false;
    size_t peak_idx = 0;

    for (size_t i = 1; i < params.curve_length; ++i) {
        float current_value = params.equity_curve[i];

        if (current_value > running_max) {
            running_max = current_value;
            running_max_idx = i;
            in_drawdown = false;
        } else if (current_value < running_max && !in_drawdown) {
            in_drawdown = true;
            peak_idx = running_max_idx;
        }

        if (in_drawdown && current_value >= running_max) {
            size_t recovery_time = i - peak_idx;
            total_recovery_time += static_cast<float>(recovery_time);
            num_events++;

            if (recovery_time > max_recovery_time) {
                max_recovery_time = static_cast<float>(recovery_time);
                longest_recovery_peak_idx = peak_idx;
                longest_recovery_trough_idx = i - 1;
                longest_recovery_end_idx = i;
            }

            in_drawdown = false;
            running_max = current_value;
            running_max_idx = i;
        }
    }

    if (in_drawdown) {
        size_t recovery_time = params.curve_length - 1 - peak_idx;
        total_recovery_time += static_cast<float>(recovery_time);
        num_events++;

        if (recovery_time > max_recovery_time) {
            max_recovery_time = static_cast<float>(recovery_time);
            longest_recovery_peak_idx = peak_idx;
            longest_recovery_trough_idx = params.curve_length - 1;
            longest_recovery_end_idx = params.curve_length - 1;
        }
    }

    result.num_drawdown_events = num_events;
    result.max_recovery_time = max_recovery_time;
    result.mean_recovery_time = (num_events > 0) ? (total_recovery_time / num_events) : 0.0f;
    result.longest_recovery_peak_idx = longest_recovery_peak_idx;
    result.longest_recovery_trough_idx = longest_recovery_trough_idx;
    result.longest_recovery_end_idx = longest_recovery_end_idx;

    return result;
}

RecoveryTimeResult RecoveryTime::calculate_gpu(const RecoveryTimeParameters& params) const {
    RecoveryTimeResult result = {};

    if (params.curve_length < 2) {
        return result;
    }

    float* d_equity_curve = nullptr;
    RecoveryTimeResult* d_result = nullptr;

    cudaMalloc(&d_equity_curve, params.curve_length * sizeof(float));
    cudaMalloc(&d_result, sizeof(RecoveryTimeResult));

    cudaMemcpy(d_equity_curve, params.equity_curve, params.curve_length * sizeof(float), cudaMemcpyHostToDevice);

    cuda_kernels::recovery_time_kernel<<<1, 32>>>(d_equity_curve, params.curve_length, d_result);

    cudaMemcpy(&result, d_result, sizeof(RecoveryTimeResult), cudaMemcpyDeviceToHost);

    cudaFree(d_equity_curve);
    cudaFree(d_result);

    return result;
}

// ============================================================================
// RecoveryFactor Implementation
// ============================================================================

RecoveryFactor::RecoveryFactor() {
    int device_count;
    cudaGetDeviceCount(&device_count);
    if (device_count > 0) {
        cudaSetDevice(0);
    }
}

RecoveryFactor::~RecoveryFactor() {
}

RecoveryFactorResult RecoveryFactor::calculate_cpu(const RecoveryFactorParameters& params) const {
    RecoveryFactorResult result = {};

    if (params.curve_length == 0) {
        return result;
    }

    // Get final value and calculate net profit
    float final_value = params.equity_curve[params.curve_length - 1];
    float net_profit = final_value - params.initial_capital;
    float net_profit_pct = (params.initial_capital > 1e-10f) ? (net_profit / params.initial_capital) * 100.0f : 0.0f;

    result.final_value = final_value;
    result.net_profit = net_profit;
    result.net_profit_pct = net_profit_pct;

    // Compute maximum drawdown
    float running_max = params.equity_curve[0];
    size_t running_max_idx = 0;
    float mdd_absolute = 0.0f;
    size_t peak_idx = 0;
    size_t trough_idx = 0;

    for (size_t i = 1; i < params.curve_length; ++i) {
        float current_value = params.equity_curve[i];
        float drawdown = running_max - current_value;

        if (drawdown > mdd_absolute) {
            mdd_absolute = drawdown;
            peak_idx = running_max_idx;
            trough_idx = i;
        }

        if (current_value > running_max) {
            running_max = current_value;
            running_max_idx = i;
        }
    }

    float mdd_pct = 0.0f;
    if (running_max > 1e-10f) {
        mdd_pct = (mdd_absolute / running_max) * 100.0f;
    }

    result.maximum_drawdown = mdd_pct;
    result.maximum_drawdown_absolute = mdd_absolute;
    result.peak_index = peak_idx;
    result.trough_index = trough_idx;

    // Calculate Recovery Factor
    if (mdd_absolute > 1e-10f) {
        result.recovery_factor = net_profit / mdd_absolute;
    } else {
        result.recovery_factor = (net_profit >= 0.0f) ? 1000.0f : -1000.0f;
    }

    return result;
}

RecoveryFactorResult RecoveryFactor::calculate_gpu(const RecoveryFactorParameters& params) const {
    RecoveryFactorResult result = {};

    if (params.curve_length == 0) {
        return result;
    }

    float* d_equity_curve = nullptr;
    RecoveryFactorResult* d_result = nullptr;

    cudaMalloc(&d_equity_curve, params.curve_length * sizeof(float));
    cudaMalloc(&d_result, sizeof(RecoveryFactorResult));

    cudaMemcpy(d_equity_curve, params.equity_curve, params.curve_length * sizeof(float), cudaMemcpyHostToDevice);

    cuda_kernels::recovery_factor_kernel<<<1, 32>>>(d_equity_curve, params.curve_length, params.initial_capital, d_result);

    cudaMemcpy(&result, d_result, sizeof(RecoveryFactorResult), cudaMemcpyDeviceToHost);

    cudaFree(d_equity_curve);
    cudaFree(d_result);

    return result;
}

} // namespace risk_metrics
} // namespace tailwarp

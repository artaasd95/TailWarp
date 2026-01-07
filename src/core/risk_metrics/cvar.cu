// CVaR (Conditional Value at Risk) computation (GPU)
// Tail risk metric for position sizing and constraints

#include <cuda_runtime.h>

// Compute CVaR at given confidence level
__global__ void cvar_kernel(
    const float* returns,  // sorted in ascending order
    float* cvar_out,
    int n_samples,
    float alpha  // e.g., 0.95 for 95% CVaR
) {
    if (threadIdx.x != 0) return;
    
    int tail_start = (int)(n_samples * (1.0f - alpha));
    if (tail_start >= n_samples) tail_start = n_samples - 1;
    
    // Average of worst (1-alpha)% outcomes
    float sum = 0.0f;
    int count = n_samples - tail_start;
    for (int i = tail_start; i < n_samples; i++) {
        sum += returns[i];
    }
    
    *cvar_out = sum / count;
}

// TODO: Add VaR kernel
// TODO: Add tail index estimation (EVT)
// TODO: Add κ metric for sample sizing


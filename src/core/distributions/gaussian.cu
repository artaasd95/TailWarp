// Gaussian sampler (GPU) — reference Phase 1 baseline distribution

#include <curand_kernel.h>
#include "gaussian_launch.h"

__global__ void sample_gaussian_kernel(
    float* samples,
    int n_samples,
    unsigned long long seed
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= n_samples) return;

    curandState state;
    curand_init(seed, idx, 0, &state);
    samples[idx] = curand_normal(&state);
}

void tailwarp_gaussian_launch_kernel(
    float* d_samples,
    int n_samples,
    unsigned long long seed
) {
    if (!d_samples || n_samples <= 0) return;
    const int threads = 256;
    const int blocks = (n_samples + threads - 1) / threads;
    sample_gaussian_kernel<<<blocks, threads>>>(d_samples, n_samples, seed);
}

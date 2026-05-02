// Student-t distribution sampler (GPU)
// Heavy-tailed scenarios for tail risk modeling

#include <curand_kernel.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

__global__ void sample_student_t_kernel(
    float* samples,
    int n_samples,
    float nu,  // degrees of freedom
    unsigned long long seed
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= n_samples) return;
    
    curandState state;
    curand_init(seed, idx, 0, &state);
    
    // Box-Muller for normal
    float u1 = curand_uniform(&state);
    float u2 = curand_uniform(&state);
    float z = sqrtf(-2.0f * logf(u1)) * cosf(2.0f * M_PI * u2);
    
    // Chi-squared for denominator
    float chi_sq = 0.0f;
    for (int i = 0; i < (int)nu; i++) {
        float g = curand_normal(&state);
        chi_sq += g * g;
    }
    
    // Student-t = Z / sqrt(chi_sq / nu)
    samples[idx] = z / sqrtf(chi_sq / nu);
}

// TODO: Add α-stable sampler
// TODO: Add multivariate support

#include "student_t_launch.h"

void tailwarp_student_t_launch_kernel(
    float* d_samples,
    int n_samples,
    float nu,
    unsigned long long seed
) {
    if (!d_samples || n_samples <= 0) return;
    const int threads = 256;
    const int blocks = (n_samples + threads - 1) / threads;
    sample_student_t_kernel<<<blocks, threads>>>(d_samples, n_samples, nu, seed);
}

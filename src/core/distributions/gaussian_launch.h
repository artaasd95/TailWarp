#pragma once

#ifdef __cplusplus
extern "C" {
#endif

void tailwarp_gaussian_launch_kernel(
    float* d_samples,
    int n_samples,
    unsigned long long seed
);

#ifdef __cplusplus
}
#endif

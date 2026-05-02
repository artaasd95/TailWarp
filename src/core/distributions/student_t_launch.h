// Host-callable launch for Student-t kernel (defined in student_t.cu).
#pragma once

#ifdef __cplusplus
extern "C" {
#endif

void tailwarp_student_t_launch_kernel(
    float* d_samples,
    int n_samples,
    float nu,
    unsigned long long seed
);

#ifdef __cplusplus
}
#endif

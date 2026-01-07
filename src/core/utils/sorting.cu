// GPU sorting utilities for risk metrics

#include <thrust/sort.h>
#include <thrust/device_ptr.h>

// Wrapper for thrust sort (needed for CVaR, VaR)
extern "C" void gpu_sort_float(float* data, int n) {
    thrust::device_ptr<float> ptr(data);
    thrust::sort(ptr, ptr + n);
}

// TODO: Add parallel reduction for moments
// TODO: Add argmax/argmin kernels


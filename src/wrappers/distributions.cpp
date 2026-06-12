#include "distributions.h"

#include <cuda_runtime.h>

#include <cmath>
#include <cstdlib>
#include <stdexcept>
#include <string>

#include "core/distributions/gaussian_launch.h"
#include "core/distributions/student_t_launch.h"

namespace tailwarp {
namespace {

void throw_cuda(cudaError_t err, const char* what) {
    if (err != cudaSuccess) {
        throw std::runtime_error(std::string(what) + ": " + cudaGetErrorString(err));
    }
}

}  // namespace

std::vector<float> sample_student_t(
    int n_samples,
    float nu,
    unsigned long long seed
) {
    if (n_samples <= 0) {
        return {};
    }
    if (nu <= 0.0f || std::floor(nu) != static_cast<double>(nu)) {
        throw std::invalid_argument(
            "student_t degrees of freedom (nu) must be a positive integer");
    }
    float* d = nullptr;
    throw_cuda(cudaMalloc(&d, static_cast<size_t>(n_samples) * sizeof(float)), "cudaMalloc");
    tailwarp_student_t_launch_kernel(d, n_samples, nu, seed);
    throw_cuda(cudaGetLastError(), "sample_student_t kernel");
    std::vector<float> host(static_cast<size_t>(n_samples));
    throw_cuda(
        cudaMemcpy(host.data(), d, static_cast<size_t>(n_samples) * sizeof(float), cudaMemcpyDeviceToHost),
        "cudaMemcpy D2H");
    cudaFree(d);
    return host;
}

std::vector<float> sample_gaussian(int n_samples, unsigned long long seed) {
    if (n_samples <= 0) {
        return {};
    }
    float* d = nullptr;
    throw_cuda(cudaMalloc(&d, static_cast<size_t>(n_samples) * sizeof(float)), "cudaMalloc");
    tailwarp_gaussian_launch_kernel(d, n_samples, seed);
    throw_cuda(cudaGetLastError(), "sample_gaussian kernel");
    std::vector<float> host(static_cast<size_t>(n_samples));
    throw_cuda(
        cudaMemcpy(host.data(), d, static_cast<size_t>(n_samples) * sizeof(float), cudaMemcpyDeviceToHost),
        "cudaMemcpy D2H");
    cudaFree(d);
    return host;
}

}  // namespace tailwarp

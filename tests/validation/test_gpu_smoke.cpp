// S6-02 GPU kernel smoke test — minimal device path for ctest -R gpu_smoke.

#include "../../src/wrappers/distributions.h"

#include <cuda_runtime.h>
#include <gtest/gtest.h>

#include <cmath>
#include <vector>

namespace {

bool cuda_device_available() {
    int n = 0;
    return cudaGetDeviceCount(&n) == cudaSuccess && n > 0;
}

}  // namespace

TEST(GpuSmoke, StudentTSamplerLaunches) {
    if (!cuda_device_available()) {
        GTEST_SKIP() << "No CUDA device";
    }
    const int n = 1024;
    const float nu = 4.0f;
    auto samples = tailwarp::sample_student_t(n, nu, 42ULL);
    ASSERT_EQ(static_cast<int>(samples.size()), n);
    for (float x : samples) {
        EXPECT_FALSE(std::isnan(x));
        EXPECT_FALSE(std::isinf(x));
    }
}

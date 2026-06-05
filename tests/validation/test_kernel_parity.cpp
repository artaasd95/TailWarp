// Golden / parity tests for non-placeholder kernels (SP-MATH-04).
// GPU vs CPU: statistical tolerances (different RNG streams); host metrics: exact.

#include "../../src/wrappers/distributions.h"

#include <vector>

std::vector<float> sample_student_t_cpu(int n, float nu, unsigned long long seed);
#include "../../src/wrappers/risk_metrics.h"

#include <cuda_runtime.h>
#include <gtest/gtest.h>

#include <cmath>
#include <numeric>
#include <vector>

namespace {

bool cuda_device_available() {
    int n = 0;
    return cudaGetDeviceCount(&n) == cudaSuccess && n > 0;
}

double sample_mean(const std::vector<float>& v) {
    double s = 0.0;
    for (float x : v) {
        s += static_cast<double>(x);
    }
    return s / static_cast<double>(v.size());
}

double sample_var(const std::vector<float>& v, double mean) {
    double s = 0.0;
    for (float x : v) {
        const double d = static_cast<double>(x) - mean;
        s += d * d;
    }
    return s / static_cast<double>(v.size());
}

void assert_finite(const std::vector<float>& v) {
    for (float x : v) {
        ASSERT_FALSE(std::isnan(x));
        ASSERT_FALSE(std::isinf(x));
    }
}

}  // namespace

// Tolerances documented in docs/VALIDATION.md (Parity tolerances).
constexpr double kStudentTMeanAbsTol = 0.04;
constexpr double kStudentTVarRelTol = 0.12;
constexpr float kCvarAbsTol = 1e-5f;

TEST(KernelParity, CvarGoldenVectorHost) {
    const std::vector<float> returns = {-0.3f, -0.2f, -0.1f, 0.0f, 0.05f, 0.1f};
    const float cvar = tailwarp::compute_cvar(returns, 0.8f);
    EXPECT_NEAR(cvar, -0.25f, kCvarAbsTol);
}

TEST(KernelParity, VarLeCvarHost) {
    std::vector<float> returns(500);
    for (int i = 0; i < 500; ++i) {
        returns[static_cast<size_t>(i)] = static_cast<float>(i - 250) / 50.0f;
    }
    const float alpha = 0.9f;
    EXPECT_LE(tailwarp::compute_cvar(returns, alpha), tailwarp::compute_var(returns, alpha) + 1e-5f);
}

TEST(KernelParity, StudentTGpuMomentsVsTheory) {
    if (!cuda_device_available()) {
        GTEST_SKIP() << "No CUDA device";
    }
    const int n = 200000;
    const float nu = 6.0f;
    auto gpu = tailwarp::sample_student_t(n, nu, 99ULL);
    assert_finite(gpu);
    const double mean = sample_mean(gpu);
    const double var = sample_var(gpu, mean);
    const double theory_var = static_cast<double>(nu) / static_cast<double>(nu - 2.0f);
    EXPECT_NEAR(mean, 0.0, kStudentTMeanAbsTol);
    EXPECT_NEAR(var, theory_var, theory_var * kStudentTVarRelTol);
}

TEST(KernelParity, StudentTCpuReferenceFinite) {
    auto cpu = sample_student_t_cpu(10000, 4.0f, 42ULL);
    assert_finite(cpu);
}

TEST(KernelParity, WarningStateDeterministicGolden) {
    tailwarp::WarningStateParams p{
        .solvency_distance = 8.0f,
        .max_drawdown = 0.05f,
        .gross_exposure = 2.5f,
        .cvar_95 = -0.08f,
    };
    auto r = tailwarp::compute_warning_state(p);
    EXPECT_EQ(r.state, tailwarp::WarningState::GREEN);
}

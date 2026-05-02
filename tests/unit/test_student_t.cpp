// Unit test: Student-t sampler

#include "../../src/wrappers/distributions.h"
#include <gtest/gtest.h>
#include <cmath>

TEST(StudentT, OutputSize) {
    auto samples = tailwarp::sample_student_t(1000, 4.0f, 42);
    EXPECT_EQ(samples.size(), 1000);
}

TEST(StudentT, NoNaNOrInf) {
    auto samples = tailwarp::sample_student_t(10000, 4.0f, 42);
    for (float x : samples) {
        EXPECT_FALSE(std::isnan(x));
        EXPECT_FALSE(std::isinf(x));
    }
}

TEST(StudentT, MomentsVsTheory) {
    const int n = 200000;
    const float nu = 6.0f;
    auto s = tailwarp::sample_student_t(n, nu, 12345ULL);
    ASSERT_EQ(static_cast<int>(s.size()), n);
    double mean = 0.0;
    for (float x : s) {
        mean += static_cast<double>(x);
    }
    mean /= static_cast<double>(n);
    double var = 0.0;
    for (float x : s) {
        const double d = static_cast<double>(x) - mean;
        var += d * d;
    }
    var /= static_cast<double>(n);
    const double theory_var = static_cast<double>(nu) / static_cast<double>(nu - 2.0f);
    EXPECT_NEAR(mean, 0.0, 0.03);
    EXPECT_NEAR(var, theory_var, 0.08);
}

TEST(StudentT, GaussianBaselineFinite) {
    auto g = tailwarp::sample_gaussian(50000, 7ULL);
    for (float x : g) {
        EXPECT_FALSE(std::isnan(x));
        EXPECT_FALSE(std::isinf(x));
    }
}


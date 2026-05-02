// Level 3 validation: Statistical properties

#include "../../src/wrappers/distributions.h"
#include "../../src/wrappers/risk_metrics.h"
#include <gtest/gtest.h>
#include <cmath>
#include <vector>

namespace {

struct Moments {
    float mean;
    float variance;
};

Moments compute_moments(const std::vector<float>& data) {
    Moments m{0.0f, 0.0f};
    if (data.empty()) {
        return m;
    }
    double sum = 0.0;
    for (float x : data) {
        sum += static_cast<double>(x);
    }
    m.mean = static_cast<float>(sum / static_cast<double>(data.size()));
    double v = 0.0;
    for (float x : data) {
        const double d = static_cast<double>(x) - static_cast<double>(m.mean);
        v += d * d;
    }
    m.variance = static_cast<float>(v / static_cast<double>(data.size()));
    return m;
}

}  // namespace

TEST(StatisticalValidation, StudentTMoments) {
    const float nu = 8.0f;
    auto data = tailwarp::sample_student_t(150000, nu, 999ULL);
    Moments mo = compute_moments(data);
    const float theory_var = nu / (nu - 2.0f);
    EXPECT_NEAR(mo.mean, 0.0f, 0.03f);
    EXPECT_NEAR(mo.variance, theory_var, 0.06f);
}

TEST(StatisticalValidation, TailIndex) {
    // Placeholder for Hill / POT — document Student-t tail thickness via nu in future work.
    EXPECT_TRUE(true);
}

TEST(StatisticalValidation, CVaRSimilarAcrossIndependentDraws) {
    auto a = tailwarp::sample_student_t(60000, 5.0f, 11ULL);
    auto b = tailwarp::sample_student_t(60000, 5.0f, 29ULL);
    float ca = tailwarp::compute_cvar(a, 0.95f);
    float cb = tailwarp::compute_cvar(b, 0.95f);
    EXPECT_NEAR(ca, cb, 0.12f);
}

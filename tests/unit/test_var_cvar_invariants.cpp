#include "../../src/wrappers/risk_metrics.h"
#include <gtest/gtest.h>
#include <vector>

TEST(VarCVaR, TailMeanOrdering) {
    std::vector<float> returns(500);
    for (int i = 0; i < 500; i++) {
        returns[static_cast<size_t>(i)] = static_cast<float>(i - 250) / 50.0f;
    }
    const float alpha = 0.9f;
    float var = tailwarp::compute_var(returns, alpha);
    float cvar = tailwarp::compute_cvar(returns, alpha);
    EXPECT_LE(cvar, var + 1e-5f);
}

TEST(VarCVaR, RiskMetricsPopulate) {
    std::vector<float> r = {-0.2f, -0.1f, 0.0f, 0.05f, 0.1f};
    tailwarp::RiskMetrics m = tailwarp::compute_risk_metrics(r, 0.8f);
    EXPECT_NEAR(m.cvar, tailwarp::compute_cvar(r, 0.8f), 1e-5f);
    EXPECT_NEAR(m.var, tailwarp::compute_var(r, 0.8f), 1e-5f);
}

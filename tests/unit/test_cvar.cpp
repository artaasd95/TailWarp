// Unit test: CVaR computation

#include "../../src/wrappers/risk_metrics.h"
#include "../../src/reference/cvar_cpu.cpp"
#include <gtest/gtest.h>
#include <vector>

TEST(CVaR, SimpleCase) {
    std::vector<float> returns = {-0.1f, -0.05f, 0.0f, 0.02f, 0.05f};
    float cvar = tailwarp::compute_cvar(returns, 0.8f);
    
    // Worst 20% = {-0.1}
    EXPECT_NEAR(cvar, -0.1f, 1e-5f);
}

TEST(CVaR, Monotonicity) {
    std::vector<float> returns(1000);
    for (int i = 0; i < 1000; i++) {
        returns[i] = static_cast<float>(i - 500) / 100.0f;
    }
    
    float cvar_90 = tailwarp::compute_cvar(returns, 0.90f);
    float cvar_95 = tailwarp::compute_cvar(returns, 0.95f);
    float cvar_99 = tailwarp::compute_cvar(returns, 0.99f);
    
    // CVaR should decrease (more negative) as alpha increases
    EXPECT_LT(cvar_99, cvar_95);
    EXPECT_LT(cvar_95, cvar_90);
}

TEST(CVaR, GPUvsCPU) {
    // TODO: Compare GPU and CPU implementations
    EXPECT_TRUE(true);  // Placeholder
}


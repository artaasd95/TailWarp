// Level 4 validation: End-to-end pipeline

#include "../../src/algorithms/position_sizing.h"
#include "../../src/algorithms/sample_covariance_with_ridge.h"
#include <gtest/gtest.h>

TEST(EndToEnd, CVaRPositionSizing) {
    // Full pipeline: sample -> compute payoff -> CVaR -> size
    float max_cvar = 0.05f;
    float price = 100.0f;
    
    auto result = tailwarp::compute_position_size(
        max_cvar, price, 100000, 4.0f, 0.95f, 42ULL
    );
    
    // Should produce valid result
    EXPECT_GE(result.optimal_size, 0.0f);
    EXPECT_LE(result.expected_cvar, max_cvar);
    
    // TODO: Add more comprehensive checks
}

TEST(EndToEnd, SampleCovarianceWithRidge) {
    std::vector<std::vector<float>> ret;
    for (int t = 0; t < 100; ++t) {
        float a = static_cast<float>(t) * 0.01f;
        float b = static_cast<float>(t) * 0.02f + 0.1f;
        ret.push_back({a, b});
    }
    std::vector<float> cov = tailwarp::sample_covariance_with_ridge(ret);
    ASSERT_EQ(cov.size(), 4u);
    EXPECT_GT(cov[0], 0.0f);
    EXPECT_GT(cov[3], 0.0f);
}


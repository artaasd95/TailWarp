// Level 4 validation: End-to-end pipeline

#include "../../src/algorithms/position_sizing.cpp"
#include <gtest/gtest.h>

TEST(EndToEnd, CVaRPositionSizing) {
    // Full pipeline: sample -> compute payoff -> CVaR -> size
    float max_cvar = 0.05f;
    float price = 100.0f;
    
    auto result = tailwarp::compute_position_size(
        max_cvar, price, 1000000, 4.0f
    );
    
    // Should produce valid result
    EXPECT_GE(result.optimal_size, 0.0f);
    EXPECT_LE(result.expected_cvar, max_cvar);
    
    // TODO: Add more comprehensive checks
}

TEST(EndToEnd, RobustCovarianceEstimation) {
    // TODO: Full pipeline for covariance estimation
    EXPECT_TRUE(true);  // Placeholder
}


#include "../../src/algorithms/sample_covariance_with_ridge.h"
#include <gtest/gtest.h>
#include <vector>

TEST(SampleCovarianceWithRidge, SymmetricPositiveDiagonal) {
    std::vector<std::vector<float>> ret;
    for (int t = 0; t < 50; ++t) {
        float a = static_cast<float>(t) * 0.01f;
        float b = static_cast<float>(t) * 0.02f + 0.1f;
        ret.push_back({a, b});
    }
    auto cov = tailwarp::sample_covariance_with_ridge(ret, 1e-4f);
    ASSERT_EQ(cov.size(), 4u);
    EXPECT_NEAR(cov[0], cov[3], 1e-5f);  // symmetric 2x2 layout [00,01,10,11]
    EXPECT_NEAR(cov[1], cov[2], 1e-5f);
    EXPECT_GT(cov[0], 0.0f);
    EXPECT_GT(cov[3], 0.0f);
}

TEST(SampleCovarianceWithRidge, EmptyReturnsEmpty) {
    EXPECT_TRUE(tailwarp::sample_covariance_with_ridge({}).empty());
}

TEST(SampleCovarianceWithRidge, SingleSampleUsesIdentityDiagonal) {
    std::vector<std::vector<float>> ret = {{0.1f, -0.2f}};
    auto cov = tailwarp::sample_covariance_with_ridge(ret);
    ASSERT_EQ(cov.size(), 4u);
    EXPECT_NEAR(cov[0], 1.0f, 1e-5f);
    EXPECT_NEAR(cov[3], 1.0f, 1e-5f);
}

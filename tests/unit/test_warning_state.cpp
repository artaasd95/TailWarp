// Unit tests: TailWarpWarningState (S2-02 / S3-04 benchmark path)

#include "../../src/wrappers/risk_metrics.h"
#include <gtest/gtest.h>

using namespace tailwarp;

static WarningStateParams healthy() {
    return WarningStateParams{
        .solvency_distance = 8.0f,
        .max_drawdown = 0.05f,
        .gross_exposure = 2.0f,
        .cvar_95 = -0.08f,
    };
}

TEST(WarningState, AllGreen) {
    auto result = compute_warning_state(healthy());
    EXPECT_EQ(result.state, WarningState::GREEN);
    EXPECT_EQ(result.triggered_metrics, 0);
    EXPECT_NE(result.reason.find("GREEN"), std::string::npos);
}

TEST(WarningState, SolvencyCritical) {
    auto params = healthy();
    params.solvency_distance = 0.8f;
    auto result = compute_warning_state(params);
    EXPECT_EQ(result.state, WarningState::CRITICAL);
    EXPECT_TRUE(result.triggered_metrics & (1 << 0));
}

TEST(WarningState, DrawdownYellow) {
    auto params = healthy();
    params.max_drawdown = 0.25f;
    auto result = compute_warning_state(params);
    EXPECT_EQ(result.state, WarningState::YELLOW);
    EXPECT_TRUE(result.triggered_metrics & (1 << 1));
}

TEST(WarningState, ExposureRed) {
    auto params = healthy();
    params.gross_exposure = 6.0f;
    auto result = compute_warning_state(params);
    EXPECT_EQ(result.state, WarningState::RED);
    EXPECT_TRUE(result.triggered_metrics & (1 << 2));
}

TEST(WarningState, CvarRed) {
    auto params = healthy();
    params.cvar_95 = -0.20f;
    auto result = compute_warning_state(params);
    EXPECT_EQ(result.state, WarningState::RED);
    EXPECT_TRUE(result.triggered_metrics & (1 << 3));
}

TEST(WarningState, MonotonicitySolvency) {
    auto params = healthy();
    auto green = compute_warning_state(params);
    params.solvency_distance = 2.5f;
    auto yellow = compute_warning_state(params);
    params.solvency_distance = 1.5f;
    auto red = compute_warning_state(params);
    params.solvency_distance = 0.5f;
    auto critical = compute_warning_state(params);

    EXPECT_LE(green.state, yellow.state);
    EXPECT_LE(yellow.state, red.state);
    EXPECT_LE(red.state, critical.state);
}

TEST(WarningState, Deterministic) {
    auto params = healthy();
    params.max_drawdown = 0.35f;
    params.gross_exposure = 4.0f;
    auto a = compute_warning_state(params);
    auto b = compute_warning_state(params);
    EXPECT_EQ(a.state, b.state);
    EXPECT_EQ(a.triggered_metrics, b.triggered_metrics);
    EXPECT_EQ(a.reason, b.reason);
}

TEST(BenchmarkRiskMetrics, CVaRWorstTail) {
    std::vector<float> returns = {-0.1f, -0.05f, 0.0f, 0.02f, 0.05f};
    float cvar = compute_cvar(returns, 0.8f);
    EXPECT_NEAR(cvar, -0.1f, 1e-5f);
}

TEST(BenchmarkRiskMetrics, CVaRMonotonicity) {
    std::vector<float> returns(100);
    for (int i = 0; i < 100; ++i) {
        returns[i] = static_cast<float>(i - 50) / 100.0f;
    }
    float c90 = compute_cvar(returns, 0.90f);
    float c95 = compute_cvar(returns, 0.95f);
    float c99 = compute_cvar(returns, 0.99f);
    EXPECT_LT(c99, c95);
    EXPECT_LT(c95, c90);
}

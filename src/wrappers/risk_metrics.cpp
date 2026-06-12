#include "risk_metrics.h"

#include <algorithm>
#include <cmath>
#include <numeric>

namespace tailwarp {
namespace {

int worst_tail_count(int n, float alpha) {
    if (n <= 0) return 0;
    int k = static_cast<int>(std::ceil((1.0f - alpha) * static_cast<float>(n)));
    k = std::max(1, k);
    k = std::min(k, n);
    return k;
}

void sort_copy(const std::vector<float>& returns, std::vector<float>& sorted) {
    sorted = returns;
    std::sort(sorted.begin(), sorted.end());
}

}  // namespace

float compute_var(const std::vector<float>& returns, float alpha) {
    if (alpha <= 0.0f || alpha >= 1.0f) {
        return 0.0f;
    }
    if (returns.empty()) {
        return 0.0f;
    }
    std::vector<float> s;
    sort_copy(returns, s);
    const int n = static_cast<int>(s.size());
    const int k = worst_tail_count(n, alpha);
    return s[static_cast<size_t>(k - 1)];
}

float compute_cvar(const std::vector<float>& returns, float alpha) {
    if (alpha <= 0.0f || alpha >= 1.0f) {
        return 0.0f;
    }
    if (returns.empty()) {
        return 0.0f;
    }
    std::vector<float> s;
    sort_copy(returns, s);
    const int n = static_cast<int>(s.size());
    const int k = worst_tail_count(n, alpha);
    const float sum = std::accumulate(s.begin(), s.begin() + k, 0.0f);
    return sum / static_cast<float>(k);
}

RiskMetrics compute_risk_metrics(const std::vector<float>& returns, float alpha) {
    RiskMetrics m{};
    if (returns.empty()) {
        return m;
    }
    const size_t n = returns.size();
    double sum = 0.0;
    for (float x : returns) {
        sum += static_cast<double>(x);
    }
    m.mean = static_cast<float>(sum / static_cast<double>(n));

    double var_acc = 0.0;
    for (float x : returns) {
        const double d = static_cast<double>(x) - static_cast<double>(m.mean);
        var_acc += d * d;
    }
    m.std_dev = static_cast<float>(std::sqrt(var_acc / static_cast<double>(n)));

    if (n > 2u && m.std_dev > 1e-20f) {
        double m3 = 0.0;
        double m4 = 0.0;
        for (float x : returns) {
            const double d = (static_cast<double>(x) - static_cast<double>(m.mean)) / static_cast<double>(m.std_dev);
            m3 += d * d * d;
            m4 += d * d * d * d;
        }
        m.skewness = static_cast<float>(m3 / static_cast<double>(n));
        m.kurtosis = static_cast<float>(m4 / static_cast<double>(n));
    }

    m.var = compute_var(returns, alpha);
    m.cvar = compute_cvar(returns, alpha);
    return m;
}

// ============================================================================
// Warning State Computation (S2-02)
// ============================================================================

WarningStateResult compute_warning_state(const WarningStateParams& params) {
    WarningStateResult result{};
    result.state = WarningState::GREEN;
    result.triggered_metrics = 0;

    auto check_solvency = [&]() {
        int solvency_level = 0;  // 0=GREEN, 1=YELLOW, 2=RED, 3=CRITICAL
        std::string solvency_msg;

        if (params.solvency_distance <= 1.0f) {
            solvency_level = 3;
            solvency_msg = "solvency_distance ≤ 1σ (CRITICAL)";
        } else if (params.solvency_distance <= 2.0f) {
            solvency_level = 2;
            solvency_msg = "solvency_distance 1-2σ (RED)";
        } else if (params.solvency_distance <= 3.0f) {
            solvency_level = 1;
            solvency_msg = "solvency_distance 2-3σ (YELLOW)";
        } else {
            solvency_level = 0;
            solvency_msg = "solvency_distance > 3σ (GREEN)";
        }
        return std::make_pair(solvency_level, solvency_msg);
    };

    auto check_drawdown = [&]() {
        int drawdown_level = 0;
        std::string drawdown_msg;

        if (params.max_drawdown >= 0.60f) {
            drawdown_level = 3;
            drawdown_msg = "max_drawdown ≥ 60% (CRITICAL)";
        } else if (params.max_drawdown >= 0.40f) {
            drawdown_level = 2;
            drawdown_msg = "max_drawdown 40-60% (RED)";
        } else if (params.max_drawdown >= 0.20f) {
            drawdown_level = 1;
            drawdown_msg = "max_drawdown 20-40% (YELLOW)";
        } else {
            drawdown_level = 0;
            drawdown_msg = "max_drawdown < 20% (GREEN)";
        }
        return std::make_pair(drawdown_level, drawdown_msg);
    };

    auto check_exposure = [&]() {
        int exposure_level = 0;
        std::string exposure_msg;

        if (params.gross_exposure >= 8.0f) {
            exposure_level = 3;
            exposure_msg = "gross_exposure ≥ 8x (CRITICAL)";
        } else if (params.gross_exposure >= 5.0f) {
            exposure_level = 2;
            exposure_msg = "gross_exposure 5-8x (RED)";
        } else if (params.gross_exposure >= 3.0f) {
            exposure_level = 1;
            exposure_msg = "gross_exposure 3-5x (YELLOW)";
        } else {
            exposure_level = 0;
            exposure_msg = "gross_exposure < 3x (GREEN)";
        }
        return std::make_pair(exposure_level, exposure_msg);
    };

    auto check_cvar = [&]() {
        int cvar_level = 0;
        std::string cvar_msg;

        if (params.cvar_95 <= -0.25f) {
            cvar_level = 3;
            cvar_msg = "CVaR@95% ≤ -25% (CRITICAL)";
        } else if (params.cvar_95 <= -0.15f) {
            cvar_level = 2;
            cvar_msg = "CVaR@95% -15% to -25% (RED)";
        } else if (params.cvar_95 <= -0.10f) {
            cvar_level = 1;
            cvar_msg = "CVaR@95% -10% to -15% (YELLOW)";
        } else {
            cvar_level = 0;
            cvar_msg = "CVaR@95% > -10% (GREEN)";
        }
        return std::make_pair(cvar_level, cvar_msg);
    };

    auto [solvency_level, solvency_msg] = check_solvency();
    auto [drawdown_level, drawdown_msg] = check_drawdown();
    auto [exposure_level, exposure_msg] = check_exposure();
    auto [cvar_level, cvar_msg] = check_cvar();

    int max_level = std::max({solvency_level, drawdown_level, exposure_level, cvar_level});
    result.state = static_cast<WarningState>(max_level);

    if (solvency_level > 0) result.triggered_metrics |= (1 << 0);
    if (drawdown_level > 0) result.triggered_metrics |= (1 << 1);
    if (exposure_level > 0) result.triggered_metrics |= (1 << 2);
    if (cvar_level > 0) result.triggered_metrics |= (1 << 3);

    std::string state_name;
    switch (result.state) {
        case WarningState::GREEN:    state_name = "GREEN"; break;
        case WarningState::YELLOW:   state_name = "YELLOW"; break;
        case WarningState::RED:      state_name = "RED"; break;
        case WarningState::CRITICAL: state_name = "CRITICAL"; break;
    }

    result.reason = "WarningState " + state_name + ": ";
    std::vector<std::string> triggered;
    if (solvency_level > 0) triggered.push_back(solvency_msg);
    if (drawdown_level > 0) triggered.push_back(drawdown_msg);
    if (exposure_level > 0) triggered.push_back(exposure_msg);
    if (cvar_level > 0) triggered.push_back(cvar_msg);

    if (!triggered.empty()) {
        for (size_t i = 0; i < triggered.size(); ++i) {
            result.reason += triggered[i];
            if (i < triggered.size() - 1) result.reason += " | ";
        }
    } else {
        result.reason += "All metrics healthy";
    }

    return result;
}

}  // namespace tailwarp

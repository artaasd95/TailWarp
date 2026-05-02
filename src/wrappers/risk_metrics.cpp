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

}  // namespace tailwarp

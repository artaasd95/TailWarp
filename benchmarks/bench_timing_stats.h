#pragma once

#include <algorithm>
#include <cmath>
#include <vector>

inline void bench_timing_stats(
    const std::vector<double>& times_ms,
    double& mean_ms,
    double& median_ms,
    double& std_ms,
    double& p95_ms
) {
    if (times_ms.empty()) {
        mean_ms = median_ms = std_ms = p95_ms = 0.0;
        return;
    }
    std::vector<double> sorted = times_ms;
    std::sort(sorted.begin(), sorted.end());
    double sum = 0.0;
    for (double t : times_ms) {
        sum += t;
    }
    mean_ms = sum / static_cast<double>(times_ms.size());
    const size_t n = sorted.size();
    median_ms = (n % 2 == 0)
        ? (sorted[n / 2 - 1] + sorted[n / 2]) / 2.0
        : sorted[n / 2];
    const size_t p95_idx = static_cast<size_t>(
        std::ceil(0.95 * static_cast<double>(n))) - 1;
    p95_ms = sorted[std::min(p95_idx, n - 1)];
    if (n < 2) {
        std_ms = 0.0;
        return;
    }
    double var_acc = 0.0;
    for (double t : times_ms) {
        const double d = t - mean_ms;
        var_acc += d * d;
    }
    std_ms = std::sqrt(var_acc / static_cast<double>(n));
}

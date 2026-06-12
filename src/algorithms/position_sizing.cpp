// Position sizing under CVaR constraint (linear exposure in Student-t returns).

#include "position_sizing.h"

#include "../wrappers/distributions.h"
#include "../wrappers/risk_metrics.h"

#include <cmath>
#include <vector>

namespace tailwarp {

PositionSizingResult compute_position_size(
    float max_cvar_limit,
    float underlying_price,
    int n_scenarios,
    float nu,
    float alpha,
    unsigned long long seed
) {
    PositionSizingResult result{};
    result.optimal_size = 0.0f;
    result.expected_cvar = 0.0f;
    result.expected_return = 0.0f;
    result.constraint_satisfied = false;

    if (max_cvar_limit <= 0.0f || underlying_price <= 0.0f || n_scenarios < 2) {
        return result;
    }

    std::vector<float> samples = sample_student_t(n_scenarios, nu, seed);
    const float unit_cvar = compute_cvar(samples, alpha);
    const float denom = std::abs(unit_cvar);
    if (denom < 1e-12f) {
        result.optimal_size = 0.0f;
        result.expected_cvar = 0.0f;
        result.expected_return = 0.0f;
        result.constraint_satisfied = true;
        return result;
    }

    float w = max_cvar_limit / denom;

    std::vector<float> scaled(static_cast<size_t>(n_scenarios));
    for (int i = 0; i < n_scenarios; ++i) {
        scaled[static_cast<size_t>(i)] = w * samples[static_cast<size_t>(i)];
    }

    result.optimal_size = w / underlying_price;
    result.expected_cvar = compute_cvar(scaled, alpha);
    double mean = 0.0;
    for (float x : scaled) {
        mean += static_cast<double>(x);
    }
    result.expected_return = static_cast<float>(mean / static_cast<double>(n_scenarios));
    result.constraint_satisfied =
        (std::abs(result.expected_cvar) <= max_cvar_limit * (1.0f + 1e-4f));
    return result;
}

}  // namespace tailwarp

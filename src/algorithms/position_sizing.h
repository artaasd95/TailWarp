#pragma once

namespace tailwarp {

struct PositionSizingResult {
    float optimal_size;
    float expected_cvar;
    float expected_return;
    bool constraint_satisfied;
};

// Linear scale: PnL_i = size * return_i. Pick largest size with |CVaR(PnL)| <= max_cvar_limit at given alpha.
PositionSizingResult compute_position_size(
    float max_cvar_limit,
    float underlying_price,
    int n_scenarios = 1000000,
    float nu = 4.0f,
    float alpha = 0.95f,
    unsigned long long seed = 42ULL
);

}  // namespace tailwarp

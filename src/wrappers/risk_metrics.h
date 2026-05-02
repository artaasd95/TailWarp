// Host wrappers for risk metrics

#ifndef TAILWARP_RISK_METRICS_H
#define TAILWARP_RISK_METRICS_H

#include <vector>

namespace tailwarp {

struct RiskMetrics {
    float var;      // Value at Risk
    float cvar;     // Conditional VaR
    float mean;
    float std_dev;
    float skewness;
    float kurtosis;
};

// Historical VaR: (1-alpha) lower tail threshold on sorted returns (PnL convention).
float compute_var(const std::vector<float>& returns, float alpha = 0.95f);

// Expected shortfall / CVaR: mean of the worst (1-alpha) fraction (sorted ascending).
float compute_cvar(const std::vector<float>& returns, float alpha = 0.95f);

// Compute full risk metrics
RiskMetrics compute_risk_metrics(const std::vector<float>& returns, float alpha = 0.95f);

// TODO: Add tail index estimation
// TODO: Add κ metric

}  // namespace tailwarp

#endif  // TAILWARP_RISK_METRICS_H


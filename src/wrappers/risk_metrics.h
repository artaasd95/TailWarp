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

// Compute CVaR from returns
float compute_cvar(const std::vector<float>& returns, float alpha = 0.95f);

// Compute full risk metrics
RiskMetrics compute_risk_metrics(const std::vector<float>& returns, float alpha = 0.95f);

// TODO: Add tail index estimation
// TODO: Add κ metric

}  // namespace tailwarp

#endif  // TAILWARP_RISK_METRICS_H


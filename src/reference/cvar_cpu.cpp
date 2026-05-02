// CPU reference: CVaR — delegates to tailwarp::compute_cvar (single implementation).

#include "../wrappers/risk_metrics.h"
#include <vector>

float compute_cvar_cpu(std::vector<float> returns, float alpha) {
    return tailwarp::compute_cvar(returns, alpha);
}

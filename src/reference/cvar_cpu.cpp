// CPU reference: CVaR computation

#include <vector>
#include <algorithm>
#include <numeric>

float compute_cvar_cpu(std::vector<float> returns, float alpha) {
    std::sort(returns.begin(), returns.end());
    
    int tail_start = (int)(returns.size() * (1.0f - alpha));
    if (tail_start >= returns.size()) tail_start = returns.size() - 1;
    
    float sum = std::accumulate(
        returns.begin() + tail_start,
        returns.end(),
        0.0f
    );
    
    return sum / (returns.size() - tail_start);
}


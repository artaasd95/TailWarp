#pragma once

#include <vector>

namespace tailwarp {

std::vector<float> estimate_robust_covariance(
    const std::vector<std::vector<float>>& returns,
    int max_iter = 100,
    float tol = 1e-6f
);

std::vector<float> barycenter_covariances(
    const std::vector<std::vector<float>>& covs,
    int n
);

}  // namespace tailwarp

#pragma once

#include <vector>

namespace tailwarp {

// Sample covariance with diagonal ridge (host-only). NOT Tyler's M-estimator.
// Status: partial — see docs/VALIDATION.md.
std::vector<float> sample_covariance_with_ridge(
    const std::vector<std::vector<float>>& returns,
    float ridge = 1e-4f
);

std::vector<float> barycenter_covariances(
    const std::vector<std::vector<float>>& covs,
    int n
);

}  // namespace tailwarp

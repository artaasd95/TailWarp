// Robust covariance: sample covariance with ridge for numerical stability.

#include "robust_covariance.h"

#include <vector>

namespace tailwarp {

std::vector<float> estimate_robust_covariance(
    const std::vector<std::vector<float>>& returns,
    int max_iter,
    float tol
) {
    (void)max_iter;
    (void)tol;

    if (returns.empty() || returns[0].empty()) {
        return {};
    }

    const int n_samples = static_cast<int>(returns.size());
    const int n_assets = static_cast<int>(returns[0].size());
    std::vector<double> mean(static_cast<size_t>(n_assets), 0.0);

    for (int t = 0; t < n_samples; ++t) {
        for (int j = 0; j < n_assets; ++j) {
            mean[static_cast<size_t>(j)] += static_cast<double>(returns[static_cast<size_t>(t)][static_cast<size_t>(j)]);
        }
    }
    for (double& m : mean) {
        m /= static_cast<double>(n_samples);
    }

    std::vector<float> cov(static_cast<size_t>(n_assets * n_assets), 0.0f);
    if (n_samples < 2) {
        for (int i = 0; i < n_assets; ++i) {
            cov[static_cast<size_t>(i * n_assets + i)] = 1.0f;
        }
        return cov;
    }

    const double scale = 1.0 / static_cast<double>(n_samples - 1);
    for (int i = 0; i < n_assets; ++i) {
        for (int j = 0; j < n_assets; ++j) {
            double s = 0.0;
            for (int t = 0; t < n_samples; ++t) {
                const double xi =
                    static_cast<double>(returns[static_cast<size_t>(t)][static_cast<size_t>(i)]) -
                    mean[static_cast<size_t>(i)];
                const double xj =
                    static_cast<double>(returns[static_cast<size_t>(t)][static_cast<size_t>(j)]) -
                    mean[static_cast<size_t>(j)];
                s += xi * xj;
            }
            cov[static_cast<size_t>(i * n_assets + j)] = static_cast<float>(s * scale);
        }
    }

    const float ridge = 1e-4f;
    for (int i = 0; i < n_assets; ++i) {
        cov[static_cast<size_t>(i * n_assets + i)] += ridge;
    }

    return cov;
}

std::vector<float> barycenter_covariances(const std::vector<std::vector<float>>& covs, int n) {
    if (covs.empty()) {
        return {};
    }
    const int dim = n * n;
    std::vector<float> acc(static_cast<size_t>(dim), 0.0f);
    const float w = 1.0f / static_cast<float>(covs.size());
    for (const auto& c : covs) {
        if (static_cast<int>(c.size()) != dim) {
            continue;
        }
        for (int i = 0; i < dim; ++i) {
            acc[static_cast<size_t>(i)] += w * c[static_cast<size_t>(i)];
        }
    }
    return acc;
}

}  // namespace tailwarp

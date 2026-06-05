// [PLANNED] Host API for SPD manifold — not implemented for v1.0 headline paths.
// GPU stubs: src/core/manifolds/spd_operations.cu

#ifndef TAILWARP_MANIFOLDS_H
#define TAILWARP_MANIFOLDS_H

#include <vector>

namespace tailwarp {

// [PLANNED] Riemannian operations on SPD manifold — do not use in headline claims.
class SPDManifold {
public:
    static std::vector<float> exp_map(const std::vector<float>& log_matrix, int n);
    static std::vector<float> log_map(const std::vector<float>& spd_matrix, int n);
    static float distance(const std::vector<float>& A, const std::vector<float>& B, int n);
    static std::vector<float> project_to_pd(const std::vector<float>& matrix, int n, float eps = 1e-6f);
};

}  // namespace tailwarp

#endif  // TAILWARP_MANIFOLDS_H


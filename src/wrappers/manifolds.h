// Host wrappers for SPD manifold operations

#ifndef TAILWARP_MANIFOLDS_H
#define TAILWARP_MANIFOLDS_H

#include <vector>

namespace tailwarp {

// Riemannian operations on SPD manifold
class SPDManifold {
public:
    // Matrix exponential (tangent -> manifold)
    static std::vector<float> exp_map(const std::vector<float>& log_matrix, int n);
    
    // Matrix logarithm (manifold -> tangent)
    static std::vector<float> log_map(const std::vector<float>& spd_matrix, int n);
    
    // Geodesic distance
    static float distance(const std::vector<float>& A, const std::vector<float>& B, int n);
    
    // Project to positive definite cone
    static std::vector<float> project_to_pd(const std::vector<float>& matrix, int n, float eps = 1e-6f);
    
    // TODO: Add Riemannian gradient
    // TODO: Add retraction
    // TODO: Add parallel transport
};

}  // namespace tailwarp

#endif  // TAILWARP_MANIFOLDS_H


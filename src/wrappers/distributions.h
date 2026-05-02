// Host wrappers for distribution samplers

#ifndef TAILWARP_DISTRIBUTIONS_H
#define TAILWARP_DISTRIBUTIONS_H

#include <vector>

namespace tailwarp {

// Sample from Student-t distribution
std::vector<float> sample_student_t(
    int n_samples,
    float nu,  // degrees of freedom
    unsigned long long seed = 42
);

// Standard normal samples (mean 0, variance 1)
std::vector<float> sample_gaussian(
    int n_samples,
    unsigned long long seed = 42
);

// TODO: Add α-stable sampler wrapper
// TODO: Add multivariate distributions

}  // namespace tailwarp

#endif  // TAILWARP_DISTRIBUTIONS_H


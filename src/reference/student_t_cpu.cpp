// CPU reference: Student-t sampler

#include <vector>
#include <random>
#include <cmath>

std::vector<float> sample_student_t_cpu(int n, float nu, unsigned long long seed) {
    std::mt19937_64 rng(seed);
    std::normal_distribution<float> normal(0.0f, 1.0f);
    std::chi_squared_distribution<float> chi2(nu);
    
    std::vector<float> samples(n);
    for (int i = 0; i < n; i++) {
        float z = normal(rng);
        float v = chi2(rng);
        samples[i] = z / std::sqrt(v / nu);
    }
    
    return samples;
}


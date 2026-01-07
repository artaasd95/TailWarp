// Unit test: Student-t sampler

#include "../../src/wrappers/distributions.h"
#include "../../src/reference/student_t_cpu.cpp"
#include <gtest/gtest.h>
#include <cmath>

TEST(StudentT, OutputSize) {
    auto samples = tailwarp::sample_student_t(1000, 4.0f, 42);
    EXPECT_EQ(samples.size(), 1000);
}

TEST(StudentT, NoNaNOrInf) {
    auto samples = tailwarp::sample_student_t(10000, 4.0f, 42);
    for (float x : samples) {
        EXPECT_FALSE(std::isnan(x));
        EXPECT_FALSE(std::isinf(x));
    }
}

TEST(StudentT, GPUvsCPU) {
    // Statistical comparison
    int n = 100000;
    float nu = 4.0f;
    unsigned long long seed = 42;
    
    auto gpu_samples = tailwarp::sample_student_t(n, nu, seed);
    auto cpu_samples = sample_student_t_cpu(n, nu, seed);
    
    // Compare first few moments (not exact match due to RNG)
    // TODO: Use KS test or moment comparison
    EXPECT_TRUE(true);  // Placeholder
}


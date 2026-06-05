// CUDA microbench: Gaussian sampling throughput (JSON line to stdout with --json).

#include "distributions.h"

#include <chrono>
#include <cstdlib>
#include <iostream>
#include <string>

int main(int argc, char** argv) {
    int n_samples = 1'000'000;
    unsigned long long seed = 7ULL;
    bool json_out = false;
    int k_runs = 1;
    int warmup = 0;

    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "--json") {
            json_out = true;
        } else if (arg == "--samples" && i + 1 < argc) {
            n_samples = std::atoi(argv[++i]);
        } else if (arg == "--k" && i + 1 < argc) {
            k_runs = std::atoi(argv[++i]);
        } else if (arg == "--warmup" && i + 1 < argc) {
            warmup = std::atoi(argv[++i]);
        }
    }

    auto run_once = [&]() {
        const auto t0 = std::chrono::steady_clock::now();
        auto s = tailwarp::sample_gaussian(n_samples, seed);
        const auto t1 = std::chrono::steady_clock::now();
        const double ms =
            std::chrono::duration<double, std::milli>(t1 - t0).count();
        if (s.empty()) {
            std::cerr << "sample_gaussian returned empty\n";
            std::exit(1);
        }
        return ms;
    };

    for (int w = 0; w < warmup; ++w) {
        (void)run_once();
    }

    double sum_ms = 0.0;
    for (int k = 0; k < k_runs; ++k) {
        sum_ms += run_once();
    }
    const double mean_ms = sum_ms / static_cast<double>(k_runs);
    const double throughput = static_cast<double>(n_samples) / (mean_ms / 1000.0);

    if (json_out) {
        std::cout << "{"
                  << "\"name\":\"gaussian_sample\","
                  << "\"n_samples\":" << n_samples << ","
                  << "\"mean_ms\":" << mean_ms << ","
                  << "\"samples_per_sec\":" << throughput << ","
                  << "\"k_runs\":" << k_runs << ","
                  << "\"warmup_runs\":" << warmup
                  << "}\n";
    } else {
        std::cout << "gaussian n=" << n_samples << " mean_ms=" << mean_ms
                  << " samples/sec=" << throughput << "\n";
    }
    return 0;
}

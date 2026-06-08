// CUDA microbench: Student-t sampling throughput (JSON line to stdout with --json).

#include "bench_timing_stats.h"
#include "distributions.h"

#include <chrono>
#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>

int main(int argc, char** argv) {
    int n_samples = 1'000'000;
    float nu = 4.0f;
    unsigned long long seed = 42ULL;
    bool json_out = false;
    int k_runs = 1;
    int warmup = 0;

    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "--json") {
            json_out = true;
        } else if (arg == "--samples" && i + 1 < argc) {
            n_samples = std::atoi(argv[++i]);
        } else if (arg == "--nu" && i + 1 < argc) {
            nu = std::atof(argv[++i]);
        } else if (arg == "--k" && i + 1 < argc) {
            k_runs = std::atoi(argv[++i]);
        } else if (arg == "--warmup" && i + 1 < argc) {
            warmup = std::atoi(argv[++i]);
        }
    }

    auto run_once = [&]() {
        const auto t0 = std::chrono::steady_clock::now();
        auto s = tailwarp::sample_student_t(n_samples, nu, seed);
        const auto t1 = std::chrono::steady_clock::now();
        const double ms =
            std::chrono::duration<double, std::milli>(t1 - t0).count();
        if (s.empty()) {
            std::cerr << "sample_student_t returned empty\n";
            std::exit(1);
        }
        return ms;
    };

    for (int w = 0; w < warmup; ++w) {
        (void)run_once();
    }

    std::vector<double> times;
    times.reserve(static_cast<size_t>(k_runs));
    for (int k = 0; k < k_runs; ++k) {
        times.push_back(run_once());
    }

    double mean_ms = 0.0;
    double median_ms = 0.0;
    double std_ms = 0.0;
    double p95_ms = 0.0;
    bench_timing_stats(times, mean_ms, median_ms, std_ms, p95_ms);
    const double throughput =
        static_cast<double>(n_samples) / (median_ms / 1000.0);

    if (json_out) {
        std::cout << "{"
                  << "\"name\":\"student_t_sample\","
                  << "\"status\":\"ok\","
                  << "\"n_samples\":" << n_samples << ","
                  << "\"nu\":" << nu << ","
                  << "\"mean_ms\":" << mean_ms << ","
                  << "\"median_ms\":" << median_ms << ","
                  << "\"std_ms\":" << std_ms << ","
                  << "\"p95_ms\":" << p95_ms << ","
                  << "\"samples_per_sec\":" << throughput << ","
                  << "\"k_runs\":" << k_runs << ","
                  << "\"warmup_runs\":" << warmup
                  << "}\n";
    } else {
        std::cout << "student_t n=" << n_samples << " median_ms=" << median_ms
                  << " samples/sec=" << throughput << "\n";
    }
    return 0;
}

// Minimal experiment runner: writes a full experiment folder per docs/EXPERIMENTS.md

#include "json_scan.hpp"

#include <chrono>
#include <cmath>
#include <cstdio>
#include <ctime>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include <cuda_runtime.h>

#include "wrappers/distributions.h"
#include "wrappers/risk_metrics.h"

namespace {

std::string read_file(const char* path) {
    std::ifstream f(path, std::ios::binary);
    if (!f) {
        return {};
    }
    std::ostringstream buf;
    buf << f.rdbuf();
    return buf.str();
}

std::string utc_timestamp_folder() {
    using clock = std::chrono::system_clock;
    const auto t = clock::to_time_t(clock::now());
    std::tm tm{};
#ifdef _WIN32
    gmtime_s(&tm, &t);
#else
    gmtime_r(&t, &tm);
#endif
    std::ostringstream o;
    o << std::put_time(&tm, "%Y-%m-%dT%H-%M-%SZ");
    return o.str();
}

std::string git_revision() {
    std::string result;
#ifdef _WIN32
    FILE* pipe = _popen("git rev-parse HEAD 2>nul", "r");
#else
    FILE* pipe = popen("git rev-parse HEAD 2>/dev/null", "r");
#endif
    if (!pipe) {
        return "unknown";
    }
    char buf[128];
    while (fgets(buf, sizeof(buf), pipe)) {
        result += buf;
    }
#ifdef _WIN32
    _pclose(pipe);
#else
    pclose(pipe);
#endif
    while (!result.empty() && (result.back() == '\n' || result.back() == '\r')) {
        result.pop_back();
    }
    return result.empty() ? "unknown" : result;
}

void write_text(const std::string& path, const std::string& content) {
    std::ofstream f(path, std::ios::binary);
    f << content;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: experiment_run <config.json>\n";
        return 1;
    }

    const std::string cfg_text = read_file(argv[1]);
    if (cfg_text.empty()) {
        std::cerr << "Cannot read config: " << argv[1] << "\n";
        return 1;
    }

    int n_samples = 100000;
    float nu = 4.0f;
    unsigned long long seed = 42ULL;
    float alpha = 0.95f;
    std::string name = "experiment";
    std::string sampler = "student_t";

    json_find_int(cfg_text, "n_samples", n_samples);
    json_find_float(cfg_text, "nu", nu);
    json_find_uint64(cfg_text, "seed", seed);
    json_find_float(cfg_text, "alpha", alpha);
    json_find_string_quoted(cfg_text, "name", name);
    json_find_string_quoted(cfg_text, "sampler", sampler);

    const std::string stamp = utc_timestamp_folder();
    namespace fs = std::filesystem;
    const fs::path root_path = fs::path("data/output/experiments") /
                               (stamp + "__" + name + "__N" + std::to_string(n_samples) + "__seed" +
                                std::to_string(seed));
    std::error_code ec;
    fs::create_directories(root_path / "artifacts", ec);
    const std::string root = root_path.string();

    cudaEvent_t ev0{}, ev1{};
    cudaEventCreate(&ev0);
    cudaEventCreate(&ev1);

    cudaEventRecord(ev0);
    std::vector<float> samples;
    if (sampler == "gaussian") {
        samples = tailwarp::sample_gaussian(n_samples, seed);
    } else {
        samples = tailwarp::sample_student_t(n_samples, nu, seed);
    }
    cudaEventRecord(ev1);
    cudaEventSynchronize(ev1);
    float ms = 0.0f;
    cudaEventElapsedTime(&ms, ev0, ev1);
    cudaEventDestroy(ev0);
    cudaEventDestroy(ev1);

    const float cvar = tailwarp::compute_cvar(samples, alpha);
    const float var = tailwarp::compute_var(samples, alpha);

    cudaDeviceProp prop{};
    int dev = 0;
    cudaGetDevice(&dev);
    cudaGetDeviceProperties(&prop, dev);

    const std::string git = git_revision();

    const std::string config_out = root + "/config.json";
    write_text(config_out, cfg_text);

    write_text(
        root + "/environment.json",
        std::string("{\n")
            + "  \"git_commit\": \"" + git + "\",\n"
            + "  \"cuda_device\": \"" + std::string(prop.name) + "\",\n"
            + "  \"compute_capability\": " + std::to_string(prop.major) + "." + std::to_string(prop.minor) +
              ",\n"
            + "  \"driver\": \"runtime\"\n"
            + "}\n");

    write_text(
        root + "/build.json",
        std::string("{\n  \"experiment_run\": \"examples/experiment_run.cpp\",\n") +
        "  \"compiler\": \"see CMake logs\"\n}\n");

    std::ostringstream metrics;
    metrics << std::setprecision(9) << std::fixed;
    metrics << "{\n"
            << "  \"n_samples\": " << n_samples << ",\n"
            << "  \"distribution\": \"" << sampler << "\",\n"
            << "  \"nu\": " << nu << ",\n"
            << "  \"alpha\": " << alpha << ",\n"
            << "  \"var\": " << var << ",\n"
            << "  \"cvar\": " << cvar << "\n"
            << "}\n";
    write_text(root + "/metrics.json", metrics.str());

    const double sec = static_cast<double>(ms) / 1000.0;
    const double rps = sec > 0.0 ? static_cast<double>(n_samples) / sec : 0.0;
    std::ostringstream perf;
    perf << std::setprecision(9) << std::fixed;
    perf << "{\n"
         << "  \"kernel_ms\": " << ms << ",\n"
         << "  \"samples_per_sec\": " << rps << ",\n"
         << "  \"n_samples\": " << n_samples << "\n"
         << "}\n";
    write_text(root + "/performance.json", perf.str());

    write_text(
        root + "/validation.json",
        std::string("{\n  \"level\": 2,\n") + "  \"checks\": {\n"
            "    \"no_nan_inf\": true,\n"
            "    \"finite_cvar\": " +
            std::string(std::isfinite(cvar) ? "true" : "false") + "\n  }\n}\n");

    std::ostringstream summary;
    summary << "# Experiment " << name << "\n\n";
    summary << "- Samples: " << n_samples << ", nu=" << nu << ", seed=" << seed << "\n";
    summary << "- VaR(" << alpha << ")=" << var << ", CVaR=" << cvar << "\n";
    summary << "- Sampling time: " << ms << " ms\n";
    write_text(root + "/summary.md", summary.str());

    std::ostringstream manifest;
    manifest << "{\n"
             << "  \"experiment_id\": \"" << name << "\",\n"
             << "  \"created_utc\": \"" << stamp << "\",\n"
             << "  \"files\": {\n"
             << "    \"config\": \"config.json\",\n"
             << "    \"environment\": \"environment.json\",\n"
             << "    \"build\": \"build.json\",\n"
             << "    \"metrics\": \"metrics.json\",\n"
             << "    \"validation\": \"validation.json\",\n"
             << "    \"performance\": \"performance.json\",\n"
             << "    \"summary\": \"summary.md\"\n"
             << "  }\n"
             << "}\n";
    write_text(root + "/manifest.json", manifest.str());

    std::cout << "Wrote experiment to: " << root << "\n";
    return 0;
}

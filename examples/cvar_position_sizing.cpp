// Demo: CVaR-constrained position sizing from a JSON config.

#include "json_scan.hpp"

#include <fstream>
#include <iostream>
#include <sstream>
#include <string>

#include "algorithms/position_sizing.h"

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

}  // namespace

int main(int argc, char** argv) {
    const char* cfg_path = "configs/example_cvar_sizing.json";
    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        if (a == "--config" && i + 1 < argc) {
            cfg_path = argv[++i];
        }
    }

    const std::string cfg = read_file(cfg_path);
    if (cfg.empty()) {
        std::cerr << "Cannot read config: " << cfg_path << "\n";
        return 1;
    }

    int n_samples = 100000;
    float nu = 4.0f;
    float alpha = 0.95f;
    float max_cvar = 0.05f;
    unsigned long long seed = 42ULL;

    json_find_int(cfg, "n_samples", n_samples);
    json_find_uint64(cfg, "seed", seed);
    json_find_float(cfg, "max_cvar", max_cvar);
    // "nu" may appear under nested JSON; flat scan still finds first \"nu\"
    json_find_float(cfg, "nu", nu);
    json_find_float(cfg, "alpha", alpha);

    const float price = 100.0f;
    tailwarp::PositionSizingResult r =
        tailwarp::compute_position_size(max_cvar, price, n_samples, nu, alpha, seed);

    std::cout << std::fixed;
    std::cout << "optimal_size=" << r.optimal_size << "\n";
    std::cout << "expected_cvar=" << r.expected_cvar << "\n";
    std::cout << "expected_return=" << r.expected_return << "\n";
    std::cout << "constraint_satisfied=" << (r.constraint_satisfied ? "true" : "false") << "\n";
    return 0;
}

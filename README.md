# TailWarp

Geometric methods for tail-aware risk optimization using GPU acceleration.

## Overview

TailWarp implements Riemannian optimization on manifolds (SPD, Fisher-Rao) for robust risk measurement, position sizing, hedging, and portfolio allocation under heavy-tailed distributions.

**Implemented today**
- GPU sampling: Student-t, Gaussian (univariate)
- CUDA metrics: drawdown/pain, structural ruin, basic exposure (see `src/core/`)
- Host API: VaR / CVaR / summary stats; wrappers call GPU samplers
- Example CLIs: `experiment_run` (artifact folder), `cvar_position_sizing`

**Planned / partial (see [docs/project-plan-docs/07-RISK-SIMPLE-PLAN.md](docs/project-plan-docs/07-RISK-SIMPLE-PLAN.md))**
- α-stable and multivariate samplers; EVT / POT tail validation
- Full SPD manifold geometry (exp/log map, geodesic distance); Tyler M-estimator; Riemannian optimization demos

## Quick Start

```bash
# Configure and build (tests + examples)
cmake -B build -DBUILD_TESTS=ON
cmake --build build

# Tests
ctest --test-dir build --output-on-failure

# Record a minimal experiment folder (see docs/EXPERIMENTS.md)
./build/examples/experiment_run configs/experiment_student_t_cvar.json

# CVaR sizing demo
./build/examples/cvar_position_sizing --config configs/example_cvar_sizing.json
```

Optional: `make` builds CUDA objects only (see [Makefile](Makefile)); prefer CMake for full linking.

## Project Structure

```
TailWarp/
├── src/               # CUDA kernels, wrappers, algorithms
├── tests/             # Unit tests, validation, integration tests
├── benchmarks/        # Performance evaluation suite
├── configs/           # Experiment configurations
├── data/              # Input data and experiment outputs
├── scripts/           # Build and validation scripts
└── docs/              # Documentation and research notes
```

## Requirements

- CUDA 11.0+
- CMake 3.18+ or Make
- C++17 compiler
- GPU with compute capability 8.6+ (RTX 30-series or newer)
- Optional: GTest for tests, Python 3.8+ for scripts

## Research Focus

Based on "Statistical Consequences of Fat Tails" (Taleb) and Riemannian optimization literature:

1. **Position Sizing**: CVaR-constrained sizing via geodesic convex optimization
2. **Robust Covariance**: Tyler's M-estimator on SPD manifold with affine-invariant metric
3. **Hedging**: Correlation uncertainty via Riemannian trust regions
4. **Option Pricing**: Anchor-based tail pricing using EVT

See [docs/ideas-plan.md](docs/ideas-plan.md) and [docs/project-plan-docs/](docs/project-plan-docs/) for workflow.

## Documentation

- **Research Plan**: [docs/ideas-plan.md](docs/ideas-plan.md)
- **Workflow**: `docs/project-plan-docs/QUICK-REFERENCE.md`
- **Experiments**: `docs/EXPERIMENTS.md`
- **Validation**: `docs/VALIDATION.md`

## License

See LICENSE file.

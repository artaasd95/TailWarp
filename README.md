# TailWarp

Geometric methods for tail-aware risk optimization using GPU acceleration.

## Overview

TailWarp implements Riemannian optimization on manifolds (SPD, Fisher-Rao) for robust risk measurement, position sizing, hedging, and portfolio allocation under heavy-tailed distributions.

**Core Features:**
- Heavy-tailed scenario generation (Student-t, α-stable) on GPU
- SPD manifold operations for robust covariance estimation
- CVaR-constrained optimization with geodesic convexity
- Tyler's M-estimator and Riemannian barycenters
- Extreme Value Theory (EVT) for tail validation

## Quick Start

```bash
# Build
make

# Run tests
make test

# Run example experiment
./build/examples/cvar_position_sizing --config configs/example_cvar_sizing.json
```

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

See `docs/ideas-plan.md` for detailed research plan and `docs/project-plan-docs/` for workflow.

## Documentation

- **Research Plan**: `docs/ideas-plan.md`
- **Workflow**: `docs/project-plan-docs/QUICK-REFERENCE.md`
- **Experiments**: `docs/EXPERIMENTS.md`
- **Validation**: `docs/VALIDATION.md`

## License

See LICENSE file.

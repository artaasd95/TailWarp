# TailWarp

Geometric methods for tail-aware risk optimization using GPU acceleration.

## Overview

TailWarp implements **Black Swan Defense** — a GPU-accelerated framework for tail-aware risk measurement and survival under heavy-tailed distributions. Current focus (S2-01) is on validated primitives: solvency distance, drawdown pain, CVaR-constrained sizing, and Student-t sampling for realistic fat-tail scenarios.

**Why Black Swan Defense?**
Black swans (rare, unpredictable extreme events) live in "Extremistan" where:
- Traditional mean-variance models fail
- Tail risk dominates realized losses
- **We cannot eliminate black swan risk, only mitigate and antifragility-position**

See [RESULTS.md](RESULTS.md) for the full claim-vs-measured separation and S2-01 scope lock.

**Implemented & Validated Today** (Phase 1 — Survival Baseline)
- ✅ GPU sampling: Student-t, Gaussian (univariate)
- ✅ CUDA metrics: solvency distance, drawdown/pain, exposure/leverage (see `src/core/`)
- ✅ Host API: VaR / CVaR / summary stats; wrappers call GPU samplers
- ✅ Example CLIs: `experiment_run` (artifact folder), `cvar_position_sizing`
- ✅ Warning state framework (green/yellow/red/critical with deterministic thresholds)

**Planned & Partial** (Phase 2–3, explicitly excluded from S2-01 headline; see [docs/project-plan-docs/07-RISK-SIMPLE-PLAN.md](docs/project-plan-docs/07-RISK-SIMPLE-PLAN.md))
- ⚠️ SPD manifold covariance (stubs exist, host pipeline incomplete)
- ⚠️ Robust covariance via Tyler's M-estimator (manifold ops needed)
- ⚠️ α-stable and multivariate samplers; EVT / POT tail validation
- ⚠️ Riemannian optimization (geodesic distance, trust-region hedging)

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
├── app/               # Optional Streamlit dashboards (CPU)
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

## Black Swan dashboard (optional, CPU-only)

Install Python dependencies, then run from the repository root:

```bash
pip install -r app/requirements-black-swan-dashboard.txt
streamlit run app/streamlit_black_swan_dashboard.py
```

The default bundle is `benchmarks/results/sample_black_swan/`; replay rows live under `data/input/sample_replays/`. No GPU is required for this path.

### Black Swan replay benchmark (CPU-safe)

Regenerate the sample artifact bundle from the repository root:

```bash
pip install -r app/requirements-black-swan-dashboard.txt
python benchmarks/run_black_swan_benchmark.py --config benchmarks/configs/black_swan_replay.json
```

Outputs land in `benchmarks/results/sample_black_swan/` (`results.json`, `summary.md`, `tailwarp_vs_variance.csv`, plots, and `environment.json`). See [benchmarks/README.md](benchmarks/README.md) for config schema.

## Documentation

- **Results & Claims:** [RESULTS.md](RESULTS.md) — Separates target Black Swan Defense claims from measured results (S2-01)
- **Research Plan**: [docs/ideas-plan.md](docs/ideas-plan.md)
- **Workflow**: `docs/project-plan-docs/QUICK-REFERENCE.md`
- **Experiments**: `docs/EXPERIMENTS.md`
- **Validation**: `docs/VALIDATION.md`

## License

See LICENSE file.

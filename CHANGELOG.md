# Changelog

## v1.0.0 (2026-06-10)

### Core CUDA Kernels (`src/core/`)
- Student-t sampler (`distributions/student_t.cu`)
- Gaussian sampler (`distributions/gaussian.cu`)
- SPD manifold operations (`manifolds/spd_operations.cu`)
- Structural ruin metrics (`Structural-Ruin/`: ror, absorbing barrier, survival probability, solvency distance)
- Drawdown/pain metrics (`Drawdown-Pain/`: MDD, average drawdown, ulcer index, recovery metrics)
- Exposure/leverage metrics (`Exposure-Leverage/`: exposure metrics, concentration risk)
- CSV loader (`utils/csv_loader.cu`)
- GPU sorting helpers (`utils/sorting.cu`)

### C++ Host Wrappers (`src/wrappers/`)
- Risk metrics: VaR, CVaR, risk summary, warning state
- Distribution wrappers

### Python API (`python/tailwarp/`)
- `TailWarpClient` with native extension dispatch
- CPU fallback implementations (VaR, CVaR, drawdown, position sizing, warning state)
- Type-safe result dataclasses

### Algorithms (`src/algorithms/`)
- Position sizing with CVaR constraint
- Sample covariance with ridge regularization

### Benchmarks (`benchmarks/`)
- Black swan replay benchmark
- Posture/convexity metrics

### Testing
- Unit tests for Student-t, Gaussian, CVaR, warning state, position sizing
- Validation tests for kernel parity, benchmark risk metrics, posture metrics
- Integration tests (end-to-end, invariants, GPU vs CPU)

### Documentation
- 10-lens risk framework (`docs/risk-metrics/`)
- Research notes, project plans, CI plan, quick reference
- Architecture boundary guide, validation specification
- Experiment methodology and execution manifest

# Phase 1 — Gaussian baseline (note)

## Status

- CUDA Gaussian sampler: `src/core/distributions/gaussian.cu` (cuRAND normal).
- Host VaR/CVaR: `src/wrappers/risk_metrics.cpp` (sorted historical tail).
- Run an artifact folder: `examples/experiment_run` with `configs/gaussian_varcvar.json`.

## Next validation steps

- Record throughput on target GPU (`performance.json` from `experiment_run`).
- Add device-side VaR/CVaR when sample sizes require it; keep host reference for regression.

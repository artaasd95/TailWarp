# TailWarp technical debt register

Tracked deferrals that are intentional until CI capacity or Phase gates land.

## TD-TW-02 — GPU vs CPU parity for benchmark-path metrics (S5-03)

**Vault seed:** S5-03 · **Depends on:** S5-02 posture fields, S5-01 CUDA reproduction  
**Status:** Open (manual procedure until GPU CI)

### Scope

When new benchmark metrics are added (CVaR on GPU-sorted samples, posture fields after Lens-5 kernels),
CI must either:

1. Run parity or golden tests on a GPU runner with documented tolerances, or  
2. Document an acceptable manual check when GPU CI is unavailable.

### Current state (CPU CI only)

| Metric / check | CPU CI | GPU CI | Tolerance (target) |
|----------------|--------|--------|-------------------|
| Warning state thresholds (Python vs C++) | `tests/unit/test_warning_state.cpp`, `test_benchmark_risk_metrics.py` | N/A | Exact bands |
| Host historical CVaR monotonicity | `test_benchmark_risk_metrics.py` | N/A | Algebraic |
| GPU vs CPU CVaR @ 10M samples | **Deferred** (`TestGpuParity` skipped) | Manual | ±0.01% relative ([docs/VALIDATION.md](docs/VALIDATION.md)) |
| Posture heuristics (convexity, antifragility, complexity) | `test_posture_metrics.py` | Manual after CUDA run | Document per metric when kernels ship |
| SPD / robust covariance on replay path | Not asserted | Not asserted | Out of Phase 1 |

### Manual check procedure (no GPU CI)

1. Build CUDA target per [docs/project-plan-docs/CI-PLAN.md](docs/project-plan-docs/CI-PLAN.md).
2. Run Black Swan reproduction with `cuda_measured: true` and a distinct `output_dir`
   (for example `benchmarks/results/cuda_black_swan/`).
3. Compare `results.json` headline fields against the CPU sample bundle:
   - `lead_time_seconds` — expect same sign; magnitude may differ if GPU CVaR sort differs.
   - `risk.cvar_95` — record relative delta; acceptable if within ±0.01% on large windows.
   - `warning_state.state` — must match when inputs are identical; document mismatch with artifact path.
4. Record GPU metadata from `environment.json` (`gpu_model`, `driver_version`, `cuda_version`, `git_commit`).
5. Add a **CUDA-measured** row to [RESULTS.md](RESULTS.md) (template section) with K runs, timestamps, and limitations.

### Failure message convention

Parity tests must name the metric and artifact path, for example:

```
GPU/CPU mismatch: risk.cvar_95 in benchmarks/results/cuda_black_swan/results.json
  cpu=-0.006000 gpu=-0.006001 rel_delta=1.6e-4 tolerance=1e-4
```

### Test hook

`tests/validation/test_benchmark_risk_metrics.py::TestGpuParity` remains skipped with
`GPU_CVAR_PARITY_DEFERRED = True` until a GPU workflow exists. Remove the skip when
`.github/workflows/` gains a CUDA job and tolerances are pinned.

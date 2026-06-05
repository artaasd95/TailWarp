# S7 complete-run execution manifest (planned — do not execute in S6)

This document lists **every command and artifact** for the future **S7 complete run** on real GPU hardware. S6 authors the manifest only; **S7 execution is deferred** until S6-02 (GPU smoke) and S6-05 (GPU validation workflow) exit.

**Ordering note:** YAML issue seeds for S7 are intentionally **not** synced until S6 completes ([Decision-Log](project-plan-docs/) in vault: TW-2026-23).

## Hardware prerequisites

| Requirement | Notes |
|-------------|-------|
| NVIDIA GPU | Compute capability ≥ 8.6 (see root `README.md`) |
| CUDA toolkit | 11.0+; match `docker/Dockerfile.cuda` pin when using container |
| Driver | Record `nvidia-smi` output in `environment.json` |
| Build | `cmake -B build -DBUILD_TESTS=ON -DBUILD_BENCHMARKS=ON && cmake --build build` |

## Measurement labels

| Label | Meaning | CI |
|-------|---------|-----|
| `cpu_sample` | CPU replay / host quantile / no device timing | `.github/workflows/black_swan_smoke.yml` |
| `cuda_measured` | Built binaries + GPU kernels in timed region | Manual or `workflow_dispatch` (SP-BENCH-05) |

## Warm-up and K-run policy (S7 default)

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Warm-up runs | 3 | Exclude from statistics (see `docs/project-plan-docs/06-PERFORMANCE-PROTOCOL.md`) |
| K measured runs | 5 | Median reported; store all K in `results.json` when using `run_benchmarks.py` |
| Regression gate | ±20% vs `benchmarks/baselines/*.json` | `scripts/check_regression.py` (warn/fail configurable) |

---

## Matrix

| ID | Command / target | CUDA? | Artifact / RESULTS link | Status (S6) |
|----|------------------|-------|-------------------------|-------------|
| T01 | `ctest --test-dir build --output-on-failure` | Partial (GPU tests skip without device) | CI log | Ready (CPU) |
| T02 | `build/tailwarp_tests` (GTest) | Partial | — | Ready |
| T03 | `build/bench_student_t --json` | **Yes** | `benchmarks/results/<run_id>/results.json` → `benchmarks[]` | Wiring via `run_benchmarks.py` |
| T04 | `build/bench_gaussian --json` | **Yes** | same | Wiring via `run_benchmarks.py` |
| T05 | `build/examples/experiment_run configs/experiment_student_t_cvar.json` | **Yes** | `data/output/experiments/*/` | Manual S7 |
| T06 | `build/examples/cvar_position_sizing --config configs/example_cvar_sizing.json` | Mixed | stdout / config artifact | Manual S7 |
| T07 | `python benchmarks/run_black_swan_benchmark.py --config benchmarks/configs/black_swan_replay.json` | No (`cpu_sample`) | `benchmarks/results/sample_black_swan/` | **Done** (CPU) — [RESULTS.md](../RESULTS.md) Test 4 |
| T08 | `python benchmarks/run_black_swan_benchmark.py --config benchmarks/configs/black_swan_replay_cuda.json` | **Yes** (native build required) | `benchmarks/results/cuda_black_swan/` | **Deferred** — [RESULTS.md](../RESULTS.md) Test 5 template |
| T09 | `python benchmarks/run_benchmarks.py --profile cpu_smoke` | No | `benchmarks/results/<run_id>/results.json` | Wiring only (S6/SP-BENCH-01) |
| T10 | `python benchmarks/run_benchmarks.py --profile cuda_full` | **Yes** | same + refresh `RESULTS.md` throughput table | **Deferred** (S7) |
| T11 | `scripts/validate_experiment.py <experiment_dir>` | No | `validation.json` in bundle | Manual S7 |
| T12 | `scripts/check_regression.py --results benchmarks/results/<run_id>/results.json` | No | exit code / CI | Ready (baseline gate) |
| T13 | `pytest tests/validation/ -v` | No | — | Ready (CPU CI) |
| T14 | GPU parity subset | **Yes** | `tests/validation/test_kernel_parity.cpp` | Manual when device present |
| T15 | `scripts/validate_experiment.py` + statistical_tests | Partial | `tests/validation/statistical_tests.cpp` | Manual S7 |

---

## S7 single entrypoint (planned)

After SP-BENCH-01 lands:

```bash
# CPU-safe smoke (no GPU required)
python benchmarks/run_benchmarks.py --profile cpu_smoke --run-id s7_cpu_smoke_$(date -u +%Y%m%d)

# Full CUDA matrix (S7 — run only on GPU machine)
python benchmarks/run_benchmarks.py --profile cuda_full --run-id s7_cuda_$(date -u +%Y%m%d)
```

Then update [RESULTS.md](../RESULTS.md) rows from the emitted `results.json` paths and run:

```bash
python scripts/check_regression.py --results benchmarks/results/<run_id>/results.json
```

---

## Explicitly out of S7 scope (headline)

- SPD `spd_log` / `spd_distance` — `[PLANNED]`
- Tyler robust covariance — use `sample_covariance_with_ridge` only (`partial`)
- Python NumPy risk stack as source of headline numbers

---

## Related docs

- [ARCHITECTURE_BOUNDARY.md](ARCHITECTURE_BOUNDARY.md)
- [VALIDATION.md](VALIDATION.md) — correctness registry and tolerances
- [benchmarks/README.md](../benchmarks/README.md)
- [Tech-Debt.md](../Tech-Debt.md) — TD-TW-02 GPU parity

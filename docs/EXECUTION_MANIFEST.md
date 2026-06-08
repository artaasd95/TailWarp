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
| `cpu_sample` | CPU replay / host quantile / no device timing | `.github/workflows/ci.yml` |
| `cuda_measured` | Built binaries + GPU kernels in timed region | `.github/workflows/gpu-smoke.yml` (`workflow_dispatch`) |

## Warm-up and K-run policy (S7 default)

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Warm-up runs | 3 | Exclude from statistics (see `docs/project-plan-docs/06-PERFORMANCE-PROTOCOL.md`) |
| K measured runs | 5 | Median reported; store all K in `results.json` when using `run_benchmarks.py` |
| Regression gate | ±20% vs `benchmarks/baselines/*.json` | `scripts/check_regression.py` (warn/fail configurable) |

---

## Matrix

| ID | Command / target | CUDA? | K / warmup | Artifact dir | RESULTS row | Status (S6) |
|----|------------------|-------|------------|--------------|-------------|-------------|
| T01 | `ctest --test-dir build --output-on-failure` | Partial (GPU tests skip without device) | — / — | CI log | — | Ready (CPU) |
| T02 | `build/tailwarp_tests` (GTest) | Partial | — / — | — | — | Ready |
| T03 | `build/bench_student_t --json --k 5 --warmup 3` | **Yes** | 5 / 3 | `benchmarks/results/<run_id>/` | [RESULTS.md](../RESULTS.md) Throughput / Student-t | Wiring via `run_benchmarks.py` |
| T04 | `build/bench_gaussian --json --k 5 --warmup 3` | **Yes** | 5 / 3 | same | [RESULTS.md](../RESULTS.md) Throughput / Gaussian | Wiring via `run_benchmarks.py` |
| T05 | `build/examples/experiment_run configs/experiment_student_t_cvar.json` | **Yes** | 1 / 0 | `data/output/experiments/*/` | Test 2 | Manual S7 |
| T06 | `build/examples/cvar_position_sizing --config configs/example_cvar_sizing.json` | Mixed | 1 / 0 | stdout / config artifact | — | Manual S7 |
| T07 | `python benchmarks/run_black_swan_benchmark.py --config benchmarks/configs/black_swan_replay.json` | No (`cpu_sample`) | 1 / 0 | `benchmarks/results/sample_black_swan/` | Test 4 | **Done** (CPU) |
| T08 | `python benchmarks/run_black_swan_benchmark.py --config benchmarks/configs/black_swan_replay_cuda.json` | **Yes** | 5 / 3 | `benchmarks/results/cuda_black_swan/` | Test 5 | **Deferred** |
| T09 | `python benchmarks/run_benchmarks.py --profile cpu_smoke --k 5 --warmup 3` | No | 5 / 3 | `benchmarks/results/<run_id>/results.json` | — | Wiring (SP-BENCH-01) |
| T10 | `python benchmarks/run_benchmarks.py --profile cuda_full --k 5 --warmup 3` | **Yes** | 5 / 3 | same | Throughput table | **Deferred** (S7) |
| T11 | `scripts/validate_experiment.py <experiment_dir>` | No | — / — | `validation.json` in bundle | — | Manual S7 |
| T12 | `scripts/check_regression.py --results benchmarks/results/<run_id>/results.json` | No | — / — | exit code / CI | — | Ready (baseline gate) |
| T13 | `pytest tests/validation/ tests/python/ -v` | No | — / — | — | — | Ready (CPU CI) |
| T14 | `ctest -R KernelParity` (`tests/validation/test_kernel_parity.cpp`) | **Yes** | — / — | ctest log | — | Manual when device present |
| T15 | `ctest` + `tests/validation/statistical_tests.cpp` | Partial | — / — | — | — | Manual S7 |
| T16 | `ctest -R gpu_smoke` (`tests/validation/test_gpu_smoke.cpp`) | **Yes** | — / — | ctest log | — | Ready (S6-02) |

**Parity note (S6-04):** GPU parity is exercised via `ctest -R KernelParity`, not a separate CMake target.

---

## S7 single entrypoint (planned)

```bash
# CPU-safe smoke (no GPU required)
python benchmarks/run_benchmarks.py --profile cpu_smoke --run-id s7_cpu_smoke_$(date -u +%Y%m%d) --k 5 --warmup 3

# Full CUDA matrix (S7 — run only on GPU machine)
python benchmarks/run_benchmarks.py --profile cuda_full --run-id s7_cuda_$(date -u +%Y%m%d) --k 5 --warmup 3
```

Then update [RESULTS.md](../RESULTS.md) rows from the emitted `results.json` paths and run:

```bash
python scripts/check_regression.py --results benchmarks/results/<run_id>/results.json
```

---

## S7 sign-off checklist (execution sprint)

Reviewer ticks rows post-GPU-run without editing commands.

- [ ] **T01** — prereq: cmake build — command: `ctest --test-dir build --output-on-failure` — artifact: CI log — RESULTS row: —
- [ ] **T02** — prereq: GTest — command: `build/tailwarp_tests` — artifact: — — RESULTS row: —
- [ ] **T03** — prereq: GPU build — command: `build/bench_student_t --json --k 5 --warmup 3` — artifact: `benchmarks/results/<run_id>/results.json` — RESULTS row: Throughput / Student-t
- [ ] **T04** — prereq: GPU build — command: `build/bench_gaussian --json --k 5 --warmup 3` — artifact: same — RESULTS row: Throughput / Gaussian
- [ ] **T05** — prereq: GPU build — command: `build/examples/experiment_run configs/experiment_student_t_cvar.json` — artifact: `data/output/experiments/*/` — RESULTS row: Test 2
- [ ] **T06** — prereq: GPU build — command: `build/examples/cvar_position_sizing --config configs/example_cvar_sizing.json` — artifact: stdout — RESULTS row: —
- [ ] **T07** — prereq: Python deps — command: `python benchmarks/run_black_swan_benchmark.py --config benchmarks/configs/black_swan_replay.json` — artifact: `benchmarks/results/sample_black_swan/` — RESULTS row: Test 4
- [ ] **T08** — prereq: GPU + native build — command: `python benchmarks/run_black_swan_benchmark.py --config benchmarks/configs/black_swan_replay_cuda.json` — artifact: `benchmarks/results/cuda_black_swan/` — RESULTS row: Test 5
- [ ] **T09** — prereq: CPU — command: `python benchmarks/run_benchmarks.py --profile cpu_smoke` — artifact: `benchmarks/results/<run_id>/` — RESULTS row: —
- [ ] **T10** — prereq: GPU — command: `python benchmarks/run_benchmarks.py --profile cuda_full` — artifact: same — RESULTS row: Throughput table
- [ ] **T11** — prereq: experiment dir — command: `scripts/validate_experiment.py <dir>` — artifact: `validation.json` — RESULTS row: —
- [ ] **T12** — prereq: results.json — command: `scripts/check_regression.py --results ...` — artifact: exit code — RESULTS row: —
- [ ] **T13** — prereq: pytest — command: `pytest tests/validation/ tests/python/ -v` — artifact: — — RESULTS row: —
- [ ] **T14** — prereq: GPU — command: `ctest -R KernelParity` — artifact: ctest log — RESULTS row: —
- [ ] **T15** — prereq: build — command: statistical_tests via ctest — artifact: — — RESULTS row: —
- [ ] **T16** — prereq: GPU — command: `ctest -R gpu_smoke` — artifact: ctest log — RESULTS row: —

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

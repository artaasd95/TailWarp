# CUDA-first architecture boundary

TailWarp is a **CUDA-native risk computation engine**. Numerically meaningful metrics are implemented in **CUDA kernels** (`src/core/**/*.cu`) and **C++ host wrappers** (`src/wrappers/`, `src/algorithms/`). Python is **orchestration, I/O, and visualization only** — not a second implementation of risk math for headline paths.

## Ownership map

| Layer | Path | Role |
|-------|------|------|
| Kernels | `src/core/` | Device math: distributions, drawdown, ruin, exposure, manifolds (where implemented) |
| Wrappers | `src/wrappers/` | Stable C++ API: launch kernels, host fallbacks where documented |
| Algorithms | `src/algorithms/` | Compose kernels/wrappers (e.g. position sizing, sample covariance) |
| Reference | `src/reference/` | CPU references for tests and parity (not headline replay path) |
| Orchestration | `benchmarks/*.py`, `app/`, `scripts/` | Config load, subprocess to built binaries, artifact JSON/CSV, dashboards |
| Examples | `examples/` | CLIs that call the C++ libraries |

## Non-goals (enforced)

1. **No Python risk framework** for headline metrics — do not reimplement drawdown, CVaR, solvency distance, or `TailWarpWarningState` logic in NumPy/Pandas/sklearn for claims in `README.md` or `RESULTS.md`.
2. **Black Swan replay** (`benchmarks/run_black_swan_benchmark.py`) uses a **documented CPU replay path** for CI (`measurement_label: cpu_sample`). That path mirrors C++ threshold bands but is explicitly **not** CUDA-measured until `cuda_measured: true` and native build prerequisites are met (see [EXECUTION_MANIFEST.md](EXECUTION_MANIFEST.md)).
3. **New benchmark fields** in `results.json` must trace to a **kernel symbol** or **wrapper function** in `src/`. If only a Python heuristic exists, mark `status: cpu_replay_heuristic` and exclude from headline tables.
4. **Phase 2–3 features** (SPD geodesics, Tyler M-estimator, multivariate tails) remain `[PLANNED]` until implemented — see [VALIDATION.md](VALIDATION.md) correctness registry.

## Build prerequisite for CUDA-measured runs

```bash
cmake -B build -DBUILD_TESTS=ON -DBUILD_BENCHMARKS=ON
cmake --build build
ctest --test-dir build --output-on-failure
```

Canonical performance entrypoints: `build/bench_student_t`, `build/bench_gaussian` (see `CMakeLists.txt`). Full matrix: [EXECUTION_MANIFEST.md](EXECUTION_MANIFEST.md).

## Where Python is allowed

| Use case | OK? | Notes |
|----------|-----|-------|
| Run replay, write artifacts | Yes | Must label `measurement_label` |
| Streamlit dashboard | Yes | Reads saved JSON only |
| `benchmarks/run_benchmarks.py` | Yes | Subprocess to CMake targets + ctest; does not compute CVaR for headline rows |
| Unit tests for artifact schema | Yes | `tests/validation/test_*.py` |
| NumPy CVaR as product API | **No** (v1.0) | Deferred to optional `tailwarp` pip package (Product-MVP), not headline path |

## Review checklist (PRs)

- [ ] Metric change has a C++/CUDA owner under `src/`
- [ ] `docs/VALIDATION.md` correctness row updated (`verified` / `partial` / `placeholder`)
- [ ] No new README/RESULTS claim without status tag
- [ ] Python-only math labeled and excluded from headline if used for smoke only

See also [CONTRIBUTING.md](../CONTRIBUTING.md), [VALIDATION.md](VALIDATION.md), [project-plan-docs/07-RISK-SIMPLE-PLAN.md](project-plan-docs/07-RISK-SIMPLE-PLAN.md).

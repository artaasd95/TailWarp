# Benchmarks

Performance evaluation and Black Swan replay artifacts. **CUDA-native microbenches** live in CMake targets; **Python** loads configs and writes bundles only ([docs/ARCHITECTURE_BOUNDARY.md](../docs/ARCHITECTURE_BOUNDARY.md)).

## Structure

| Path | Purpose |
|------|---------|
| `configs/` | Replay and suite JSON |
| `baselines/` | Golden JSON for `scripts/check_regression.py` |
| `results/` | Generated run bundles (`<run_id>/results.json`) |
| `run_benchmarks.py` | Canonical runner (SP-BENCH-01) — see [EXECUTION_MANIFEST](../docs/EXECUTION_MANIFEST.md) |
| `run_black_swan_benchmark.py` | CPU-safe Black Swan replay (S3) |
| `bench_student_t`, `bench_gaussian` | C++ sources; built as `build/bench_*` |

## Build prerequisites (CUDA path)

```bash
cmake -B build -DBUILD_TESTS=ON -DBUILD_BENCHMARKS=ON
cmake --build build
```

Targets:

- `build/bench_student_t` — Student-t sampling throughput (`--json` for machine-readable line)
- `build/bench_gaussian` — Gaussian sampling throughput
- `build/examples/experiment_run` — experiment artifact folder

## Canonical runner

```bash
# CPU smoke: ctest + optional microbench + Black Swan replay
python benchmarks/run_benchmarks.py --profile cpu_smoke --run-id my_smoke

# CUDA full matrix (S7 — requires GPU build)
python benchmarks/run_benchmarks.py --profile cuda_full --run-id my_cuda --k 5 --warmup 3
```

Output: `benchmarks/results/<run_id>/results.json` (schema in [results/README.md](results/README.md)).

Regression check:

```bash
python scripts/check_regression.py --results benchmarks/results/<run_id>/results.json
```

## Black Swan replay benchmark (CPU-safe)

Config schema (`configs/black_swan_replay.json`):

| Field | Purpose |
|-------|---------|
| `scenario_id` | Label for results bundle |
| `replay_csv` | Replay stream (`timestamp`, `return`, `equity`, `exposure`, optional `variance_baseline`) |
| `event_windows_json` | Sidecar with labeled ISO-8601 windows |
| `output_dir` | Bundle directory under `results/` |
| `k_runs` / `aggregation_policy` | Repeat runs and headline aggregation |
| `tailwarp` | Alert threshold, window size, CVaR α, warning-state toggle |
| `baseline` | Variance EWMA type, λ, alert threshold |
| `student_t_scenario_refresh` | Optional Monte Carlo refresh (disabled in sample) |

```bash
pip install -r app/requirements-black-swan-dashboard.txt
python benchmarks/run_black_swan_benchmark.py --config benchmarks/configs/black_swan_replay.json
```

Writes `results.json` (schema v2: `posture`, `limitations`, `measurement_label`), `summary.md`, `tailwarp_vs_variance.csv`, `environment.json`, and plots.

**GPU measured run:** build native targets first, then use `configs/black_swan_replay_cuda.json` with `cuda_measured: true`. Record rows in [RESULTS.md](../RESULTS.md). Parity: [Tech-Debt.md](../Tech-Debt.md) (TD-TW-02).

### Dashboard

```bash
streamlit run app/streamlit_black_swan_dashboard.py
```

## Performance targets (reference — RTX 3060 class)

| Kernel | Target throughput | Notes |
|--------|-------------------|-------|
| Student-t sampler | > 200M samples/sec | `bench_student_t` |
| Gaussian sampler | Similar order | `bench_gaussian` |
| Host CVaR (10M) | < 20 ms | Not GPU-sorted yet |

Regression: ±20% vs `benchmarks/baselines/` default (`scripts/check_regression.py --threshold 0.20`).

## CI

- **CPU:** `.github/workflows/black_swan_smoke.yml` — replay + pytest validation
- **GPU benchmarks:** manual or `workflow_dispatch` per [docs/project-plan-docs/CI-PLAN.md](../docs/project-plan-docs/CI-PLAN.md) and [docs/EXECUTION_MANIFEST.md](../docs/EXECUTION_MANIFEST.md)

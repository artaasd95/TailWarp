# Benchmark results

Generated bundles live under `benchmarks/results/<run_id>/`.

## `results.json` schema (v1)

Produced by `benchmarks/run_benchmarks.py` (SP-BENCH-01). Full field set for hardware-attributed rows expands in SP-BENCH-02.

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | int | Currently `1` |
| `run_id` | string | Directory name |
| `profile` | string | `cpu_smoke` \| `cuda_full` |
| `commit_sha` | string | `git rev-parse HEAD` |
| `timestamp` | string | UTC ISO-8601 |
| `warmup_runs` | int | Excluded from microbench stats |
| `k_runs` | int | Measured repetitions |
| `environment` | object | `platform`, `python`, optional `gpu_model`, `driver_version`, `cuda_version`, `measurement_label` |
| `benchmarks` | array | Per-target rows (`name`, `status`, timing fields) |

### Per-benchmark row (microbench)

| Field | Description |
|-------|-------------|
| `name` | e.g. `student_t_sample`, `gaussian_sample` |
| `status` | `ok` \| `skipped` \| `failed` \| `error` |
| `n_samples` | Workload size |
| `mean_ms` | Mean wall time (ms) |
| `samples_per_sec` | Throughput |
| `k_runs`, `warmup_runs` | Methodology |

Black Swan bundles use schema v2 in `run_black_swan_benchmark.py` (`posture`, `warning_state`, etc.) — see [docs/VALIDATION.md](../../docs/VALIDATION.md).

## Regression

```bash
python scripts/check_regression.py --results benchmarks/results/<run_id>/results.json
```

Baselines: `benchmarks/baselines/*.json`.

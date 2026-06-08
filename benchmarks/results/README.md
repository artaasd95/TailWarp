# Benchmark results

Generated bundles live under `benchmarks/results/<run_id>/`.

## `results.json` schema (v2)

Produced by `benchmarks/run_benchmarks.py` (SP-BENCH-02).

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | int | Currently `2` |
| `run_id` | string | Directory name |
| `profile` | string | `cpu_smoke` \| `cuda_full` |
| `commit_sha` | string | `git rev-parse HEAD` |
| `timestamp` | string | UTC ISO-8601 |
| `hardware` | object | `platform`, `python`, `processor`, optional `gpu_model` |
| `cuda_version` | string \| null | From `nvcc --version` when available |
| `driver_version` | string \| null | From `nvidia-smi` when available |
| `warmup_runs` | int | Excluded from microbench stats |
| `k_runs` | int | Measured repetitions |
| `environment` | object | Alias of `hardware` + `measurement_label` |
| `benchmarks` | array | Per-target rows |

### Per-benchmark row (microbench)

| Field | Description |
|-------|-------------|
| `name` | e.g. `student_t_sample`, `gaussian_sample` |
| `status` | `ok` \| `skipped` \| `failed` \| `error` \| `dry_run` |
| `n_samples` | Workload size |
| `mean_ms` | Mean wall time (ms) over K runs |
| `median_ms` | Median wall time (ms) |
| `std_ms` | Sample std dev (ms) |
| `p95_ms` | 95th percentile (ms) |
| `samples_per_sec` | Throughput (median-based) |
| `k_runs`, `warmup_runs` | Methodology |

Black Swan bundles use schema v2 in `run_black_swan_benchmark.py` (`posture`, `warning_state`, etc.) — see [docs/VALIDATION.md](../../docs/VALIDATION.md).

## Dry-run

```bash
python benchmarks/run_benchmarks.py --dry-run --run-id schema_probe
```

Populates all v2 fields without executing native binaries.

## Regression

```bash
python scripts/check_regression.py --results benchmarks/results/<run_id>/results.json
python scripts/check_regression.py --warn-only --results benchmarks/results/<run_id>/results.json
```

Baselines: `benchmarks/baselines/*.json`.

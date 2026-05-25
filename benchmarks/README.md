# Benchmarks

Performance evaluation suite for CUDA kernels and Black Swan replay defense benchmarks.

## Structure

- `configs/` — Benchmark configurations (kernel suite, Black Swan replay)
- `baselines/` — Reference performance numbers
- `results/` — Benchmark outputs (timestamped bundles)
- `run_black_swan_benchmark.py` — CPU-safe Black Swan replay runner (S3-01)
- `risk_metrics.py` — Host-side warning state and CVaR helpers for the replay path

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

Run from repository root:

```bash
pip install -r app/requirements-black-swan-dashboard.txt
python benchmarks/run_black_swan_benchmark.py --config benchmarks/configs/black_swan_replay.json
```

Writes `results.json` (schema v2: `posture`, `limitations`, `measurement_label`), `summary.md`, `tailwarp_vs_variance.csv`, `environment.json`, and plots under the configured `output_dir`.

Lead time convention: `baseline_first_alert_ts − tailwarp_first_alert_ts` (positive ⇒ TailWarp earlier).

### Dashboard

```bash
streamlit run app/streamlit_black_swan_dashboard.py
```

Discovers all runs under `results/`; see [dashboard/README.md](../dashboard/README.md).

### CUDA reproduction (next sprint)

Set `cuda_measured: true` and a distinct `output_dir` in config (template: `configs/black_swan_replay_cuda.json`). Record a **CUDA-measured** row in [RESULTS.md](../RESULTS.md). Manual parity: [Tech-Debt.md](../Tech-Debt.md) (TD-TW-02).

## Kernel performance suite

```bash
# Run full kernel benchmark suite (GPU; script planned)
./scripts/run_benchmarks.sh

# Run specific kernel benchmark
./build/benchmark_student_t
```

## Performance Targets (RTX 3060)

| Kernel | Target Throughput | Memory Budget |
|--------|------------------|---------------|
| Student-t sampler | > 200M samples/sec | < 1 GB |
| CVaR (10M samples) | < 10 ms | - |
| SPD exp/log | < 5 ms (batch of 1000) | - |

Regression threshold: ±5% acceptable, >10% requires investigation.

## CI

CPU-safe Black Swan smoke: `.github/workflows/black_swan_smoke.yml` (no GPU). CUDA kernel benchmarks remain manual per [docs/project-plan-docs/CI-PLAN.md](../docs/project-plan-docs/CI-PLAN.md).

# Experiments & Reproducibility (TailWarp)

This repo is research-first. The goal of this document is to define how **every run** becomes a reproducible experiment with traceable provenance, without requiring a GUI or “productization”.

## 1) Goals

- **Reproducible runs**: A run can be re-executed later with the same inputs, configuration, and code revision.
- **Comparable results**: Different kernels/models can be compared under a consistent protocol.
- **Research output ready**: Experiments produce artifacts that can be used in papers/blogs/learning content (tables, plots, metrics, provenance).

## 2) Experiment = (Config + Code + Hardware + Results)

Every experiment run should capture:

- **Config**: model parameters, risk metrics requested, scenario count, precision mode, RNG settings, thresholds, etc.
- **Code identity**: git commit hash, dirty state, build flags, compiler versions.
- **Hardware identity**: GPU name, compute capability, driver/runtime versions.
- **Results**: raw outputs (optional), derived metrics (required), summary tables (required).

## 3) Minimal experiment folder layout

Proposed layout for `data/output/experiments`:

```text
data/output/experiments/
  2026-01-04T12-34-56Z__student_t_varcvar__N100M__seed1234/
    manifest.json
    config.json
    environment.json
    build.json
    metrics.json
    validation.json
    performance.json
    summary.md
    logs.txt
    artifacts/
      histogram.csv
      quantiles.csv
      pot_fit.csv
```

Notes:
- `manifest.json` is the index and points to the other files.
- Raw scenario outputs are optional (usually too large). Prefer histogram/quantile artifacts.

## 4) Configuration format

Use `config.json` initially to avoid extra dependencies. Later YAML can be supported.

Suggested top-level keys:
- `experiment`: name, description, tags
- `data`: source (`csv`, `mock`), symbol(s), date range, preprocessing
- `model`: distribution/process, parameters
- `portfolio`: instruments, weights, pricing mode (spot/returns/options)
- `simulation`: scenario_count, batch_size, precision, device_id
- `rng`: algorithm, seed, stream policy
- `metrics`: list of metrics (VaR, CVaR, drawdown, POT/EVT), confidence levels, thresholds
- `validation`: which validators to run and tolerances
- `performance`: which benchmarks to run (kernel timing, end-to-end timing)

## 5) Provenance capture: what to record

At run start, record:
- git commit hash and whether working tree is dirty
- compiler versions (NVCC, host compiler)
- build type and flags (Debug/Release, `-O3`, `--use_fast_math`, arch `sm_86`)
- GPU and driver versions (CUDA runtime, NVIDIA driver)
- OS, CPU model (for CPU validators)

This becomes `environment.json` and `build.json`.

## 6) Reproducibility policy (research-appropriate)

GPU Monte Carlo is often not bitwise reproducible across:
- different GPUs / driver versions
- different thread block scheduling
- different reduction orders

So define two levels:

- **Level A: Statistical reproducibility (default)**  
  Re-running yields metrics within an expected tolerance / confidence interval.

- **Level B: Run-to-run reproducibility on same machine**  
  Fixed seed + fixed grid/block policy + fixed reductions where feasible.

The repo should explicitly declare which level each module supports.

## 7) How it’s used (workflow)

1. Create a `config.json` describing the run.
2. Run a CLI (future) like:
   - `tailwarp run --config configs/student_t_varcvar.json --out data/output/experiments`
3. The run writes the experiment folder with metrics + provenance.
4. Optional: `tailwarp report` generates/updates `summary.md` from `metrics.json`.

Until a CLI exists, scripts can implement the same behavior as a convention.



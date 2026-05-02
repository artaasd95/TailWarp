# Experiment artifacts

Every research run should produce a **self-contained experiment folder** under `data/output/experiments/` so results are reproducible and reviewable.

## Directory layout

Use a timestamped folder name, for example:

`data/output/experiments/2026-05-02T14-30-00Z__student_t_cvar__N1M__seed42/`

### Required files

| File | Purpose |
|------|---------|
| `manifest.json` | Index of all artifact paths and versions |
| `config.json` | Input configuration (copied or merged from run args) |
| `environment.json` | Hostname, OS, GPU name, driver, CUDA runtime, **git commit** |
| `build.json` | Compiler, CMake flags, CUDA arch |
| `metrics.json` | Scalar outputs (e.g. VaR, CVaR, sample count) |
| `validation.json` | Pass/fail checks and validation level |
| `performance.json` | Timing, throughput, VRAM (optional for exploratory runs) |
| `summary.md` | Short human-readable summary |
| `artifacts/` | Extra outputs: CSVs, plots, histograms |

### `manifest.json` (minimal schema)

- `experiment_id` (string): folder name or UUID  
- `created_utc` (string): ISO-8601 timestamp  
- `files` (object): map logical name → relative path  

### `metrics.json` (minimal schema)

- `n_samples` (integer)  
- `distribution` (string, optional): e.g. `"student_t"`  
- `nu` (number, optional): degrees of freedom  
- `cvar` (number, optional): conditional VaR at configured alpha  
- `var` (number, optional): VaR at configured alpha  
- `alpha` (number, optional): confidence level for tail metrics  

Extend with drawdown, ruin, or exposure metrics as kernels are used.

## Configs

JSON configs live in [`configs/`](../configs/). The [`examples/experiment_run`](../examples/experiment_run.cpp) tool reads a config path and writes the folder above.

## Validation

After a run, check the folder with:

```bash
python scripts/validate_experiment.py data/output/experiments/<your_run_folder>
```

See [VALIDATION.md](VALIDATION.md) for validation levels and gates.

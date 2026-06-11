# How to Add a Module (Step-by-Step)

This guide walks you through adding a **new module** (distribution kernel, risk metric, data source, etc.) to TailWarp while keeping the repo stable and research-grade.

---

## Step 1: Define the Module's Purpose

Answer these questions before writing code:

- **What does this module do?** (e.g., "samples from Student-t distribution", "computes max drawdown")
- **What inputs does it need?** (parameters, data arrays, config)
- **What outputs does it produce?** (samples, metrics, diagnostic data)
- **What validation checks are appropriate?** (see `../VALIDATION.md`)
- **What's the expected performance?** (memory-bound? compute-bound? target scenarios/sec?)

Write these answers in a short design note (can be a comment in the code or a markdown snippet).

---

## Step 2: Implement the Core Logic

### For a CUDA kernel:
- Place it in `src/core/` with a descriptive name (e.g., `student_t_sampler.cu`)
- Add a host wrapper function in `src/wrappers/`
- Use consistent naming: `kernel_name<<<grid, block>>>(...)`

### For a CPU reference:
- Place it in `src/reference/` or `scripts/` (Python is fine for references)
- Keep it simple and high-precision (prefer `double` over `float`)

### For a risk metric:
- Add it to `src/wrappers/risk_metrics.cpp` or similar
- Ensure it can be called with a standard interface (input array → output metric)

---

## Step 3: Add Validation Tests

Follow the validation levels from `../VALIDATION.md`:

1. **Level 0 (Sanity)**: Check for NaN/Inf, range violations
2. **Level 1 (Unit)**: Test on small known inputs with tight tolerances
3. **Level 2 (Properties)**: Test invariants (monotonicity, symmetry, etc.)
4. **Level 3 (Statistical)**: Compare distributions/moments to reference
5. **Level 4 (End-to-end)**: Run a full experiment and validate metrics

**Minimum requirement**: Levels 0–2 must pass before the module is considered "working".

---

## Step 4: Benchmark Performance

Run the performance protocol (see `06-PERFORMANCE-PROTOCOL.md`):

- Measure kernel execution time
- Measure memory usage (VRAM)
- Compute scenarios/sec or throughput metric
- Record baseline in an experiment artifact

**Goal**: Establish a baseline so future changes can be checked for regressions.

---

## Step 5: Create an Experiment Config

Write a `config.json` that exercises the new module:

```json
{
  "experiment": {
    "name": "student_t_test",
    "description": "Validate Student-t sampler with nu=4"
  },
  "model": {
    "distribution": "student_t",
    "parameters": {"nu": 4, "mu": 0, "sigma": 1}
  },
  "simulation": {
    "scenario_count": 10000000,
    "precision": "float",
    "device_id": 0
  },
  "rng": {
    "algorithm": "philox",
    "seed": 42
  },
  "metrics": ["VaR_95", "VaR_99", "CVaR_95", "CVaR_99"],
  "validation": {
    "enabled": true,
    "reference": "cpu_double",
    "tolerance": 0.01
  }
}
```

---

## Step 6: Run and Record

1. **Run the experiment** and produce an experiment folder (see `../EXPERIMENTS.md`)
2. **Check validation reports**: all checks should pass
3. **Check performance reports**: numbers should be reasonable for RTX 3060
4. **Save artifacts**: commit the config and a summary of results

---

## Step 7: Document the Module

Add a short section to the relevant doc or code comment:

- **What it does**
- **Key parameters**
- **Validation approach**
- **Performance characteristics**
- **References** (papers, formulas)

---

## Step 8: Integration Checklist

Before marking the module "done", use the checklist from `02-CHECKLISTS.md`:

- [ ] Code compiles and runs
- [ ] Validation tests pass
- [ ] Performance baseline recorded
- [ ] Experiment artifacts produced
- [ ] Documentation updated

---

## Common Pitfalls

- **Skipping validation**: "It looks right" is not enough for research-grade work
- **No baseline**: Without a performance baseline, you can't detect regressions
- **Hardcoded parameters**: Make everything configurable via `config.json`
- **No reference**: Always have a CPU or analytic reference to compare against
- **Ignoring edge cases**: Test with zero variance, extreme parameters, empty data

---

## Example: Adding Student-t Distribution

1. **Purpose**: Sample from Student-t with configurable degrees of freedom
2. **Implementation**: Inverse CDF method using cuRAND normals + chi-squared
3. **Validation**:
   - Sanity: no NaN/Inf
   - Unit: small sample matches known quantiles
   - Statistical: empirical quantiles vs analytic CDF within tolerance
   - Tail: log-log survival plot slope matches expected tail index
4. **Performance**: Target 100M+ scenarios/sec on RTX 3060
5. **Config**: `student_t_test.json` with nu=4, seed=42, N=10M
6. **Artifacts**: metrics.json shows VaR/CVaR, validation.json shows all checks passed

---

## When to Skip Steps

You can defer some steps **temporarily** during rapid prototyping, but:

- **Never skip Level 0 validation** (sanity checks)
- **Never skip performance measurement** (even a rough baseline)
- **Always produce experiment artifacts** (config + metrics)

Mark deferred work clearly in TODOs and come back to it before calling the module "done".


# Quick Reference Card

One-page summary of the TailWarp workflow. Print this or keep it open while working.

---

## The Core Loop

```
Formulate → Implement → Validate → Benchmark → Record
```

**Never skip Validate, Benchmark, or Record.**

---

## File Structure (What Goes Where)

```
TailWarp/
├── src/
│   ├── core/              # CUDA kernels (.cu)
│   ├── wrappers/          # Host C++ wrappers
│   ├── algorithms/        # Risk metrics, optimization
│   └── reference/         # CPU reference implementations
├── data/
│   ├── input/             # Sample CSV files
│   └── output/
│       └── experiments/   # All experiment runs go here
├── configs/               # Experiment configs (.json)
│   └── research/          # Research project configs
├── scripts/               # Helper scripts, validation
└── docs/
    ├── EXPERIMENTS.md     # Experiment structure spec
    ├── VALIDATION.md      # Validation strategy spec
    ├── research_notes/    # Research findings
    └── project-plan-docs/ # This folder
```

---

## Experiment Folder (What Every Run Produces)

```
data/output/experiments/2026-01-04T12-34-56Z__name__N10M__seed42/
├── manifest.json          # Index of all files
├── config.json            # Input configuration
├── environment.json       # Hardware, driver, git hash
├── build.json             # Compiler, flags
├── metrics.json           # Risk metrics (VaR, CVaR, etc.)
├── validation.json        # Validation results (pass/fail)
├── performance.json       # Timing, throughput, VRAM
├── summary.md             # Human-readable summary
└── artifacts/             # Plots, tables, histograms
    ├── quantiles.csv
    ├── histogram.csv
    └── ...
```

---

## Validation Levels (Do You Need All of Them?)

| Level | What | When Required |
|-------|------|---------------|
| **0** | Sanity (no NaN/Inf) | Always |
| **1** | Unit tests (small inputs) | Always |
| **2** | Invariants (monotonicity, etc.) | Always |
| **3** | Statistical (quantiles, moments) | For distributions/metrics |
| **4** | End-to-end (full experiment) | Before sharing results |

**Minimum to call code "working": Levels 0–2**

---

## Performance Targets (RTX 3060)

| Kernel | Target | Budget |
|--------|--------|--------|
| Gaussian sampler | > 500M scenarios/sec | VRAM < 1 GB |
| Student-t sampler | > 200M scenarios/sec | VRAM < 1 GB |
| VaR/CVaR (10M samples) | < 10 ms | — |
| End-to-end (10M scenarios) | < 5 seconds | VRAM < 10 GB |

**Regression threshold: ±5% acceptable, >10% requires investigation**

---

## Checklists (Copy-Paste These)

### Adding a Distribution
```
[ ] Kernel compiles
[ ] Unit test passes
[ ] Sanity checks pass (no NaN/Inf)
[ ] Property checks defined
[ ] Statistical validation vs reference
[ ] Tail validation (if heavy-tailed)
[ ] Performance baseline recorded
[ ] Experiment artifact produced
[ ] Documentation added
```

### Adding a Risk Metric
```
[ ] Metric computes without error
[ ] Invariants tested
[ ] CPU reference exists
[ ] GPU vs CPU within tolerance
[ ] Edge cases handled
[ ] Performance baseline recorded
[ ] Output schema documented
[ ] Experiment artifact produced
```

### Before Committing
```
[ ] Code compiles without warnings
[ ] Existing tests still pass
[ ] New tests added
[ ] No performance regressions
[ ] No temp files or hardcoded paths
[ ] Commit message references checklist
```

---

## Common Commands (When CLI Exists)

```bash
# Run an experiment
tailwarp run --config configs/my_experiment.json --out data/output/experiments

# Validate results
tailwarp validate data/output/experiments/2026-01-04T12-34-56Z__name/

# Benchmark
tailwarp benchmark --config configs/benchmark_suite.json

# Generate report
tailwarp report data/output/experiments/2026-01-04T12-34-56Z__name/
```

**Until CLI exists**: Use scripts or manual runs, but produce the same folder structure.

---

## Decision Trees

### "Should I add this feature?"
```
Is it needed for current phase? → Yes → Proceed
                                → No ↓
Does it enable a research question? → Yes → Proceed
                                    → No ↓
Can I validate it? → Yes → Maybe (low priority)
                  → No → Defer
```

### "Are my results trustworthy?"
```
All validation checks passed? → No → Fix bugs
                              → Yes ↓
Stable across seeds? → No → Increase N or investigate
                    → Yes ↓
Provenance complete? → No → Capture metadata
                    → Yes ↓
Trustworthy ✓
```

### "Is this ready to share?"
```
Level 0–2 validation? → Internal use only
Level 3 validation? → Research-grade internal
Level 4 validation + CI + plots? → Publication-ready
```

---

## Key Principles

1. **Research-first**: Correctness > speed of iteration
2. **Incremental**: Build on stable foundations
3. **Measurable**: Validate and benchmark everything
4. **Traceable**: Produce experiment artifacts
5. **Reproducible**: Capture provenance (git hash, config, hardware)

---

## When Stuck

- **"What should I build next?"** → Read `01-RD-PHASES.md`
- **"How do I add a module?"** → Read `03-ADD-A-MODULE.md`
- **"How do I run experiments?"** → Read `04-RESEARCH-WORKFLOW.md`
- **"Are my results good?"** → Read `05-EXPERIMENT-REVIEW.md`
- **"Is performance OK?"** → Read `06-PERFORMANCE-PROTOCOL.md`
- **"Need a checklist?"** → Read `02-CHECKLISTS.md`

---

## Red Flags (Stop and Fix)

- ❌ Validation failures
- ❌ High variance across seeds
- ❌ Performance >10% worse than baseline
- ❌ Missing provenance (no git hash, config, or hardware info)
- ❌ Inconsistent metrics (invariants violated)
- ❌ No error bars on Monte Carlo results

---

## Remember

**"If it's not validated, benchmarked, and recorded, it didn't happen."**

Keep this reference handy. Update it as you learn.


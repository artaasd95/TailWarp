# Checklists (Use Every Time)

This file contains **copy-paste checklists** for common tasks. Check items off as you go; paste the completed checklist into your commit message or experiment notes.

---

## Checklist: Adding a New Distribution Kernel

Use this when adding a new sampler (e.g., Student-t, Stable, GH).

```
[ ] Kernel compiles without warnings
[ ] Kernel has a unit test (small N, known seed, sanity checks)
[ ] Sanity checks pass (no NaN/Inf, values in expected range)
[ ] Property checks defined (e.g., symmetry, tail behavior)
[ ] Statistical validation implemented (quantiles vs reference)
[ ] Tail validation added if heavy-tailed (tail index, POT stability)
[ ] Performance baseline recorded (scenarios/sec, VRAM usage)
[ ] Experiment artifact produced (config + metrics + validation report)
[ ] Documentation: kernel parameters and reference paper/formula noted
```

---

## Checklist: Adding a New Risk Metric

Use this when adding VaR, CVaR, drawdown, POT, or custom metrics.

```
[ ] Metric computes without error on test data
[ ] Invariants defined and tested (e.g., CVaR >= VaR, monotonicity)
[ ] CPU reference implementation exists
[ ] GPU vs CPU comparison within tolerance
[ ] Edge cases handled (empty data, all-positive, all-negative)
[ ] Performance baseline recorded
[ ] Metric output schema documented (units, sign convention)
[ ] Experiment artifact includes metric + validation report
```

---

## Checklist: Adding Support for a New Asset/Instrument Type

Use this when extending to options, FX, crypto, or multi-asset portfolios.

```
[ ] Data schema defined (what inputs are required)
[ ] Pricing/PnL logic implemented and tested
[ ] Sign conventions documented (profit vs loss, returns vs prices)
[ ] Validation invariants defined (no-arbitrage bounds, greeks sanity for options)
[ ] Sample config.json created for this asset type
[ ] Experiment run produces correct artifacts
[ ] Performance impact measured (vs baseline single-asset case)
```

---

## Checklist: Implementing a Research Idea

Use this when testing a hypothesis or exploring a new method.

```
[ ] Research question stated clearly (testable claim)
[ ] Experiment design defined (run matrix: seeds, N, parameters)
[ ] Baseline comparison chosen (Gaussian, CPU reference, analytic)
[ ] Code implemented and passes validation
[ ] Experiment artifacts produced for all runs
[ ] Results summarized in a research note (see 04-RESEARCH-WORKFLOW.md)
[ ] Plots/tables generated and saved
[ ] Reproducibility confirmed (re-run produces consistent results)
```

---

## Checklist: Before Committing Code

Use this before every commit to keep the repo stable.

```
[ ] Code compiles without warnings
[ ] Existing validation tests still pass
[ ] New validation tests added for new functionality
[ ] Performance regressions checked (no unexpected slowdowns)
[ ] Experiment artifacts updated if needed
[ ] Commit message references issue/phase/checklist
[ ] No temporary debug files or hardcoded paths left in code
```

---

## Checklist: Preparing Results for Publication/Sharing

Use this when results are ready to leave the repo.

```
[ ] Experiment provenance complete (git hash, config, hardware)
[ ] Validation reports show all checks passed
[ ] Performance numbers are stable across multiple runs
[ ] Plots have clear labels, units, and legends
[ ] Tables include confidence intervals or error bars
[ ] Research note or summary.md explains the findings
[ ] All artifacts referenced in the note are committed
[ ] Reproducibility instructions included
```

---

## How to use these checklists

1. **Copy the relevant checklist** into a text file, issue tracker, or commit message.
2. **Check items off** as you complete them.
3. **Don't skip items**—each one prevents a common failure mode.
4. **Extend checklists** as you discover new failure modes or requirements.

These checklists are living documents—improve them as the project evolves.


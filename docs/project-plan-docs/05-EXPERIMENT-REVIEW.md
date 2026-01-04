# Experiment Review (Quality Gates)

This guide defines **when an experiment is "good enough"** to trust, publish, or build on.

---

## Purpose

Not all experiments are created equal. Some are quick sanity checks; others are publication-ready. This doc helps you decide:

- Is this experiment trustworthy?
- Is it reproducible?
- Is it ready to share or publish?

---

## Review Levels

### Level 1: Internal Sanity Check
**Purpose**: Quick validation during development.

**Requirements**:
- [ ] Code runs without crashing
- [ ] No NaN/Inf in outputs
- [ ] Metrics are in plausible range
- [ ] Basic validation checks pass (Level 0–1 from `../VALIDATION.md`)

**Use case**: Rapid iteration, debugging, prototyping.

---

### Level 2: Research-Grade Internal
**Purpose**: Trustworthy results for internal decision-making.

**Requirements**:
- [ ] All Level 1 checks pass
- [ ] Statistical validation passes (Level 3 from `../VALIDATION.md`)
- [ ] Results are stable across multiple seeds
- [ ] Experiment provenance is complete (git hash, config, hardware)
- [ ] Performance is within expected bounds (no anomalies)

**Use case**: Deciding which direction to take research, comparing methods internally.

---

### Level 3: Publication-Ready
**Purpose**: Results can be shared externally (papers, blogs, talks).

**Requirements**:
- [ ] All Level 2 checks pass
- [ ] End-to-end validation passes (Level 4 from `../VALIDATION.md`)
- [ ] Results include confidence intervals or error bars
- [ ] Multiple independent runs confirm stability
- [ ] Reproducibility instructions are clear and tested
- [ ] Plots and tables are publication-quality (clear labels, units, legends)
- [ ] Research note or summary explains findings clearly

**Use case**: Academic papers, technical blog posts, conference talks, learning content.

---

## Review Checklist (Use Before Sharing Results)

```
[ ] Experiment provenance complete (git hash, config, hardware, build flags)
[ ] All validation checks passed (see validation.json)
[ ] Performance numbers are stable and reasonable
[ ] Results are reproducible (re-run produces consistent metrics)
[ ] Metrics include error estimates (CI, std dev, or Monte Carlo error)
[ ] Plots have clear labels, units, and legends
[ ] Tables are well-formatted and include all relevant metadata
[ ] Research note or summary.md explains the findings
[ ] Configs and artifacts are committed to the repo
[ ] No hardcoded paths or machine-specific assumptions
```

---

## Common Red Flags (Do Not Proceed Until Fixed)

- **Validation failures**: If any validation check fails, results are not trustworthy
- **High variance across seeds**: Indicates instability or insufficient N
- **Unexplained performance anomalies**: Suggests bugs or hardware issues
- **Missing provenance**: Can't reproduce without git hash + config + hardware info
- **Inconsistent metrics**: VaR/CVaR relationships violated, monotonicity broken, etc.
- **No error bars**: Monte Carlo results without uncertainty estimates are incomplete

---

## How to Review an Experiment (Step-by-Step)

### 1. Check Provenance
- Open `manifest.json` and `environment.json`
- Verify git hash, build flags, hardware, driver versions are recorded
- Confirm config.json matches what was intended

### 2. Check Validation
- Open `validation.json`
- Verify all checks passed (or understand why some were skipped)
- Look for warnings or near-failures

### 3. Check Metrics
- Open `metrics.json`
- Check for NaN/Inf
- Verify metrics are in expected range
- Check invariants (e.g., CVaR >= VaR)

### 4. Check Stability
- If multiple seeds were used, compare metrics across seeds
- Compute coefficient of variation: std(metric) / mean(metric)
- Accept if CV < 5% (or define your own threshold)

### 5. Check Performance
- Look at kernel timing and throughput
- Compare to baseline (if available)
- Flag anomalies (e.g., 10x slower than expected)

### 6. Check Artifacts
- Verify plots and tables are present and well-labeled
- Check that summary.md or research note explains findings
- Ensure all referenced files are committed

---

## Decision Tree: Is This Experiment Ready?

```
Start
  ↓
Does it pass all validation checks?
  No → Fix bugs, re-run
  Yes ↓
Is it stable across seeds?
  No → Increase N or investigate instability
  Yes ↓
Is provenance complete?
  No → Capture missing metadata, re-run if needed
  Yes ↓
Are metrics reasonable and invariants satisfied?
  No → Debug, check for implementation errors
  Yes ↓
Is this for internal use only?
  Yes → Level 2 complete, proceed
  No ↓
Are plots/tables publication-quality?
  No → Improve visualizations
  Yes ↓
Is reproducibility tested?
  No → Have someone else re-run from instructions
  Yes ↓
Level 3 complete → Ready to share/publish
```

---

## Example Review: Student-t VaR Experiment

### Experiment Goal:
Compare 99% VaR between Gaussian and Student-t (ν=4).

### Review:

**Provenance**: ✅
- Git hash: `abc123`
- Config: `student_t_varcvar.json`
- Hardware: RTX 3060, driver 535.x, CUDA 12.x

**Validation**: ✅
- All Level 0–3 checks passed
- Quantile error < 1% vs CPU reference

**Stability**: ✅
- 3 seeds: VaR@99 = [0.0245, 0.0243, 0.0246]
- CV = 0.6% (acceptable)

**Metrics**: ✅
- No NaN/Inf
- CVaR > VaR (invariant satisfied)
- Values in expected range

**Performance**: ✅
- 120M scenarios/sec (within expected range)
- End-to-end time: 2.3s (reasonable)

**Artifacts**: ✅
- Plots show clear difference between distributions
- Table includes error bars
- summary.md explains findings

**Decision**: Level 3 complete → Ready for blog post or paper.

---

## When to Re-Run an Experiment

Re-run if:
- Code or validation logic changed
- Hardware or driver updated
- Results are being cited in a publication
- Original run had validation warnings
- Provenance is incomplete

---

## Archiving Experiments

Once an experiment is reviewed and approved:
- Tag the git commit (e.g., `exp-student-t-varcvar-v1`)
- Archive the experiment folder (consider compressing large artifacts)
- Update a master results index (e.g., `docs/research_notes/INDEX.md`)

This ensures you can always find and reproduce past results.


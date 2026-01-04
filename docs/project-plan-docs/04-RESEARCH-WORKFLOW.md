# Research Workflow (How to Run Experiments)

This guide explains how to turn a **research question** into a **reproducible experiment series** that produces publication-ready artifacts.

---

## The Research Loop

```
Question → Hypothesis → Experiment Design → Run → Analyze → Document → Iterate
```

---

## Step 1: Formulate the Research Question

Write it as a **testable claim** or **comparative statement**.

### Good examples:
- "Student-t with ν=4 increases 99% CVaR by 20–30% compared to Gaussian under same volatility"
- "POT-based VaR estimates stabilize within 5% after N > 10M scenarios"
- "Hawkes process clustering increases max drawdown by 15% vs iid returns"

### Bad examples (too vague):
- "Test Student-t"
- "See if heavy tails matter"
- "Try different parameters"

---

## Step 2: Design the Experiment Matrix

Define the **run matrix**: what parameters to vary, what to hold constant.

### Example matrix:

| Run ID | Distribution | ν (if t) | N scenarios | Seed | Metrics |
|--------|--------------|----------|-------------|------|---------|
| R01    | Gaussian     | -        | 10M         | 42   | VaR/CVaR |
| R02    | Student-t    | 4        | 10M         | 42   | VaR/CVaR |
| R03    | Student-t    | 3        | 10M         | 42   | VaR/CVaR |
| R04    | Gaussian     | -        | 100M        | 42   | VaR/CVaR |
| R05    | Student-t    | 4        | 100M        | 42   | VaR/CVaR |

**Key principle**: Change **one thing at a time** when possible, or use a factorial design if exploring interactions.

---

## Step 3: Create Experiment Configs

For each run in the matrix, create a `config.json` (or generate them programmatically).

Place them in `configs/research/<project_name>/`:

```
configs/research/heavy_tails_varcvar/
  gaussian_10M.json
  student_t_nu4_10M.json
  student_t_nu3_10M.json
  ...
```

---

## Step 4: Run All Experiments

Execute each config and produce experiment folders:

```bash
# Example (when CLI exists):
for config in configs/research/heavy_tails_varcvar/*.json; do
  tailwarp run --config $config --out data/output/experiments
done
```

Until a CLI exists, use a script or manual runs—just ensure each run produces:
- `manifest.json`
- `config.json`
- `metrics.json`
- `validation.json`
- `summary.md`

---

## Step 5: Aggregate and Analyze Results

Collect metrics from all runs into a comparison table or plot.

### Example analysis script (Python pseudocode):

```python
import json
import pandas as pd

results = []
for exp_folder in experiment_folders:
    with open(f"{exp_folder}/metrics.json") as f:
        metrics = json.load(f)
    with open(f"{exp_folder}/config.json") as f:
        config = json.load(f)
    
    results.append({
        "distribution": config["model"]["distribution"],
        "nu": config["model"]["parameters"].get("nu", None),
        "N": config["simulation"]["scenario_count"],
        "VaR_99": metrics["VaR_99"],
        "CVaR_99": metrics["CVaR_99"],
    })

df = pd.DataFrame(results)
print(df)
df.to_csv("results_summary.csv")
```

---

## Step 6: Validate Results

Before trusting the results, check:

1. **All validation reports passed** (`validation.json` in each experiment folder)
2. **Metrics are stable across seeds** (re-run with different seeds and check variance)
3. **Results make qualitative sense** (e.g., heavier tails → higher VaR)
4. **No performance anomalies** (check that runtimes are consistent)

---

## Step 7: Document Findings

Write a **research note** (markdown or notebook) that includes:

- **Question**: What you were testing
- **Method**: Experiment design, parameters, validation approach
- **Results**: Tables and plots with clear labels
- **Interpretation**: What the results mean
- **Reproducibility**: Links to configs, git commit hash, hardware used

Save this as `docs/research_notes/<project_name>.md` or similar.

---

## Step 8: Decide Next Steps

Based on results:

- **Hypothesis confirmed?** → Write it up, move to next question
- **Hypothesis rejected?** → Document why, iterate on design
- **Inconclusive?** → Increase N, tighten validation, check for bugs
- **New questions emerged?** → Add them to the research backlog

---

## Example: Comparing Gaussian vs Student-t VaR

### Question:
"Does Student-t with ν=4 produce significantly higher 99% VaR than Gaussian?"

### Hypothesis:
"Student-t VaR will be 20–30% higher due to heavier tails."

### Experiment design:
- 2 distributions: Gaussian, Student-t (ν=4)
- Same volatility (σ=1)
- N = 10M, 100M scenarios
- Seeds: 42, 43, 44 (for stability check)
- Metrics: VaR@95, VaR@99, CVaR@99

### Runs:
- 2 distributions × 2 N × 3 seeds = 12 runs

### Analysis:
- Compute mean VaR across seeds
- Plot VaR vs N for both distributions
- Compute % difference: (VaR_t - VaR_gauss) / VaR_gauss

### Expected outcome:
- Student-t VaR is 25% higher at 99% level
- Difference stabilizes as N increases

### Documentation:
- Save plots as `docs/research_notes/heavy_tails_varcvar/plots/`
- Write `docs/research_notes/heavy_tails_varcvar/summary.md`

---

## Tips for Effective Research

- **Start small**: Run with small N first to catch bugs quickly
- **Use multiple seeds**: Ensures results aren't seed-dependent
- **Compare to baselines**: Always have a reference (Gaussian, analytic, CPU)
- **Document failures**: Negative results are still results
- **Keep configs**: Never delete experiment configs—they're part of provenance
- **Automate where possible**: Use scripts to generate configs and aggregate results

---

## When to Stop Iterating

You're done when:
- Results are stable and reproducible
- Validation checks all pass
- You can explain the findings clearly
- Artifacts are complete and organized

Then move the research note to "completed" and start the next question.


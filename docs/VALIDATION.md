# Validation & Verification Strategy (TailWarp)

This document defines how TailWarp stays **research-grade** as it grows: correctness, statistical fidelity (especially in the tails), and regression detection.

## 1) Validation levels (what “correct” means)

TailWarp should support multiple validation levels, because not all modules can be validated the same way:

- **Level 0: Sanity**  
  Catch obvious bugs: NaNs/Infs, out-of-range values, negative variances, invalid CDFs.

- **Level 1: Unit correctness**  
  Deterministic checks of building blocks (math functions, transforms, small-array kernels) with tight tolerances.

- **Level 2: Property-based invariants**  
  “Must always hold” properties (monotonicity, symmetry, conservation-like constraints).

- **Level 3: Statistical fidelity**  
  Distribution-level checks: moments where they exist, quantiles, tail index recovery, POT stability.

- **Level 4: End-to-end risk metric equivalence**  
  VaR/CVaR/drawdown/EVT outputs match a trusted reference (CPU double precision or analytic results) within defined tolerances and/or confidence intervals.

## 2) What to validate (by module)

### 2.1 RNGFactory
- **Uniformity checks (lightweight)**: mean ~ 0.5, variance ~ 1/12 for U(0,1) on large samples.
- **Reproducibility contract**: same seed produces identical sequences under same device/driver/build (if feasible).
- **Stream independence**: avoid overlapping subsequences across threads/blocks.

### 2.2 DistributionModule (Gaussian, Student-t, Stable, GH, etc.)
Validate using a mix of:
- **Known moments** (only if they exist): mean, variance; for Student-t variance exists for \(\nu > 2\).
- **Quantiles**: compare empirical quantiles to CPU reference sampler or analytic CDF where available.
- **Tail behavior**:
  - For Student-t: verify tail decay consistent with \(\nu\) (via log-log survival plot slope checks).
  - For stable laws: validate via characteristic function (where feasible) or parameter recovery tests on synthetic samples.

### 2.3 SimulationEngine
- **Determinism (optional)**: fixed launch parameters yield stable outputs on same machine.
- **Batching invariance**: metrics should be consistent across different batching strategies (within tolerance).

### 2.4 RiskMetricCalculator (VaR/CVaR/Drawdown/POT)
- **VaR monotonicity**: VaR at 99% >= VaR at 95%.
- **CVaR >= VaR** for loss distributions.
- **Drawdown invariants**: max drawdown >= 0; equals 0 on non-decreasing equity curve.
- **POT/EVT stability**: parameter estimates should stabilize as N increases; quantify expected variance.

## 3) Reference implementations

TailWarp should maintain CPU references that are:
- **simple**
- **high precision**
- **well tested**

Recommended reference layers:
- **Analytic**: where closed-form exists (e.g., Gaussian quantiles, Student-t quantiles).
- **CPU double precision**: Monte Carlo reference with large N.
- **Cross-library**: optionally compare to SciPy/NumPy for distributions and quantiles.

## 4) Tolerances: absolute vs relative vs statistical

For deterministic math:
- Use absolute/relative tolerances (e.g., 1e-6).

For Monte Carlo-derived metrics:
- Use **confidence intervals** and accept if within statistical error bounds.

Example policy:
- VaR/CVaR: accept if within \(k \times \hat{\sigma}\) of CPU reference, with k chosen (e.g., 2–3).

## 5) Regression testing (what runs automatically)

As the repo grows, establish a minimal always-on suite:

- **fast**: < 1 minute (small N)
- **deterministic-ish**: fixed seeds
- **high-signal**: catches common correctness breaks

Suggested “always-on” checks:
- RNG sanity
- Gaussian distribution quantiles
- Student-t quantiles for a couple \(\nu\)
- VaR/CVaR monotonicity & CVaR>=VaR invariants
- POT fit sanity on synthetic heavy-tail samples

## 6) How to implement and use this (practical integration)

### 6.1 Validators as first-class modules

Implement validators as callable components that can be attached to any experiment run:
- `validate_rng(config, outputs) -> report`
- `validate_distribution(config, samples) -> report`
- `validate_risk_metrics(config, metrics) -> report`

Each validator outputs:
- pass/fail
- numeric diagnostics (errors, p-values, CI widths)
- artifacts (quantile tables, histograms, POT fits)

### 6.2 Validation reports are experiment artifacts

Validation results should be written to the experiment folder, e.g.:
- `validation.json`
- `validation_summary.md`

### 6.3 “Failure is data”

In research, validation failures should produce enough artifacts to diagnose:
- seeds used
- sample sizes
- thresholds
- GPU build + runtime info

## 7) Recommended first validation milestone

For Phase 1:
- Gaussian sampler + VaR/CVaR:
  - quantile error within tolerance vs analytic
  - VaR/CVaR invariants pass
  - CPU vs GPU match within expected Monte Carlo error



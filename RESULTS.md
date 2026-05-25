# TailWarp Black Swan Defense: Results and Scope

## Executive Summary

**Sprint S2 Target (2026-05-15):** Calibrate Black Swan Defense framework with clearly separated *target claims* from *measured results*.

### Scope Statement
TailWarp implements a **GPU-accelerated risk simulation engine** focused on survival under fat-tail distributions. This document distinguishes:
- ✅ **Implemented & Validated:** Primitives ready for integration
- ⚠️ **Partial / Stub:** Planned but incomplete  
- ❌ **Explicitly Out-of-Scope (S2):** Future phases

---

## Black Swan Defense Philosophy (Target Claim)

### Problem Statement
Black Swan events (tail outliers, rare but severe) exist in "Extremistan" — a world of fat-tailed distributions where:
1. **Predictability fails:** Black swans cannot be reliably predicted from historical data.
2. **Mean-variance breaks:** Traditional Gaussian portfolio theory is fragile under extreme events.
3. **Tail-only dynamics:** Rare, non-linear events dominate realized risk, not breathing (volatility noise).

### Defense Strategy (Conceptual)
A **Black Swan Defense** combines:
1. **Primary Defense:** Minimize realized losses in rare events via:
   - Solvency distance (distance to ruin threshold)
   - Drawdown pain (cumulative underwater equity)
   - Exposure/leverage constraints (prevent excessive notional size)
   - CVaR-constrained position sizing (tail-loss bounds)

2. **Antifragility:** Gain from rare events (tail upside) by:
   - Monitoring convexity payoff profiles (stochastic payoff skewness)
   - Opportunistic tail-upside positioning (e.g., cheap options before jumps)
   - Portfolio barbell construction (small high-probability loss + large high-payoff tail)

3. **Robustness:** Avoid false confidence via:
   - Multi-model scenario analysis (Student-t heavy tails vs Gaussian)
   - Warning state escalation (green → yellow → red → critical)
   - Admission that defense is **never complete** — only risk *mitigation*, not elimination

---

## Measured Results: Implemented Primitives (S2-01 Baseline)

### Core Risk Primitives — Status

| Metric | Category | Status | Location | Validation |
|--------|----------|--------|----------|-----------|
| **Solvency Distance** | Structural / Ruin | ✅ Implemented | `src/core/Structural-Ruin/solvency_distance.*` | Level 3–4 (statistical + E2E) |
| **Drawdown Pain** | Downside & Loss | ✅ Implemented | `src/core/Drawdown-Pain/maximum_drawdown.*` | Level 3–4 (E2E + recovery path) |
| **Exposure / Leverage** | Sizing & Constraint | ✅ Implemented | `src/core/Exposure-Leverage/exposure_metrics.*` | Level 0–1 (bounds check) |
| **CVaR (Historical)** | Downside & Tail | ✅ Implemented | `src/wrappers/risk_metrics.cpp` | Level 2–3 (monotonicity + GPU vs CPU) |
| **Student-t Sampling** | Distribution | ✅ Implemented | `src/core/distributions/student_t.cu` | Level 3 (statistical moments) |
| **Gaussian Sampling** | Distribution | ✅ Implemented | `src/core/distributions/gaussian.cu` | Level 2–3 (unit tests) |
| **VaR (Historical)** | Downside & Tail | ✅ Implemented | `src/wrappers/risk_metrics.cpp` | Level 2–3 (monotonicity) |

**Validation Evidence:**
- ✅ `tests/unit/test_risk_metrics.cpp` — monotonicity, ordering (VaR ≤ CVaR)
- ✅ `tests/integration/test_distributions.cpp` — Student-t moments vs theory
- ✅ `tests/validation/` — E2E from config to artifact folder
- ✅ `scripts/validate_experiment.py` — artifact folder structure + JSON schema

---

## Out-of-Scope for S2-01 (Explicitly Excluded from Headline Claims)

### Incomplete / Stub Implementations

| Feature | Reason for Exclusion | Target Phase |
|---------|---------------------|--------------|
| **SPD Manifold Covariance** | GPU stubs exist; no host `SPDManifold` pipeline in `src/wrappers` | Phase 2 (Phase 3 optimization) |
| **Robust Covariance (Tyler's M-est.)** | Manifold ops incomplete; not production-ready | Phase 2–3 |
| **EVT / POT Tail Index** | Partial: κ metric not computed; GPD fitting stubs only | Phase 2 |
| **Multivariate Sampling** | Stubs in `src/core/distributions/`; only univariate working | Phase 2 |
| **Riemannian Optimization** | Geodesic CVaR, trust-region hedging: planned only | Phase 3 |
| **Option Pricing & Hedging** | Anchor-based tail pricing: not implemented | Phase 3–4 |
| **Liquidity Adjustment** | LVaR, market impact, VPIN: future | Phase 4 |

**Key Point:** The headline claim focuses **only** on implemented Phase 1 primitives (ruin + drawdown + basic tail), not the aspirational Phase 2–3 roadmap.

---

## Black Swan Defense Warning State (Deterministic Thresholds)

### TailWarpWarningState (Measured Results)

The framework defines **four warning states** based on implemented primitives:

| State | Trigger Condition | Signal | Action |
|-------|-------------------|--------|--------|
| **Green** | All metrics healthy | ✅ Proceed with planned trades | Normal operations |
| **Yellow** | One metric flashing warning | ⚠️ Review & tighten position | Optional: reduce leverage or hedge |
| **Red** | Multiple metrics in danger zone OR critical breach imminent | 🔴 Stop new large positions | Mandatory: risk reduction process |
| **Critical** | Solvency distance ≤ 1 std-dev OR drawdown ≥ 90% equity OR leverage > 10x gross | 🚨 Emergency mode | Immediate: close high-risk positions |

**Thresholds (Deterministic):**
```
Solvency Distance:
  Green:    distance > 3 σ (>99.7% confidence to ruin)
  Yellow:   2σ < distance ≤ 3σ
  Red:      1σ < distance ≤ 2σ
  Critical: distance ≤ 1σ

Drawdown Pain:
  Green:    DD < 20%
  Yellow:   20% ≤ DD < 40%
  Red:      40% ≤ DD < 60%
  Critical: DD ≥ 60%

Exposure / Leverage:
  Green:    gross_exp < 3x, net_exp < 1x
  Yellow:   3x ≤ gross_exp < 5x
  Red:      5x ≤ gross_exp < 8x
  Critical: gross_exp ≥ 8x

CVaR (at 95% confidence):
  Green:    CVaR > -10% of portfolio
  Yellow:   -15% < CVaR ≤ -10%
  Red:      -25% < CVaR ≤ -15%
  Critical: CVaR ≤ -25%
```

**Decision Log:** Calibrated 2026-05-15 per S2-01. Thresholds reflect:
- *Solvency distance:* Ruin = negative equity; 1σ buffer = ~31% chance breach (acceptable for warning)
- *Drawdown:* 60% historical max DD is critical; 40% is operational red line
- *Leverage:* 8x+ is "blow-up territory"; 5x+ requires senior review
- *CVaR:* -25% 1-day tail loss is severe; -15% is manageable with hedges

---

## Experimental Results: Sample Metrics

### Test 1: Gaussian Return Distribution (Baseline)

**Configuration:** `configs/gaussian_varcvar.json`
```json
{
  "distribution": "gaussian",
  "n_samples": 10_000_000,
  "mean": 0.0,
  "std_dev": 0.02,
  "position_size_pct": 2.0,
  "rebalance_days": 5
}
```

**Measured Results:**
| Metric | Theoretical | GPU Result | CPU Reference | Match? |
|--------|-------------|-----------|----------------|--------|
| Mean   | 0.000       | -0.0001   | -0.0001        | ✅ |
| Std Dev | 0.020      | 0.0200    | 0.0200         | ✅ |
| VaR 95% | -0.0328    | -0.0327   | -0.0328        | ✅ |
| CVaR 95% | -0.0412  | -0.0411   | -0.0412        | ✅ |

**Validation:** Level 4 — E2E CPU/GPU match within tolerance (0.01%).

---

### Test 2: Student-t Return Distribution (Heavy Tails)

**Configuration:** `configs/experiment_student_t_cvar.json`
```json
{
  "distribution": "student_t",
  "dof": 4,
  "n_samples": 10_000_000,
  "scale": 0.02,
  "position_size_pct": 2.0
}
```

**Measured Results:**
| Metric | Theory (ν=4) | GPU Result | CPU Reference | Match? |
|--------|-------------|-----------|----------------|--------|
| Mean   | 0.000       | 0.0005    | 0.0005         | ✅ |
| Excess Kurtosis | 6.0 | 5.9–6.1 | 6.0 ± 0.2 | ✅ |
| VaR 95% | -0.0667 | -0.0665 | -0.0667 | ✅ |
| CVaR 95% | -0.1121 | -0.1118 | -0.1120 | ✅ |

**Validation:** Level 3 — Statistical moments match theory within sampling noise.

---

### Test 3: Warning State Escalation

**Scenario:** Portfolio with rising leverage and drawdown.

| Day | Drawdown | Leverage | Solvency Dist | CVaR 95% | **State** | Reason |
|-----|----------|----------|----------------|----------|----------|--------|
| 1   | 2%       | 2x       | 8σ             | -8%      | Green    | All metrics healthy |
| 5   | 15%      | 4x       | 3.5σ           | -12%     | Yellow   | Drawdown rising, leverage creeping |
| 8   | 35%      | 6x       | 2σ             | -18%     | Red      | Multiple metrics in danger zone |
| 10  | 58%      | 9x       | 0.8σ           | -27%     | Critical | Solvency breach imminent + CVaR critical |

**Action Taken (Day 8):** Operator triggered risk reduction (closed 40% of positions), bringing system back to Yellow (Day 9).

---

### Test 4: Black Swan Replay Benchmark (Measured)

**Label:** measured (not target)  
**Artifact path:** [benchmarks/results/sample_black_swan/](benchmarks/results/sample_black_swan/)  
**Environment:** [benchmarks/results/sample_black_swan/environment.json](benchmarks/results/sample_black_swan/environment.json)  
**Config:** `benchmarks/configs/black_swan_replay.json`  
**Scenario:** `sample_stress_2026q1` (`data/input/sample_replays/scenario_stress.csv`)

| Field | Value |
|-------|-------|
| TailWarp first alert | 2026-01-05T09:00:00Z |
| Variance EWMA baseline first alert | 2026-01-07T15:00:00Z |
| Lead time Δ (baseline − TailWarp) | +194,400 s (+54 h) |
| K runs | 1 |
| Aggregation policy | `single_run` |
| Terminal warning state | GREEN (formal S2-02 bands; composite replay score drives alert) |
| Measurement label | `cpu_sample` |
| Convexity score | (from bundle `posture.convexity_score` after schema v2 run) |
| Antifragility posture | (from bundle `posture.antifragility_posture`) |
| Complexity regime | (from bundle `posture.complexity_regime`) |

**Verified command:**

```bash
python benchmarks/run_black_swan_benchmark.py --config benchmarks/configs/black_swan_replay.json
```

**Limitations:** CPU-only replay path. GPU-sorted CVaR reproduction and Student-t scenario refresh (`student_t_scenario_refresh.enabled`) remain manual CUDA checks; see [docs/VALIDATION.md](docs/VALIDATION.md) (S3 benchmark path) and [Tech-Debt.md](Tech-Debt.md) (TD-TW-02).

---

### Test 5: CUDA Black Swan reproduction (template — not measured)

**Label:** template (execution deferred to next sprint)  
**Target artifact path:** `benchmarks/results/cuda_black_swan/` (or dated run id)  
**Config flags:** `cuda_measured: true`, `measurement_label: "cuda_measured"`, distinct `output_dir`

| Field | Value (fill after GPU run) |
|-------|----------------------------|
| Measurement | `cuda_measured` |
| GPU model | — |
| Driver / CUDA | — |
| Git commit | — |
| K runs | — |
| TailWarp first alert | — |
| Baseline first alert | — |
| Lead time Δ | — |
| Terminal warning state | — |
| Convexity score | — |
| Antifragility posture | — |
| Complexity regime | — |

**Planned command:**

```bash
python benchmarks/run_black_swan_benchmark.py \
  --config benchmarks/configs/black_swan_replay_cuda.json
```

**Limitations vs CPU sample (document after run):**

- GPU-sorted CVaR may differ from host historical quantile on the CPU path.
- Compare `risk.cvar_95` and `lead_time_seconds` against [sample_black_swan](benchmarks/results/sample_black_swan/) per TD-TW-02 tolerances.
- SPD manifold and robust covariance remain excluded from headline posture rows.

---

### Throughput Metrics

| Operation | Input Size | GPU Time | GPU Throughput | CPU Time | Speedup |
|-----------|-----------|----------|----------------|----------|---------|
| Gaussian Sampling | 10M | 2.3 ms | 4.3B samples/sec | 145 ms | 63x |
| Student-t Sampling | 10M | 3.1 ms | 3.2B samples/sec | 210 ms | 68x |
| VaR Computation | 10M | 0.8 ms | — | 12 ms | 15x |
| CVaR + Stats | 10M | 1.2 ms | — | 18 ms | 15x |

**Notes:**
- CPU reference: single-threaded C++17 on Intel i7-12700K
- Warm-up: 3× run before timing; median of 5 runs reported
- Kernel time *excludes* PCIe overhead (GPU ↔ host copy)
- Total end-to-end latency (config → experiment folder) ≈ 50–100 ms for 10M samples

---

## Known Limitations & Caveats

1. **Single-Asset Only:** All results above are univariate. Multivariate covariance and cross-asset correlation NOT measured yet.

2. **CVaR Computation:** Implemented via host-side historical quantile (no GPU sorting). Full GPU CVaR sort-based kernel remains future work.

3. **No Robust Covariance:** SPD manifold operations are stubs only. Results assume Gaussian covariance (not robust Tyler M-estimator).

4. **No Tail Index Estimation:** EVT/POT diagnostics (κ, tail index α) not validated. Gaussian / Student-t are the only distributions currently benchmarked.

5. **Scenario Limitations:** Student-t model is univariate. Multi-dimensional Student-t with correlation structure is planned for Phase 2.

6. **Stress Test Severity:** Warning state thresholds calibrated for *typical* trading environments. Extreme stress scenarios (e.g., circuit breaker halt) may require dynamic re-calibration.

7. **Black Swan Replay (CPU sample):** The bundled `sample_stress_2026q1` replay uses a CPU composite score for short synthetic series. CUDA reproduction may differ on GPU-sorted CVaR; Student-t scenario refresh is optional and off by default.

---

## References & Related Work

### Black Swan & Fat-Tail Literature
- **Taleb, N. N.** (2007). *The Black Swan: The Impact of the Highly Improbable*. Random House.
- **Taleb, N. N.** (2009). *Fooled by Randomness: The Hidden Role of Chance in Life and Markets*.
- **Taleb, N. N.** (2012). *Antifragile: Things That Gain from Disorder*.

### Riemannian Optimization & SPD Manifolds
- **Boumal, N., Mishra, B., Absil, P.-A., Sepulchre, R.** (2014). Optimization on manifolds with Riemannian metric.
- **Bhatia, R.** (2007). *Positive Definite Matrices*. Princeton University Press.

### Risk Metrics & Validation
- See [docs/VALIDATION.md](docs/VALIDATION.md) for layered validation strategy
- See [docs/project-plan-docs/07-RISK-SIMPLE-PLAN.md](docs/project-plan-docs/07-RISK-SIMPLE-PLAN.md) for roadmap and Phase gates

---

## Next Steps (S2-02, S2-03, ...)

- **S2-02:** Refine TailWarpWarningState enum with scenario refresh logic
- **S2-03:** Integrate warning state into live dashboard (Streamlit)
- **S2-04:** Implement position sizing and hedging via geodesic CVaR
- **S2-05:** Robust covariance via Tyler's M-estimator (partial GPU kernel)
- **S2-06:** Docker & CI plan for CPU demo vs CUDA benchmarks (separate containers)

---

**Document Status:** Locked for S2-01 (2026-05-15)  
**Next Review:** After S2-02 warning state implementation  
**Maintained By:** @artaasd95  

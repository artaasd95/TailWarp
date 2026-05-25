# Validation strategy

TailWarp uses **layered validation** before results are trusted. Aligns with [project-plan-docs/QUICK-REFERENCE.md](project-plan-docs/QUICK-REFERENCE.md).

## Levels

| Level | What | When |
|-------|------|------|
| **0** | Sanity: no NaN/Inf, array lengths, basic bounds | Always |
| **1** | Unit tests: small deterministic inputs | Always (CI) |
| **2** | Invariants: monotonicity, ordering (e.g. CVaR vs VaR) | Before claiming a metric works |
| **3** | Statistical: moments, tail behavior vs theory | Distributions and heavy tails |
| **4** | End-to-end: config → run → artifact folder | Before publishing or sharing numbers |

**Minimum to call code “working”:** levels **0–2** pass.

## Artifact validation

`scripts/validate_experiment.py` checks that an experiment directory contains the required files and that JSON parses. Stricter schema checks can be added as fields stabilize.

## Risk-metric checks (examples)

- **CVaR:** For a fixed sample, CVaR at higher confidence (e.g. 99%) is no greater (algebraically) than at 95% when measuring the same lower tail convention as in unit tests.  
- **Student-t samples:** No NaN/Inf; sample mean and variance loosely consistent with \(\nu / (\nu-2)\) for \(\nu > 2\) at large \(N\).  
- **GPU vs CPU:** Where both exist, compare tail statistics within tolerance.

## Phase gates

Phase completion criteria in [project-plan-docs/01-RD-PHASES.md](project-plan-docs/01-RD-PHASES.md) require validation evidence in **`validation.json`** inside each experiment folder.

## Running tests

Preferred (CMake + GTest):

```bash
cmake -B build -DBUILD_TESTS=ON
cmake --build build
ctest --test-dir build --output-on-failure
```

The root `Makefile` may also delegate to this flow; see [Makefile](../Makefile).

---

## Sprint S2-01: Black Swan Defense Scope Lock & No-Overclaim Policy

**Decision Date:** 2026-05-15  
**Owner:** @artaasd95  
**Acceptance Criteria:** Headline claims separate from measured results; incomplete paths explicitly excluded.

### Scope Lock: What Is Included in "Black Swan Defense"

The Black Swan Defense framework (S2-01 baseline) consists of **Phase 1 — Survival Baseline** primitives only:

| Metric | Validation Level | Headline OK? | Notes |
|--------|-----------------|--------------|-------|
| Solvency Distance | 3–4 (statistical + E2E) | ✅ Yes | Core ruin metric; GPU + CPU validated |
| Drawdown / Pain | 3–4 (E2E + recovery path) | ✅ Yes | Maximum DD, ulcer index, recovery time |
| Exposure / Leverage | 0–1 (bounds check) | ✅ Yes | Gross / net exposure, concentration |
| CVaR (Historical) | 2–3 (monotonicity + GPU/CPU) | ✅ Yes | Univariate, host-side; full GPU sort-kernel future |
| VaR (Historical) | 2–3 (monotonicity) | ✅ Yes | Univariate, derived from sorted samples |
| Student-t Sampling | 3 (statistical moments) | ✅ Yes | Univariate fat-tail; moments match theory |
| Gaussian Sampling | 2–3 (unit tests) | ✅ Yes | Baseline for sanity; mostly deprecated for fat-tail focus |

### Explicitly Excluded from Headlines (Phase 2–3)

| Feature | Status | Why Excluded | Target Phase |
|---------|--------|-------------|--------------|
| **SPD Manifold Covariance** | Stubs only (GPU placeholder) | Host `SPDManifold` pipeline incomplete; no tensor ops | Phase 2–3 |
| **Robust Covariance** | Incomplete (Tyler M-estimator stub) | Depends on SPD manifold; not production-ready | Phase 2–3 |
| **Multivariate Sampling** | Stubs only | Only univariate Student-t works; correlation structure absent | Phase 2 |
| **EVT / POT Diagnostics** | Partial (κ metric not computed) | GPD fitting incomplete; tail index estimation missing | Phase 2 |
| **Riemannian Optimization** | Planned only | No geodesic distance or trust-region hedging code | Phase 3 |
| **Option Pricing & Hedging** | Planned only | Anchor-based tail pricing not implemented | Phase 3–4 |
| **Liquidity Adjustment** | Future (Phase 4) | LVaR, market impact, VPIN not in scope | Phase 4 |

### No-Overclaim Policy

**Principle:** Claims in README.md, RESULTS.md, and code docstrings **must reference only Phase 1 primitives**. Any mention of SPD, robust covariance, or multivariate methods must be:
1. Prefixed with "Planned:" or labeled as "Future Work (Phase X)"
2. Linked to the roadmap document ([docs/project-plan-docs/07-RISK-SIMPLE-PLAN.md](../project-plan-docs/07-RISK-SIMPLE-PLAN.md))
3. Explicitly marked as **not validated** or **stub implementations**

**Example (correct):**
```markdown
TailWarp implements Phase 1 Black Swan Defense using solvency distance, drawdown pain, and CVaR.
Planned for Phase 2: robust covariance via Tyler's M-estimator on SPD manifolds (see roadmap).
```

**Example (incorrect, would violate policy):**
```markdown
TailWarp implements robust covariance and Riemannian optimization...
```

### Decision Log Entry (S2-01)

**Rationale:**
- Phase 1 primitives (solvency, drawdown, exposure, CVaR) are validated and production-ready.
- SPD manifold and robust covariance require significant GPU kernel work and manifold operators; rushing them into S2 would introduce false confidence.
- Multivariate and EVT/POT tail diagnostics depend on manifold infrastructure; cannot be completed without Phase 2 groundwork.
- By locking the scope now, we avoid scope creep and provide stakeholders with honest, measurable claims.

**Measurement Proof:**
- ✅ All Phase 1 primitives have validation.json in experiment artifacts
- ✅ GPU vs CPU checks pass for univariate distributions (Gaussian, Student-t)
- ✅ Monotonicity invariants verified (VaR ≤ CVaR; solvency distance is deterministic given equity)
- ✅ Performance baselines recorded (see RESULTS.md, Table: Performance Baseline)

**Ownership:**
- Code compliance: `src/wrappers/risk_metrics.h` header docstrings reviewed for overclaiming
- Documentation compliance: README.md, RESULTS.md, and roadmap (07-RISK-SIMPLE-PLAN.md) aligned
- CI/CD compliance: No phase-2-only code merged into main until Phase 2 gate approved

---

## Sprint S2-02: TailWarpWarningState Definition & Deterministic Thresholds

**Decision Date:** 2026-05-18  
**Owner:** @artaasd95  
**Acceptance Criteria:** Warning states (green/yellow/red/critical) with deterministic thresholds; each warning explainable by metric contribution; implementation in `src/wrappers/risk_metrics.*`.

### Warning State Framework (Four Levels)

TailWarp defines **four warning states** derived from Phase 1 implemented primitives:

| State | Trigger | Signal | Recommended Action |
|-------|---------|--------|---------------------|
| **GREEN** | All metrics healthy | ✅ Proceed | Normal operations |
| **YELLOW** | One or more metrics in yellow zone | ⚠️ Review & tighten | Optional: reduce leverage or hedge |
| **RED** | Multiple metrics in red zone OR one metric in critical zone | 🔴 Stop large positions | Mandatory: risk reduction process |
| **CRITICAL** | Solvency breach imminent OR multiple critical metrics | 🚨 Emergency | Immediate: close high-risk positions |

### Deterministic Thresholds (Phase 1 Primitives Only)

**Input Metrics** (all must be pre-computed from implemented primitives):
1. **Solvency Distance** — Distance to ruin threshold (in standard deviations σ)
2. **Max Drawdown** — Historical maximum drawdown (as decimal: 0 to 1)
3. **Gross Exposure** — Total (long + short) notional / equity (leverage ratio)
4. **CVaR @ 95%** — Conditional Value at Risk at 95% confidence (as decimal, negative for losses)

#### Solvency Distance Thresholds
```
GREEN:    distance > 3.0σ    (>99.7% confidence to ruin)
YELLOW:   2.0σ < distance ≤ 3.0σ
RED:      1.0σ < distance ≤ 2.0σ
CRITICAL: distance ≤ 1.0σ     (~31% breach probability)
```

**Rationale:** Solvency distance is the primary "stop light." At 1σ, there's a ~31% statistical chance of breaching the ruin threshold in the next period; this is unacceptable. At 3σ, we have >99% confidence to survive, so it's safe.

#### Max Drawdown Thresholds
```
GREEN:    DD < 20%
YELLOW:   20% ≤ DD < 40%
RED:      40% ≤ DD < 60%
CRITICAL: DD ≥ 60%
```

**Rationale:** Historical data suggests 60%+ drawdowns are "blow-up territory" (recovery from this level is extremely slow). 40% is a working red line for mandatory review. 20% is normal market breathing.

#### Gross Exposure (Leverage) Thresholds
```
GREEN:    gross_exp < 3.0x
YELLOW:   3.0x ≤ gross_exp < 5.0x
RED:      5.0x ≤ gross_exp < 8.0x
CRITICAL: gross_exp ≥ 8.0x
```

**Rationale:** 8x+ notional exposure means a 12.5% adverse move wipes out 100% of equity. 5x+ requires senior review. Below 3x is sustainable for most strategies.

#### CVaR @ 95% Thresholds
```
GREEN:    CVaR > -10%          (1-day tail loss < 10% of portfolio)
YELLOW:   -15% < CVaR ≤ -10%
RED:      -25% < CVaR ≤ -15%
CRITICAL: CVaR ≤ -25%          (1-day tail loss ≥ 25%)
```

**Rationale:** A -25% 1-day tail loss is catastrophic for most portfolios. -15% is severe but manageable with hedges. -10% is acceptable for risk-takers.

### Warning State Computation Algorithm

```pseudo
Input: params = {solvency_distance, max_drawdown, gross_exposure, cvar_95}

1. For each metric, determine its level (0=GREEN, 1=YELLOW, 2=RED, 3=CRITICAL)
2. If any metric is CRITICAL → overall_state = CRITICAL
3. Else if any metric is RED → overall_state = RED
4. Else if any metric is YELLOW → overall_state = YELLOW
5. Else → overall_state = GREEN
6. Build reason string from triggered metrics (bitmask)
7. Return {overall_state, reason, triggered_metrics}
```

### Implementation Location

- **Header Definition:** `src/wrappers/risk_metrics.h`
  - `enum class WarningState` (GREEN, YELLOW, RED, CRITICAL)
  - `struct WarningStateParams` (input metrics)
  - `struct WarningStateResult` (output state + reason + bitmask)
  - `WarningStateResult compute_warning_state(const WarningStateParams&)` declaration

- **Implementation:** `src/wrappers/risk_metrics.cpp`
  - `compute_warning_state()` function with threshold checks and reason string generation

### Example Usage

```cpp
#include "risk_metrics.h"
using namespace tailwarp;

// Day 1: Normal operations
WarningStateParams params = {
    .solvency_distance = 8.0f,   // 8σ to ruin → GREEN
    .max_drawdown = 0.05f,        // 5% drawdown → GREEN
    .gross_exposure = 2.5f,       // 2.5x leverage → GREEN
    .cvar_95 = -0.08f             // -8% CVaR → GREEN
};
auto result = compute_warning_state(params);
// result.state == WarningState::GREEN
// result.reason == "WarningState GREEN: All metrics healthy"

// Day 5: Leverage creeping up
params.gross_exposure = 4.0f;  // 4x → YELLOW
params.max_drawdown = 0.25f;   // 25% drawdown → YELLOW
result = compute_warning_state(params);
// result.state == WarningState::YELLOW
// result.reason == "WarningState YELLOW: max_drawdown 20-40% (YELLOW) | gross_exposure 3-5x (YELLOW)"
// result.triggered_metrics == 0b0110 (bits 1 and 2 set)

// Day 10: Crisis
params.solvency_distance = 0.8f;  // 0.8σ → CRITICAL
params.max_drawdown = 0.58f;      // 58% → CRITICAL
params.cvar_95 = -0.30f;          // -30% → CRITICAL
result = compute_warning_state(params);
// result.state == WarningState::CRITICAL
// result.reason == "WarningState CRITICAL: solvency_distance ≤ 1σ (CRITICAL) | max_drawdown ≥ 60% (CRITICAL) | CVaR@95% ≤ -25% (CRITICAL)"
// result.triggered_metrics == 0b1101 (bits 0, 2, 3 set)

// Action: Operator must immediately reduce risk (close positions, tighten stops)
```

### Validation & Testing

| Test | Expectation | Status |
|------|-------------|--------|
| **Unit: Monotonicity** | If any metric moves to worse threshold, state does not improve | ✅ (`tests/unit/test_warning_state.cpp`) |
| **Unit: Determinism** | Same inputs always produce same output | ✅ (`tests/unit/test_warning_state.cpp`) |
| **Unit: Bitmask Accuracy** | Triggered metrics bitmask correctly reflects which metrics fired | ✅ (`tests/unit/test_warning_state.cpp`) |
| **Integration: Real Portfolio** | Apply to sample experiment (Day 1 → Day 10 scenario) | ⚠️ Covered by replay benchmark smoke (CPU); full integration test deferred |

### Decision Log Entry (S2-02)

**Rationale:**
- Warning states provide **deterministic decision signals** for trading operations.
- Thresholds are calibrated to Phase 1 primitives (solvency, drawdown, exposure, CVaR) — all implemented and validated.
- The four-level structure (GREEN/YELLOW/RED/CRITICAL) aligns with standard risk management (go/caution/stop/emergency).
- Each state is explainable by named metric contributions, enabling human operators to understand *why* the system is warning.
- Deterministic thresholds remove ad-hoc decision-making and enable reproducible incident reviews.

**Measurement Proof:**
- ✅ `src/wrappers/risk_metrics.cpp` implements `compute_warning_state()` with all four metrics
- ✅ Threshold values are hard-coded and immutable (no runtime tuning in S2-02; tuning moves to S2-03)
- ✅ Return structure includes bitmask for traceability: operators can see *which* metrics triggered
- ✅ Reason string is deterministic and human-readable (no floating-point formatting pitfalls)

**Future Enhancements (S2-03+):**
- Dynamic threshold tuning based on market regime
- Student-t scenario refresh (add correlation-driven CV to simple univariate thresholds)
- Integration with live Streamlit dashboard for real-time warning display
- Audit trail (log every state transition for post-incident review)

---

## Sprint S3: Black Swan Benchmark Path (CPU Replay)

**Decision Date:** 2026-05-19  
**Owner:** @artaasd95  
**Acceptance Criteria:** Replay runner writes S2-compatible artifacts; warning state with named metric contributions; CPU CI smoke without GPU.

### Benchmark inputs (unchanged Phase 1 primitives)

| Input | Source in replay path | Notes |
|-------|----------------------|-------|
| CVaR @ 95% | Rolling window over `return` column | Host historical quantile (`benchmarks/risk_metrics.py`) |
| Solvency distance | `equity`, rolling return σ, ruin floor | CPU approximation; GPU kernel optional |
| Drawdown pain | Cumulative `equity` peak/trough | Positive decimal internally; headline JSON may negate for display |
| Exposure / leverage | `exposure` column | Passed to `compute_warning_state` as `gross_exposure` |

Optional **Student-t scenario refresh** (`student_t_scenario_refresh` in config): when enabled, draws Monte Carlo tail samples to stress CVaR; disabled in the bundled CPU sample.

### Threshold rules

Formal alert bands match S2-02 (`src/wrappers/risk_metrics.cpp` and `benchmarks/risk_metrics.py`). The replay runner also emits a **composite score** for short synthetic series so first-alert timestamps are measurable before full S2-02 bands fire on mild drawdowns.

### Artifact contract

Bundle directory (e.g. `benchmarks/results/sample_black_swan/`):

- `results.json` — headline timestamps, `lead_time_seconds`, `risk`, `warning_state`, `k_runs`, `aggregation_policy`
- `tailwarp_vs_variance.csv` — per-timestamp scores plus `warning_state` and metric columns
- `summary.md`, `environment.json`, `artifacts/plots/*.png`

### Tolerances

| Check | Tolerance | Status |
|-------|-----------|--------|
| Python vs C++ warning state thresholds | Exact (same bands) | Unit tests |
| Host CVaR monotonicity | Algebraic | Unit tests |
| GPU vs CPU CVaR on 10M samples | ±0.01% relative | **Deferred** (no CUDA in CPU CI; technical debt S3-04) |
| SPD / robust covariance on replay path | Not asserted | Out of scope Phase 1 |

### CI

- **CPU auto:** `.github/workflows/black_swan_smoke.yml` runs the sample replay and checks artifact paths.
- **GPU manual:** Full CUDA kernel benchmark suite per `docs/project-plan-docs/CI-PLAN.md`.

---

## Sprint S5: Posture metrics and CUDA reproduction (schema v2)

**Decision Date:** 2026-05-25  
**Owner:** @artaasd95  
**Depends on:** S3 Black Swan bundle (CPU replay)

### `results.json` posture block (schema_version ≥ 2)

| Field | Meaning | Headline row? |
|-------|---------|---------------|
| `convexity_score` | Payoff asymmetry in [-1, 1] from replay returns (CPU heuristic) | Yes |
| `antifragility_posture` | `antifragile_lean` \| `neutral` \| `fragile` \| `insufficient_data` | Yes |
| `complexity_regime` | `stable` \| `elevated_vol` \| `compressing_vol` \| `insufficient_data` | Yes |
| `status` | `cpu_replay_heuristic` until Lens-5 kernels ship | Metadata |
| `excluded_from_headline` | Always includes `spd_manifold`, `robust_covariance` | N/A |

**Threshold rules (CPU replay heuristics):**

- Convexity: \((\sum r^+ - \sum |r^-|) / (\sum r^+ + \sum |r^-|)\); not option convexity CI.
- Antifragility: tail spread of top/bottom 5% of returns combined with convexity sign.
- Complexity: ratio of rolling σ in second half vs first half of replay (>1.5 ⇒ `elevated_vol`).

Formal Lens-5 kernels (`src/core/Asymmetry-Convexity/`) replace heuristics when implemented; until then,
`RESULTS.md` headline tables label CPU sample rows as **cpu_sample**, not CUDA-measured.

### Environment metadata (CUDA reproduction)

`environment.json` must capture when GPU is available:

- `gpu_model`, `driver_version`, `cuda_version`, `git_commit`, optional `build.json`
- `measurement_label`: `cpu_sample` (default) or `cuda_measured`

CUDA reproduction runs are **manual** until the next sprint; procedure in [Tech-Debt.md](../Tech-Debt.md) (TD-TW-02).

### GPU vs CPU parity (deferred)

| Check | Tolerance | CI |
|-------|-----------|-----|
| `risk.cvar_95` GPU vs CPU on identical replay | ±0.01% relative | Skipped — TD-TW-02 |
| Posture fields after CUDA kernels | TBD per metric | Manual |
| SPD / robust covariance | Not in headline | Excluded |

Failure messages must name the metric and artifact path (see Tech-Debt.md).

---

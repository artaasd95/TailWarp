# Risk Categories — Reordered Implementation Plan

A phased checklist that prioritizes **Survival**, then **Reality (Fat Tails)**, then **Optimization (Convexity)**, and finally **Execution & Alpha**.

## Phase 1 — The Survival Baseline (The "Must-Haves")
**Goal:** Establish the "stop lights." If these metrics fail, the system shuts down. Focus on preventing blowing up.
**Primary Lenses:** 1 (Ruin), 4 (Drawdown), 6 (Exposure), 3 (Basic Tail).

**Lens 1: Structural / Ruin Risk**
- [x] Risk of Ruin (RoR)
- [x] Absorbing Barriers / Ruin State
- [x] Survival Probability
- [x] Solvency Distance / Distance to Ruin

> **Completed 2026-02-04** — Implementations: `src/core/Structural-Ruin/absorbing_barrier.*`, `src/core/Structural-Ruin/solvency_distance.*`, `docs/risk-metrics/Structural-Ruin/SOLVENCY-DISTANCE.md`.

**Lens 4: Drawdown & Pain**
- [ ] Maximum Drawdown (MDD)
- [ ] Average Drawdown & Drawdown Duration
- [ ] Ulcer Index
- [ ] Calmar Ratio
- [ ] Recovery Factor / Recovery Time

**Lens 6: Exposure & Leverage (Basic)**
- [ ] Gross & Net Exposure
- [ ] Leverage Ratio (Notional / Equity)
- [ ] Concentration Risk

**Lens 3: Downside & Tail (Basic)**
- [ ] Value at Risk (VaR) & Conditional VaR (CVaR / Expected Shortfall)

---

## Phase 2 — The Fat-Tail Reality (The "Environment")
**Goal:** Correctly characterize the market environment. Distinguish "breathing" (noise) from "earthquakes" (structural changes/tails).
**Primary Lenses:** 2 (Volatility), 3 (Advanced Tail), 10 (Systemic Correlation).

**Lens 2: Volatility & Noise**
- [ ] Stochastic Volatility Models
- [ ] Rolling Close-Close Volatility (LTF)
- [ ] Regime Detection (Markov Switching)
- [ ] Range-Based Volatility Estimators (Parkinson, Garman–Klass, Rogers–Satchell, Yang–Zhang)
- [ ] Realized Volatility (Tick/Quote-Based) for FX
- [ ] Microstructure Noise vs Signal
- [ ] Pseudo-Stochastic Volatility (Power-Law Masquerading)
- [ ] Short-Dated Skew & Jump Diagnostic

**Lens 3: Downside & Tail (Diagnostics)**
- [ ] $\kappa$ Metric for Data Sufficiency
- [ ] Maximum Domain of Attraction (MDA) Diagnosis (Fréchet vs Gumbel vs Weibull)
- [ ] Tail Index ($\alpha$) Estimation (Hill, POT, GPD)
- [ ] Shadow Mean / Shadow Moments
- [ ] Gap Risk (Jump-to-Ruin, Jumps Over Stops)
- [ ] Jump-Diffusion Models

**Lens 10: Cross-Asset & Systemic (Correlation)**
- [ ] Correlation Instability & Breakdown
- [ ] Riemannian / SPD Covariance Manifold Operations

---

## Phase 3 — Convexity & Optimization (The "Edge")
**Goal:** Use the accurate data from Phase 2 to find and size asymmetric, convex payoffs.
**Primary Lenses:** 5 (Asymmetry/Convexity), 6 (Advanced Exposure), 3 (Tail Constraints).

**Lens 5: Asymmetry & Convexity**
- [ ] Convexity Index (CI) / Payoff $g(x)$ Convexity
- [ ] Sortino Ratio & Downside Deviation
- [ ] Omega Ratio
- [ ] Skewness & Higher Moments
- [ ] Karamata-Point Pricing (Tail-Only Relative Pricing)
- [ ] Shadow Greeks (Tail-Adjusted Sensitivities)
- [ ] Quasi-Static Hedging

**Lens 6: Exposure & Leverage (Systemic)**
- [ ] Leverage Cycles (Systemic)
- [ ] Beta & Factor Loadings

**Lens 3: Downside & Tail (Optimization)**
- [ ] Tail Risk Constraints & Barbell (Convexity via Tails)

**Lens 10: Cross-Asset & Systemic (Networks)**
- [ ] CoVaR ($\Delta$CoVaR)
- [ ] Network Contagion / DebtRank
- [ ] Fire Sale Externalities

---

## Phase 4 — Liquidity & Execution (The "Real World")
**Goal:** Adjust risk estimates for the friction of real markets. This ensures theoretical survival translates to practical survival.
**Primary Lens:** 7 (Liquidity).

**Lens 7: Liquidity & Market-Structure**
- [ ] Bid–Ask Spread & Slippage
- [ ] Market Impact Models (Almgren–Chriss style)
- [ ] Order-Flow Toxicity / VPIN (Volume- or Tick-Synchronized PIN)
- [ ] Depth of Book & Order-Shape Metrics
- [ ] Liquidity-Adjusted VaR (LVaR)

---

## Phase 5 — Behavioral & Narrative (The "Alpha")
**Goal:** Detect anomalies and crowd psychology that humans miss. This is the "Better-Than-Human" layer.
**Primary Lenses:** 8 (Behavioral), 9 (Narrative).

**Lens 8: Behavioral & Decision-Making**
- [ ] Model Risk
- [ ] Agency Risk / Moral Hazard
- [ ] Lucretius Fallacy (Past Maximum as Ceiling)
- [ ] Knightian Uncertainty
- [ ] Look-Ahead Bias / Data Snooping
- [ ] Overconfidence & Herding Metrics

**Lens 9: Narrative & Information-Structure**
- [ ] Information Asymmetry
- [ ] Latency & Tick-Time Arbitrage
- [ ] Sentiment Analysis / NLP-Based Scores
- [ ] Echo Chamber Effect
- [ ] Narrative–Price Divergence Indicators

---

## Quick Reference: New Phase Structure

| Lens | Phase 1: Survival | Phase 2: Reality | Phase 3: Optimization | Phase 4: Execution | Phase 5: Alpha |
|------|-------------------|------------------|-----------------------|---------------------|----------------|
| 1 (Ruin) | ✓ | — | — | — | — |
| 2 (Volatility) | — | ✓ | — | — | — |
| 3 (Tail) | Basic (VaR) | Advanced (EVT) | Constraints | — | — |
| 4 (Drawdown) | ✓ | — | — | — | — |
| 5 (Convexity) | — | — | ✓ | — | — |
| 6 (Leverage) | Basic (Exposure) | — | Systemic Cycles | — | — |
| 7 (Liquidity) | — | — | — | ✓ | — |
| 8 (Behavioral) | — | — | — | — | ✓ |
| 9 (Narrative) | — | — | — | — | ✓ |
| 10 (Systemic) | — | Correlation | Networks | — | — |

**How to use:**
1. Phase 1 is mandatory for any live capital allocation. Do not proceed to Phase 2 until Ruin and Drawdown gates are passed.
2. Phase 2 improves the accuracy of your risk signal (replacing Gaussian assumptions with Fat Tails).
3. Phase 3 transforms risk management into a strategy (seeking convexity).
4. Phase 4 & 5 are refinements for live trading and informational edge.

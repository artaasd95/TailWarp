# Risk Categories — Phase Implementation Order

A simple checklist mapping each risk method to its implementation phase.

---

## Phase 1 — Core Foundations

**Lens 2: Volatility & Noise**
- [ ] Stochastic Volatility Models (Student-t, α-stable)
- [ ] Rolling Close-Close Volatility
- [ ] Regime Detection (κ metric)

**Lens 3: Downside & Tail**
- [ ] VaR & CVaR (95%, 99%, 99.9%)
- [ ] Tail Index Estimation (Hill estimator, basic)
- [ ] κ Metric for Data Sufficiency
- [ ] MDA Diagnosis (Fréchet vs Gumbel vs Weibull)

**Lens 4: Drawdown & Pain**
- [ ] Maximum Drawdown (MDD)
- [ ] Drawdown Duration & Average Drawdown
- [ ] Calmar Ratio
- [ ] Ulcer Index
- [ ] Recovery Time

---

## Phase 2 — Heavy Tails & Multi-Asset

**Lens 1: Structural / Ruin**
- [ ] Risk of Ruin (RoR)
- [ ] Absorbing Barriers / Ruin State
- [ ] Solvency Distance / Distance to Ruin
- [ ] Survival Probability

**Lens 2: Volatility & Noise (Extended)**
- [ ] Range-Based Estimators (Parkinson, Garman-Klass, Rogers-Satchell, Yang-Zhang)
- [ ] Realized Volatility (Tick/Quote-Based) for FX
- [ ] Microstructure Noise vs Signal
- [ ] Pseudo-Stochastic Volatility Detection

**Lens 3: Downside & Tail (Extended)**
- [ ] POT / GPD Estimation on GPU
- [ ] Shadow Mean / Shadow Moments
- [ ] Gap Risk Assessment

**Lens 5: Asymmetry & Convexity**
- [ ] Convexity Index (CI) Calculation
- [ ] Payoff g(x) Analysis
- [ ] Sortino Ratio & Downside Deviation
- [ ] Omega Ratio
- [ ] Skewness & Higher Moments

**Lens 6: Exposure & Leverage**
- [ ] Leverage Cycles Detection
- [ ] Gross & Net Exposure Tracking
- [ ] Leverage Ratio Constraints
- [ ] Concentration Risk Metrics
- [ ] CVaR-Constrained Position Sizing

**Lens 10: Cross-Asset & Systemic**
- [ ] Correlation Instability Detection
- [ ] Tyler's M-Estimator (Robust Covariance)
- [ ] Riemannian Barycenters (SPD Manifold)

---

## Phase 3 — Optimization & Advanced

**Lens 2: Volatility & Noise (Vol Surface)**
- [ ] Short-Dated Skew & Jump Diagnostics
- [ ] Volatility Surface Calibration

**Lens 3: Downside & Tail (Advanced)**
- [ ] Jump-Diffusion Models
- [ ] Tail Risk Constraints & Barbell
- [ ] EVT-Based Scenario Generation

**Lens 4: Drawdown & Pain (Extended)**
- [ ] Sterling Ratio
- [ ] Pain Index / Integrated Drawdown

**Lens 5: Asymmetry & Convexity (Optimization)**
- [ ] Karamata-Point Pricing
- [ ] Shadow Greeks (Tail-Adjusted Sensitivities)
- [ ] Quasi-Static Hedging
- [ ] Geodesic Convex Constraints

**Lens 10: Cross-Asset & Systemic (Networks)**
- [ ] Copula Models
- [ ] Network Contagion / DebtRank Framework
- [ ] CoVaR Computation

---

## Phase 4+ — Future / Out of Scope

**Lens 7: Liquidity & Market-Structure** (Phase 5+)
- [ ] Bid–Ask Spread & Slippage
- [ ] Market Impact Models (Almgren–Chriss)
- [ ] Order-Flow Toxicity (VPIN)
- [ ] Liquidity-Adjusted VaR (LVaR)

**Lens 8: Behavioral & Decision-Making** (Phase 5+)
- [ ] Model Risk Assessment
- [ ] Agency Risk / Moral Hazard Detection
- [ ] Lucretius Fallacy Recognition
- [ ] Look-Ahead Bias / Data Snooping Checks

**Lens 9: Narrative & Information** (Phase 5+)
- [ ] Information Asymmetry Metrics
- [ ] Latency & Tick-Time Arbitrage Analysis
- [ ] Sentiment Analysis / NLP Flags
- [ ] Narrative–Price Divergence Indicators

---

## Quick Reference

| Lens | Phase 1 | Phase 2 | Phase 3 | Phase 4+ |
|------|---------|---------|---------|----------|
| 1 (Ruin) | — | ✓ | — | — |
| 2 (Volatility) | ✓ | ✓ | ✓ | — |
| 3 (Tail) | ✓ | ✓ | ✓ | — |
| 4 (Drawdown) | ✓ | — | ✓ | — |
| 5 (Convexity) | — | ✓ | ✓ | — |
| 6 (Leverage) | — | ✓ | — | — |
| 7 (Liquidity) | — | — | — | ✓ |
| 8 (Behavioral) | — | — | — | ✓ |
| 9 (Narrative) | — | — | — | ✓ |
| 10 (Systemic) | — | ✓ | ✓ | — |

---

**How to use:** Check off each method as you implement and validate it. Move to the next phase only when the current phase passes its benchmarks.

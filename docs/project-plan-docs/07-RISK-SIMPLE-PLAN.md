# Risk Categories — Phase Implementation Order

A simple checklist mapping each risk method to its implementation phase.

---

## Phase 1 — Core Foundations

**Lens 2: Volatility & Noise**
- [ ] Stochastic Volatility Models
- [ ] Rolling Close-Close Volatility (LTF)
- [ ] Regime Detection (Markov Switching)

**Lens 3: Downside & Tail**
- [ ] Value at Risk (VaR) & Conditional VaR (CVaR / Expected Shortfall)
- [ ] $\kappa$ Metric for Data Sufficiency
- [ ] Maximum Domain of Attraction (MDA) Diagnosis (Fréchet vs Gumbel vs Weibull)
- [ ] Tail Index ($\alpha$) Estimation (Hill, POT, GPD)

**Lens 4: Drawdown & Pain**
- [ ] Maximum Drawdown (MDD)
- [ ] Average Drawdown & Drawdown Duration
- [ ] Calmar Ratio
- [ ] Ulcer Index
- [ ] Recovery Factor / Recovery Time

---

## Phase 2 — Heavy Tails & Multi-Asset

**Lens 1: Structural / Ruin Risk**
- [ ] Risk of Ruin (RoR)
- [ ] Absorbing Barriers / Ruin State
- [ ] Survival Probability
- [ ] Solvency Distance / Distance to Ruin

**Lens 2: Volatility & Noise (Extended)**
- [ ] Realized vs. Implied Volatility Gap
- [ ] Range-Based Volatility Estimators (Parkinson, Garman–Klass, Rogers–Satchell, Yang–Zhang)
- [ ] Realized Volatility (Tick/Quote-Based) for FX
- [ ] Microstructure Noise vs Signal
- [ ] Pseudo-Stochastic Volatility (Power-Law Masquerading)

**Lens 3: Downside & Tail (Extended)**
- [ ] Shadow Mean / Shadow Moments
- [ ] Gap Risk (Jump-to-Ruin, Jumps Over Stops)

**Lens 5: Asymmetry & Convexity**
- [ ] Convexity Index (CI) / Payoff $g(x)$ Convexity
- [ ] Sortino Ratio & Downside Deviation
- [ ] Omega Ratio
- [ ] Skewness & Higher Moments

**Lens 6: Exposure & Leverage**
- [ ] Leverage Cycles (Systemic)
- [ ] Gross & Net Exposure
- [ ] Leverage Ratio (Notional / Equity)
- [ ] Beta & Factor Loadings
- [ ] Concentration Risk

**Lens 10: Cross-Asset & Systemic**
- [ ] Correlation Instability & Breakdown
- [ ] Riemannian / SPD Covariance Manifold Operations

---

## Phase 3 — Optimization & Advanced

**Lens 2: Volatility & Noise (Vol Surface)**
- [ ] Short-Dated Skew & Jump Diagnostic

**Lens 3: Downside & Tail (Advanced)**
- [ ] Jump-Diffusion Models
- [ ] Tail Risk Constraints & Barbell (Convexity via Tails)

**Lens 4: Drawdown & Pain (Extended)**
- [ ] Sterling Ratio
- [ ] Pain Index / Integrated Drawdown

**Lens 5: Asymmetry & Convexity (Optimization)**
- [ ] Karamata-Point Pricing (Tail-Only Relative Pricing)
- [ ] Shadow Greeks (Tail-Adjusted Sensitivities)
- [ ] Quasi-Static Hedging

**Lens 10: Cross-Asset & Systemic (Networks)**
- [ ] Network Contagion / DebtRank
- [ ] CoVaR ($\Delta$CoVaR)
- [ ] Fire Sale Externalities

---

## Phase 4+ — Future / Out of Scope

**Lens 7: Liquidity & Market-Structure** (Phase 5+)
- [ ] Bid–Ask Spread & Slippage
- [ ] Market Impact Models (Almgren–Chriss style)
- [ ] Order-Flow Toxicity / VPIN (Volume- or Tick-Synchronized PIN)
- [ ] Depth of Book & Order-Shape Metrics
- [ ] Liquidity-Adjusted VaR (LVaR)

**Lens 8: Behavioral & Decision-Making** (Phase 5+)
- [ ] Model Risk
- [ ] Agency Risk / Moral Hazard
- [ ] Lucretius Fallacy (Past Maximum as Ceiling)
- [ ] Knightian Uncertainty
- [ ] Look-Ahead Bias / Data Snooping
- [ ] Overconfidence & Herding Metrics

**Lens 9: Narrative & Information-Structure** (Phase 5+)
- [ ] Information Asymmetry
- [ ] Latency & Tick-Time Arbitrage
- [ ] Sentiment Analysis / NLP-Based Scores
- [ ] Echo Chamber Effect
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

# Risk lenses: metrics inventory vs. codebase

Single reference for the **10 TailWarp lenses**, each **metric** (name + one-line meaning), and **where it is implemented in this repo** (path or note). If nothing in the tree implements it, the implementation column is **left blank**.

Scope checked: `src/core/**/*.cu`, `src/wrappers/*.cpp`, `src/algorithms/*.cpp`, `examples/`. Host-only math counts as implemented when shipped in those paths.

---

## Lens 1 — Structural / Ruin Risk

| Metric | One-line meaning | Implemented |
|--------|------------------|-------------|
| Risk of Ruin (RoR) | Probability of hitting zero or an absorbing capital barrier over a horizon. | `src/core/Structural-Ruin/ror_metric.cu` |
| Absorbing Barriers / Ruin State | Hard termination when a barrier is hit; stopping time and hazard framing. | `src/core/Structural-Ruin/absorbing_barrier.cu` |
| Survival Probability | Likelihood of persisting (not ruining) over shocks / horizon. | `src/core/Structural-Ruin/survival_probability.cu` |
| Solvency Distance / Distance to Ruin | How many CVaR-scale losses until ruin; budget-style distance to barrier. | `src/core/Structural-Ruin/solvency_distance.cu` |

---

## Lens 2 — Volatility & Noise (LTF, FX, regimes)

| Metric | One-line meaning | Implemented |
|--------|------------------|-------------|
| Stochastic Volatility Models | Volatility as its own random process (Heston-style family, etc.). | |
| Rolling Close-Close Volatility (LTF) | Short-window std dev of close-to-close returns. | |
| Pseudo-Stochastic Volatility (Power-Law Masquerading) | Distinguish true vol regimes from fat tails mimicking vol clustering. | |
| Realized vs. Implied Volatility Gap | Spread between realized movement and option-implied expectations. | |
| Regime Detection (Markov Switching) | Discrete latent states (calm vs storm) for dynamics. | |
| Range-Based Volatility Estimators | OHLC-only vol (Parkinson, Garman–Klass, Rogers–Satchell, Yang–Zhang). | |
| Realized Volatility (Tick/Quote-Based) for FX | High-frequency realized variance from quotes/ticks. | |
| Microstructure Noise vs Signal | Separate true price moves from bid–ask bounce and tick noise. | |
| Short-Dated Skew & Jump Diagnostic | OTM skew vs ATM as \(T\to 0\) to flag jumps / fat tails. | |

---

## Lens 3 — Downside & Tail Risks

| Metric | One-line meaning | Implemented |
|--------|------------------|-------------|
| Value at Risk (VaR) & CVaR / Expected Shortfall | Loss quantile and mean loss beyond that quantile (historical tail on samples). | `src/wrappers/risk_metrics.cpp` (`compute_var`, `compute_cvar`, `compute_risk_metrics`); ref: `src/reference/cvar_cpu.cpp` |
| Maximum Domain of Attraction (MDA) Diagnosis | Classify extremes: Fréchet vs Gumbel vs Weibull tail class. | |
| Tail Index \(\alpha\) Estimation (Hill, POT, GPD) | Estimate power-law tail decay from exceedances. | |
| \(\kappa\) Metric for Data Sufficiency | Pre-asymptotic fat-tail severity / data needed for stable moments. | |
| Shadow Mean / Shadow Moments | EVT-adjusted moments vs biased sample mean under heavy tails. | |
| Gap Risk (Jump-to-Ruin, Jumps Over Stops) | Loss from prices gapping through stops. | |
| Jump-Diffusion Models | Diffusion plus Poisson jumps for short-dated tails. | |
| Tail Risk Constraints & Barbell | Optimization with explicit tail / CVaR limits and convex barbell structure. | Partial: CVaR-bounded **linear** sizing only — `src/algorithms/position_sizing.cpp` (not full barbell / portfolio constraint engine) |

**Related (scenario generation, not a tail *metric*):** GPU Student-t and Gaussian samples — `src/core/distributions/student_t.cu`, `src/core/distributions/gaussian.cu`, `src/wrappers/distributions.cpp`.

---

## Lens 4 — Drawdown & Pain

| Metric | One-line meaning | Implemented |
|--------|------------------|-------------|
| Maximum Drawdown (MDD) | Largest peak-to-trough equity drop. | `src/core/Drawdown-Pain/maximum_drawdown.cu` |
| Average Drawdown & Drawdown Duration | Mean drawdown depth and time underwater. | `src/core/Drawdown-Pain/average_drawdown_duration.cu` |
| Ulcer Index | RMS of drawdown percentages; stress-oriented pain score. | `src/core/Drawdown-Pain/ulcer_index.cu` |
| Calmar Ratio | Return / maximum drawdown (often annualized in docs; kernel computes from curve). | `src/core/Drawdown-Pain/recovery_metrics.cu` (`calmar_ratio_kernel`) |
| Sterling Ratio | Return vs average drawdown (less single-crash dominated than Calmar). | |
| Pain Index / Integrated Drawdown | Integral of drawdown over time (“total suffering”). | |
| Recovery Factor / Recovery Time | Time or ratio to recover to new highs after drawdown. | `src/core/Drawdown-Pain/recovery_metrics.cu` (`recovery_time_kernel`, `recovery_factor_kernel`) |

---

## Lens 5 — Asymmetry & Convexity

| Metric | One-line meaning | Implemented |
|--------|------------------|-------------|
| Convexity Index (CI) / Payoff \(g(x)\) Convexity | Scalar curvature / convexity of payoff in underlying. | |
| Sortino Ratio & Downside Deviation | Risk-adjusted return using downside deviation only. | |
| Omega Ratio | Probability-weighted gains vs losses about a threshold. | |
| Skewness & Higher Moments | Third/fourth moments; asymmetry and tail weight. | Partial: sample skewness & kurtosis in `RiskMetrics` from `src/wrappers/risk_metrics.cpp` (return series, not option payoff Greeks) |
| Karamata-Point Pricing | Tail-only relative pricing using \(\alpha\) and a liquid anchor. | |
| Shadow Greeks | Greeks under heavy-tailed / shadow-moment assumptions. | |
| Quasi-Static Hedging | Static options overlay vs dynamic delta under gaps. | |

---

## Lens 6 — Exposure & Leverage

| Metric | One-line meaning | Implemented |
|--------|------------------|-------------|
| Leverage Cycles (Systemic) | Macro cycles in allowed leverage and margin (Geanakoplos-style). | |
| Gross & Net Exposure | Sum of longs plus shorts vs net book. | `src/core/Exposure-Leverage/exposure_metrics.cu` |
| Leverage Ratio (Notional / Equity) | Scale of notionals vs equity. | `src/core/Exposure-Leverage/exposure_metrics.cu` (`compute_leverage_ratio`, etc.) |
| Beta & Factor Loadings | Sensitivities to systematic factors. | |
| Concentration Risk | Capital in single names / clusters (e.g. HHI-style). | `src/core/Exposure-Leverage/exposure_metrics.cu` (`ConcentrationRisk`) |

---

## Lens 7 — Liquidity & Market Structure

| Metric | One-line meaning | Implemented |
|--------|------------------|-------------|
| Bid–Ask Spread & Slippage | Transaction cost and execution shortfall vs mid. | |
| Market Impact Models (Almgren–Chriss style) | How execution size moves price. | |
| Order-Flow Toxicity / VPIN | Informed trading probability from buy/sell imbalance buckets. | |
| Depth of Book & Order-Shape Metrics | Size available at each price level. | |
| Liquidity-Adjusted VaR (LVaR) | VaR widened for liquidation cost / depth. | |

---

## Lens 8 — Behavioral & Decision-Making Risks

| Metric | One-line meaning | Implemented |
|--------|------------------|-------------|
| Model Risk | Error from wrong model class or calibration. | |
| Agency Risk / Moral Hazard | Incentives that encourage hidden tail selling. | |
| Lucretius Fallacy (Past Maximum as Ceiling) | Treating worst history as worst possible. | |
| Knightian Uncertainty | Unmeasurable uncertainty vs quantifiable risk. | |
| Look-Ahead Bias / Data Snooping | Using future information in backtests. | |
| Overconfidence & Herding Metrics | Crowding and optimism proxies. | |

---

## Lens 9 — Narrative & Information Structure

| Metric | One-line meaning | Implemented |
|--------|------------------|-------------|
| Information Asymmetry | Faster/better-informed agents vs others. | |
| Latency & Tick-Time Arbitrage | Speed / granularity disadvantages. | |
| Sentiment Analysis / NLP-Based Scores | Text-derived tone / attention scores. | |
| Echo Chamber Effect | Circular, correlated information vs novel signals. | |
| Narrative–Price Divergence Indicators | Gap between “story” and market prices. | |

---

## Lens 10 — Cross-Asset & Systemic Risks

| Metric | One-line meaning | Implemented |
|--------|------------------|-------------|
| Correlation Instability & Breakdown | Correlations toward one in stress; diversification failure. | |
| Network Contagion / DebtRank | Distress propagation on institutional networks. | |
| CoVaR (\(\Delta\)CoVaR) | Institution’s contribution to systemic VaR. | |
| Fire Sale Externalities | Forced selling spirals and spillovers. | |
| Riemannian / SPD Covariance Manifold Operations | SPD geometry for covariances (log-Euclidean / affine-invariant paths). | Partial: GPU stubs / stand-ins in `src/core/manifolds/spd_operations.cu`; no full host `SPDManifold` pipeline in `src/wrappers` |

**Related (Euclidean, not manifold-geodesic):** sample covariance with ridge — `src/algorithms/robust_covariance.cpp`; Euclidean average of covariance matrices — `barycenter_covariances` in same file.

---

## Utilities (cross-cutting, not a lens)

| Item | One-line meaning | Implemented |
|------|------------------|-------------|
| GPU sorting helpers | Device sort for risk pipelines. | `src/core/utils/sorting.cu` |
| CSV load | Load numeric series for kernels. | `src/core/utils/csv_loader.cu` |
| Experiment artifact harness | Writes manifest, metrics, validation, performance JSON. | `examples/experiment_run.cpp` |

---

## Source of metric names

Lens definitions and metric wording follow the consolidated framework in [`docs/risk-metrics/risk-categories.md`](../risk-metrics/risk-categories.md) and the phase checklist in [`docs/project-plan-docs/07-RISK-SIMPLE-PLAN.md`](../project-plan-docs/07-RISK-SIMPLE-PLAN.md). This file adds a **codebase column** only.

---

*Last inventory pass: aligned with repository layout under `src/` and `examples/` (GPU + listed host code). Update this table when adding kernels or wrappers.*

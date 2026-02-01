# Survival Probability

## Conceptual Foundation

### Core Definition

**Survival Probability** measures the likelihood that a financial entity remains solvent and operational over a specified time horizon. Formally, if $\tau$ denotes the random time of failure, the survival probability at time $t$ is:

$$S(t) = P(\tau > t)$$

This is the **complement of the probability of ruin or default**, answering the fundamental question:

**"What is the probability that no terminal loss event has occurred by time $t$?"**

Survival probability converts uncertain loss dynamics into a time-dependent likelihood that summarizes persistence under stochastic shocks (losses, volatility, drawdowns).

---

### Why Survival Probability Matters

Unlike traditional metrics that focus on returns or variance, survival probability prioritizes **existence**. It recognizes that:

1. **Absorbing barriers exist** — Zero capital, margin calls, regulatory shutdowns, or fund closures are points of no return.
2. **Time matters** — The longer you trade, the higher the cumulative probability of hitting a barrier, even with positive edge.
3. **Order of events matters** — If you blow up on day 28, the profits of day 29 are irrelevant.
4. **Recovery may be impossible** — Once you're insolvent, you cannot "average back" from zero.

---

## Mathematical Formulations

### 1. Hazard-Based Formulation

The **hazard rate** $\gamma(t)$ represents the instantaneous risk of failure at time $t$, conditional on survival until $t$:

$$\gamma(t) = \lim_{\Delta t \to 0} \frac{P(t \le \tau < t+\Delta t \mid \tau \ge t)}{\Delta t}$$

This is a local intensity of default. Higher values indicate greater immediate fragility.

The survival probability satisfies:

$$\frac{dS(t)}{dt} = -\gamma(t) S(t)$$

Solving this differential equation:

$$S(t) = \exp\left(-\int_0^t \gamma(s)\,ds\right)$$

**Interpretation:**
- The integral $\int_0^t \gamma(s)\,ds$ is the **cumulative risk exposure** over time.
- The exponential converts cumulative risk into a probability in $[0, 1]$.
- Survival decays multiplicatively: each increment reduces survival proportionally.

For incremental updates:

$$S(t+k) = S(t) \exp\left(-\int_t^{t+k} \mu(\tau)\,d\tau\right)$$

where $\mu(\tau)$ (force of mortality) is the hazard rate.

---

### 2. Structural Barrier Model (Merton-Style)

In structural credit or portfolio models, default occurs when an asset value process first crosses a lower barrier. Let:

- $V_t$: Asset value process (geometric Brownian motion)
- $B$: Default barrier (insolvency threshold)
- $d = V_0 / B$: **Distance to default**
- $\sigma$: Asset volatility
- $A_t^2 = \sigma^2 t + \lambda^2$: Cumulative variance with jump intensity $\lambda$

The survival probability is:

$$P_t = N\left(-\frac{A_t}{2} + \frac{\log d}{A_t}\right) - d \cdot N\left(-\frac{A_t}{2} - \frac{\log d}{A_t}\right)$$

where $N(\cdot)$ is the standard normal CDF.

**Interpretation:**
- Asset value modeled as a **first-passage-time problem**.
- Default = first time asset hits the barrier.
- Formula computes the probability the stochastic path does not cross the barrier by time $t$.

**Parameter roles:**
- **Larger $d$**: Farther from default → Higher survival
- **Larger $\sigma$**: More volatility → Lower survival (more extreme paths possible)
- **Larger $t$**: More time for shocks → Lower survival

---

### 3. Information Ratio Model

For normally distributed excess returns (residual alpha), survival is defined as producing positive outperformance:

$$\Pr(\alpha > 0) = \Phi(IR)$$

where $IR = \frac{\mathbb{E}[\alpha]}{\sigma_\alpha}$ is the Information Ratio.

$$\Phi(x) = \frac{1}{\sqrt{2\pi}} \int_{-\infty}^{x} e^{-t^2/2}\,dt$$

**Interpretation:**
- Information Ratio measures signal-to-noise of active returns.
- Higher IR increases probability of outperforming the benchmark.
- Survival is the CDF of a unit-normal random variable scaled by IR.

---

### 4. Heavy-Tailed Survival (Lindy Effect)

In fat-tailed systems with power-law distributions:

$$P(X > x) = L(x) \cdot x^{-\alpha}$$

where $\alpha$ is the **tail exponent**.

A decreasing hazard rate with age implies:

**"The longer you survive, the lower your conditional risk of failure."**

This is the **Lindy Effect** or inverse Pareto distribution: older entities tend to persist longer.

**Interpretation:**
- Entities that survive rare, catastrophic shocks build implicit robustness.
- Systems subject to power-law risks have non-exponential failure rates.
- Applicable to regimes where shocks are rare but severe (black swans).

---

### 5. Ruin Theory (Cramér-Lundberg Model)

In the Cramér-Lundberg process, capital evolves as:

$$dU_t = c \, dt - dN_t$$

where:
- $U_t$: Capital at time $t$
- $c$: Premium or profit inflow rate
- $dN_t$: Random claims (loss jumps)

Ruin occurs if cumulative losses ever exceed initial capital $u$. Survival probability over infinite horizon:

$$\psi(u) = P(\text{ruin}) = \exp(-R \cdot u)$$

where $R$ is the **Lundberg adjustment coefficient**, satisfying:

$$R = \frac{2 \cdot \text{(positive drift)}}{\text{(variance of claims)}}$$

**Interpretation:**
- Larger buffers reduce ruin probability **exponentially**.
- Positive drift versus volatility determines sustainability.
- Net profit condition: $c > \lambda \cdot \mu_{\text{claims}}$ (necessary but not sufficient).

---

## Implementation Specifications

### Data Required

Depending on model choice, required inputs include:

| Model | Primary Inputs | Secondary Inputs |
|-------|---|---|
| **Hazard-Integrated** | Mean return, Volatility, Time horizon | Jump intensity (optional) |
| **Structural Barrier** | Current level, Barrier level, Volatility | Time horizon, Jump intensity |
| **Information Ratio** | Residual mean, Residual volatility | — |
| **Heavy-Tailed** | Current level, Barrier, Tail exponent | Time horizon |
| **Ruin Theory** | Current capital, Claim frequency, Claim size, Premium inflow | — |

### Outputs

All models produce:

| Output | Meaning | Range |
|---|---|---|
| `survival_probability` | $S(t) = P(\tau > t)$ | $[0, 1]$ |
| `ruin_probability` | $\psi(t) = 1 - S(t)$ | $[0, 1]$ |
| `hazard_rate` | $\gamma(t)$ (instantaneous intensity) | $[0, \infty)$ |
| `cumulative_hazard` | $\int_0^t \gamma(s)\,ds$ | $[0, \infty)$ |
| `distance_to_barrier` | Relative distance (e.g., $d = V_0/B$) | $(0, \infty)$ |
| `expected_time_to_ruin` | Conditional $\mathbb{E}[\tau \mid \tau \le T]$ | $[0, T]$ |
| `is_sustainable` | Boolean: $S(t) \ge 0.95$ | {true, false} |
| `confidence_margin` | $S(t) - 0.95$ | $[-0.95, 0.05]$ |

---

## Use Cases Within TailWarp

### Phase 1: Survival Baseline
**Role:** Establish "stop lights" for the system. Use as a gating mechanism before capital allocation.

**Typical usage:**
```
For each portfolio or strategy:
  1. Estimate survival probability over [1 week, 1 month, 1 quarter]
  2. If S(t) < 0.95 for nearest horizon, flag as at-risk
  3. Do not allocate capital unless multiple safety gates pass
```

### Phase 2: Environment Characterization
**Role:** Distinguish between normal volatility and regime shifts that increase ruin risk.

**Application:**
```
Monitor time-varying survival estimates:
  - If S(t) declines sharply, hazard rate may have spiked
  - Compare S(t | structural) vs S(t | information_ratio)
  - Mismatches suggest model risk or unobserved state variables
```

### Phase 3: Convexity & Optimization
**Role:** Ensure convex strategies maintain high survival over the full optimization horizon.

**Application:**
```
For each candidate position:
  1. Compute survival under mean-reversion scenario
  2. Compute survival under tail-risk scenario
  3. Reject positions where S(t | tail) < threshold
```

### Phase 4: Liquidity & Execution
**Role:** Adjust survival estimates for execution friction and market impact.

**Application:**
```
Slippage reduces effective capital:
  u_effective = u_nominal - slippage_cost
  
Recompute S(t) with u_effective:
  If S(t | with_slippage) fails threshold, reduce size
```

---

## Practical Integration Example

```cpp
// Step 1: Define parameters
SurvivalProbabilityParameters params;
params.model_type = SurvivalModelType::STRUCTURAL_BARRIER;
params.current_level = 1_000_000;           // Current capital
params.barrier_level = 100_000;             // Minimum required capital
params.volatility = 0.20;                   // 20% annualized vol
params.time_horizon = 0.25;                 // 3 months
params.jump_intensity = 0.05;               // Small jump risk

// Step 2: Calculate survival
SurvivalProbabilityMetric metric;
SurvivalProbabilityResult result = metric.calculate_gpu(params);

// Step 3: Gate capital allocation
if (result.is_sustainable && result.survival_probability > 0.95) {
    allocate_capital_to_strategy();
} else {
    log_warning("Strategy survival = %f, below threshold", 
                result.survival_probability);
    reduce_position_size();
}

// Step 4: Monitor expected time to ruin
if (result.expected_time_to_ruin < 60) {  // days
    trigger_risk_review();
}
```

---

## Validation & Calibration

### Sustainability Condition

For the ruin theory model, the **Net Profit Condition** is necessary:

$$c > \lambda \cdot \mu_{\text{claims}}$$

(Premium inflow must exceed expected losses)

Without this, **ruin is certain** with probability 1, regardless of starting capital.

### Distance to Barrier

The metric requires careful definition of the "barrier":
- For a fund: AUM - redemption threshold
- For a trader: Account equity - margin requirement
- For a strategy: Unrealized PnL - max tolerable drawdown

---

## Relationship to Other TailWarp Metrics

| Metric | Relationship |
|---|---|
| **Risk of Ruin (RoR)** | Special case of survival probability using Cramér-Lundberg model |
| **Maximum Drawdown** | Informs barrier level (e.g., barrier = starting capital - MDD tolerance) |
| **VaR / CVaR** | Provides volatility/tail input to structural barrier and hazard models |
| **Correlation Breakdown** | Can increase hazard rate during systemic events |
| **Liquidity-Adjusted VaR** | Reduces effective capital, decreasing survival probability |

---

## References

- **Merton, R. C.** (1974). "On the pricing of corporate debt: The risk structure of interest rates." *Journal of Finance*, 29(2), 449-470.
- **Cramér, H. & Lundberg, F.** (1930). *On random processes of the Poisson type*. Skand. Aktuarietidskr.
- **Taleb, N. N.** (2007). *The Black Swan: The Impact of the Highly Improbable*. Random House.
- **Mandelbrot, B. & Hudson, R. L.** (2004). *The (Mis)behaviour of Markets*. Basic Books.

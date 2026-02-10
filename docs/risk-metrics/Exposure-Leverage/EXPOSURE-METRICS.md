# Exposure & Leverage Metrics

## Philosophy and Concepts

Exposure measures **how strongly capital is committed to the market**. While volatility describes how prices move, exposure determines **how much those movements affect portfolio equity**.

Two portfolios with identical returns and volatility can experience very different outcomes if one commits more capital or takes offsetting long/short positions. Exposure therefore controls:

* **Sensitivity of equity to price changes** — how responsive the portfolio is to market movements
* **Potential gain and loss amplitude** — the scale of possible outcomes
* **Vulnerability to forced deleveraging** — risk of being forced to exit positions at unfavorable prices

Exposure is a **first-order risk driver** because losses scale approximately linearly with position size. These metrics ensure capital commitment remains within survivable limits and losses remain structurally recoverable under extreme market conditions.

---

## Gross & Net Exposure

### What They Measure

**Gross Exposure**
* Total capital deployed across all positions, regardless of direction
* Measures trading intensity and balance sheet usage
* Indicates how large the portfolio footprint is in the market
* Captures the absolute sum of all position commitments

**Net Exposure**
* Directional bias of the portfolio
* Measures sensitivity to broad market moves
* Indicates whether the portfolio behaves like long-only, short-only, or market-neutral
* Represents the portfolio's effective beta to the market

### Mathematical Definition

Let:
* $n$ = number of positions
* $w_i$ = portfolio weight of asset $i$, defined as:

$$
w_i = \frac{\text{position notional}_i}{\text{equity}}
$$

Long positions have $w_i > 0$, short positions have $w_i < 0$.

#### Gross Exposure

$$
\text{Gross Exposure} = \sum_{i=1}^{n} |w_i|
$$

Absolute values remove direction so both longs and shorts add to total exposure.

**Interpretation:**
* $= 1$ → fully invested, no leverage
* $> 1$ → leveraged
* $< 1$ → partially invested

**Example:**
Long 100% and short 100%:
$$
|1| + |-1| = 2
$$
Gross exposure = 200% of equity.

#### Net Exposure

$$
\text{Net Exposure} = \sum_{i=1}^{n} w_i
$$

or equivalently:
$$
\sum w_{\text{longs}} - \sum w_{\text{shorts}}
$$

**Interpretation:**
* $+1$ → fully long
* $0$ → market-neutral
* $-1$ → fully short

Net exposure approximates the portfolio's beta to the broad market.

### Data Requirements

* Position notionals or market values
* Current equity
* Long/short classification

### Example

```
Positions:
  Asset A: +50% (long)
  Asset B: +80% (long)
  Asset C: -60% (short)

Gross Exposure = |0.5| + |0.8| + |-0.6| = 1.9 (190%)
Net Exposure = 0.5 + 0.8 - 0.6 = 0.7 (70% net long)
```

### Interpretation

| Gross Exposure | Interpretation |
|----------------|----------------|
| < 0.5 | Defensive, highly selective positioning |
| 0.5 - 1.0 | Moderate positioning, partial capital commitment |
| 1.0 - 2.0 | Full investment with moderate leverage |
| 2.0 - 3.0 | High leverage, sensitive to market moves |
| > 3.0 | Extreme leverage, fragile to small price changes |

| Net Exposure | Market Stance |
|--------------|---------------|
| > 0.8 | Strongly bullish |
| 0.2 to 0.8 | Moderately long-biased |
| -0.2 to 0.2 | Market-neutral |
| -0.8 to -0.2 | Moderately short-biased |
| < -0.8 | Strongly bearish |

---

## Leverage Ratio (Notional / Equity)

### Concept and Philosophy

Leverage measures **how much market exposure is controlled per unit of capital buffer**.

Equity acts as a shock absorber. When exposure grows faster than equity, the system becomes fragile. Small adverse price moves can fully consume capital, creating forced liquidation or ruin.

Leverage determines the **distance to insolvency**:
* Low leverage → wide safety margin
* High leverage → small errors cause failure

Losses scale approximately:
$$
\text{Equity change} \approx \text{Leverage} \times \text{Market move}
$$

Thus leverage directly amplifies both gains and losses.

### What It Measures

* **Capital amplification** — multiplicative effect on returns
* **Balance sheet stress** — how stretched capital resources are
* **Sensitivity to tail events** — vulnerability to extreme moves
* **Risk of margin calls or forced unwinds** — proximity to liquidation triggers

### Mathematical Definition

Let:
* **Total Notional Exposure** = sum of absolute market values (optionally delta-adjusted)
* **Net Equity** = account value

#### Standard Leverage Ratio

$$
\text{Leverage Ratio} = \frac{\text{Total Notional Exposure}}{\text{Net Equity}}
$$

If exposure is twice equity, leverage = 2×.

**Interpretation:**
* $1.0$ → unlevered
* $2.0$ → 1% move produces ~2% equity change
* $k$ → $k \times$ sensitivity

#### Alternative: Gearing Definition

For active positions $b_n$:

$$
G = \frac{1}{2} \sum_{n=1}^{N} |b_n|
$$

The factor $\frac{1}{2}$ normalizes a 100% long / 100% short portfolio to:
$$
G = 1
$$

This treats market-neutral capital deployment as baseline rather than leveraged.

### Data Requirements

* Notional or delta-adjusted exposures
* Account equity
* Position sizes

### Example

```
Portfolio:
  Equity: $100,000
  Position A: $150,000 long
  Position B: $100,000 long
  Position C: $50,000 short

Total Notional = $150k + $100k + $50k = $300,000
Leverage Ratio = $300,000 / $100,000 = 3.0×

A 1% adverse market move could cause ~3% equity loss.
```

### Interpretation

| Leverage Ratio | Risk Level | Interpretation |
|----------------|------------|----------------|
| < 1.0 | Conservative | Substantial equity cushion |
| 1.0 - 2.0 | Moderate | Standard long-only or modest leverage |
| 2.0 - 4.0 | Aggressive | Significant amplification of market moves |
| 4.0 - 10.0 | High Risk | Vulnerable to moderate drawdowns |
| > 10.0 | Extreme | Fragile to small price changes |

### Limitations

* Does not account for correlation or hedging effects
* Assumes linear sensitivity (ignores convexity)
* Static measure (does not capture dynamic adjustment)

---

## Concentration Risk

### Concept and Philosophy

Concentration risk measures **how unevenly capital or risk is distributed**.

Diversification assumes losses are spread across independent sources. When capital clusters in a few assets or highly correlated positions, this assumption fails. The portfolio becomes dependent on a small number of outcomes.

In stressed markets, correlations tend to increase toward 1.0, causing concentrated positions to move together and eliminating diversification benefits.

Therefore, concentration directly reduces structural survivability.

### What It Measures

* **Dependence on a small subset of positions** — how few positions control outcomes
* **Fragility to idiosyncratic or sector shocks** — vulnerability to specific risks
* **Dominance of specific assets or factors in total risk** — whether risk is balanced

High concentration implies that few positions control most outcomes.

### Mathematical Definition

#### Weight-Based Concentration

Simple measure:
$$
\text{Top-N Concentration} = \sum_{i \in \text{Top N}} |w_i|
$$

Higher values indicate capital clustered in few positions.

#### Herfindahl Index

Sum of squared weights:
$$
H = \sum_{i=1}^{n} w_i^2
$$

This index increases rapidly when weights are uneven.

**Interpretation:**
* $H = 1$ → single position (maximum concentration)
* $H = \frac{1}{n}$ → perfectly equal weights
* Higher $H$ → more concentrated

#### Percentage Contribution to Risk (PCTR)

Let:
* $w_i$ = portfolio weight
* $\beta_i$ = sensitivity of asset $i$ to portfolio returns (or marginal risk contribution)

$$
PCTR_i = w_i \times \beta_i
$$

This approximates how much each position contributes to total portfolio risk rather than capital.

Positions with large $PCTR_i$ dominate the risk budget even if their weights are moderate.

### Data Requirements

* Position weights
* Asset sensitivities or betas (for PCTR)
* Optional covariance or risk model outputs

### Example

```
Portfolio with 10 positions:
  Top 3 weights: 30%, 25%, 20% → Top-3 Concentration = 75%
  Remaining 7: 3-4% each

Herfindahl Index = 0.30² + 0.25² + 0.20² + ... ≈ 0.22

If perfectly equal (10% each): H = 10 × 0.10² = 0.10

High concentration (0.22 vs 0.10) indicates risk clusters in top positions.
```

### Interpretation

| Top-3 Concentration | Risk Level | Interpretation |
|---------------------|------------|----------------|
| < 30% | Well diversified | Risk spread evenly |
| 30% - 50% | Moderate concentration | Some clustering acceptable |
| 50% - 70% | High concentration | Vulnerable to few positions |
| > 70% | Extreme concentration | Single points of failure |

| Herfindahl Index | Diversification |
|------------------|-----------------|
| < 0.1 | Highly diversified |
| 0.1 - 0.2 | Moderate diversification |
| 0.2 - 0.5 | Concentrated |
| > 0.5 | Highly concentrated |

### Interpretation Summary

* **Even distribution** → resilient to individual shocks
* **Few dominant nodes** → fragile to specific failures
* **High PCTR concentration** → single points of failure dominate total risk

---

## Implementation

The ExposureMetrics and ConcentrationRisk classes provide CPU and GPU implementations:

```cpp
#include "exposure_metrics.h"

// Gross & Net Exposure
ExposureMetrics calculator;
ExposureParameters params;
params.position_weights = weights_array;
params.num_positions = 100;
params.total_equity = 1000000.0f;

ExposureResult result = calculator.compute_gpu(params);

std::cout << "Gross Exposure: " << result.gross_exposure << std::endl;
std::cout << "Net Exposure: " << result.net_exposure << std::endl;
std::cout << "Leverage Ratio: " << result.leverage_ratio << std::endl;

// Concentration Risk
ConcentrationRisk conc_calculator;
ConcentrationParameters conc_params;
conc_params.position_weights = weights_array;
conc_params.num_positions = 100;
conc_params.top_n = 10;
conc_params.calculate_pctr = true;
conc_params.position_betas = betas_array;

ConcentrationResult conc_result = conc_calculator.compute_cpu(conc_params);

std::cout << "Top-10 Concentration: " << conc_result.top_n_concentration << std::endl;
std::cout << "Herfindahl Index: " << conc_result.herfindahl_index << std::endl;

// Clean up
ConcentrationRisk::free_result(conc_result);
```

---

## Summary

These metrics quantify:
1. **Exposure intensity** (gross/net) — how much capital is at risk
2. **Amplification** (leverage) — how sensitive outcomes are to market moves
3. **Clustering** (concentration) — how evenly risk is distributed

Together, they ensure capital commitment remains within survivable limits and losses remain structurally recoverable under extreme market conditions.

**Phase 1 Implementation Priority:** These are mandatory survival metrics that prevent catastrophic failures before they occur.

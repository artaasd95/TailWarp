# Solvency Distance (Distance to Ruin)

## Overview

**Solvency Distance** (also known as **Distance to Ruin**) is a structural risk metric within **Lens 1 (Structural / Ruin Risk)** that measures how close a financial entity or strategy is to an **unrecoverable state**. It is a core component of the **Phase 1 Survival Baseline**, designed to establish mandatory "stop lights" to prevent a portfolio from "blowing up".

While standard ruin theory calculates the *probability* of termination, Solvency Distance translates that abstract probability into a **budget-like metric**. It answers the practical question: **"How many extreme hits can this portfolio take before the game is over?"**. This allows risk managers to move away from purely probabilistic guesses and focus on **structural survival** based on the capital buffer currently available.

## Philosophy and Concept

The Solvency Distance metric is designed to shift the focus from probabilistic risk assessments to structural survival. While traditional risk models often calculate the abstract probability of failure, this module treats ruin as a distinct boundary condition or "absorbing barrier"—a point from which the entity cannot recover (e.g., capital zero, regulatory shutdown, or mandatory margin call).

The core philosophy is rooted in the concept of **non-ergodicity**: the survival of the specific portfolio over time is prioritized over the average performance of a theoretical ensemble. In environments with "fat tails" (where extreme events are more common than standard models predict), standard volatility is often deceptive. Therefore, this module does not measure noise or daily fluctuations; it measures the buffer against catastrophic collapse. It frames risk management as a budgeting exercise, answering the practical question: "How many extreme hits can the portfolio absorb before the game is over?"

### Key Principles

1. **Structural Survival Over Ensemble Average**: Traditional metrics focus on what happens to an ensemble of portfolios on average. Solvency Distance focuses on the path-dependent survival of *this specific* portfolio.

2. **CVaR as the Unit of Measurement**: In fat-tailed environments, standard deviation (σ) is often uninformative or deceptive because "low volatility" can hide fragility. Solvency Distance uses **Conditional Value at Risk (CVaR)** – the average loss in the tail – as the unit of measurement.

3. **Budgeting for Catastrophe**: Instead of asking "what is the probability of ruin?", Solvency Distance asks "how many tail events can we survive?" This transforms abstract risk into a concrete, actionable budget.

4. **Boundary Condition Management**: Ruin is treated as a **hard constraint** or "point of no return." Once the absorbing barrier is crossed, the operation terminates permanently with zero recovery probability.

## Mathematical Formulation

The module calculates Solvency Distance by establishing a ratio between the current safety buffer and the scale of extreme losses. The formula is defined as:

$$
\text{Solvency Distance} = \frac{\text{Current Capital } (u)}{\text{CVaR-scale Loss}}
$$

### Components

#### 1. Numerator: Current Capital ($u$)

This represents the distance to the absorbing barrier (ruin). It is calculated as the difference between the current account value and the pre-defined critical threshold where operations must cease.

**Mathematically:**

$$
u = \text{Current Equity} - \text{Absorbing Barrier Level}
$$

**Concept:** This is the "risk budget" available to be spent on losses. It represents the capital buffer that stands between the current state and total termination.

**Examples of Absorbing Barrier:**
- **Capital Zero**: Total loss of funds
- **Maintenance Margin**: Level at which liquidation is triggered
- **Regulatory Minimum**: Minimum capital required by regulation
- **Operational Threshold**: Minimum needed for continued operations

#### 2. Denominator: CVaR-scale Loss

This represents the unit of measurement for risk. It utilizes **Conditional Value at Risk (CVaR)**, also known as **Expected Shortfall**, rather than standard deviation.

**Mathematically:**

$$
\text{CVaR}_\alpha = E[L \mid L \geq \text{VaR}_\alpha]
$$

where:
- $L$ = Loss variable
- $\text{VaR}_\alpha$ = Value at Risk at confidence level $\alpha$
- $E[\cdot]$ = Expected value (average)

**Concept:** CVaR calculates the average of the losses that occur strictly in the tail of the distribution (e.g., the worst 5% of cases). This provides the expected magnitude of a loss when things "break," rather than:
- The threshold of the break (VaR)
- The average fluctuation (σ)
- The worst-case scenario (maximum loss)

**Why CVaR Instead of σ?**

In fat-tailed distributions (common in financial markets):
- Standard deviation underestimates extreme events
- VaR only gives a threshold, not the magnitude beyond it
- CVaR captures the *average severity* of tail events

For example:
- σ might say "typical daily move is ±1%"
- VaR might say "95% of days, loss won't exceed 3%"
- CVaR says "when things go bad (worst 5% of days), average loss is 7%"

## What It Measures

The module quantifies the **fragility or robustness** of the strategy by measuring the number of "extreme events" the portfolio can withstand. It outputs a **dimensionless scalar** representing the "count" of tail risks covered by the current capital buffer.

**Interpretation:**
- **Solvency Distance = 3**: Portfolio can survive **three** consecutive average tail events before hitting the absorbing barrier
- **Solvency Distance = 0.5**: Portfolio can survive only **half** of one average tail event (critical danger)
- **Solvency Distance = 10**: Portfolio can survive **ten** average tail events (robust)

### Risk Classification

The metric provides actionable thresholds for decision-making:

| Zone | Distance Range | Interpretation | Action |
|------|---------------|----------------|--------|
| **Green** | > 5 | Safe – Can absorb 5+ tail events | Normal operations |
| **Yellow** | 3–5 | Warning – Can absorb 3-5 tail events | Reduce risk, monitor closely |
| **Red** | < 3 | Critical – Can absorb < 3 tail events | Immediate risk reduction required |
| **Critical** | < 1 | Emergency – Cannot survive 1 tail event | Emergency protocols, consider shutdown |

These thresholds can be customized based on:
- Risk tolerance
- Volatility regime
- Regulatory requirements
- Business continuity plans

## How It Measures

The metric functions by normalizing the capital buffer against the severity of tail risks:

### 1. Scale Definition
It defines the scale of a "disaster" not by mild variance, but by the CVaR, effectively budgeting for "earthquakes" rather than "rainy days."

**Traditional Approach:**
- Measures risk using daily volatility
- Focuses on typical market movements
- Can miss rare but catastrophic events

**Solvency Distance Approach:**
- Measures risk using tail events
- Focuses on extreme but realistic scenarios
- Explicitly accounts for catastrophic events

### 2. Boundary Calculation
It treats the absorbing barrier as a hard limit. If the distance ($u$) approaches zero, the strategy is flagged as "fragile," regardless of its historical returns or upside potential.

**Key Insight:** A strategy with excellent average returns but Solvency Distance < 1 is **fragile** and at risk of termination. The best performing strategy is worthless if it doesn't survive.

### 3. Survival Quantification
By dividing the buffer by the tail loss, the metric translates a monetary amount into a unit of survival (e.g., "3 units of safety"), allowing for intuitive "stop light" decision-making.

**Example:**
- Portfolio Value: $1,000,000
- Absorbing Barrier: $200,000 (maintenance margin)
- CVaR (95%): $150,000
- **Buffer:** $1,000,000 - $200,000 = $800,000
- **Solvency Distance:** $800,000 / $150,000 = **5.33**

**Interpretation:** The portfolio can survive approximately **5 tail events** before hitting the margin call.

### 4. Dynamic Monitoring
The metric should be recalculated continuously as:
- Portfolio value changes
- Market volatility evolves
- CVaR estimate updates with new data

**Workflow:**
1. Calculate current capital buffer daily
2. Update CVaR estimate (rolling window or regime-dependent)
3. Compute Solvency Distance
4. Check against thresholds
5. Trigger alerts or actions if entering yellow/red zones

## Data Requirements

To calculate the Solvency Distance, the module requires the following specific data inputs:

### 1. Current Account Health
The real-time marked-to-market value of the portfolio or strategy equity.

**Source:**
- Trading account balance
- Portfolio management system
- Real-time pricing feeds

**Frequency:** As frequent as possible; minimum daily

### 2. Absorbing Barrier Definition
A pre-determined threshold value representing the "unrecoverable state."

**Options:**
- **Zero Capital:** Total loss (account value = $0)
- **Maintenance Margin Requirement:** Liquidation level for leveraged accounts
- **Regulatory Capital Minimum:** Required by financial regulations
- **Operational Minimum:** Minimum needed for continued operations

**Specification:** Must be defined clearly in advance and updated if circumstances change

### 3. PnL Distribution Data
A dataset of historical Profit and Loss (PnL) returns or simulated scenario inputs. This data is used to calculate the statistical tail risk.

**Requirements:**
- **Granularity:** Daily or higher frequency preferred
- **History:** Sufficient to capture extreme events (minimum 1 year, preferably 3-5 years)
- **Quality:** Must include actual tail events, not just calm periods
- **Format:** Returns or dollar PnL values

**Sources:**
- Historical trading data
- Backtesting results
- Stress test scenarios
- Monte Carlo simulations

**Important:** The dataset must be sufficiently granular to capture fat-tailed events. Using only "normal" periods will underestimate CVaR and overestimate Solvency Distance, creating a false sense of security.

### 4. Confidence Level Parameter
The specific alpha ($\alpha$) level at which to calculate the CVaR, determining which portion of the tail is considered an "extreme event."

**Common Values:**
- **95% (α = 0.95):** Captures worst 5% of events – more conservative
- **99% (α = 0.99):** Captures worst 1% of events – very conservative
- **90% (α = 0.90):** Captures worst 10% of events – less conservative

**Recommendation:** Use 95% as a baseline. Increase to 99% for highly critical systems or where consequences of ruin are severe.

**Trade-off:**
- Higher α → fewer events in tail → higher CVaR → lower Solvency Distance (more conservative)
- Lower α → more events in tail → lower CVaR → higher Solvency Distance (less conservative)

### 5. Optional: Additional Context
For enhanced analysis, the following data can improve the metric:

- **VaR Threshold:** To compare against CVaR
- **Current Volatility:** To detect regime changes
- **Historical Maximum Drawdown:** To calibrate CVaR
- **Leverage Ratio:** To adjust barrier level

## Implementation Details

### CPU Implementation
The CPU version (`calculate_cpu`) provides:
- Single-scenario calculation
- Reference implementation for validation
- Suitable for low-frequency monitoring

### GPU Implementation
The GPU version (`calculate_gpu` and `calculate_gpu_batch`) provides:
- Massive parallelization for batch calculations
- Real-time portfolio-level monitoring
- Monte Carlo scenario analysis
- High-frequency recalculation

**Use Cases:**
- Real-time monitoring of multiple strategies
- Scenario analysis (1000s of simulations)
- Portfolio optimization under solvency constraints
- Stress testing across parameter spaces

### Configuration
The `SolvencyDistanceConfig` allows customization of thresholds:

```cpp
SolvencyDistanceConfig config;
config.green_threshold = 5.0f;      // Safe zone
config.yellow_threshold = 3.0f;     // Warning zone
config.red_threshold = 1.0f;        // Critical zone
```

Thresholds can be adjusted based on:
- Risk appetite
- Volatility regime
- Regulatory requirements
- Recovery capabilities

## Usage Example

### Basic Calculation

```cpp
#include "solvency_distance.h"

// Define parameters
SolvencyDistanceParameters params;
params.current_equity = 1000000.0f;        // $1M current value
params.absorbing_barrier = 200000.0f;      // $200K margin call
params.cvar_scale = 150000.0f;             // $150K CVaR (95%)
params.confidence_level = 0.95f;           // 95% confidence

// Create calculator
SolvencyDistance calculator;

// Calculate on CPU
auto result = calculator.calculate_cpu(params);

// Check results
if (result.is_critical) {
    std::cout << "CRITICAL: Solvency Distance = " 
              << result.solvency_distance << std::endl;
    // Trigger emergency protocols
} else if (result.is_fragile) {
    std::cout << "WARNING: Solvency Distance = " 
              << result.solvency_distance << std::endl;
    // Reduce risk exposure
} else {
    std::cout << "SAFE: Solvency Distance = " 
              << result.solvency_distance << std::endl;
    // Normal operations
}
```

### Batch Processing (GPU)

```cpp
// Create array of scenarios
std::vector<SolvencyDistanceParameters> scenarios(1000);
// ... populate scenarios ...

// Calculate on GPU
auto results = calculator.calculate_gpu_batch(scenarios.data(), scenarios.size());

// Analyze results
for (const auto& result : results) {
    if (result.is_critical) {
        // Handle critical cases
    }
}
```

## Integration with Other Metrics

Solvency Distance should be used in conjunction with other metrics:

1. **Risk of Ruin (RoR):** Provides probabilistic complement to distance metric
2. **Absorbing Barrier:** Provides detailed stopping time and hazard rate analysis
3. **CVaR:** Provides the unit of measurement
4. **Maximum Drawdown:** Validates historical worst-case scenarios

## Limitations and Considerations

1. **CVaR Estimation Quality:** Solvency Distance is only as good as the CVaR estimate. Poor data or inadequate tail sampling will lead to overestimation of safety.

2. **Static Barrier Assumption:** The metric assumes a fixed absorbing barrier. In reality, margin requirements or operational minimums may change.

3. **Independence Assumption:** The metric treats each CVaR-scale event as independent. In reality, extreme events often cluster (volatility clustering, contagion effects).

4. **Historical vs. Forward-Looking:** CVaR is typically estimated from historical data, which may not reflect future tail risk.

5. **Regime Changes:** The metric should be recalcrated when entering new volatility regimes or market conditions.

## Best Practices

1. **Regular Recalculation:** Update at least daily, more frequently during volatile periods
2. **Conservative CVaR:** Use high confidence levels (95-99%) and include stress scenarios
3. **Dynamic Thresholds:** Adjust thresholds based on current volatility regime
4. **Pre-defined Actions:** Establish clear protocols for yellow and red zones
5. **Complementary Metrics:** Use alongside RoR, CVaR, and drawdown metrics
6. **Backtesting:** Validate CVaR estimates against actual tail events
7. **Stress Testing:** Simulate extreme scenarios beyond historical data

## References

- Taleb, N. N. (2007). *The Black Swan: The Impact of the Highly Improbable*
- Taleb, N. N. (2018). *Skin in the Game: Hidden Asymmetries in Daily Life*
- Peters, O., & Gell-Mann, M. (2016). "Evaluating gambles using dynamics"
- Acerbi, C., & Tasche, D. (2002). "Expected Shortfall: A natural coherent alternative to Value at Risk"

## See Also

- [Risk of Ruin (RoR)](RoR.md)
- [Absorbing Barrier / Ruin State](../README.md)
- [Survival Probability](SURVIVAL-PROBABILITY.md)
- [Structural-Ruin Implementation](../../../src/core/Structural-Ruin/)

# Drawdown & Pain (Lens 4) — Deprecated

**This file has been split into individual metric files. Please see:**

- [Maximum Drawdown (MDD)](MAXIMUM-DRAWDOWN.md)
- [Average Drawdown & Duration](AVERAGE-DRAWDOWN-DURATION.md)
- [Ulcer Index (UI)](ULCER-INDEX.md)
- [Overview & Integration](README.md)

---

## Archived Content Below

### 1. Maximum Drawdown (MDD)

### Philosophy and Concepts

Maximum Drawdown (MDD) is a metric designed to quantify the severity of the worst-case "pain" experienced by a portfolio over a specific period. Unlike volatility metrics that view risk as general fluctuation, MDD views risk through the lens of **loss magnitude**. 

The core insight is that in financial markets with "fat tails" (where extreme events occur more frequently than standard models predict), deep declines are not rare anomalies but **structural realities**. The concept focuses on the **peak-to-trough excursion**, measuring the deepest hole the equity curve fell into before recovering.

**Key Principle:** If you had bought at the absolute worst possible time (the peak) and sold at the absolute worst possible outcome (the subsequent trough), MDD is what you would have lost.

### Mathematical Formulation

The MDD is calculated by identifying the maximum drop in value from a historical peak. For a time series of prices or equity values $S$ observed over $n$ time steps:

$$
\text{MDD} = \max_{i \in (0, n)} \left( S_i - \min_{j \in (i, n)} S_j \right)
$$

Where:
- $S_i$ is the peak value at time $i$
- $\min_{j \in (i, n)} S_j$ is the lowest value (trough) occurring at any time $j$ after time $i$

In many applications, this is converted to a percentage to standardize the metric across different capital sizes:

$$
\text{MDD (\%)} = \frac{\text{Peak Value} - \text{Trough Value}}{\text{Peak Value}}
$$

### What It Measures

The metric measures the **largest single losing period** experienced during the observation window. It defines the **worst-case scenario** for an investor who:
- Entered at the absolute highest peak
- Exited at the absolute lowest trough

It effectively **ignores the frequency of small losses** and focuses entirely on the **depth of the most significant capital erosion**.

### How It Measures

The algorithm works as follows:

1. **Scan Phase:** Traverse the entire equity curve from beginning to end
2. **Track Maximum:** Maintain a "running high water mark" representing the highest value seen so far
3. **Compute Drawdown:** At each point, calculate the decline from the running high
4. **Record Maximum:** Keep track of the largest decline observed and note:
   - The peak index where this maximum occurred
   - The trough index (lowest point after that peak)
   - Peak and trough values
5. **Recovery Tracking:** Identify whether the portfolio recovered to the peak value before the end of the period

**Efficiency:** The algorithm runs in $O(n)$ time with a single pass through the data.

### Data Requirements

1. **Time-Series Data:** A historical record of portfolio equity values or asset prices at consistent intervals (daily, hourly, etc.)
2. **Time Window:** Clearly defined start and end points
3. **Data Quality:** All values must be positive (equity curves cannot have negative values)

### Example

```
Equity Curve: [100, 120, 110, 80, 70, 90, 95, 100, 115]
         Peak:  100, 120, 120,120,120,120,120, 120, 120
        Trough:              70
          MDD: (120 - 70) = 50 or 41.67%
      Peak Index: 1 (value 120)
    Trough Index: 4 (value 70)
  Time to Recovery: 3 periods (index 7 first exceeds 120)
```

### Interpretation

| MDD Range | Severity | Interpretation |
|-----------|----------|----------------|
| 0-10% | Mild | Minor drawdowns; strategy exhibits good resilience |
| 10-20% | Moderate | Significant but manageable declines |
| 20-40% | Severe | Substantial losses; psychological tolerance required |
| 40-60% | Critical | Extreme declines; most retail investors cannot endure |
| > 60% | Catastrophic | Near-total capital loss; strategy failure |

### Limitations

- **Static Perspective:** Focuses only on the worst pair of points; does not capture multiple drawdown events
- **No Recovery Time:** Does not indicate how long recovery took
- **No Frequency:** Cannot distinguish between one catastrophic event and many moderate ones
- **Historical Bias:** Cannot predict future drawdowns; based on past observations

---

## 2. Average Drawdown & Drawdown Duration

### Philosophy and Concepts

While Maximum Drawdown measures the **acute shock** of a single worst-case event, Average Drawdown and Duration measure **chronic stress**. 

The philosophy here is that the **longevity of being underwater**—the duration of pain—often causes more psychological damage and operational risk than the depth of the loss itself. A strategy that frequently dips and takes months to recover is psychologically draining and operationally risky, even if it never hits a catastrophic maximum drawdown.

These metrics answer practical questions:
- **What is the typical drawdown I should expect?** (Average Drawdown)
- **How long will I wait in a losing position?** (Average Duration)

### Mathematical Formulation

#### Average Drawdown

Let $d$ be the total number of distinct drawdown events found in the data. Average Drawdown is the arithmetic mean of the size of all drawdowns:

$$
\text{Avg DD} = \frac{1}{d} \sum_{i=1}^{d} \text{DD}_i
$$

Where $\text{DD}_i$ is the magnitude (percentage or value) of the $i$-th drawdown.

#### Average Drawdown Duration

This calculates the mean time required to recover from each drawdown:

$$
\text{Avg Duration} = \frac{1}{d} \sum_{i=1}^{d} (\text{Time of Recovery}_i - \text{Time of Peak}_i)
$$

The recovery time is the number of periods from the peak (start of drawdown) until the equity curve exceeds or equals that peak value.

### What It Measures

**Average Drawdown:** 
- The typical "hit" the portfolio takes
- Indicates the standard severity of negative periods
- Combined with frequency, provides a stress profile

**Average Duration:**
- The "time cost" of losses
- Quantifies how long capital is tied up in a loss state
- Reflects the waiting period before breaking even

**Chronic Pain Index:**
- `pain_frequency = total_periods_underwater / total_periods`
- Indicates what fraction of time is spent in drawdown
- High frequency (>30%) indicates chronic stress

### How It Measures

The algorithm:

1. **Event Identification:** Parse the equity curve to isolate every distinct instance where value dropped below a previous high-water mark
2. **Event Recording:** For each instance, record:
   - Depth of the drop (drawdown magnitude)
   - Time elapsed from peak until recovery to at least that peak level
3. **Aggregation:** Sum all values and divide by event count to compute averages
4. **Pain Frequency:** Calculate the fraction of total periods spent underwater

**Example:**

```
Equity Curve: [100, 120, 110, 100, 95, 110, 115, 110, 105, 120]

Event 1: Peak 120 (index 1) → Trough 95 (index 4) → Recovery 110 (index 5)
  Magnitude: 25 (or 20.8%)
  Duration: 4 periods

Event 2: Peak 115 (index 6) → Trough 105 (index 8) → No Recovery by end
  Magnitude: 10 (or 8.7%)
  Duration: 4 periods (index 9 does not exceed 115)

Average DD: (25 + 10) / 2 = 17.5
Avg Duration: (4 + 4) / 2 = 4 periods
Pain Frequency: 6 underwater periods / 9 total = 66.7% (very high!)
```

### Data Requirements

1. **Timestamped Equity Curve:** Time series with corresponding dates/times
2. **High-Water Mark Tracking:** Algorithmic ability to distinguish temporary dips from full recovery
3. **Event Boundary Definition:** Clear rules for when a drawdown starts and ends

### Interpretation

| Metric | Low (Good) | Moderate | High (Concerning) |
|--------|-----------|----------|------------------|
| Avg DD | < 5% | 5-15% | > 15% |
| Avg Duration | < 10 periods | 10-30 periods | > 30 periods |
| Pain Frequency | < 10% | 10-30% | > 30% |

High average duration combined with high frequency is a red flag: the strategy spends most of its time fighting to recover.

---

## 3. Ulcer Index (UI)

### Philosophy and Concepts

The Ulcer Index was developed by Dr. Peter Halley to address the shortcomings of **standard deviation** as a risk metric. Standard deviation treats **upward gains and downward losses as equal "risk,"** which contradicts the reality that:
- Investors **fear losses** but **welcome gains**
- Risk should only penalize downside moves

The Ulcer Index operates on the principle of **"experienced pain."** It is a **downside-only measure** that penalizes severity **disproportionately**. By squaring the drawdowns, the index ensures that:
- Deep, long-lasting recessions contribute significantly more to the risk score
- Minor, short-lived dips contribute minimally
- The mathematical score aligns with the **psychological stress** of an investor

**Key Insight:** Ulcer Index treats every underwater period as a "wound" and compounds the pain based on how deep underwater you are.

### Mathematical Formulation

The UI is calculated as the **Root Mean Square (RMS)** of percentage drawdowns:

$$
\text{UI} = \sqrt{\frac{1}{n} \sum_{i=1}^{n} D_i^2}
$$

Where:
- $D_i$ is the percentage drawdown at time $i$ (0 if not underwater)
- $D_i = \frac{\text{Current Value} - \text{Running High}}{\text{Running High}} \times 100$
- $n$ is the total number of observations in the period

**Key Steps:**

1. **Track Running High:** Maintain the highest historical value seen up to each point
2. **Calculate Drawdown:** At each time step, compute the percentage distance from running high
3. **Square Each Drawdown:** Amplify the penalty for deep drops
4. **Average Squares:** Divide by total number of observations
5. **Take Square Root:** Return to percentage scale for interpretability

### What It Measures

The Ulcer Index measures the **severity and frequency of downward volatility**. It provides a single composite score representing:
- The "depth of the ulcer" or intensity of pain
- Time spent underwater
- Severity of being underwater

A higher UI indicates a strategy that:
- Spends significant time deep underwater
- Experiences severe declines regularly
- Creates psychological stress for investors

### How It Measures

**Core Algorithm:**

1. **Initialize:** `running_high = first_equity_value`
2. **For each subsequent period:**
   - If `current_value > running_high`: update `running_high`
   - Calculate `DD_pct = (current_value - running_high) / running_high`
   - If `DD_pct < 0` (underwater): add `DD_pct^2` to accumulator
3. **Compute UI:** `UI = sqrt(sum_of_squares / total_periods)`

**Why Squaring Works:**

- A 10% drawdown contributes: $10^2 = 100$ to the sum
- A 5% drawdown contributes: $5^2 = 25$ to the sum
- The 10% drawdown contributes **4 times more** than the 5% drawdown

This non-linear weighting reflects psychological reality: losing 10% feels far worse than twice as bad as losing 5%.

### Data Requirements

1. **Time-Series Data:** Complete history of portfolio values or prices
2. **Running High Calculation:** System must track historical maximum dynamically
3. **Consistent Frequency:** Data points should be at regular intervals

### Example

```
Equity Curve: [100, 105, 95, 90, 92, 98, 102, 98, 96, 100]
Running High:  100, 105,105,105,105,105, 105,105,105, 105

Drawdown %:     0,   0, -9.5, -14.3, -12.4, -6.7, -2.9, -6.7, -8.6, 0

Squared DD:     0,   0, 90.25, 204.49, 153.76, 44.89, 8.41, 44.89, 73.96, 0

UI = sqrt(620.65 / 10) = sqrt(62.065) ≈ 7.88%
```

Interpretation: The portfolio experienced an average "pain" equivalent to being 7.88% underwater (RMS of all underwater periods).

### Interpretation

| UI Value | Severity | Interpretation |
|----------|----------|----------------|
| 0-5 | Minimal | Strategy exhibits excellent downside control |
| 5-10 | Low | Manageable drawdown experience |
| 10-15 | Moderate | Moderate psychological stress; acceptable for many |
| 15-25 | High | Significant chronic pain; demanding strategy |
| > 25 | Severe | Extreme psychological stress; few investors tolerate |

### Why UI > Standard Deviation

**Example:**
```
Strategy A: +50%, -50%, +50%, -50% (highly volatile but symmetric)
Strategy B: 0%, 0%, 0%, -100% (total loss but low variance until the end)

Std Dev of A: ~51.8%
Std Dev of B: ~50% (treats the -100% the same as others)

UI of A: Can recover from each drawdown
UI of B: UI spikes to 100 (near-total loss) → reflects true risk
```

Standard deviation doesn't distinguish between upside and downside. UI does.

---

## Integrated Usage: The Drawdown-Pain Framework

These three metrics work together to provide a complete picture of drawdown risk:

| Metric | Answers | Best For |
|--------|---------|----------|
| **MDD** | "What is the worst-case scenario?" | Risk limits, tail risk management |
| **Avg DD & Duration** | "What is typical stress? How long do I wait?" | Operational resilience, investor tolerance |
| **UI** | "What is total experienced pain?" | Psychological assessment, strategy comparison |

### Decision Framework

```
1. Calculate MDD
   └─ If MDD > 40%: High risk, consider risk reduction
   
2. Calculate Avg DD & Duration
   └─ If Avg Duration > 30 periods: High time cost
   └─ If Pain Frequency > 30%: Chronic stress warning
   
3. Calculate UI
   └─ If UI > 15: Severe pain; recalibrate strategy
   └─ If UI trending up: Regime shift; volatility increasing
   
4. Act on findings:
   ├─ Red flag (MDD>40% AND UI>15): Emergency protocols
   ├─ Yellow flag (Multiple moderate signals): Reduce exposure
   └─ Green flag: Normal operations
```

---

## Data Requirements (All Three Metrics)

To implement all Lens 4 metrics, provide:

1. **Equity Curve Time Series**
   - Historical marked-to-market portfolio values
   - Consistent frequency (daily minimum recommended)
   - Sufficient history (1-5 years for robust statistics)
   - High data quality (no gaps, proper forward-fill or interpolation)

2. **Time Alignment**
   - Timestamps aligned with market close or strategy reporting frequency
   - Clear start/end boundaries
   - No duplicate timestamps

3. **Value Format**
   - All positive (equity curves cannot be negative)
   - Consistent currency/units
   - Representative of actual account value

---

## Implementation Characteristics

### CPU Implementation
- Single-curve calculation
- Reference implementation
- Suitable for low-frequency monitoring

### GPU Implementation
- Massive parallelization
- Batch processing of thousands of curves
- Real-time monitoring
- Scenario analysis

**Typical Use Cases:**
- Real-time strategy monitoring (1000s of strategies)
- Portfolio optimization under drawdown constraints
- Stress testing across parameter grids
- Monte Carlo scenario analysis

---

## Best Practices

1. **Recalculate Frequently:** Update at least daily, more frequently during volatile periods
2. **Use Rolling Windows:** Track both lifetime and recent (30/60/90-day) metrics
3. **Set Thresholds:** Establish clear action levels before trading
4. **Combine Metrics:** Use MDD for extremes, Avg for typical, UI for chronic
5. **Historical Validation:** Backtesting with these metrics improves strategy robustness
6. **Regime Detection:** Monitor for shifts in drawdown patterns (indicator of regime change)
7. **Benchmark:** Compare against relevant benchmarks and peer strategies

---

## References

- Halley, Peter. (1989). "The Ulcer Index – A Risk Measure That Actually Works"
- Taleb, N. N. (2007). *The Black Swan: The Impact of the Highly Improbable*
- Peters, O., & Gell-Mann, M. (2016). "Evaluating gambles using dynamics"
- Pye, Gordon. (2000). "Drawdown Distributions and the Management of Tail Risk"

## See Also

- [Structural-Ruin / Risk of Ruin](../Structural-Ruin/)
- [Volatility & Noise](../Volatility-Noise/)
- [Downside & Tail Risk](../Downside-Tail/)
- [Drawdown-Pain Implementation](../../../src/core/Drawdown-Pain/)

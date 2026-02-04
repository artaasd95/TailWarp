# Maximum Drawdown (MDD)

## Philosophy and Concepts

Maximum Drawdown (MDD) is a metric designed to quantify the severity of the worst-case "pain" experienced by a portfolio over a specific period. Unlike volatility metrics that view risk as general fluctuation, MDD views risk through the lens of **loss magnitude**. 

The core insight is that in financial markets with "fat tails" (where extreme events occur more frequently than standard models predict), deep declines are not rare anomalies but **structural realities**. The concept focuses on the **peak-to-trough excursion**, measuring the deepest hole the equity curve fell into before recovering.

**Key Principle:** If you had bought at the absolute worst possible time (the peak) and sold at the absolute worst possible outcome (the subsequent trough), MDD is what you would have lost.

## Mathematical Formulation

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

## What It Measures

The metric measures the **largest single losing period** experienced during the observation window. It defines the **worst-case scenario** for an investor who:
- Entered at the absolute highest peak
- Exited at the absolute lowest trough

It effectively **ignores the frequency of small losses** and focuses entirely on the **depth of the most significant capital erosion**.

## How It Measures

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

## Data Requirements

1. **Time-Series Data:** A historical record of portfolio equity values or asset prices at consistent intervals (daily, hourly, etc.)
2. **Time Window:** Clearly defined start and end points
3. **Data Quality:** All values must be positive (equity curves cannot have negative values)

## Example

```
Equity Curve: [100, 120, 110, 80, 70, 90, 95, 100, 115]
         Peak:  100, 120, 120,120,120,120,120, 120, 120
        Trough:              70
          MDD: (120 - 70) = 50 or 41.67%
      Peak Index: 1 (value 120)
    Trough Index: 4 (value 70)
  Time to Recovery: 3 periods (index 7 first exceeds 120)
```

## Interpretation

| MDD Range | Severity | Interpretation |
|-----------|----------|----------------|
| 0-10% | Mild | Minor drawdowns; strategy exhibits good resilience |
| 10-20% | Moderate | Significant but manageable declines |
| 20-40% | Severe | Substantial losses; psychological tolerance required |
| 40-60% | Critical | Extreme declines; most retail investors cannot endure |
| > 60% | Catastrophic | Near-total capital loss; strategy failure |

## Limitations

- **Static Perspective:** Focuses only on the worst pair of points; does not capture multiple drawdown events
- **No Recovery Time:** Does not indicate how long recovery took
- **No Frequency:** Cannot distinguish between one catastrophic event and many moderate ones
- **Historical Bias:** Cannot predict future drawdowns; based on past observations

## Implementation

The MaximumDrawdown class provides CPU and GPU implementations:

```cpp
#include "maximum_drawdown.h"

// Single calculation
MaximumDrawdown calculator;
MaximumDrawdownParameters params;
params.equity_curve = curve_data;
params.curve_length = 1000;
params.use_percentage = true;

auto result = calculator.calculate_cpu(params);
std::cout << "MDD: " << result.mdd_value << "%\n";
std::cout << "Peak at index: " << result.peak_index << "\n";
std::cout << "Trough at index: " << result.trough_index << "\n";
std::cout << "Recovery: " << (result.fully_recovered ? "Yes" : "No") << "\n";
```

## See Also

- [Average Drawdown & Duration](AVERAGE-DRAWDOWN-DURATION.md)
- [Ulcer Index](ULCER-INDEX.md)
- [Drawdown & Pain Overview](README.md)

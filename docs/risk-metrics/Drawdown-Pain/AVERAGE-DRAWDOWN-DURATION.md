# Average Drawdown & Drawdown Duration

## Philosophy and Concepts

While Maximum Drawdown measures the **acute shock** of a single worst-case event, Average Drawdown and Duration measure **chronic stress**. 

The philosophy here is that the **longevity of being underwater**—the duration of pain—often causes more psychological damage and operational risk than the depth of the loss itself. A strategy that frequently dips and takes months to recover is psychologically draining and operationally risky, even if it never hits a catastrophic maximum drawdown.

These metrics answer practical questions:
- **What is the typical drawdown I should expect?** (Average Drawdown)
- **How long will I wait in a losing position?** (Average Duration)

## Mathematical Formulation

### Average Drawdown

Let $d$ be the total number of distinct drawdown events found in the data. Average Drawdown is the arithmetic mean of the size of all drawdowns:

$$
\text{Avg DD} = \frac{1}{d} \sum_{i=1}^{d} \text{DD}_i
$$

Where $\text{DD}_i$ is the magnitude (percentage or value) of the $i$-th drawdown.

### Average Drawdown Duration

This calculates the mean time required to recover from each drawdown:

$$
\text{Avg Duration} = \frac{1}{d} \sum_{i=1}^{d} (\text{Time of Recovery}_i - \text{Time of Peak}_i)
$$

The recovery time is the number of periods from the peak (start of drawdown) until the equity curve exceeds or equals that peak value.

## What It Measures

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

## How It Measures

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

## Data Requirements

1. **Timestamped Equity Curve:** Time series with corresponding dates/times
2. **High-Water Mark Tracking:** Algorithmic ability to distinguish temporary dips from full recovery
3. **Event Boundary Definition:** Clear rules for when a drawdown starts and ends

## Interpretation

| Metric | Low (Good) | Moderate | High (Concerning) |
|--------|-----------|----------|------------------|
| Avg DD | < 5% | 5-15% | > 15% |
| Avg Duration | < 10 periods | 10-30 periods | > 30 periods |
| Pain Frequency | < 10% | 10-30% | > 30% |

High average duration combined with high frequency is a red flag: the strategy spends most of its time fighting to recover.

## Implementation

The AverageDrawdownDuration class provides CPU and GPU implementations:

```cpp
#include "average_drawdown_duration.h"

AverageDrawdownDuration calculator;
AverageDrawdownDurationParameters params;
params.equity_curve = curve_data;
params.curve_length = 1000;
params.use_percentage = true;

auto result = calculator.calculate_cpu(params);
std::cout << "Average Drawdown: " << result.average_drawdown << "%\n";
std::cout << "Average Duration: " << result.average_duration << " periods\n";
std::cout << "Pain Frequency: " << result.pain_frequency * 100 << "%\n";
std::cout << "Total Events: " << result.total_drawdown_events << "\n";

if (result.frequent_pain) {
    std::cout << "WARNING: Strategy exhibits chronic stress\n";
}
```

## See Also

- [Maximum Drawdown](MAXIMUM-DRAWDOWN.md)
- [Ulcer Index](ULCER-INDEX.md)
- [Drawdown & Pain Overview](README.md)

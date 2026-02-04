# Ulcer Index (UI)

## Philosophy and Concepts

The Ulcer Index was developed by Dr. Peter Halley to address the shortcomings of **standard deviation** as a risk metric. Standard deviation treats **upward gains and downward losses as equal "risk,"** which contradicts the reality that:
- Investors **fear losses** but **welcome gains**
- Risk should only penalize downside moves

The Ulcer Index operates on the principle of **"experienced pain."** It is a **downside-only measure** that penalizes severity **disproportionately**. By squaring the drawdowns, the index ensures that:
- Deep, long-lasting recessions contribute significantly more to the risk score
- Minor, short-lived dips contribute minimally
- The mathematical score aligns with the **psychological stress** of an investor

**Key Insight:** Ulcer Index treats every underwater period as a "wound" and compounds the pain based on how deep underwater you are.

## Mathematical Formulation

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

## What It Measures

The Ulcer Index measures the **severity and frequency of downward volatility**. It provides a single composite score representing:
- The "depth of the ulcer" or intensity of pain
- Time spent underwater
- Severity of being underwater

A higher UI indicates a strategy that:
- Spends significant time deep underwater
- Experiences severe declines regularly
- Creates psychological stress for investors

## How It Measures

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

## Data Requirements

1. **Time-Series Data:** Complete history of portfolio values or prices
2. **Running High Calculation:** System must track historical maximum dynamically
3. **Consistent Frequency:** Data points should be at regular intervals

## Example

```
Equity Curve: [100, 105, 95, 90, 92, 98, 102, 98, 96, 100]
Running High:  100, 105,105,105,105,105, 105,105,105, 105

Drawdown %:     0,   0, -9.5, -14.3, -12.4, -6.7, -2.9, -6.7, -8.6, 0

Squared DD:     0,   0, 90.25, 204.49, 153.76, 44.89, 8.41, 44.89, 73.96, 0

UI = sqrt(620.65 / 10) = sqrt(62.065) ≈ 7.88%
```

Interpretation: The portfolio experienced an average "pain" equivalent to being 7.88% underwater (RMS of all underwater periods).

## Interpretation

| UI Value | Severity | Interpretation |
|----------|----------|----------------|
| 0-5 | Minimal | Strategy exhibits excellent downside control |
| 5-10 | Low | Manageable drawdown experience |
| 10-15 | Moderate | Moderate psychological stress; acceptable for many |
| 15-25 | High | Significant chronic pain; demanding strategy |
| > 25 | Severe | Extreme psychological stress; few investors tolerate |

## Why UI > Standard Deviation

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

## Implementation

The UlcerIndex class provides CPU and GPU implementations:

```cpp
#include "ulcer_index.h"

UlcerIndex calculator;
UlcerIndexParameters params;
params.equity_curve = curve_data;
params.curve_length = 1000;

auto result = calculator.calculate_cpu(params);
std::cout << "Ulcer Index: " << result.ulcer_index << "\n";
std::cout << "Pain Intensity Score: " << result.pain_intensity_score << "/100\n";
std::cout << "Average Drawdown Depth: " << result.average_drawdown_depth << "%\n";
std::cout << "Max Underwater: " << result.max_underwater_percentage << "%\n";
std::cout << "Time Underwater: " << result.percentage_time_underwater * 100 << "%\n";

if (result.is_high_pain) {
    std::cout << "WARNING: UI > 15, high chronic pain detected\n";
}
```

## Batch Processing (GPU)

```cpp
// Process multiple equity curves in parallel
std::vector<UlcerIndexParameters> curves(100);
// ... populate curves ...

auto results = calculator.calculate_gpu_batch(curves.data(), curves.size());

// Analyze results
for (const auto& result : results) {
    if (result.is_high_pain) {
        // Handle strategies with high pain
    }
}
```

## See Also

- [Maximum Drawdown](MAXIMUM-DRAWDOWN.md)
- [Average Drawdown & Duration](AVERAGE-DRAWDOWN-DURATION.md)
- [Drawdown & Pain Overview](README.md)

# Recovery and Resilience Metrics

## Philosophy and Concepts

Recovery metrics evaluate performance through the lens of **capital impairment and time spent underwater**, rather than return volatility. The focus is on the real investor experience: how deeply capital falls, how long recovery takes, and whether the system can realistically recover from losses.

These measures emphasize **survivability and capital regeneration**, not only profitability. They answer three critical questions:

1. **Calmar Ratio**: "How much return am I earning per unit of worst-case loss?"
2. **Recovery Time**: "How long am I stuck underwater after a peak?"
3. **Recovery Factor**: "How many times have I earned back my worst loss?"

---

## Calmar Ratio

### Concept

The Calmar Ratio measures **return earned per unit of worst historical loss**. Instead of treating risk as statistical fluctuation (variance or standard deviation), risk is defined as **actual realized capital damage**, captured by Maximum Drawdown (MDD).

This aligns with the philosophy that:

* Investors fail due to **large losses**, not small fluctuations
* Capital destruction is more relevant than volatility
* The worst loss is the true constraint on survival

The metric therefore evaluates how efficiently a strategy compensates for the most severe historical decline.

### What it Measures

* Return efficiency relative to capital damage
* Reward per unit of drawdown pain
* Whether returns justify the worst observed loss

Higher values indicate:
* Strong returns with controlled drawdowns
* Faster compounding with limited capital impairment

Lower values indicate:
* Excessive losses relative to gains
* Fragile performance that may be psychologically or financially unsustainable

### Mathematical Definition

#### Annualized Return

Let $V_0$ be initial equity and $V_T$ be final equity after $T$ years.

$$
\text{Annualized Return} = \left(\frac{V_T}{V_0}\right)^{1/T} - 1
$$

This converts total growth into a yearly compounded rate.

#### Maximum Drawdown (MDD)

Let $E_t$ be the equity curve.

Define the running peak:

$$
P_t = \max_{s \le t} E_s
$$

Drawdown at time $t$:

$$
D_t = \frac{P_t - E_t}{P_t}
$$

Maximum Drawdown:

$$
\text{MDD} = \max_t D_t \times 100\%
$$

This represents the largest peak-to-trough percentage loss observed.

#### Calmar Ratio Formula

$$
\text{Calmar Ratio} = \frac{\text{Annualized Return (\%)}}{\text{Maximum Drawdown (\%)}}
$$

### Interpretation

| Calmar Ratio | Interpretation |
|---|---|
| > 2.0 | Excellent risk-adjusted performance; strong return-to-drawdown efficiency |
| 1.0 - 2.0 | Acceptable; reasonable compensation for historical drawdowns |
| < 1.0 | Insufficient compensation for risk; drawdowns may exceed returns |
| Negative | Strategy produced net losses |

### Required Data

* Time series of portfolio equity or cumulative returns
* Initial and final capital
* Time period in years for annualization
* Historical peaks and troughs

No distributional assumptions are required.

### Usage

The Calmar Ratio is most useful for:
* **Strategy comparison**: Evaluating which strategy compensates best per unit of loss
* **Risk-adjusted performance**: Beyond Sharpe ratio or Sortino; emphasizes real drawdowns
* **Survivor assessment**: Strategies with low Calmar Ratios may be psychologically unsustainable

---

## Recovery Time

### Concept

Recovery Time measures **how long it takes to return to a new high after a drawdown begins**.

While drawdown magnitude measures loss size, recovery time measures **loss persistence**.

Long recovery periods:
* lock capital
* reduce compounding
* increase abandonment risk
* create psychological fatigue

In many cases, duration matters more than depth.

### What it Measures

* Average time spent below previous peak
* Worst-case recovery duration
* Number of distinct drawdown events
* Persistence of losses
* Speed of system healing

Short recovery times indicate resilience and consistent compounding.

### Mathematical Definition

For each drawdown event:

1. Identify peak time $t_p$
2. Identify trough $t_{tr}$
3. Identify recovery time $t_r$ where:

$$
E_{t_r} \geq E_{t_p}
$$

Recovery duration:

$$
\text{Recovery Time} = t_r - t_p
$$

Aggregate statistics:

* Mean recovery time (average across all events)
* Maximum recovery time (longest event)
* Number of drawdown events

### Interpretation

| Metric | Interpretation |
|---|---|
| Mean Recovery Time | Typical duration of capital impairment; lower is better |
| Max Recovery Time | Worst-case stress test; how long can investor endure? |
| Num Events | How frequently does the strategy experience drawdowns? |

**Example**: 
* Mean recovery time = 20 periods: on average, recovers in 20 bars
* Max recovery time = 120 periods: worst recovery took 120 bars
* Num events = 12: experienced 12 distinct drawdown cycles

### Required Data

* Timestamped equity curve
* Identification of peaks and recoveries
* Sequential ordering of returns

---

## Recovery Factor

### Concept

Recovery Factor measures **profit generated relative to the worst loss endured**. It quantifies the strategy's ability to "earn back" damage.

It answers: **How many times has the system repaid its worst drawdown through net profits?**

This reflects capital regeneration strength and robustness after shocks.

### What it Measures

* Earning power vs. historical damage
* Capacity to recover from extreme events
* Practical survivability
* How much "spare profit" exists beyond the worst loss

Higher values indicate that the strategy quickly rebuilds equity after losses.

Lower values indicate fragile recovery or potential capital stagnation.

### Mathematical Definition

Let:
* Net Profit $= V_T - V_0$
* MDD (absolute) as previously defined

$$
\text{Recovery Factor} = \frac{\text{Net Profit}}{\text{MDD (Absolute)}}
$$

Where MDD (Absolute) is the peak-to-trough loss in dollar (or unit) terms.

### Interpretation

| Recovery Factor | Interpretation |
|---|---|
| > 3-5 | Strong recovery capability; profit well exceeds worst loss |
| 1-3 | Acceptable; strategy has earned back its damage multiple times |
| < 1 | Weak recovery; total profit barely exceeds worst loss; risky |
| Negative | Strategy produced net loss; failed to recover damage |

**Example**:
* Initial capital = $100,000
* Final capital = $250,000
* Net Profit = $150,000
* Max Drawdown = $40,000
* Recovery Factor = $150,000 / $40,000 = **3.75**

This strategy has earned back its worst loss 3.75 times, indicating strong recovery capability.

### Required Data

* Initial capital
* Final capital
* Equity curve for drawdown calculation
* Total returns over period

---

## Measurement Philosophy

These metrics treat risk as:

* **realized capital loss** (not volatility)
* **time spent impaired** (not frequency of small moves)
* **recovery difficulty** (earning power after shocks)

They avoid volatility-based assumptions and instead focus on:

* worst-case events
* duration of stress
* survivability constraints

The system is considered healthy only if:

* drawdowns are limited (low MDD)
* recovery is fast (low recovery time)
* profits outweigh worst losses (high recovery factor)
* return-to-loss ratio is favorable (high Calmar ratio)

This framework ensures strategies remain both financially and psychologically sustainable under real trading conditions.

---

## Practical Guidance

### When to Use Each Metric

**Calmar Ratio**:
* Comparing strategies on a risk-adjusted basis
* Evaluating whether returns justify historical pain
* Assessing consistency of return generation relative to drawdowns

**Recovery Time**:
* Assessing psychological tolerance for drawdowns
* Evaluating capital lockup risk
* Comparing speed of healing across strategies
* Identifying "death spirals" (very long recovery times)

**Recovery Factor**:
* Understanding profitability relative to worst-case loss
* Assessing capital regeneration strength
* Evaluating risk-reward asymmetry
* Determining whether strategy can realistically recover from shocks

### Combined Assessment

For robust strategy evaluation, examine all three metrics together:

1. **Calmar Ratio**: Does return compensate for drawdown?
2. **Recovery Time**: How long is capital impaired?
3. **Recovery Factor**: How strong is recovery capability?

A healthy strategy exhibits:
* Calmar Ratio > 1.5
* Mean Recovery Time < 50 periods
* Max Recovery Time < 200 periods
* Recovery Factor > 2.0

---

## Limitations

* **Historical bias**: These metrics depend entirely on observed history; extreme future losses may exceed historical MDD
* **Time-horizon dependent**: Recovery time varies greatly by holding period
* **Annualization assumptions**: Calmar ratio assumes linear annualization (may not hold for non-stationary data)
* **No forward guidance**: None of these metrics predict future performance
* **Single worst-case**: Focuses on single worst drawdown; doesn't assess tail risk distribution
* **Path-dependent**: Recovery factor can be inflated by large gains after recovery

---

## Implementation Notes

### CPU vs GPU Calculation

Both CPU and GPU implementations are provided:

* **CPU**: Suitable for analysis, backtest optimization, parameter sweeps
* **GPU**: Suitable for real-time monitoring, high-frequency analysis, batch processing

GPU implementation provides identical results with hardware acceleration for large datasets.

### Data Requirements

* Equity curve must be **monotonically positive** (no negative equity)
* Time series should be **regularly sampled** (daily, hourly, etc.)
* **Sufficient history** needed for statistical validity (minimum 50-100 observations recommended)

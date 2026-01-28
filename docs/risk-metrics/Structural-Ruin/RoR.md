# Risk of Ruin (RoR)

## Conceptual Foundation

### The Core Philosophy: Survival over Utility

Traditional finance focuses on average returns, Sharpe ratios, and expected value. Risk of Ruin shifts this paradigm fundamentally by asking a different question:

**"Is this trade capable of killing me?"**

Rather than maximizing returns or minimizing variance, RoR prioritizes one thing above all else: **not going broke**.

### Why RoR Matters

In trading and investing, there exist **absorbing barriers** — points of no return:
- **Zero capital**: You can no longer trade
- **Margin call**: Your position is forcibly liquidated
- **Regulatory shutdown**: Your license is revoked
- **Fund closure**: Your fund is dissolved

Once you cross an absorbing barrier, the game ends permanently. You cannot average back up from zero. This is fundamentally different from other risk metrics that assume recovery is always possible.

### Path Dependence: Time Probability vs. Ensemble Probability

Standard risk models use **ensemble probability**: "In parallel universes, what happens to 100 traders?"

RoR uses **time probability**: "What happens to *you* over time?"

**Example:** 
- A strategy has a 50% daily loss probability
- Ensemble view: "Statistically, half the traders blow up"
- RoR view: "You will blow up with ~99.99% certainty if you trade long enough"

The order of losses matters critically. If you blow up on Day 28, the profits of Day 29 are irrelevant to your survival.

### The Lindy Effect

Your operational lifespan is directly proportional to your **distance to the absorbing barrier**:

$$\text{Expected Longevity} \propto \text{Current Capital}$$

More capital = longer time horizon. The closer you are to zero, the statistically shorter your life becomes.

---

## Mathematical Foundation: The Cramér-Lundberg Model

### The Surplus Process

The foundation of RoR theory is the **Cramér-Lundberg Model**, used in insurance mathematics to model solvency under repeated random shocks:

$$U(t) = u + ct - S(t)$$

Where:
- **$u$**: Initial capital (your safety buffer)
- **$ct$**: Drift term (steady income: theta decay, yield, edge)
- **$S(t)$**: Cumulative shock process (market losses)
- **$t$**: Time (trading periods)

### Interpreting the Surplus Process

Imagine your account balance as a dynamic graph:

1. **You start with capital $u$** (e.g., $100,000)
2. **Every period, you earn $c$** (your expected edge, theta, yield)
   - The account drifts upward at rate $c$
3. **Randomly, losses occur $S(t)$** (market crashes, drawdowns)
   - The account jumps downward

**The Central Question:** Will the downward jumps of $S(t)$ ever exceed your accumulated cushion ($u + ct$)?

**Ruin Condition:** Ruin occurs when:
$$\inf_{t \geq 0} U(t) < 0$$

In other words, at any point in time, does your account ever go negative?

### The Net Profit Condition (Prerequisite)

Before even calculating RoR, we must check if survival is possible:

$$c - \lambda\mu > 0$$

Where:
- **$c$**: Your expected return per period
- **$\lambda$**: Frequency of losses (e.g., 0.2 = 20% of trades are losses)
- **$\mu$**: Average magnitude of a loss (e.g., 0.05 = 5% loss)

**Critical Insight:** If your expected loss rate ($\lambda\mu$) exceeds your edge ($c$), you will go broke with **100% probability**, regardless of starting capital.

**Example:**
- Your edge: +1% per trade
- Loss frequency: 30% of trades result in loss
- Average loss magnitude: 5%
- Expected loss rate: 0.3 × 0.05 = 1.5%
- Verdict: 1.5% > 1% → **You are doomed**

Positive drift is a necessary but not sufficient condition for survival.

---

## The Lundberg Inequality: Practical Approximation

### The Exact Ruin Probability (Theoretical)

For the Cramér-Lundberg process, the exact ruin probability is complex to compute for arbitrary loss distributions. However, the **Lundberg Inequality** provides an upper bound:

$$\psi(u) \leq e^{-Ru}$$

Where **$R$** (the **Lundberg Adjustment Coefficient**) is the unique positive solution to:

$$\mathbb{E}[e^{RX}] = 1 + \frac{c}{\lambda\mu}$$

This means: "The moment-generating function of losses, evaluated at $R$, equals the adjusted net profit rate."

### Practical Approximation for Implementation

For trading systems, we cannot solve this equation exactly for arbitrary distributions. Instead, we use a simplified approximation assuming Gamma or Exponential loss distributions:

$$R \approx \frac{2 \cdot \text{Mean Return}}{\text{Variance}}$$

Where:
- **Mean Return** ($\mu$): Average PnL per period
- **Variance** ($\sigma^2$): Variance of PnL distribution

**Why this works:** This approximation captures the essential risk-reward tradeoff:
- Higher mean return → Higher $R$ → Lower ruin risk
- Higher variance → Lower $R$ → Higher ruin risk

### The Ruin Probability

Given the Lundberg Adjustment Coefficient $R$, the ruin probability is:

$$\psi(u) = e^{-R \cdot u}$$

Where $u$ is current capital.

**Interpretation:**
- **Small $R$** (high variance relative to edge): Ruin probability decays slowly with capital
  - Doubling capital barely reduces risk
- **Large $R$** (high edge relative to variance): Ruin probability decays exponentially
  - Doubling capital exponentially reduces risk
- **Exponential relationship**: The key insight is the exponential decay
  - Small increases in capital give massive risk reduction when $R$ is high
  - This is the power of the Lindy Effect

### The Survival Score

The probability of **not** going ruin is:

$$\text{Survival\_Score} = 1 - \psi(u) = 1 - e^{-R \cdot u}$$

$$= 1 - e^{\left(\frac{-2 \cdot \text{Mean Return} \cdot \text{Current Capital}}{\text{Variance}}\right)}$$

This ranges from 0 (certain ruin) to 1 (certain survival).

---

## The RoR Metric in Practice

### Step 1: Calculate Lundberg Adjustment Coefficient

$$R = \frac{2 \cdot \mu}{\sigma^2}$$

**Input parameters:**
- $\mu$ = Mean daily/per-trade PnL
- $\sigma^2$ = Variance of PnL

**Example:**
- Mean daily return: +0.02% = 0.0002
- Daily variance: 0.0001
- $R = \frac{2 \times 0.0002}{0.0001} = 4.0$

### Step 2: Calculate Ruin Probability

$$\psi(u) = e^{-R \cdot u}$$

**Input parameters:**
- $R$ = Lundberg coefficient (from Step 1)
- $u$ = Current capital

**Example (continued):**
- $R = 4.0$
- Current capital: $100,000
- $\psi = e^{-4.0 \times 100,000} = e^{-400,000}$ ≈ 0 (essentially zero ruin probability)

### Step 3: Evaluate Against Threshold

Set a risk threshold (e.g., "I accept up to 1% ruin probability"):

$$\text{IF } \psi > 0.01: \text{ REJECT TRADE}$$
$$\text{ELSE: ALLOW TRADE}$$

### Step 4: Calculate Solvency Distance (Bonus Metric)

How many average losses can you absorb before ruin?

$$\text{Solvency Distance} = \frac{\text{Current Capital}}{\text{Expected Loss per Period}}$$

**Example:**
- Current capital: $100,000
- Expected loss per bad period: $500
- Solvency distance: 200 periods

You can survive 200 bad periods at maximum loss before hitting zero.

---

## Key Mathematical Properties

### Property 1: Exponential Decay

Ruin probability decays exponentially with capital:

$$\psi(2u) = e^{-2Ru} = [e^{-Ru}]^2 = \psi(u)^2$$

**Implication:** Doubling capital **squares** the ruin probability reduction when $R$ is constant.

### Property 2: Variance Sensitivity

RoR is extremely sensitive to variance:

$$R = \frac{2\mu}{\sigma^2} \Rightarrow R \propto \frac{1}{\sigma^2}$$

Even small increases in volatility dramatically reduce $R$ and increase ruin risk.

### Property 3: The Kelly Connection

The Lundberg coefficient is related to the **Kelly Criterion** optimal bet size:

$$f^* = \frac{\text{Edge}}{\text{Worst-Case Loss}} \approx \frac{R}{\text{Max Loss}}$$

Optimal position sizing emerges naturally from RoR theory.

---

## Critical Assumptions & Limitations

1. **Loss Distribution:** The approximation assumes Gamma or Exponential distributed losses. Fat-tailed distributions (Pareto, Student-t) may underestimate risk.

2. **Stationary Parameters:** We assume mean and variance remain constant over time. Regime changes violate this.

3. **Infinite Horizon:** RoR answers "Will I ever go broke?" If you only trade for 1 year, the probability is different.

4. **Independent Shocks:** Losses are assumed independent. Clustered losses (VIX spikes) may be more dangerous.

---

## Summary: The RoR Framework

| Element | Definition | Formula |
|---------|-----------|---------|
| **Lundberg Coefficient** | Risk-reward quality | $R = \frac{2\mu}{\sigma^2}$ |
| **Ruin Probability** | Prob of eventual ruin | $\psi = e^{-Ru}$ |
| **Survival Score** | Prob of indefinite survival | $1 - \psi$ |
| **Solvency Distance** | Periods until ruin | $\frac{u}{\text{Avg Loss}}$ |

**Decision Rule:**
- If $\psi < \text{threshold}$ (e.g., 0.01): **Safe to trade**
- If $\psi \geq \text{threshold}$: **Reject or resize**

---

## References

- **Cramér-Lundberg Model**: Classical ruin theory in actuarial mathematics
- **Lundberg Inequality**: Exponential bound on ruin probability
- **Taleb's Ruin Theory**: "Skin in the Game," applications to trader risk
- **Kelly Criterion**: Optimal betting theory and position sizing

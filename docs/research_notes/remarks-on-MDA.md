# Practical Heuristics: MDA & EVT for Lower Time Frame Trading

To effectively apply **Extreme Value Theory (EVT)** and the **Maximum Domain of Attraction (MDA)** to real-world trading—particularly in **lower time frames (LTF)** like intraday or short-dated options—you must abandon the Gaussian focus on "averages" and shift to monitoring the **tail index**.

In fat-tailed environments, the "tail wags the dog." The following heuristics bridge the gap between statistical theory and trading execution.

---

### 1. The "Shadow Mean" Heuristic (Risk Anchoring)
In LTF data, the sample mean (the average move visible on your screen) is statistically deceptive. It often appears stable simply because the "true" mean is determined by rare, extreme events that haven't happened in your limited sample window.

*   **The Heuristic:** Do not use the sample mean for risk management. Estimate the **Shadow Mean** (the true population mean) using the tail index. In fat-tailed domains (Fréchet MDA), the true mean is often **3 to 4 times higher** than the observed sample mean.
*   **Application:** If your intraday strategy shows an average loss of $100, your risk models should be anchored to a "Shadow" loss of **$300–$400**. This accounts for the "invisible" tail risk that exists statistically but has not yet manifested in your data.

### 2. Wittgenstein’s Ruler for LTF Anomalies (Model Rejection)
Traders often dismiss "10-sigma" intraday moves as "flash crashes" or outliers that won't repeat. This is a logical error. Wittgenstein’s Ruler posits that if you use a ruler to measure a table and get a strange result, you should not blame the table—you should suspect the ruler.

*   **The Heuristic:** If you observe a single "6-sigma" or "10-sigma" event, **reject the model**, not the data. It is statistically more probable that you are using the wrong distribution (Gaussian/Gumbel) than that a true 10-sigma event occurred.
*   **Application:** Upon seeing a massive deviation, immediately switch your risk calculations from Standard Deviation (Sigma) to **Tail Index ($\alpha$)**. Assume the asset belongs to the **Fréchet MDA** (power law), where such events are the norm, not the exception.

### 3. The $\kappa$ (Kappa) Data-Sufficiency Metric
A critical danger in LTF backtesting is "pseudo-stabilization," where short datasets (e.g., 3 months of 5-minute data) look "normal" simply because not enough time has passed for a tail event to occur.

*   **The Heuristic:** Use the **$\kappa$ metric** to gauge if your dataset is large enough to be meaningful. A high $\kappa$ (closer to 1) means the Law of Large Numbers works excruciatingly slowly.
*   **Application:** If you are backtesting a strategy and the $\kappa$ of returns is **$>0.15$**, your results are likely "unreliable and a result of sample insufficiency." You may need **orders of magnitude more data** (years, not months) before your "average return" becomes a stable indicator.

### 4. The "Short-Dated Skew" Jump Diagnostic
Standard diffusion models (like Black-Scholes or Heston) fail for short expirations because they cannot generate the large jumps seen in reality. They predict that volatility should flatten as time to expiry ($T \to 0$). It often does the opposite.

*   **The Heuristic:** Monitor the **Volatility Skew** for very short-dated options. If the market is bidding up prices for far OTM options (e.g., 13 standard deviations away) relative to the ATM, the market is signaling a **Jump-Diffusion** or **Fréchet** environment.
*   **Application:** If the skew increases significantly faster as expiry approaches than a stochastic model predicts, stop using Gaussian-based metrics (like Sharpe Ratio). You are in a regime where **jumps dominate noise**.

### 5. Quasi-Static Hedging (The "Barrier" Heuristic)
Dynamic hedging (continuously adjusting delta) relies on the assumption of continuous price movement. In LTF data, gaps and jumps make dynamic hedging mathematically impossible for barrier options.

*   **The Heuristic:** Use **Static or Quasi-Static Hedging**. Do not rely on stop-losses in the underlying asset, as the price can "gap" over your limit. Instead, offset risk using **other options**.
*   **Application:** For a position that "knocks out" at a certain level, buy a static hedge (like a long OTM put). This protects you regardless of the speed of the market move, ensuring you are **convex to the jump**.

### 6. Avoiding the "Lucretius Fallacy" (High Watermark Rule)
The Lucretius Fallacy is the belief that the tallest mountain in the world is the tallest one you have personally seen. In risk terms, this is assuming that the worst historical drawdown is the worst possible drawdown.

*   **The Heuristic:** Treat the **past maximum as a floor, not a ceiling**, for future risk.
*   **Application:** Calibrate your risk management for events **larger than the historical record**. For example, a "Grey Swan" event (like the Brexit crash in the Pound) was perfectly consistent with the currency's power-law properties, even though it was unprecedented in recent data.

### 7. Relative Pricing at the "Karamata Point"
Beyond a certain threshold (the Karamata point), the behavior of a distribution is dominated by the Strong Pareto Law, and the specific shape of the "body" of the distribution becomes irrelevant.

*   **The Heuristic:** Use an **"anchor" price** for a liquid tail option and extrapolate the value of further strikes using only the **tail index ($\alpha$)**.
*   **Application:** Because $\alpha$ is conserved in the MDA, you can price far OTM options relative to each other without needing a full volatility surface or complex Gaussian assumptions.

---
To apply the statistical concepts of **Maximum Domain of Attraction (MDA)**, the **$\kappa$ metric**, and **Shadow Moments** to a dataset, you must move from standard descriptive statistics to **Extreme Value Theory (EVT)** and **Power Law heuristics**.

Below are the mathematical formulations and formulas required to implement these methods on your data.

### **1. Diagnosing the Tail Index ($\alpha$) and MDA**
The first step is determining if your data belongs to the **Fréchet MDA** (Fat Tails). For a random variable $X$, the power-law tail is defined by its survival function:
$$P(X > x) = L(x)x^{-\alpha}$$
Where $L(x)$ is a slowly varying function. 

**The Heuristic Formula (Wittgenstein’s Ruler):**
If you observe a "6-sigma" event in your data, you should reject the Gaussian (Gumbel MDA) in favor of the Power Law (Fréchet MDA). The probability of the data being Gaussian given a 10-sigma event is effectively zero:
$$P(\text{Gaussian} | \text{Event}) \approx \frac{P(G)P(E|G)}{P(\text{Non-}G)P(E|\text{Non-}G)} \to 0$$

### **2. Measuring Data Sufficiency: The $\kappa$ (Kappa) Metric**
To know if your dataset is large enough to trust its mean, use the **$\kappa$ metric**. This measures the "speed" of the Law of Large Numbers.

**The Formulation:**
Let $M(n)$ be the Mean Absolute Deviation (MAD) of the sum of $n$ observations. The rate of convergence $\kappa$ between two sample sizes $n_0$ and $n$ is:
$$\kappa(n_0, n) = 2 - \frac{\log(n) - \log(n_0)}{\log(M(n) / M(n_0))}$$

*   **Interpretation:** If $\kappa \approx 0$, the data is Gaussian and converges quickly. If $\kappa$ is high (e.g., $> 0.15$), you may need **orders of magnitude more data** before the sample mean becomes a stable indicator.

### **3. Estimating the "Shadow Mean" (Population Mean)**
In fat-tailed datasets, the observed sample mean is often a biased underestimation because the largest events haven't happened yet.

**The "Plug-in" Formula:**
Instead of using the sample average, estimate the tail exponent $\alpha$ and use the **Shadow Mean** formula for a Pareto distribution with minimum value $L$:
$$E[X]_{\text{Shadow}} = L \frac{\alpha}{\alpha - 1}$$
For datasets with a known physical or economic upper bound $H$ (e.g., total world population or total market cap), the formulation becomes:
$$E[Y] = (H - L)e^{\frac{1}{\xi} \frac{\sigma}{H}} \left( \frac{\sigma}{H \xi} \right)^{\frac{1}{\xi}} \Gamma \left( 1 - \frac{1}{\xi}, \frac{\sigma}{H \xi} \right) + L$$
*Where $\xi = 1/\alpha$ is the shape parameter from the Generalized Pareto Distribution (GPD).*

### **4. Relative Pricing Heuristic (Beyond Black-Scholes)**
If your dataset consists of option prices or tail exposures, you can price deeper "tail" events ($K_2$) relative to a known "anchor" price ($K_1$) using only the tail index $\alpha$, bypassing the need for a full volatility surface.

**The Relative Pricing Formula:**
For strikes $K_1, K_2$ beyond the **Karamata Point** (the point where the tail starts):
$$C(K_2) = C(K_1) \left( \frac{K_2}{K_1} \right)^{1-\alpha}$$
*   **Application:** If you know the price of a 5% OTM option ($K_1$) and your data has an $\alpha = 3$, you can derive the price of a 10% OTM option ($K_2$) with high robustness.

### **5. Replacing Standard Deviation with MAD**
Because Standard Deviation (STD) overweights outliers in fat-tailed data, it is unstable. Use **Mean Absolute Deviation (MAD)** instead:
$$\text{MAD} = \frac{1}{n} \sum_{i=1}^{n} |x_i - \bar{x}|$$
**The Efficiency Ratio:**
In a Gaussian world, $STD/MAD = \sqrt{\pi/2} \approx 1.25$. If your dataset shows a ratio much higher than 1.25, your "volatility" measurements are being dominated by the tails, and STD should be retired.
Reorganized list: TailWarp-focused chapters (removed Raft-LM sections).

---

#### **Project 2: TailWarp (GPU Simulation & Monte Carlo Framework)**
- **Chapter 4: Univariate Fat Tails, Level 1, Finite Moments**  
  *Provides heuristics for stochastic volatility in realistic simulations.*
- **Chapter 5: Level 2: Subexponentials and Power Laws**  
  *Core reference for implementing heavy-tailed distribution kernels.*
- **Chapter 6: Thick Tails in Higher Dimensions**  
  *Essential for multi-asset path simulations and correlated shocks.*
- **Chapter 8: How Much Data Do You Need? An Operational Metric for Fat-Tailedness**  
  *Introduces the 𝜅 metric for determining Monte Carlo scenario stability.*
- **Chapter 9: Extreme Values and Hidden Tails**  
  *Covers Extreme Value Theory (EVT) for tail validation.*
- **Chapter 10: "It Is What It Is": Diagnosing the SP500**  
  *Methodology for testing maximum drawdowns via parallel prefix scans.*

---

**Chapter 4: Univariate Fat Tails, Level 1, Finite Moments**  
- **Projects:** TailWarp  
- **Lenses:** Lens 2 (Volatility & Noise Categories) via subchapter 4.4.5  
- **Reason:** Provides stochastic volatility heuristics for realistic market simulations.

**Chapter 4.4.5: Why we should retire standard deviation, now!**  
- **Projects:** —  
- **Lenses:** Lens 2 (Volatility & Noise Categories)  
- **Reason:** Demonstrates the inadequacy of standard deviation under fat tails.

**Chapter 5: Level 2: Subexponentials and Power Laws**  
- **Projects:** TailWarp  
- **Lenses:** Lens 2 (Volatility & Noise Categories) via subchapter 5.6  
- **Reason:** Core for implementing heavy-tailed distributions in simulation kernels.

**Chapter 5.6: Pseudo-stochastic volatility: an investigation**  
- **Projects:** —  
- **Lenses:** Lens 2 (Volatility & Noise Categories)  
- **Reason:** Explores how constant power laws can mimic changing volatility, misleading risk models.

**Chapter 6: Thick Tails in Higher Dimensions**  
- **Projects:** TailWarp  
- **Lenses:** —  
- **Reason:** Essential for multi-asset simulations and handling correlated shocks.

**Chapter 8: How Much Data Do You Need? An Operational Metric for Fat-Tailedness**  
- **Projects:** TailWarp  
- **Lenses:** —  
- **Reason:** Introduces the 𝜅 metric to determine required Monte Carlo scenarios for stability.

**Chapter 9: Extreme Values and Hidden Tails**  
- **Projects:** TailWarp  
- **Lenses:** Lens 3 (Downside & Tail Categories)  
- **Reason:** Covers EVT and addresses the Lucretius Fallacy for extrapolating beyond past extremes.

**Chapter 10: "It Is What It Is": Diagnosing the SP500**  
- **Projects:** TailWarp  
- **Lenses:** Lens 4 (Drawdown & “Pain” Categories) via subchapter 10.2.2  
- **Reason:** Provides methodology for analyzing maximum drawdowns using power laws.

**Chapter 10.2.2: Maximum Drawdowns**  
- **Projects:** —  
- **Lenses:** Lens 4 (Drawdown & “Pain” Categories)  
- **Reason:** Establishes power-law behavior of drawdowns and Paretian waiting times for extreme excursions.

**Chapter 11.2: Spurious overestimation of tail probability in psychology**  
- **Projects:** —  
- **Lenses:** Lens 8 (Behavioral & Perception Categories)  
- **Reason:** Debunks claims of human overestimation of rare risks, emphasizing rational payoff-based assessment.

**Chapter 23: Lindy as Distance from an Absorbing Barrier**  
- **Projects:** —  
- **Lenses:** Lens 1 (Structural / Ruin Risk)  
- **Reason:** Provides the mathematical foundation for ruin risk and absorbing barriers.

**Chapter 29: Portfolios should never rely on correlation**  
- **Projects:** —  
- **Lenses:** Lens 10 (Cross-Asset & Systemic Categories)  
- **Reason:** Demonstrates the instability of correlation under non-Gaussian variables and systemic risk.

--- 

If you want, I can also extract these into a separate TailWarp-only markdown file or reorder them by priority.
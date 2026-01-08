# TailWarp Risk Preference & Training Chapters

Based on the provided sources, here are the chapters, papers, and conceptual frameworks relevant for TailWarp, focusing on simulation design, metric calculation, and the optimization layer.

## 1. Conceptual Risk Frameworks for Simulation & Metric Design

### From "The Ten Lenses of Convex Risk Mapping"

#### Category 1: Structural / Ruin Risk
**Why selected for TailWarp:** Provides the fundamental mathematical concept of an absorbing barrier, which is essential for designing and calibrating Monte Carlo simulations where paths can terminate upon hitting a ruin threshold.

#### Category 5: Asymmetry & Convexity
**Why selected for TailWarp:** This framework is crucial for TailWarp's Optimization Layer (Phase 4). It defines the payoff asymmetry (CI) that the GPU-based optimizers will target when solving for parameters that minimize tail risk or maximize convex exposure.

#### Category 8: Behavioral & Perception
**Why selected for TailWarp:** Informs the design of synthetic data generators and Hawkes process models by capturing how human behavioral patterns (e.g., herding, panic clustering) manifest in market microstructure and volatility bursts.

### From "Asymmetric Constructivism: The Path of the Convexity Hunter"

#### Title: The Path: Seeking the Formulation of Risk Preference
**Why selected for TailWarp:** This intellectual shift provides the "why" behind simulating non-Gaussian distributions. It justifies TailWarp's core focus on fat tails and EVT as necessary for exploring and validating convex strategies.

#### Title: The Preference System: The "Convexity Score"
**Why selected for TailWarp:** The Vitality Score can be implemented as a target metric within the RiskMetricCalculator. This allows TailWarp to compute this novel "Quality of Uncertainty" measure across millions of simulated scenarios.

#### Title: The "Religion" of the Algorithm
**Why selected for TailWarp:** Serves as a guiding principle for the research direction, ensuring that simulation benchmarks and optimization problems are designed to test the robustness of asymmetric, convex strategies against standard linear models.

---

## 2. Relevant Academic Papers & Chapters for Simulation & Optimization

### Paper: "Geometry and convergence of natural policy gradient methods"

#### Chapter 3.1: Definition and general properties of natural gradients
**Why selected for TailWarp:** Highly relevant for implementing the Geometric Optimization methods in TailWarp's Phase 4. The mathematical principles of natural gradients on manifolds are key for optimizing parameters on spaces like the set of positive-definite correlation matrices.

### Paper: "Riemannian Metric Learning: Closer to You than You imagine"

#### Chapter 5.1: Statistical Guarantees for Nonlinear Metric Learning
**Why selected for TailWarp:** Supports the research into geometry-aware optimizers within TailWarp's flexible optimization layer. It provides statistical foundations for learning risk-aware metrics in high-dimensional spaces, which can be tested via simulation.

---

## 3. Excluded Papers & Rationale

*   **Paper:** "What is the Alignment Objective of GRPO?"
    *   **Rationale:** This focuses on LLM/RL agent alignment, which is outside TailWarp's core scope of simulation and numerical optimization.

*   **Paper:** "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via RL"
    *   **Rationale:** This details LLM-specific training mechanisms and is not directly applicable to TailWarp's GPU kernel development and Monte Carlo engine.

*   **Paper:** "A Locally Adaptive Normal Distribution (LAND)"
    *   **Rationale:** As noted, this focuses on probability density estimation and is not directly related to TailWarp's primary tasks.
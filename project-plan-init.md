
# Project Plan: TailWarp

**Project Type:** Research-Grade High-Performance Computing (HPC) Suite  
**Primary Hardware Target:** NVIDIA RTX 3060 (Consumer/Ampere Architecture)  
**Status:** Research & Prototype Development  
**Core Focus:** Massive parallelism for financial risk simulation, correctness verification of fat-tail distributions, and algorithm exploration.

## 1. Project Overview & Philosophy
The goal of this project is to build a modular, high-performance computational suite designed to test, validate, and showcase advanced financial risk models on GPU hardware. Unlike production libraries optimized for low-latency trading APIs, this suite is optimized for **throughput, numerical precision, and algorithmic flexibility.**

We will focus on "Fat Tail" events and Extreme Value Theory (EVT), utilizing the massive parallelism of CUDA to perform "brute force" simulations that are intractable on CPUs. The project will serve as a testbed for implementing new academic ideas (e.g., geometric optimization, RL-based quoting) without the overhead of commercial software deployment.

## 2. Top-Layer Architecture & Abstractions

The system is designed as a pipeline: **Data Input $\to$ GPU Compute Modules $\to$ Analysis/Optimization $\to$ Result Output.**

### 2.1. Data Abstraction Layer (The "Interface")
Since data sources are variable but processing is the focus, we use a **File-First Architecture**.
*   **Abstract Base Class `DataSource`**: Defines a generic interface to load market data.
*   **Concrete Implementations**:
    *   `CSVDataSource`: Reads time-series data (OHLCV, Tick data) from flat files.
    *   `BinaryDataSource`: Reads custom binary formats for speed (simulating future low-latency feeds).
    *   `MockDataGenerator`: Generates parametric data directly on host for testing specific distributions without file I/O overhead.
*   **Design Philosophy**: The host (CPU) prepares data buffers. The goal is rapid transfer to GPU (PCIe) rather than complex database querying at this stage.

### 2.2. The Compute Core (CUDA Engine)
The heart of the suite, organized by mathematical domain rather than asset class.
*   **`RNGFactory`**: Pluggable Random Number Generators.
    *   *Curand integration* for Philox/XORWOW.
    *   *Custom Kernels* for Quasi-Monte Carlo (Sobol) sequences.
*   **`DistributionModule`**: A registry of probability distribution samplers.
    *   *Fat-Tails:* Student-t, Skew-t, Generalized Hyperbolic.
    *   *Infinite Variance:* $\alpha$-Stable distributions (Chambers-Mallows-Stuck method).
    *   *Microstructure:* Poisson processes, Hawkes processes (self-exciting point processes).
*   **`SimulationEngine`**: Orchestrates the execution.
    *   Manages Grid/Block dimensions based on RTX 3060 specifications (e.g., balancing occupancy vs. register usage).
    *   Handles batched simulations (running multiple "what-if" scenarios in parallel).

### 2.3. Analytics & Risk Assessment Layer
Processes raw simulation outputs into risk metrics on-device (minimizing data transfer).
*   **`RiskMetricCalculator`**:
    *   Standard: VaR, CVaR (Expected Shortfall).
    *   EVT-based: Peaks-Over-Threshold (POT) estimation directly on GPU histograms.
    *   Drawdown: Parallel prefix scans for max drawdown.
*   **`AlgorithmLibrary`** (The "Research" Slot):
    *   *Optimization Solvers:* Gradient Descent, Stochastic Gradient Descent (SGD), and Geometric Optimization (Manifold descent for covariance matrices).
    *   *RL Interface:* (Future/Experimental) Kernels for parallel environment stepping for Reinforcement Learning agents.

### 2.4. Validation & Benchmarking Layer
Ensures "Research Grade" correctness.
*   **`CPUValidator`**: A lightweight C++/Python reference implementation using `Eigen`/`NumPy` to compare GPU results against CPU baselines (bit-level or tolerance-based comparison).
*   **`Profiler`**: Measures kernel execution time and memory bandwidth specifically for the RTX 3060.

---

## 3. Key Features & Implementations

We are plan to implement the features further, the plan might be changed in the future, the plan might be changed in response to new research findings, technological advancements, or evolving market conditions.

### 3.1. Fat-Tail & EVT Simulation
*   **Feature:** Massively parallel generation of non-Gaussian returns.
*   **Implementation:** CUDA kernels implementing the *Inverse Transform Sampling* method for Student-t and the *CMS method* for Stable distributions.
*   **Research Value:** Allows comparison of portfolio behavior under "infinite variance" assumptions vs. standard Gaussian models.

### 3.2. Microstructure-Aware Modeling
*   **Feature:** Simulating order book events rather than just price paths.
*   **Implementation:** Parallel simulation of *Hawkes Processes*. This captures the "clustering" of orders and volatility bursts.
*   **Optimization:** Use of shared memory to aggregate event counts within a warp before writing to global memory.

### 3.3. Flexible Optimization Layer
*   **Feature:** Finding optimal parameters (spreads, hedge ratios) that minimize tail risk.
*   **Implementation:**
    *   *Gradient Descent:* Standard implementation for smooth loss functions.
    *   *Geometric Methods:* Research-oriented implementation (e.g., Riemannian Gradient Descent) for optimizing parameters that lie on manifolds (e.g., correlation matrices).
*   **Flexibility:** The cost function (Loss Function) is a pluggable parameter. We can swap "Maximize Sharpe Ratio" for "Minimize CVaR" without rewriting the solver.

### 3.4. "Paper-to-Code" Framework
*   **Feature:** Rapid prototyping of methods from new academic papers.
*   **Implementation:** A standardized "Kernel Interface" that allows researchers to inject a single `.cu` file containing a new mathematical formula into the existing build pipeline to test it against standard benchmarks.

### 3.5. Synthetic Data Generators
*   **Feature:** Configurable generators for rapid algorithm validation against known statistical properties.
*   **Implementation:**
    *   *Monte Carlo Path Generator:* Parallel geometric Brownian motion simulation with Cholesky-based correlation.
    *   *Limit Order Book Simulator:* Agent-based event generation simulating market maker/taker interactions.
    *   *Regime-Switching Generator:* GPU-accelerated Hidden Markov Model sampler for multi-regime time series.
    *   *Correlation Stress Tester:* Student's t-copula implementation for generating tail-dependent multi-asset returns.
*   **Flexibility:** Each generator exposes key parameters (volatility, correlation, regime parameters) as runtime inputs, enabling systematic backtesting across market conditions.

---

## 4. Target Hardware Profile (RTX 3060)
All code will be optimized for the specific constraints of the RTX 3060 (for now) to ensure realistic performance metrics:
*   **Memory:** 12GB GDDR6 (Focus: Efficient memory management to fit large scenario sets; avoid OOM errors).
*   **Architecture:** Ampere (Focus: Utilizing `L2` cache and `Tensor Cores` if mixed-precision calculations are introduced for heuristic speedups).
*   **Compute Capability:** 8.6 (Focus: Code compilation targeting `sm_86`).

---

## 5. Execution Roadmap & Timeline

### Phase 1: Foundations & Validation (Months 1-2)
*Focus: Setting up the environment and proving the correctness of basic math on the RTX 3060.*

*   **Tasks:**
    1.  Setup CMake/Make build pipeline for pure CUDA/C++ (no Python bloat initially).
    2.  Implement `FileDataSource` (CSV reader) and `MockDataGenerator`.
    3.  Implement `RNGFactory` (Curand wrappers).
    4.  Implement basic Gaussian Monte Carlo kernel.
    5.  **Milestone:** Run 10M scenarios of a Gaussian option price and match NumPy results within 1e-6 tolerance.

### Phase 2: Fat Tails & EVT Implementation (Months 3-4)
*Focus: Implementing the unique selling point—heavy-tailed distributions.*

*   **Tasks:**
    1.  Implement Student-t and Skew-t distribution kernels (Inverse CDF).
    2.  Implement $\alpha$-Stable distribution kernel (CMS method).
    3.  Develop `RiskMetricCalculator` (Warp-level sorting for VaR/CVaR).
    4.  Implement "Peaks-Over-Threshold" logic in CUDA.
    5.  **Milestone:** Visualize the difference between 95% VaR calculated via Gaussian assumptions vs. Student-t assumptions using 100M scenarios.

### Phase 3: Microstructure & Advanced Simulation (Months 5-6)
*Focus: Adding complexity—order flow and path dependency.*

*   **Tasks:**
    1.  Implement Hawkes Process kernel (exponential kernel decay).
    2.  Implement Limit Order Book (LOB) simulation logic (simplified) in parallel.
    3.  Optimize memory usage (ensure 12GB VRAM is sufficient for multi-asset LOB sims).
    4.  **Milestone:** Simulate a "Flash Crash" scenario using Hawkes process parameters and measure the resulting portfolio drawdown.

### Phase 4: The Optimization Suite (Months 7-8)
*Focus: Solving for decisions using the simulation results.*

*   **Tasks:**
    1.  Implement Batched Gradient Descent on GPU.
    2.  Research & Implement Geometric Optimization kernel (e.g., projection onto the Positive Definite cone).
    3.  Integrate Optimization with Simulation (the "Inner Loop" of risk management).
    4.  **Milestone:** Given a simulated fat-tailed distribution, find the optimal position size that limits CVaR to < 5% using the GPU optimizer.

### Phase 5: Research Showcase & RL Integration (Months 9-12)
*Focus: Exploration of new ideas and academic output.*

*   **Tasks:**
    1.  Design "Algorithm Registry" to easily swap new loss functions.
    2.  Implement a grid-world or toy financial environment in CUDA for basic Reinforcement Learning (parallel value iteration or policy gradient).
    3.  Generate "Result Sets": CSVs and plots comparing CPU vs. GPU performance across all modules.
    4.  **Milestone:** Complete a research-grade report/paper draft utilizing the suite to prove the failure of standard hedging strategies under Stable-distributed shocks.

---

## 6. Long-Term Tasks & Future Work

*   **Database Integration:** Refactor `DataSource` to interface directly with KDB+ or PostgreSQL via C-apis.
*   **Auto-Tuning:** Implement a kernel tuner that automatically adjusts block sizes based on input data size for the RTX 3060.
*   **Precision Analysis:** A rigorous study on the impact of `float` vs. `double` precision on the stability of EVT calculations.

## 7. Deliverables Structure (No Installers)
The final output will be a clean repository structure:
```text
/src
  /core           # CUDA kernels (.cu)
  /wrappers       # Host C++ code
  /algorithms     # Specific implementations (Optimization, EVT)
  /reference      # CPU reference implementations
/data
  /input          # Sample CSV files
  /output
    /experiments  # All experiment runs (timestamped folders)
/configs          # Experiment configurations (.json)
  /research       # Research project configs
/scripts
  run_benchmark.sh
  validate_accuracy.py  # Standalone script to compare GPU output vs NumPy
/docs
  EXPERIMENTS.md         # Experiment structure and provenance spec
  VALIDATION.md          # Validation strategy and levels
  /project-plan-docs     # Operational guides (see below)
  /research_notes        # Research findings and papers
CMakeLists.txt
```
This structure ensures "pure codes and results" without forcing the user to deal with complex package management systems.

## 8. Operational Documentation & Workflow Guides

To support long-term R&D, the repository includes comprehensive operational guides in `docs/project-plan-docs/`:

### Core Specifications
*   **`docs/EXPERIMENTS.md`**: Defines experiment structure, provenance capture, and reproducibility standards
*   **`docs/VALIDATION.md`**: Defines validation levels (0–4), reference implementations, and correctness criteria

### Workflow Guides
*   **`00-START-HERE.md`**: First-week playbook and core research loop
*   **`01-RD-PHASES.md`**: Phase gates with clear "done" criteria and priority guidance
*   **`02-CHECKLISTS.md`**: Copy-paste checklists for common tasks (adding kernels, metrics, committing code)
*   **`03-ADD-A-MODULE.md`**: Step-by-step guide for integrating new components
*   **`04-RESEARCH-WORKFLOW.md`**: How to design and run reproducible experiments
*   **`05-EXPERIMENT-REVIEW.md`**: Quality gates for determining if results are trustworthy/publishable
*   **`06-PERFORMANCE-PROTOCOL.md`**: Benchmarking standards and regression detection
*   **`QUICK-REFERENCE.md`**: One-page summary of the entire workflow

These guides ensure that as the project grows, every contributor (including future you) can:
- Add new modules without breaking existing work
- Produce research-grade artifacts consistently
- Validate correctness at multiple levels
- Track performance and prevent regressions
- Maintain reproducibility and provenance
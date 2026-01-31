# Structural-Ruin Risk Implementation

## Overview

This module implements risk metrics for **Structural / Ruin Risk** – focusing on survival, absorbing barriers, and the probability of system termination.

## Purpose

Quantify and track:
- **Risk of Ruin (RoR):** Probability of hitting capital zero or margin-call thresholds
- **Absorbing Barriers:** Hard constraints that end trading (liquidation, regulatory shutdown)
- **Survival Probability:** Likelihood of strategy persisting over N periods
- **Solvency Distance:** Number of adverse moves before hitting ruin barrier

## Key Implementation Areas

- **Risk of Ruin (RoR):** Probability of hitting absorbing barrier using Lundberg Inequality
- Ruin probability calculations
- Barrier detection and monitoring
- Survival analysis under stochastic shocks
- Capital adequacy and solvency distance metrics

## Implemented Components

### Risk of Ruin (RoR) Metric
**Files:**
- `ror_metric.h` – Header with class definitions and CUDA kernel declarations
- `ror_metric.cu` – CUDA/CPU implementation of RoR calculations

**Key Features:**
- **CPU Implementation:** Reference calculation using standard math functions
- **GPU Implementation:** CUDA kernels for single and batch RoR calculations
- **Batch Processing:** Efficiently compute RoR for multiple scenarios
- **Parameter Validation:** Net Profit Condition checks

**Mathematical Basis:**
- Survival Score = 1 - e^(-R·u)
- Lundberg Coefficient: R = 2·μ / σ²
- Ruin Probability: ψ = e^(-R·u)

### Absorbing Barrier (Ruin State) Metric
**Files:**
- `absorbing_barrier.h` – Header with class definitions and CUDA kernel declarations
- `absorbing_barrier.cu` – CUDA/CPU implementation of Absorbing Barrier calculations
- `ABSORBING_BARRIER.md` – Comprehensive mathematical and conceptual explanation

**Key Features:**
- **Stopping Time Estimation:** τ = inf{t > 0; X_t < L} – when ruin occurs
- **Cramér-Lundberg Model:** U(t) = u + ct - S(t) surplus tracking
- **Distance to Ruin:** Measured in absolute terms and CVaR units
- **Hazard Rate Calculation:** μ(τ) = Force of mortality at current state
- **Lindy Effect Integration:** Remaining life expectancy for fat-tailed systems
- **Ergodicity Detection:** Non-ergodic regime identification (tail vs. drift dominance)
- **Batch GPU Processing:** Efficient computation for multiple scenarios

**Mathematical Basis:**
- Stopping Time: τ = inf{t > 0; X_t < L}
- Cramér-Lundberg Surplus: U(t) = u + ct - S(t)
- Hazard Rate: μ(τ) = -d/dτ log(S(τ))
- Lindy Expectancy: E[remaining | age] = age (for power-law lifetimes)
- Ergodicity Metric: tail_impact / (tail_impact + drift_impact)

**Concepts Addressed:**
- Path Dependence (time probability vs. ensemble probability)
- Absorbing States (Markov chain with p_{i,i} = 1)
- Non-Ergodic Risk (single tail event > accumulated small losses)
- Capital Adequacy (solvency distance in CVaR units)

## Reference Documentation

For conceptual details and risk framework overview, see:
- [Structural-Ruin Risk Documentation](../../docs/risk-metrics/Structural-Ruin)
- [Complete Risk Categories Framework](../../docs/risk-metrics/risk-categories.md#lens-1--structural--ruin-risk)

## Related Components

- [Research Notes](../../docs/research_notes/) – Academic references and Taleb's work on ruin and absorbing barriers
- [Algorithms](../algorithms/) – Core portfolio optimization and risk-adjusted sizing

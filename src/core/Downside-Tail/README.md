# Downside-Tail Implementation

## Overview

This module implements **extreme value theory (EVT) and tail risk metrics** for capturing rare, severe events.

## Purpose

Quantify and track:
- **VaR & CVaR:** Value-at-Risk and Conditional Value-at-Risk (Expected Shortfall)
- **MDA Diagnosis:** Maximum Domain of Attraction (Fréchet, Gumbel, Weibull classification)
- **Tail Index (α) Estimation:** Hill estimator, Peaks-Over-Threshold, GPD fitting
- **κ Metric:** Data sufficiency for fat-tailed regimes
- **Shadow Mean & Shadow Moments:** True distribution mean under fat tails
- **Gap Risk:** Probability and impact of price jumps over stops
- **Jump-Diffusion:** Modeling and pricing with Poisson jumps

## Key Implementation Areas

- CUDA kernels for CVaR computation
- Extreme value theory (EVT) algorithms
- Hill estimator and GPD fitting
- Jump-diffusion calibration
- Tail risk constraints for optimization

## Reference Documentation

For conceptual details and risk framework overview, see:
- [Downside-Tail Risk Documentation](../../docs/risk-metrics/Downside-Tail)
- [Complete Risk Categories Framework](../../docs/risk-metrics/risk-categories.md#lens-3--downside--tail-risks)

## Related Components

- [CVaR Wrapper](../../wrappers/risk_metrics.cpp)
- [Student-t Distribution](../distributions/student_t.cu) – Tail-heavy modeling
- [Algorithms](../algorithms/) – Position sizing and robust optimization

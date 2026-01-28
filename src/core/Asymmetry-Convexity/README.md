# Asymmetry-Convexity Implementation

## Overview

This module implements **convexity analysis and asymmetric return metrics** for strategies that benefit from volatility and disorder.

## Purpose

Quantify and track:
- **Convexity Index (CI):** Score quantifying payoff curvature (CI > 1 = favorable convexity)
- **Sortino Ratio & Downside Deviation:** Return-to-downside-risk ratio ignoring upside volatility
- **Omega Ratio:** Probability-weighted gain-loss ratio for asymmetric payoff analysis
- **Skewness & Kurtosis:** Higher moments capturing asymmetry and tail weight
- **Karamata-Point Pricing:** Tail-only relative pricing using tail index α
- **Shadow Greeks:** Option sensitivities under heavy-tailed assumptions
- **Quasi-Static Hedging:** Static option positioning for robust barrier protection

## Key Implementation Areas

- Payoff function analysis and convexity computation
- Higher moment calculation (skewness, kurtosis)
- Return distribution asymmetry metrics
- Option Greeks under tail-adjusted models
- Hedging strategy construction

## Reference Documentation

For conceptual details and risk framework overview, see:
- [Asymmetry-Convexity Risk Documentation](../../docs/risk-metrics/Asymmetry-Convexity)
- [Complete Risk Categories Framework](../../docs/risk-metrics/risk-categories.md#lens-5--asymmetry--convexity-categories)

## Related Components

- [Distributions](../distributions/) – Heavy-tailed models for derivatives pricing
- [Manifolds](../manifolds/) – SPD geometry for covariance analysis
- [Algorithms](../algorithms/) – Barbell optimization and convex position sizing

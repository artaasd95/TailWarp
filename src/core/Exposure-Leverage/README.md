# Exposure-Leverage Implementation

## Overview

This module implements **exposure and leverage monitoring** to track committed capital and hidden factor concentrations.

## Purpose

Quantify and track:
- **Leverage Cycles:** System-wide leverage fluctuations and margin regimes
- **Gross & Net Exposure:** Notional long/short positioning metrics
- **Leverage Ratio:** Notional exposure relative to equity capital
- **Beta & Factor Loadings:** Sensitivities to market and style factors
- **Concentration Risk:** Capital allocation across assets, sectors, risk factors

## Key Implementation Areas

- Position tracking and aggregation
- Factor exposure computation
- Beta/correlation analysis
- Leverage monitoring and alerts
- Concentration metrics and limits
- CUDA kernels for efficient multi-asset analysis

## Reference Documentation

For conceptual details and risk framework overview, see:
- [Exposure-Leverage Risk Documentation](../../docs/risk-metrics/Exposure-Leverage)
- [Complete Risk Categories Framework](../../docs/risk-metrics/risk-categories.md#lens-6--exposure--leverage-categories)

## Related Components

- [Algorithms](../algorithms/) – Position sizing and factor normalization
- [Robust Covariance](../algorithms/robust_covariance.cpp) – Factor structure estimation
- [Manifolds](../manifolds/) – SPD geometry for correlation analysis

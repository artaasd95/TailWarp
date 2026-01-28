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

- Ruin probability calculations
- Barrier detection and monitoring
- Survival analysis under stochastic shocks
- Capital adequacy and solvency distance metrics

## Reference Documentation

For conceptual details and risk framework overview, see:
- [Structural-Ruin Risk Documentation](../../docs/risk-metrics/Structural-Ruin)
- [Complete Risk Categories Framework](../../docs/risk-metrics/risk-categories.md#lens-1--structural--ruin-risk)

## Related Components

- [Research Notes](../../docs/research_notes/) – Academic references and Taleb's work on ruin and absorbing barriers
- [Algorithms](../algorithms/) – Core portfolio optimization and risk-adjusted sizing

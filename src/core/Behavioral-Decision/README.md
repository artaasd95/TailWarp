# Behavioral-Decision Implementation

## Overview

This module implements **model risk, agency risk, and behavioral heuristics** to counter systematic underestimation of tail risk.

## Purpose

Quantify and track:
- **Model Risk:** Error bounds and model sensitivity analysis
- **Agency Risk / Moral Hazard:** Incentive alignment checks and leverage limits
- **Lucretius Fallacy Detection:** Warnings when historical max approaches asymptotic limits
- **Knightian Uncertainty:** Recognition of unmodelable risks requiring barbell strategies
- **Backtesting Bias Detection:** Look-ahead bias and data-snooping metrics
- **Overconfidence & Herding Metrics:** Positioning concentration and crowdedness indicators

## Key Implementation Areas

- Model validation and sensitivity testing
- Incentive structure monitoring
- Historical extreme tracking and extrapolation
- Backtesting protocol enforcement
- Stress testing and scenario analysis
- Behavioral flag generation for risk alerts

## Reference Documentation

For conceptual details and risk framework overview, see:
- [Behavioral-Decision Risk Documentation](../../docs/risk-metrics/Behavioral-Decision)
- [Complete Risk Categories Framework](../../docs/risk-metrics/risk-categories.md#lens-8--behavioral--decision-making-risks)

## Related Components

- [Research Notes](../../docs/research_notes/) – Taleb's work on model risk and ruin
- [Validation Tests](../../tests/validation/statistical_tests.cpp) – Model quality checks
- [Experiment Logging](../../docs/EXPERIMENTS.md) – Backtesting protocol and validation

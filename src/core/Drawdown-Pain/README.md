# Drawdown-Pain Implementation

## Overview

This module implements **drawdown and recovery metrics** capturing the psychological and capital reality of being underwater.

## Purpose

Quantify and track:
- **Maximum Drawdown (MDD):** Largest peak-to-trough decline
- **Average Drawdown & Duration:** Chronic "underwater" stress metrics
- **Ulcer Index:** Root-mean-square penalty combining depth and duration
- **Calmar Ratio:** Return-to-MDD ratio for risk-adjusted performance
- **Sterling Ratio:** Return-to-average-drawdown; less sensitive to single crashes
- **Pain Index:** Integrated drawdown over time
- **Recovery Time:** Speed to return to new equity highs

## Key Implementation Areas

- Equity curve tracking and peak detection
- Drawdown calculation and statistics
- Recovery path analysis
- Risk-adjusted return metrics (Calmar, Sterling, Ulcer)
- CUDA kernels for efficient computation on large datasets

## Reference Documentation

For conceptual details and risk framework overview, see:
- [Drawdown-Pain Risk Documentation](../../docs/risk-metrics/Drawdown-Pain)
- [Complete Risk Categories Framework](../../docs/risk-metrics/risk-categories.md#lens-4--drawdown--pain-categories)

## Related Components

- [Risk Metrics](../../wrappers/risk_metrics.cpp) – Core risk calculation infrastructure
- [Algorithms](../algorithms/) – Strategy evaluation and optimization

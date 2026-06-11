# Liquidity-MarketStructure Implementation

## Overview

This module implements **liquidity and market microstructure metrics** for assessing execution risk and market impact.

## Purpose

Quantify and track:
- **Bid–Ask Spread & Spread Volatility:** Liquidity cost and stress behavior
- **Market Impact Models:** Almgren–Chriss style execution impact estimation
- **Order-Flow Toxicity (VPIN):** Probability of informed trading and flash-crash warnings
- **Depth of Book:** Available liquidity at price levels
- **Liquidity-Adjusted VaR (LVaR):** VaR adjusted for execution and spread costs

## Key Implementation Areas

- FX microstructure data processing (bid/ask, mid, volume)
- Spread analysis and volatility monitoring
- Market impact estimation for large orders
- VPIN calculation from tick or quote data
- Liquidity-adjusted risk metrics

## Reference Documentation

For conceptual details and risk framework overview, see:
- [Liquidity-MarketStructure Risk Documentation](../../docs/risk-metrics/Liquidity-MarketStructure)
- [Complete Risk Categories Framework](../../docs/risk-metrics/risk-categories.md#lens-7--liquidity--market-structure-categories)

## Related Components

- [CSV Loader](../utils/csv_loader.cu) – Loading tick/quote data
- [Risk Metrics](../../wrappers/risk_metrics.cpp) – CVaR adjusted for liquidity
- [Volatility Estimation](../Volatility-Noise/) – Microstructure-aware volatility

# Volatility-Noise Implementation

## Overview

This module implements volatility and noise estimation for **LTF and FX markets with no volume data**.

## Purpose

Quantify and track:
- **Rolling Close-Close Volatility:** Standard deviation over short windows (5m, 15m, 1h)
- **Range-Based Estimators:** Parkinson, Garman–Klass, Rogers–Satchell, Yang–Zhang using OHLC
- **Realized Volatility:** Tick/quote-based volatility without volume
- **Regime Detection:** Identifying market state changes (calm vs. storm)
- **Microstructure Noise:** Separating signal from bid–ask bounce and tick noise
- **Jump Diagnostics:** Detecting jump-diffusion and short-dated skew anomalies

## Key Implementation Areas

- Volatility estimators (close-close, range-based, realized)
- CUDA kernels for high-frequency computation
- Regime detection algorithms (Markov switching, κ metric)
- Microstructure analysis for FX and LTF data
- Jump and gap detection

## Reference Documentation

For conceptual details and risk framework overview, see:
- [Volatility-Noise Risk Documentation](../../docs/risk-metrics/Volatility-Noise)
- [Complete Risk Categories Framework](../../docs/risk-metrics/risk-categories.md#lens-2--volatility--noise-incl-ltf-no-volume-fx)

## Related Components

- [Distributions](../distributions/) – Student-t and power-law tail models
- [Algorithms](../algorithms/) – Robust covariance estimation
- [CSV Loader](../utils/csv_loader.cu) – Loading and processing OHLC data

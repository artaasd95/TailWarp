# Volatility & Noise (LTF, No-Volume FX)

## Overview

**Lens 2 – Volatility & Noise** distinguishes between normal market "breathing" (volatility) and market "earthquakes" (structural shifts). This lens is critical for low-time-frame (LTF) and FX trading where volume data is unavailable and microstructure effects dominate.

## Key Risk Metrics

- **Stochastic Volatility Models:** Modeling volatility itself as a random variable rather than constant.
- **Rolling Close-Close Volatility (LTF):** Standard deviation of returns over short windows (e.g., 5m, 15m, 1h).
- **Pseudo-Stochastic Volatility:** Recognizing that a constant power-law tail can look like changing volatility regimes.
- **Realized vs. Implied Volatility Gap:** Signals when market pricing diverges from realized reality, often preceding regime shifts.
- **Regime Detection (Markov Switching):** Identifying when the market shifts between "calm" and "storm" states.
- **Range-Based Volatility Estimators:** Parkinson, Garman–Klass, Rogers–Satchell, Yang–Zhang estimators using OHLC data.
- **Realized Volatility (Tick/Quote-Based) for FX:** High-frequency volatility estimation without volume.
- **Microstructure Noise vs Signal:** Separating true price movements from bid–ask bounce and quote noise.
- **Short-Dated Skew & Jump Diagnostic:** Monitoring far-OTM option prices to detect jump-diffusion dynamics.

## Reference

For detailed information, see [Risk Categories Framework](../risk-categories.md#lens-2--volatility--noise-incl-ltf-no-volume-fx).

## Related Resources

- [Volatility-Noise Implementation](../../src/core/Volatility-Noise)
- [TailWarp Main Documentation Index](../INDEX.md)

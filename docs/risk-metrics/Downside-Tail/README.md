# Downside & Tail Risks

## Overview

**Lens 3 – Downside & Tail Risks** focuses on extreme loss estimation and "tail" behavior beyond average volatility. This lens emphasizes the distribution of rare, severe events rather than typical market movements.

## Key Risk Metrics

- **Value at Risk (VaR) & Conditional VaR (CVaR / Expected Shortfall):** VaR quantifies loss at a given percentile; CVaR averages losses beyond VaR.
- **Maximum Domain of Attraction (MDA) Diagnosis:** Determining whether extremes follow Fréchet (fat tails), Gumbel (light tails), or Weibull (bounded) distributions.
- **Tail Index (α) Estimation:** Estimating the power-law exponent via Hill estimator or Peaks-Over-Threshold (GPD).
- **κ Metric for Data Sufficiency:** Pre-asymptotic metric of fat-tailedness indicating how much data is needed for stable estimates.
- **Shadow Mean / Shadow Moments:** Estimating true mean under fat-tailed assumptions via EVT rather than biased sample mean.
- **Gap Risk (Jump-to-Ruin, Jumps Over Stops):** Risk that price gaps past stop-loss levels, especially in LTF and overnight moves.
- **Jump-Diffusion Models:** Combining Brownian diffusion with Poisson-driven jumps for realistic pricing.
- **Tail Risk Constraints & Barbell:** Formulating constraints to favor strategies with long-tail convexity.

## Reference

For detailed information, see [Risk Categories Framework](../risk-categories.md#lens-3--downside--tail-risks).

## Related Resources

- [Downside-Tail Implementation](../../src/core/Downside-Tail)
- [TailWarp Main Documentation Index](../INDEX.md)

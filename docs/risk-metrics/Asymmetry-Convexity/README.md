# Asymmetry & Convexity Categories

## Overview

**Lens 5 – Asymmetry & Convexity** focuses on payoff structure and strategies that benefit from volatility and disorder. This lens evaluates whether a portfolio is concave (fragile to volatility) or convex (robust to volatility).

## Key Risk Metrics

- **Convexity Index (CI) / Payoff g(x) Convexity:** A score quantifying curvature of payoff; $CI>1$ means favorable convexity.
- **Sortino Ratio & Downside Deviation:** Sharpe-like ratio focusing on harmful volatility only.
- **Omega Ratio:** Probability-weighted ratio of gains vs losses relative to a threshold return; uses full return distribution.
- **Skewness & Higher Moments:** Third and fourth moments capturing asymmetry and tail weight.
- **Karamata-Point Pricing:** Using tail index and liquid options to price deeper tail options, reducing model dependence.
- **Shadow Greeks:** Option Greeks computed under heavy-tailed assumptions rather than Gaussian vol.
- **Quasi-Static Hedging:** Using static options positions to hedge barrier risks when dynamic hedging fails.

## Reference

For detailed information, see [Risk Categories Framework](../risk-categories.md#lens-5--asymmetry--convexity-categories).

## Related Resources

- [Asymmetry-Convexity Implementation](../../src/core/Asymmetry-Convexity)
- [TailWarp Main Documentation Index](../INDEX.md)

# Liquidity & Market-Structure Categories

## Overview

**Lens 7 – Liquidity & Market-Structure** focuses on the ability to exit positions and the cost of execution. This lens is critical for FX and assets with no volume data, where liquidity metrics are primary risk drivers.

## Key Risk Metrics

- **Bid–Ask Spread & Slippage:** Width of bid–ask; its time variation during stress. Slippage is the cost of execution moving price.
- **Market Impact Models (Almgren–Chriss style):** Models estimating how own execution moves the market.
- **Order-Flow Toxicity / VPIN:** Volume- or Tick-Synchronized PIN measuring probability of informed trading.
- **Depth of Book & Order-Shape Metrics:** Distribution of available quantity at each price level.
- **Liquidity-Adjusted VaR (LVaR):** VaR adjusted for liquidity effects (wider spreads, reduced depth, unwind time).

## Reference

For detailed information, see [Risk Categories Framework](../risk-categories.md#lens-7--liquidity--market-structure-categories).

## Related Resources

- [Liquidity-MarketStructure Implementation](../../src/core/Liquidity-MarketStructure)
- [TailWarp Main Documentation Index](../INDEX.md)

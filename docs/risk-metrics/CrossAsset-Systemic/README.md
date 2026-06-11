# Cross-Asset & Systemic Risks

## Overview

**Lens 10 – Cross-Asset & Systemic** addresses contagion, networks, and system-wide failure. This lens captures how distress in one part of the market or portfolio propagates to others, amplifying losses through interconnected exposures.

## Key Risk Metrics

- **Correlation Instability & Breakdown:** Correlations tend to 1 in crises; diversification fails when needed most.
- **Network Contagion / DebtRank:** Measures how distress propagates through a network of institutions.
- **CoVaR (ΔCoVaR):** Contribution of an institution to systemic VaR; how much worse system risk is during distress.
- **Fire Sale Externalities:** Forced selling by one participant depressing prices and triggering further forced sales.
- **Riemannian / SPD Covariance Manifold Operations:** Treat covariance matrices on the symmetric positive-definite manifold for robust multi-asset analysis.

## Key Formulas

- **CoVaR ($\Delta$CoVaR):** $\text{CoVaR}_\alpha^{j|i} = \text{VaR}_\alpha^j \mid \text{VaR}_\alpha^i$, the VaR of institution $j$ conditional on institution $i$ being in distress. $\Delta\text{CoVaR}$ measures the marginal contribution to systemic risk.
- **DebtRank:** $R_i(t) = \sum_j W_{ij} R_j(t-1)$ where $W_{ij}$ is the liability network weight, measuring systemic impact of distress propagation.
- **SPD Manifold Distance:** $d(A, B) = \|\log(A^{-1/2} B A^{-1/2})\|_F$, the affine-invariant Riemannian distance between SPD covariance matrices.

## Implementation Status

| Metric | Code | Tests |
|--------|------|-------|
| Correlation instability | — | — |
| Network contagion / DebtRank | — | — |
| CoVaR / ΔCoVaR | — | — |
| Fire sale externalities | — | — |
| SPD manifold operations | `src/core/manifolds/spd_operations.cu` (GPU stubs) | — |

## Reference

For detailed information, see [Risk Categories Framework](../risk-categories.md#lens-10--cross-asset--systemic-risks).

## Related Resources

- [CrossAsset-Systemic Implementation](../../src/core/CrossAsset-Systemic)
- [TailWarp Main Documentation Index](../INDEX.md)

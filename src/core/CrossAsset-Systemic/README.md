# CrossAsset-Systemic Implementation

## Overview

This module implements **network contagion, systemic risk, and robust covariance analysis** for multi-asset portfolios.

## Purpose

Quantify and track:
- **Correlation Instability:** Crisis-time correlation breakdown and diversification failure
- **Network Contagion / DebtRank:** Distress propagation through institutional networks
- **CoVaR (ΔCoVaR):** Systemic VaR contribution and contagion spillovers
- **Fire Sale Externalities:** Forced selling cascades and amplified drawdowns
- **SPD Manifold Operations:** Robust covariance estimation using Riemannian geometry

## Key Implementation Areas

- Riemannian SPD manifold operations (affine-invariant, log-Euclidean metrics)
- Robust covariance matrix computation
- Network graph construction and stress propagation
- CoVaR and systemic risk quantification
- Crisis correlation detection and regime switching
- CUDA kernels for efficient multi-asset computation

## Reference Documentation

For conceptual details and risk framework overview, see:
- [CrossAsset-Systemic Risk Documentation](../../docs/risk-metrics/CrossAsset-Systemic)
- [Complete Risk Categories Framework](../../docs/risk-metrics/risk-categories.md#lens-10--cross-asset--systemic-risks)

## Related Components

- [SPD Manifold Operations](../manifolds/spd_operations.cu) – Riemannian geometry for covariance
- [Robust Covariance](../algorithms/robust_covariance.cpp) – Tail-resistant covariance estimation
- [Research Notes](../../docs/research_notes/) – Systemic risk and network contagion literature

# Algorithms

High-level algorithms combining CUDA kernels for trading applications.

## Modules

- `position_sizing.cpp` - CVaR-constrained position sizing
- `robust_covariance.cpp` - Tyler's M-estimator on SPD manifold
- `hedging.cpp` - Riemannian optimization for hedge ratios
- `option_pricing.cpp` - Anchor-based tail pricing

Each algorithm uses kernels from `core/` and wrappers from `wrappers/`.


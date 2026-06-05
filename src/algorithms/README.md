# Algorithms

High-level algorithms combining CUDA kernels for trading applications.

## Modules

- `position_sizing.cpp` - CVaR-constrained position sizing
- `sample_covariance_with_ridge.cpp` - Host sample covariance + ridge (`partial`; Tyler M-estimator `[PLANNED]`)
- `hedging.cpp` - Riemannian optimization for hedge ratios
- `option_pricing.cpp` - Anchor-based tail pricing

Each algorithm uses kernels from `core/` and wrappers from `wrappers/`.


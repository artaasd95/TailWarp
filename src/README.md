# Source Code

Core implementation of geometric methods for tail-aware risk optimization.

## Structure

- `core/` - CUDA kernels for distributions, manifold operations, risk metrics
- `wrappers/` - Host-side C++ wrappers for CUDA kernels
- `algorithms/` - High-level algorithms (optimization, estimation, hedging)
- `reference/` - CPU reference implementations for validation

## Build

CUDA 11.0+ required. All kernels in `core/` are `.cu` files.


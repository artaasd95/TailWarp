# TailWarp Python API

Full reference for `pip install tailwarp` (v1.0).

## Install

| Mode | Command | CUDA toolkit required |
|------|---------|----------------------|
| CPU (default) | `pip install .` | No |
| CUDA extra | `pip install ".[cuda]"` | No at install; native wheel optional |
| Dashboard | `pip install ".[dashboard]"` | No |

See [python/README.md](../python/README.md) and [deployment.md](deployment.md).

## Quick start

```python
from tailwarp import TailWarpClient, WarningStateParams

client = TailWarpClient()
cvar = client.compute_cvar([-0.1, -0.05, 0.0, 0.02, 0.05], alpha=0.95)
print(cvar.value, cvar.method, cvar.device, cvar.elapsed_ms)
```

## `TailWarpClient`

### Constructor

- `prefer_cuda: bool | None` — reads `TAILWARP_PREFER_CUDA` when omitted (default off).

### Methods

#### `compute_cvar(returns, alpha=0.95) -> CvarResult`

Historical CVaR (expected shortfall) on sorted ascending returns.

#### `compute_var(returns, alpha=0.95) -> VarResult`

Historical VaR quantile.

#### `compute_drawdown(equity) -> DrawdownResult`

Maximum drawdown as a positive decimal (0–1).

#### `compute_position_size(max_cvar_limit, underlying_price, ...) -> PositionSizeResult`

CVaR-constrained sizing via Student-t Monte Carlo (CPU NumPy path in v1.0).

#### `compute_warning_state(params: WarningStateParams) -> WarningStateResult`

Deterministic GREEN/YELLOW/RED/CRITICAL bands matching C++.

## Fallback behavior

1. If `tailwarp._native` pybind11 module is importable → host C++ for `compute_cvar`, `compute_var`, `compute_warning_state`.
2. Otherwise → NumPy reference in `cpu_fallback.py` (always available).

CUDA-not-found at runtime does not break import; methods stay on CPU.

## Contract

Frozen public surface: [python-api-contract.md](python-api-contract.md).

## Related

- [ARCHITECTURE_BOUNDARY.md](ARCHITECTURE_BOUNDARY.md)
- [integrations.md](integrations.md) — v2.0 consumer mocks

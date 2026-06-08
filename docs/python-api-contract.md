# Python API contract (v1.0 — frozen)

Public surface for `pip install tailwarp`. No C++ types in signatures.

## `TailWarpClient`

```python
class TailWarpClient:
    def __init__(self, prefer_cuda: bool | None = None) -> None: ...
    def compute_cvar(self, returns: Sequence[float], alpha: float = 0.95) -> CvarResult: ...
    def compute_var(self, returns: Sequence[float], alpha: float = 0.95) -> VarResult: ...
    def compute_drawdown(self, equity: Sequence[float]) -> DrawdownResult: ...
    def compute_position_size(
        self,
        max_cvar_limit: float,
        underlying_price: float,
        n_scenarios: int = 1_000_000,
        nu: float = 4.0,
        alpha: float = 0.95,
        seed: int = 42,
    ) -> PositionSizeResult: ...
    def compute_warning_state(self, params: WarningStateParams) -> WarningStateResult: ...
```

## Result dataclasses

| Type | Fields |
|------|--------|
| `CvarResult` | `value`, `method`, `device`, `elapsed_ms` |
| `VarResult` | `value`, `method`, `device`, `elapsed_ms` |
| `DrawdownResult` | `value`, `method`, `device`, `elapsed_ms` |
| `PositionSizeResult` | `optimal_size`, `expected_cvar`, `expected_return`, `constraint_satisfied`, `method`, `device`, `elapsed_ms` |
| `WarningStateResult` | `state`, `reason`, `triggered_metrics`, `contributions` |

`method` is `"native"` when `_native` pybind11 extension is loaded, else `"numpy"`.
`device` is `"cpu"` unless CUDA dispatch is added in a future release.

## C++ mapping

| Python method | C++ owner | CPU fallback tolerance |
|---------------|-----------|------------------------|
| `compute_cvar` | `src/wrappers/risk_metrics.cpp::compute_cvar` | exact (float32 sort) |
| `compute_var` | `src/wrappers/risk_metrics.cpp::compute_var` | exact |
| `compute_drawdown` | host `max_drawdown_from_equity` | ε = 1e-6 relative |
| `compute_position_size` | `src/algorithms/position_sizing.cpp` | ε = 1% on `optimal_size` (MC) |
| `compute_warning_state` | `src/wrappers/risk_metrics.cpp::compute_warning_state` | exact bands |

## Environment

| Variable | Default | Meaning |
|----------|---------|---------|
| `TAILWARP_PREFER_CUDA` | `0` | Hint for future CUDA dispatch |

## Out of scope v1.0

- Multivariate covariance, SPD manifold, GPU-sorted CVaR in Python API
- Live cross-repo adapters (see [integrations.md](integrations.md))

"""TailWarpClient — public Python API with optional native extension."""

from __future__ import annotations

import os
import time
from typing import Optional, Sequence

from . import cpu_fallback
from .types import CvarResult, DrawdownResult, PositionSizeResult, VarResult
from .warning_state import WarningStateParams, WarningStateResult

_NATIVE = None
_NATIVE_ERROR: Optional[str] = None

try:
    from . import _native as _native_mod

    _NATIVE = _native_mod
except ImportError as exc:
    _NATIVE_ERROR = str(exc)


class TailWarpClient:
    """CPU-first client; optional C++ host bindings when `_native` is built."""

    def __init__(self, prefer_cuda: Optional[bool] = None) -> None:
        if prefer_cuda is None:
            env = os.environ.get("TAILWARP_PREFER_CUDA", "0").strip().lower()
            prefer_cuda = env in ("1", "true", "yes")
        self.prefer_cuda = prefer_cuda
        self._use_native = _NATIVE is not None

    def __repr__(self) -> str:
        backend = "native" if self._use_native else "numpy"
        return f"TailWarpClient(backend={backend}, prefer_cuda={self.prefer_cuda})"

    @property
    def has_native(self) -> bool:
        return self._use_native

    def compute_cvar(
        self,
        returns: Sequence[float],
        alpha: float = 0.95,
    ) -> CvarResult:
        if self._use_native:
            t0 = time.perf_counter()
            value = float(_NATIVE.compute_cvar(list(returns), alpha))
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            device = "cuda" if self.prefer_cuda else "cpu"
            return CvarResult(
                value=value,
                method="native",
                device=device,
                elapsed_ms=elapsed_ms,
            )
        return cpu_fallback.compute_cvar(returns, alpha)

    def compute_var(
        self,
        returns: Sequence[float],
        alpha: float = 0.95,
    ) -> VarResult:
        if self._use_native:
            t0 = time.perf_counter()
            value = float(_NATIVE.compute_var(list(returns), alpha))
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            device = "cuda" if self.prefer_cuda else "cpu"
            return VarResult(
                value=value,
                method="native",
                device=device,
                elapsed_ms=elapsed_ms,
            )
        return cpu_fallback.compute_var_result(returns, alpha)

    def compute_drawdown(self, equity: Sequence[float]) -> DrawdownResult:
        return cpu_fallback.compute_drawdown(equity)

    def compute_position_size(
        self,
        max_cvar_limit: float,
        underlying_price: float,
        n_scenarios: int = 1_000_000,
        nu: float = 4.0,
        alpha: float = 0.95,
        seed: int = 42,
    ) -> PositionSizeResult:
        return cpu_fallback.compute_position_size(
            max_cvar_limit,
            underlying_price,
            n_scenarios=n_scenarios,
            nu=nu,
            alpha=alpha,
            seed=seed,
        )

    def compute_warning_state(
        self,
        params: WarningStateParams,
    ) -> WarningStateResult:
        if self._use_native:
            from .warning_state import WarningState

            raw = _NATIVE.compute_warning_state(
                params.solvency_distance,
                params.max_drawdown,
                params.gross_exposure,
                params.cvar_95,
            )
            return WarningStateResult(
                state=WarningState(raw["state"]),
                reason=raw["reason"],
                triggered_metrics=raw["triggered_metrics"],
            )
        return cpu_fallback.compute_warning_state(params)

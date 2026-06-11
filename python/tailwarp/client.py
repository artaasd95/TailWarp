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
        """Initialize the client.

        Args:
            prefer_cuda: If True, prefer CUDA backend when native is
                available. Defaults to the TAILWARP_PREFER_CUDA env var
                (truthy values: "1", "true", "yes").
        """
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
        """Whether the C++ native extension is available."""
        return self._use_native

    def compute_cvar(
        self,
        returns: Sequence[float],
        alpha: float = 0.95,
    ) -> CvarResult:
        """Compute Conditional Value at Risk (Expected Shortfall).

        Args:
            returns: Historical return series.
            alpha: Confidence level (default 0.95).

        Returns:
            CvarResult containing the CVaR value and metadata.
        """
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
        """Compute Value at Risk.

        Args:
            returns: Historical return series.
            alpha: Confidence level (default 0.95).

        Returns:
            VarResult containing the VaR value and metadata.
        """
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
        """Compute maximum drawdown from an equity curve.

        Args:
            equity: Equity curve values over time.

        Returns:
            DrawdownResult containing the max drawdown and metadata.
        """
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
        """Compute position size subject to a CVaR constraint.

        Uses Monte Carlo simulation under a Student-t distribution to
        find the maximum position size whose expected CVaR does not
        exceed the given limit.

        Args:
            max_cvar_limit: Maximum acceptable CVaR in currency units.
            underlying_price: Current price of the underlying asset.
            n_scenarios: Number of Monte Carlo scenarios.
            nu: Student-t degrees of freedom (default 4.0).
            alpha: CVaR confidence level (default 0.95).
            seed: RNG seed for reproducibility.

        Returns:
            PositionSizeResult with optimal size and diagnostics.
        """
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
        """Compute the aggregate warning state from risk metrics.

        Aggregates solvency distance, max drawdown, gross exposure, and
        CVaR into a single GREEN/YELLOW/RED/CRITICAL state.

        Args:
            params: WarningStateParams with all input metrics.

        Returns:
            WarningStateResult with overall state and per-metric
            contributions.
        """
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

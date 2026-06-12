"""NumPy reference implementations matching C++ host wrappers."""

from __future__ import annotations

import math
import time
from typing import Sequence

import numpy as np

from .types import (
    CvarResult,
    DrawdownResult,
    PositionSizeResult,
    VarResult,
)
from .warning_state import (
    WarningState,
    WarningStateParams,
    WarningStateResult,
    MetricContribution,
)


def _validate_alpha(alpha: float) -> None:
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"alpha must be in (0, 1), got {alpha!r}")


def _tail_count(n: int, alpha: float) -> int:
    return max(1, min(n, int(math.ceil((1.0 - alpha) * n))))


def _numpy_cvar(arr: np.ndarray, alpha: float) -> float:
    """CVaR on a NumPy array using partition (O(n) average)."""
    _validate_alpha(alpha)
    n = len(arr)
    if n == 0:
        return 0.0
    k = _tail_count(n, alpha)
    partitioned = np.partition(arr, k - 1)
    return float(partitioned[:k].mean())


def compute_var(returns: Sequence[float], alpha: float = 0.95) -> float:
    """Compute Value at Risk as the empirical quantile of returns.

    Args:
        returns: Historical return series.
        alpha: Confidence level (default 0.95).

    Returns:
        The VaR value at the given confidence level.
    """
    _validate_alpha(alpha)
    if not returns:
        return 0.0
    sorted_r = sorted(returns)
    n = len(sorted_r)
    k = _tail_count(n, alpha)
    return float(sorted_r[k - 1])


def compute_cvar_value(returns: Sequence[float], alpha: float = 0.95) -> float:
    """Compute CVaR (Expected Shortfall) as the mean of tail losses.

    Args:
        returns: Historical return series.
        alpha: Confidence level (default 0.95).

    Returns:
        The CVaR value (mean loss beyond the VaR threshold).
    """
    _validate_alpha(alpha)
    if not returns:
        return 0.0
    sorted_r = sorted(returns)
    n = len(sorted_r)
    k = _tail_count(n, alpha)
    return float(sum(sorted_r[:k]) / float(k))


def compute_cvar(returns: Sequence[float], alpha: float = 0.95) -> CvarResult:
    """Compute CVaR and return a CvarResult with timing metadata.

    Args:
        returns: Historical return series.
        alpha: Confidence level (default 0.95).

    Returns:
        CvarResult with the computed value and elapsed time.
    """
    t0 = time.perf_counter()
    value = compute_cvar_value(returns, alpha)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    return CvarResult(
        value=value,
        method="numpy",
        device="cpu",
        elapsed_ms=elapsed_ms,
    )


def compute_var_result(returns: Sequence[float], alpha: float = 0.95) -> VarResult:
    """Compute VaR and return a VarResult with timing metadata.

    Args:
        returns: Historical return series.
        alpha: Confidence level (default 0.95).

    Returns:
        VarResult with the computed value and elapsed time.
    """
    t0 = time.perf_counter()
    value = compute_var(returns, alpha)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    return VarResult(
        value=value,
        method="numpy",
        device="cpu",
        elapsed_ms=elapsed_ms,
    )


def max_drawdown_from_equity(equity: Sequence[float]) -> float:
    """Compute maximum drawdown from an equity curve.

    Args:
        equity: Equity curve values over time.

    Returns:
        Maximum drawdown as a fraction of peak equity.
    """
    if not equity:
        return 0.0
    peak = float(equity[0])
    max_dd = 0.0
    for e in equity:
        peak = max(peak, float(e))
        if peak > 0:
            dd = (peak - float(e)) / peak
            max_dd = max(max_dd, dd)
    return max_dd


def compute_drawdown(equity: Sequence[float]) -> DrawdownResult:
    """Compute maximum drawdown and return a DrawdownResult.

    Args:
        equity: Equity curve values over time.

    Returns:
        DrawdownResult with the max drawdown and elapsed time.
    """
    t0 = time.perf_counter()
    value = max_drawdown_from_equity(equity)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    return DrawdownResult(
        value=value,
        method="numpy",
        device="cpu",
        elapsed_ms=elapsed_ms,
    )


def _student_t_samples(n: int, nu: float, seed: int) -> np.ndarray:
    """Generate Student-t distributed random samples.

    Args:
        n: Number of samples.
        nu: Degrees of freedom.
        seed: RNG seed.

    Returns:
        Array of Student-t samples as float32.
    """
    rng = np.random.default_rng(seed)
    return rng.standard_t(df=nu, size=n).astype(np.float32)


def compute_position_size(
    max_cvar_limit: float,
    underlying_price: float,
    n_scenarios: int = 1_000_000,
    nu: float = 4.0,
    alpha: float = 0.95,
    seed: int = 42,
) -> PositionSizeResult:
    """Compute position size under a CVaR constraint via Student-t MC.

    Simulates unit-return scenarios from a Student-t distribution,
    then scales the position so that the expected CVaR does not exceed
    max_cvar_limit.

    Args:
        max_cvar_limit: Maximum acceptable CVaR in currency.
        underlying_price: Current price of the underlying.
        n_scenarios: Number of Monte Carlo scenarios.
        nu: Student-t degrees of freedom.
        alpha: CVaR confidence level.
        seed: RNG seed.

    Returns:
        PositionSizeResult with optimal size and diagnostic fields.
    """
    t0 = time.perf_counter()

    def elapsed() -> float:
        return (time.perf_counter() - t0) * 1000.0

    if max_cvar_limit <= 0.0 or underlying_price <= 0.0 or n_scenarios < 2:
        return PositionSizeResult(
            optimal_size=0.0,
            expected_cvar=0.0,
            expected_return=0.0,
            constraint_satisfied=False,
            method="numpy",
            device="cpu",
            elapsed_ms=elapsed(),
        )

    samples = _student_t_samples(n_scenarios, nu, seed)
    unit_cvar = _numpy_cvar(samples, alpha)
    denom = abs(unit_cvar)
    if denom < 1e-12:
        return PositionSizeResult(
            optimal_size=0.0,
            expected_cvar=0.0,
            expected_return=0.0,
            constraint_satisfied=True,
            method="numpy",
            device="cpu",
            elapsed_ms=elapsed(),
        )

    w = max_cvar_limit / denom
    expected_cvar = float(w * unit_cvar)
    expected_return = float(np.mean(w * samples))
    constraint_satisfied = abs(expected_cvar) <= max_cvar_limit * (1.0 + 1e-4)
    return PositionSizeResult(
        optimal_size=w / underlying_price,
        expected_cvar=expected_cvar,
        expected_return=expected_return,
        constraint_satisfied=constraint_satisfied,
        method="numpy",
        device="cpu",
        elapsed_ms=elapsed(),
    )


def _non_finite_level(name: str, v: float) -> tuple[WarningState, str]:
    return WarningState.CRITICAL, f"{name} non-finite ({v}) (CRITICAL)"


def _level_solvency(v: float) -> tuple[WarningState, str]:
    """Classify solvency distance into a warning level."""
    if not math.isfinite(v):
        return _non_finite_level("solvency_distance", v)
    if v <= 1.0:
        return WarningState.CRITICAL, "solvency_distance ≤ 1σ (CRITICAL)"
    if v <= 2.0:
        return WarningState.RED, "solvency_distance 1-2σ (RED)"
    if v <= 3.0:
        return WarningState.YELLOW, "solvency_distance 2-3σ (YELLOW)"
    return WarningState.GREEN, "solvency_distance > 3σ (GREEN)"


def _level_drawdown(v: float) -> tuple[WarningState, str]:
    """Classify max drawdown into a warning level."""
    if not math.isfinite(v):
        return _non_finite_level("max_drawdown", v)
    if v >= 0.60:
        return WarningState.CRITICAL, "max_drawdown ≥ 60% (CRITICAL)"
    if v >= 0.40:
        return WarningState.RED, "max_drawdown 40-60% (RED)"
    if v >= 0.20:
        return WarningState.YELLOW, "max_drawdown 20-40% (YELLOW)"
    return WarningState.GREEN, "max_drawdown < 20% (GREEN)"


def _level_exposure(v: float) -> tuple[WarningState, str]:
    """Classify gross exposure into a warning level."""
    if not math.isfinite(v):
        return _non_finite_level("gross_exposure", v)
    if v >= 8.0:
        return WarningState.CRITICAL, "gross_exposure ≥ 8x (CRITICAL)"
    if v >= 5.0:
        return WarningState.RED, "gross_exposure 5-8x (RED)"
    if v >= 3.0:
        return WarningState.YELLOW, "gross_exposure 3-5x (YELLOW)"
    return WarningState.GREEN, "gross_exposure < 3x (GREEN)"


def _level_cvar(v: float) -> tuple[WarningState, str]:
    """Classify CVaR@95% into a warning level."""
    if not math.isfinite(v):
        return _non_finite_level("cvar_95", v)
    if v <= -0.25:
        return WarningState.CRITICAL, "CVaR@95% ≤ -25% (CRITICAL)"
    if v <= -0.15:
        return WarningState.RED, "CVaR@95% -15% to -25% (RED)"
    if v <= -0.10:
        return WarningState.YELLOW, "CVaR@95% -10% to -15% (YELLOW)"
    return WarningState.GREEN, "CVaR@95% > -10% (GREEN)"


def compute_warning_state(params: WarningStateParams) -> WarningStateResult:
    """Compute aggregate warning state from multiple risk metrics.

    Evaluates solvency distance, max drawdown, gross exposure, and
    CVaR@95% against thresholds, then returns the most severe level.

    Args:
        params: WarningStateParams containing all input metrics.

    Returns:
        WarningStateResult with overall state and per-metric details.
    """
    checks = [
        ("solvency_distance", params.solvency_distance, _level_solvency),
        ("max_drawdown", params.max_drawdown, _level_drawdown),
        ("gross_exposure", params.gross_exposure, _level_exposure),
        ("cvar_95", params.cvar_95, _level_cvar),
    ]
    contributions: list[MetricContribution] = []
    levels: list[WarningState] = []
    triggered = 0
    for i, (name, value, fn) in enumerate(checks):
        level, msg = fn(value)
        levels.append(level)
        contributions.append(MetricContribution(name, level, value, msg))
        if level > WarningState.GREEN:
            triggered |= 1 << i

    overall = max(levels, key=lambda s: s.value)
    triggered_msgs = [c.message for c in contributions if c.level > WarningState.GREEN]
    if triggered_msgs:
        reason = f"WarningState {overall.name}: " + " | ".join(triggered_msgs)
    else:
        reason = "WarningState GREEN: All metrics healthy"

    return WarningStateResult(
        state=overall,
        reason=reason,
        triggered_metrics=triggered,
        contributions=contributions,
    )

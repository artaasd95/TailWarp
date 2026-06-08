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


def compute_var(returns: Sequence[float], alpha: float = 0.95) -> float:
    if not returns:
        return 0.0
    sorted_r = sorted(returns)
    n = len(sorted_r)
    k = max(1, min(n, int(math.ceil((1.0 - alpha) * n))))
    return float(sorted_r[k - 1])


def compute_cvar_value(returns: Sequence[float], alpha: float = 0.95) -> float:
    if not returns:
        return 0.0
    sorted_r = sorted(returns)
    n = len(sorted_r)
    k = max(1, min(n, int(math.ceil((1.0 - alpha) * n))))
    return float(sum(sorted_r[:k]) / float(k))


def compute_cvar(returns: Sequence[float], alpha: float = 0.95) -> CvarResult:
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
    t0 = time.perf_counter()
    elapsed = lambda: (time.perf_counter() - t0) * 1000.0

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
    unit_cvar = compute_cvar_value(samples.tolist(), alpha)
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
    scaled = (w * samples).tolist()
    expected_cvar = compute_cvar_value(scaled, alpha)
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


def _level_solvency(v: float) -> tuple[WarningState, str]:
    if v <= 1.0:
        return WarningState.CRITICAL, "solvency_distance ≤ 1σ (CRITICAL)"
    if v <= 2.0:
        return WarningState.RED, "solvency_distance 1-2σ (RED)"
    if v <= 3.0:
        return WarningState.YELLOW, "solvency_distance 2-3σ (YELLOW)"
    return WarningState.GREEN, "solvency_distance > 3σ (GREEN)"


def _level_drawdown(v: float) -> tuple[WarningState, str]:
    if v >= 0.60:
        return WarningState.CRITICAL, "max_drawdown ≥ 60% (CRITICAL)"
    if v >= 0.40:
        return WarningState.RED, "max_drawdown 40-60% (RED)"
    if v >= 0.20:
        return WarningState.YELLOW, "max_drawdown 20-40% (YELLOW)"
    return WarningState.GREEN, "max_drawdown < 20% (GREEN)"


def _level_exposure(v: float) -> tuple[WarningState, str]:
    if v >= 8.0:
        return WarningState.CRITICAL, "gross_exposure ≥ 8x (CRITICAL)"
    if v >= 5.0:
        return WarningState.RED, "gross_exposure 5-8x (RED)"
    if v >= 3.0:
        return WarningState.YELLOW, "gross_exposure 3-5x (YELLOW)"
    return WarningState.GREEN, "gross_exposure < 3x (GREEN)"


def _level_cvar(v: float) -> tuple[WarningState, str]:
    if v <= -0.25:
        return WarningState.CRITICAL, "CVaR@95% ≤ -25% (CRITICAL)"
    if v <= -0.15:
        return WarningState.RED, "CVaR@95% -15% to -25% (RED)"
    if v <= -0.10:
        return WarningState.YELLOW, "CVaR@95% -10% to -15% (YELLOW)"
    return WarningState.GREEN, "CVaR@95% > -10% (GREEN)"


def compute_warning_state(params: WarningStateParams) -> WarningStateResult:
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

"""
CPU-side risk metrics and TailWarpWarningState for the Black Swan benchmark path.

Mirrors threshold logic in src/wrappers/risk_metrics.cpp (S2-02 / S3-03).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Iterable, Sequence


class WarningState(IntEnum):
    GREEN = 0
    YELLOW = 1
    RED = 2
    CRITICAL = 3


METRIC_NAMES = (
    "solvency_distance",
    "max_drawdown",
    "gross_exposure",
    "cvar_95",
)


@dataclass
class WarningStateParams:
    solvency_distance: float
    max_drawdown: float
    gross_exposure: float
    cvar_95: float


@dataclass
class MetricContribution:
    name: str
    level: WarningState
    value: float
    message: str


@dataclass
class WarningStateResult:
    state: WarningState
    reason: str
    triggered_metrics: int
    contributions: list[MetricContribution] = field(default_factory=list)

    def triggered_names(self) -> list[str]:
        return [
            METRIC_NAMES[i]
            for i in range(len(METRIC_NAMES))
            if self.triggered_metrics & (1 << i)
        ]

    def to_dict(self) -> dict:
        return {
            "state": self.state.name,
            "reason": self.reason,
            "triggered_metrics": self.triggered_names(),
            "contributions": {
                c.name: {
                    "level": c.level.name,
                    "value": c.value,
                    "message": c.message,
                }
                for c in self.contributions
            },
        }


def compute_var(returns: Sequence[float], alpha: float = 0.95) -> float:
    if not returns:
        return 0.0
    sorted_r = sorted(returns)
    n = len(sorted_r)
    k = max(1, min(n, int(__import__("math").ceil((1.0 - alpha) * n))))
    return sorted_r[k - 1]


def compute_cvar(returns: Sequence[float], alpha: float = 0.95) -> float:
    if not returns:
        return 0.0
    sorted_r = sorted(returns)
    n = len(sorted_r)
    k = max(1, min(n, int(__import__("math").ceil((1.0 - alpha) * n))))
    return sum(sorted_r[:k]) / float(k)


def max_drawdown_from_equity(equity: Sequence[float]) -> float:
    """Maximum drawdown as a positive decimal (0–1), matching C++ convention."""
    if not equity:
        return 0.0
    peak = equity[0]
    max_dd = 0.0
    for e in equity:
        peak = max(peak, e)
        if peak > 0:
            dd = (peak - e) / peak
            max_dd = max(max_dd, dd)
    return max_dd


def compute_solvency_distance(
    equity: float,
    initial_equity: float,
    rolling_std: float,
    ruin_fraction: float = 0.5,
) -> float:
    """Approximate σ-distance to a ruin floor (CPU benchmark path)."""
    if rolling_std <= 1e-12 or equity <= 0 or initial_equity <= 0:
        return 99.0
    ruin_equity = initial_equity * ruin_fraction
    if equity <= ruin_equity:
        return 0.0
    loss_to_ruin = (equity - ruin_equity) / equity
    return loss_to_ruin / rolling_std


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


_STATE_SCORE = {
    WarningState.GREEN: 0.05,
    WarningState.YELLOW: 0.35,
    WarningState.RED: 0.65,
    WarningState.CRITICAL: 0.92,
}


def warning_state_to_score(result: WarningStateResult) -> float:
    """Map warning state to a 0–1 alert score for benchmark comparison."""
    base = _STATE_SCORE[result.state]
    if result.state == WarningState.GREEN:
        return base
    # Nudge score upward when multiple metrics fire.
    n = len(result.triggered_names())
    return min(0.99, base + 0.03 * max(0, n - 1))


def replay_composite_score(
    params: WarningStateParams,
    rolling_std: float,
) -> float:
    """
    Continuous stress score from the same four benchmark inputs.

    Uses softer normalization for short replays so alerts fire before the
    formal S2-02 bands on mild synthetic series; warning_state still uses
    strict thresholds.
    """
    ws_score = warning_state_to_score(compute_warning_state(params))
    dd_signal = min(1.0, params.max_drawdown / 0.025)
    exp_signal = min(1.0, max(0.0, params.gross_exposure - 0.55) / 0.35)
    cvar_signal = min(1.0, max(0.0, -params.cvar_95 - 0.008) / 0.008)
    vol_signal = min(1.0, rolling_std / 0.006)
    composite = max(
        ws_score,
        dd_signal * 0.85,
        exp_signal * 0.90,
        cvar_signal * 0.95,
        vol_signal * 0.80,
    )
    return min(0.99, composite)


def ewma_variance(returns: Iterable[float], lam: float) -> list[float]:
    out: list[float] = []
    var = 0.0
    for r in returns:
        var = lam * var + (1.0 - lam) * (r * r)
        out.append(var)
    return out

"""
CPU-side risk metrics for the Black Swan benchmark path.

Core metrics delegate to the `tailwarp` package (SP-PYAPI); benchmark-only
helpers remain here.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

_REPO = Path(__file__).resolve().parents[1]
_PYTHON = _REPO / "python"
if str(_PYTHON) not in sys.path:
    sys.path.insert(0, str(_PYTHON))

from tailwarp.cpu_fallback import (  # noqa: E402
    compute_cvar_value as _cvar_value,
    compute_var,
    max_drawdown_from_equity,
)
from tailwarp.cpu_fallback import compute_warning_state  # noqa: E402
from tailwarp.warning_state import (  # noqa: E402
    METRIC_NAMES,
    MetricContribution,
    WarningState,
    WarningStateParams,
    WarningStateResult,
)

__all__ = [
    "WarningState",
    "WarningStateParams",
    "WarningStateResult",
    "MetricContribution",
    "METRIC_NAMES",
    "compute_var",
    "compute_cvar",
    "max_drawdown_from_equity",
    "compute_solvency_distance",
    "compute_warning_state",
    "warning_state_to_score",
    "replay_composite_score",
    "ewma_variance",
]

# Replay composite score tuning (CPU short-series heuristic; not S2-02 formal bands).
_DD_SATURATION = 0.025
_EXP_ONSET = 0.55
_EXP_RANGE = 0.35
_CVAR_ONSET = 0.008
_VOL_SATURATION = 0.006
_WEIGHT_DD = 0.85
_WEIGHT_EXP = 0.90
_WEIGHT_CVAR = 0.95
_WEIGHT_VOL = 0.80


def compute_cvar(returns, alpha: float = 0.95) -> float:
    """Scalar CVaR for benchmark scripts (returns value only)."""
    return _cvar_value(returns, alpha)


def compute_solvency_distance(
    equity: float,
    initial_equity: float,
    rolling_std: float,
    ruin_fraction: float = 0.5,
) -> float:
    """Heuristic ruin-distance ratio for CPU replay (not true σ-distance).

    Computes ``(equity_buffer_fraction) / rolling_return_std`` where the buffer
    is ``(equity - ruin_floor) / equity``. This is a dimensionless replay
    heuristic, not the CVaR-scale solvency distance in
    ``src/core/Structural-Ruin/solvency_distance.cu``. Warning-state thresholds
    applied to this value are approximate on short CPU replays.
    """
    if rolling_std <= 1e-12 or equity <= 0 or initial_equity <= 0:
        return 99.0
    ruin_equity = initial_equity * ruin_fraction
    if equity <= ruin_equity:
        return 0.0
    loss_to_ruin = (equity - ruin_equity) / equity
    return loss_to_ruin / rolling_std


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
    n = len(result.triggered_names())
    return min(0.99, base + 0.03 * max(0, n - 1))


def replay_composite_score(
    params: WarningStateParams,
    rolling_std: float,
) -> float:
    """Continuous stress score for short CPU replays."""
    ws_score = warning_state_to_score(compute_warning_state(params))
    dd_signal = min(1.0, params.max_drawdown / _DD_SATURATION)
    exp_signal = min(1.0, max(0.0, params.gross_exposure - _EXP_ONSET) / _EXP_RANGE)
    cvar_signal = min(1.0, max(0.0, -params.cvar_95 - _CVAR_ONSET) / _CVAR_ONSET)
    vol_signal = min(1.0, rolling_std / _VOL_SATURATION)
    composite = max(
        ws_score,
        dd_signal * _WEIGHT_DD,
        exp_signal * _WEIGHT_EXP,
        cvar_signal * _WEIGHT_CVAR,
        vol_signal * _WEIGHT_VOL,
    )
    return min(0.99, composite)


def ewma_variance(returns: Iterable[float], lam: float) -> list[float]:
    out: list[float] = []
    var = 0.0
    for r in returns:
        var = lam * var + (1.0 - lam) * (r * r)
        out.append(var)
    return out

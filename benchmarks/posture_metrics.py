"""
S5 posture metrics for Black Swan replay bundles (CPU heuristics).

Full Lens-5 convexity kernels live under src/core/Asymmetry-Convexity/ (stubs).
SPD manifold and robust covariance are excluded from headline posture rows.
"""

from __future__ import annotations

import math
from typing import Any, Sequence

# Headline posture excludes incomplete Phase-2 pipelines (S5-02 acceptance).
EXCLUDED_FROM_HEADLINE = ("spd_manifold", "robust_covariance")

POSTURE_STATUS_CPU = "cpu_replay_heuristic"
POSTURE_STATUS_NOT_IMPLEMENTED = "not_implemented"


def compute_convexity_score(returns: Sequence[float]) -> float:
    """
    Payoff asymmetry in [-1, 1]: (sum gains - sum |losses|) / (sum gains + sum |losses|).
    Positive => upside-heavy replay; negative => downside-heavy.
    """
    if not returns:
        return 0.0
    gains = sum(r for r in returns if r > 0)
    losses = sum(abs(r) for r in returns if r < 0)
    total = gains + losses
    if total < 1e-12:
        return 0.0
    return max(-1.0, min(1.0, (gains - losses) / total))


def compute_antifragility_posture(returns: Sequence[float], convexity: float) -> str:
    """
    Coarse posture from tail payoff shape (not option convexity CI).
    """
    if len(returns) < 4:
        return "insufficient_data"
    sorted_r = sorted(returns)
    n = len(sorted_r)
    k = max(1, n // 20)
    tail_gain = sum(sorted_r[-k:]) / k
    tail_loss = sum(sorted_r[:k]) / k
    tail_spread = tail_gain + tail_loss  # tail_loss is negative
    if convexity > 0.15 and tail_spread > 0:
        return "antifragile_lean"
    if convexity < -0.15 and tail_spread < 0:
        return "fragile"
    return "neutral"


def compute_complexity_regime(returns: Sequence[float]) -> str:
    """Regime label from rolling-vol stability across the replay."""
    if len(returns) < 6:
        return "insufficient_data"
    mid = len(returns) // 2
    first = returns[:mid]
    second = returns[mid:]

    def _std(xs: Sequence[float]) -> float:
        if len(xs) < 2:
            return 0.0
        m = sum(xs) / len(xs)
        var = sum((x - m) ** 2 for x in xs) / len(xs)
        return math.sqrt(var)

    s1, s2 = _std(first), _std(second)
    if s1 < 1e-12 and s2 < 1e-12:
        return "stable"
    ratio = s2 / s1 if s1 > 1e-12 else (s2 / 1e-12)
    if ratio >= 1.5:
        return "elevated_vol"
    if ratio <= 0.67:
        return "compressing_vol"
    return "stable"


def compute_posture_block(returns: Sequence[float]) -> dict[str, Any]:
    """Build the `posture` object for results.json (schema v2+)."""
    convexity = compute_convexity_score(returns)
    return {
        "convexity_score": round(convexity, 6),
        "antifragility_posture": compute_antifragility_posture(returns, convexity),
        "complexity_regime": compute_complexity_regime(returns),
        "status": POSTURE_STATUS_CPU,
        "excluded_from_headline": list(EXCLUDED_FROM_HEADLINE),
    }

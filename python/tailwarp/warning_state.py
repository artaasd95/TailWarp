"""TailWarpWarningState — mirrors src/wrappers/risk_metrics.h."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum


class WarningState(IntEnum):
    """Warning severity levels."""
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
    """Input parameters for warning state computation.

    Attributes:
        solvency_distance: Distance to ruin in CVaR-scale units.
        max_drawdown: Current maximum drawdown as a fraction.
        gross_exposure: Gross leverage ratio (notional / equity).
        cvar_95: CVaR at 95% confidence level.
    """
    solvency_distance: float
    max_drawdown: float
    gross_exposure: float
    cvar_95: float


@dataclass
class MetricContribution:
    """Contribution of a single metric to the warning state.

    Attributes:
        name: Metric name (e.g. "solvency_distance").
        level: Warning level for this metric.
        value: Raw metric value.
        message: Human-readable explanation of the level.
    """
    name: str
    level: WarningState
    value: float
    message: str


@dataclass
class WarningStateResult:
    """Aggregate warning state across all monitored metrics.

    Attributes:
        state: Overall worst-case warning level.
        reason: Human-readable summary of triggered warnings.
        triggered_metrics: Bitmask of triggered metric indices.
        contributions: Per-metric contributions to the state.
    """
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

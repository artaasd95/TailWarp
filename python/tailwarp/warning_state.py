"""TailWarpWarningState — mirrors src/wrappers/risk_metrics.h."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum


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

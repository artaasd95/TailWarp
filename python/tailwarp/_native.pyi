from typing import TypedDict


class WarningStateDict(TypedDict):
    state: int
    reason: str
    triggered_metrics: int


def compute_cvar(returns: list[float], alpha: float = ...) -> float: ...
def compute_var(returns: list[float], alpha: float = ...) -> float: ...
def compute_warning_state(
    solvency_distance: float,
    max_drawdown: float,
    gross_exposure: float,
    cvar_95: float,
) -> WarningStateDict: ...

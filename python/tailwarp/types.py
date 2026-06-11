"""Public result types for TailWarpClient."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CvarResult:
    """Result of a CVaR (Expected Shortfall) computation.

    Attributes:
        value: The CVaR value (mean loss beyond VaR threshold).
        method: Backend used ("native" or "numpy").
        device: Device used ("cuda" or "cpu").
        elapsed_ms: Wall-clock time in milliseconds.
    """
    value: float
    method: str
    device: str
    elapsed_ms: float


@dataclass(frozen=True)
class DrawdownResult:
    """Result of a maximum drawdown computation.

    Attributes:
        value: Maximum drawdown as a fraction of peak value.
        method: Backend used ("numpy").
        device: Device used ("cpu").
        elapsed_ms: Wall-clock time in milliseconds.
    """
    value: float
    method: str
    device: str
    elapsed_ms: float


@dataclass(frozen=True)
class PositionSizeResult:
    """Result of CVaR-constrained position sizing.

    Attributes:
        optimal_size: Optimal position size (number of units).
        expected_cvar: Expected CVaR of the sized position.
        expected_return: Expected return of the sized position.
        constraint_satisfied: Whether the CVaR constraint was met.
        method: Backend used ("numpy").
        device: Device used ("cpu").
        elapsed_ms: Wall-clock time in milliseconds.
    """
    optimal_size: float
    expected_cvar: float
    expected_return: float
    constraint_satisfied: bool
    method: str
    device: str
    elapsed_ms: float


@dataclass(frozen=True)
class VarResult:
    """Result of a VaR (Value at Risk) computation.

    Attributes:
        value: The VaR value (loss quantile at the given confidence level).
        method: Backend used ("native" or "numpy").
        device: Device used ("cuda" or "cpu").
        elapsed_ms: Wall-clock time in milliseconds.
    """
    value: float
    method: str
    device: str
    elapsed_ms: float

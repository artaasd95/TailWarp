"""Public result types for TailWarpClient."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CvarResult:
    value: float
    method: str
    device: str
    elapsed_ms: float


@dataclass(frozen=True)
class DrawdownResult:
    value: float
    method: str
    device: str
    elapsed_ms: float


@dataclass(frozen=True)
class PositionSizeResult:
    optimal_size: float
    expected_cvar: float
    expected_return: float
    constraint_satisfied: bool
    method: str
    device: str
    elapsed_ms: float


@dataclass(frozen=True)
class VarResult:
    value: float
    method: str
    device: str
    elapsed_ms: float

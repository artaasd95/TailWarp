"""TailWarp Python API (v1.0)."""

from .client import TailWarpClient
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
)

__all__ = [
    "TailWarpClient",
    "CvarResult",
    "DrawdownResult",
    "PositionSizeResult",
    "VarResult",
    "WarningState",
    "WarningStateParams",
    "WarningStateResult",
    "__version__",
]

__version__ = "1.0.0"

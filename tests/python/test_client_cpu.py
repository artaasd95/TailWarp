"""CPU-path unit tests for TailWarpClient (SP-PYAPI-06)."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "python"))

from tailwarp import TailWarpClient, WarningState, WarningStateParams


@pytest.fixture
def client() -> TailWarpClient:
    return TailWarpClient(prefer_cuda=False)


class TestComputeCvar:
    def test_simple_tail(self, client: TailWarpClient) -> None:
        returns = [-0.1, -0.05, 0.0, 0.02, 0.05]
        result = client.compute_cvar(returns, 0.8)
        assert result.value == pytest.approx(-0.1, abs=1e-6)
        assert result.method == "numpy"
        assert result.device == "cpu"
        assert result.elapsed_ms >= 0.0

    def test_empty_returns(self, client: TailWarpClient) -> None:
        result = client.compute_cvar([], 0.95)
        assert result.value == 0.0

    def test_monotonicity_by_alpha(self, client: TailWarpClient) -> None:
        returns = [float(i - 50) / 100.0 for i in range(100)]
        c90 = client.compute_cvar(returns, 0.90).value
        c95 = client.compute_cvar(returns, 0.95).value
        c99 = client.compute_cvar(returns, 0.99).value
        assert c99 < c95 < c90

    def test_var_quantile(self, client: TailWarpClient) -> None:
        returns = [-0.3, -0.2, 0.0, 0.1]
        result = client.compute_var(returns, 0.75)
        assert result.value == pytest.approx(-0.3, abs=1e-6)


class TestComputeDrawdown:
    def test_peak_trough(self, client: TailWarpClient) -> None:
        equity = [1.0, 1.1, 0.9, 0.95]
        result = client.compute_drawdown(equity)
        assert result.value == pytest.approx((1.1 - 0.9) / 1.1, rel=1e-4)

    def test_empty(self, client: TailWarpClient) -> None:
        assert client.compute_drawdown([]).value == 0.0


class TestPositionSize:
    def test_valid_result(self, client: TailWarpClient) -> None:
        result = client.compute_position_size(
            max_cvar_limit=0.05,
            underlying_price=100.0,
            n_scenarios=10_000,
            nu=4.0,
            alpha=0.95,
            seed=42,
        )
        assert result.optimal_size >= 0.0
        assert result.constraint_satisfied
        assert result.method == "numpy"


class TestWarningState:
    def test_all_green(self, client: TailWarpClient) -> None:
        params = WarningStateParams(8.0, 0.05, 2.0, -0.08)
        result = client.compute_warning_state(params)
        assert result.state == WarningState.GREEN
        assert result.triggered_metrics == 0

    def test_solvency_critical(self, client: TailWarpClient) -> None:
        params = WarningStateParams(0.8, 0.05, 2.0, -0.08)
        result = client.compute_warning_state(params)
        assert result.state == WarningState.CRITICAL
        assert "solvency_distance" in result.triggered_names()

    def test_nan_input_rejected_or_finite(self, client: TailWarpClient) -> None:
        params = WarningStateParams(
            float("nan"), 0.05, 2.0, -0.08
        )
        result = client.compute_warning_state(params)
        assert result.state in WarningState
        assert not math.isnan(result.state.value)

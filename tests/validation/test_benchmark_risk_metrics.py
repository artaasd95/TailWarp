"""Validation tests for CPU benchmark-path risk metrics (S3-04)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from benchmarks.risk_metrics import (  # noqa: E402
    WarningState,
    WarningStateParams,
    compute_cvar,
    compute_solvency_distance,
    compute_var,
    compute_warning_state,
    ewma_variance,
    max_drawdown_from_equity,
    replay_composite_score,
)

# Technical debt TD-TW-02: GPU vs CPU CVaR parity — see Tech-Debt.md and docs/VALIDATION.md.
GPU_CVAR_PARITY_DEFERRED = True
TD_TW_02_DOC = "Tech-Debt.md"


class TestCVaR:
    def test_simple_tail(self):
        returns = [-0.1, -0.05, 0.0, 0.02, 0.05]
        assert compute_cvar(returns, 0.8) == pytest.approx(-0.1, abs=1e-6)

    def test_var_quantile(self):
        returns = [-0.3, -0.2, 0.0, 0.1]
        assert compute_var(returns, 0.75) == pytest.approx(-0.3, abs=1e-6)

    def test_monotonicity_by_alpha(self):
        returns = [float(i - 50) / 100.0 for i in range(100)]
        c90 = compute_cvar(returns, 0.90)
        c95 = compute_cvar(returns, 0.95)
        c99 = compute_cvar(returns, 0.99)
        assert c99 < c95 < c90

    @pytest.mark.parametrize("alpha", [0.0, 1.0, -0.1, 1.5, float("nan")])
    def test_invalid_alpha_raises(self, alpha: float):
        with pytest.raises(ValueError, match="alpha must be in"):
            compute_cvar([-0.1, 0.1], alpha)
        with pytest.raises(ValueError, match="alpha must be in"):
            compute_var([-0.1, 0.1], alpha)


class TestDrawdown:
    def test_peak_trough(self):
        equity = [1.0, 1.1, 0.9, 0.95]
        assert max_drawdown_from_equity(equity) == pytest.approx((1.1 - 0.9) / 1.1, rel=1e-4)


class TestSolvencyDistance:
    def test_at_ruin_floor(self):
        assert compute_solvency_distance(50.0, 100.0, 0.01, ruin_fraction=0.5) == 0.0

    def test_below_ruin_floor(self):
        assert compute_solvency_distance(40.0, 100.0, 0.01, ruin_fraction=0.5) == 0.0

    def test_zero_std_returns_safe_default(self):
        assert compute_solvency_distance(80.0, 100.0, 0.0) == 99.0

    def test_positive_distance(self):
        dist = compute_solvency_distance(80.0, 100.0, 0.01, ruin_fraction=0.5)
        assert dist > 0.0


class TestEwmaVariance:
    def test_empty_returns(self):
        assert ewma_variance([], 0.94) == []

    def test_single_element(self):
        result = ewma_variance([0.02], 0.94)
        assert len(result) == 1
        assert result[0] == pytest.approx(0.94 * 0.0 + 0.06 * 0.02 * 0.02)

    def test_deterministic(self):
        returns = [0.01, -0.02, 0.015]
        assert ewma_variance(returns, 0.94) == ewma_variance(returns, 0.94)


class TestWarningState:
    def test_all_green(self):
        params = WarningStateParams(8.0, 0.05, 2.0, -0.08)
        result = compute_warning_state(params)
        assert result.state == WarningState.GREEN
        assert result.triggered_metrics == 0

    def test_solvency_critical(self):
        params = WarningStateParams(0.8, 0.05, 2.0, -0.08)
        result = compute_warning_state(params)
        assert result.state == WarningState.CRITICAL
        assert "solvency_distance" in result.triggered_names()

    def test_named_contributions(self):
        params = WarningStateParams(8.0, 0.25, 2.0, -0.08)
        result = compute_warning_state(params)
        payload = result.to_dict()
        assert payload["contributions"]["max_drawdown"]["level"] == "YELLOW"

    def test_monotonicity_solvency(self):
        levels = []
        for dist in (8.0, 2.5, 1.5, 0.5):
            levels.append(
                compute_warning_state(
                    WarningStateParams(dist, 0.05, 2.0, -0.08)
                ).state.value
            )
        assert levels == sorted(levels)

    def test_nan_input_is_critical(self):
        result = compute_warning_state(
            WarningStateParams(float("nan"), 0.05, 2.0, -0.08)
        )
        assert result.state == WarningState.CRITICAL


class TestReplayComposite:
    def test_stress_series_rises(self):
        calm = WarningStateParams(100.0, 0.01, 0.5, -0.005)
        stress = WarningStateParams(100.0, 0.03, 0.9, -0.015)
        assert replay_composite_score(stress, 0.008) > replay_composite_score(calm, 0.001)

    def test_score_bounded(self):
        params = WarningStateParams(0.5, 0.9, 12.0, -0.5)
        score = replay_composite_score(params, 0.05)
        assert 0.0 <= score <= 0.99


class TestSampleBundle:
    BUNDLE = _REPO / "benchmarks" / "results" / "sample_black_swan"
    REQUIRED = (
        "results.json",
        "summary.md",
        "environment.json",
        "tailwarp_vs_variance.csv",
        "artifacts/plots/signals.png",
        "artifacts/plots/equity_stress.png",
    )

    @pytest.mark.parametrize("rel_path", REQUIRED)
    def test_artifact_exists(self, rel_path: str):
        path = self.BUNDLE / rel_path
        assert path.exists(), f"missing artifact: {path}"

    def test_results_schema(self):
        data = json.loads((self.BUNDLE / "results.json").read_text(encoding="utf-8"))
        assert data["schema_version"] >= 2
        assert data["lead_time_seconds"] > 0
        assert "warning_state" in data
        assert data["warning_state"]["state"] in {"GREEN", "YELLOW", "RED", "CRITICAL"}
        contrib = data["warning_state"].get("contributions", {})
        for name in ("solvency_distance", "max_drawdown", "gross_exposure", "cvar_95"):
            assert name in contrib, f"missing contribution driver: {name}"
        assert "posture" in data
        posture = data["posture"]
        assert "convexity_score" in posture
        assert "antifragility_posture" in posture
        assert "complexity_regime" in posture
        assert "spd_manifold" in posture.get("excluded_from_headline", [])

    def test_tech_debt_doc_exists(self):
        doc = _REPO / TD_TW_02_DOC
        assert doc.is_file(), f"Missing {TD_TW_02_DOC} for TD-TW-02 GPU parity procedure"


@pytest.mark.skipif(
    GPU_CVAR_PARITY_DEFERRED,
    reason="GPU CVaR parity deferred (TD-TW-02): see Tech-Debt.md manual procedure.",
)
class TestGpuParity:
    BUNDLE = _REPO / "benchmarks" / "results" / "sample_black_swan"

    def test_gpu_cpu_cvar(self):
        artifact = self.BUNDLE / "results.json"
        pytest.skip(
            f"GPU/CPU parity not implemented: compare risk.cvar_95 in {artifact} "
            f"per {TD_TW_02_DOC}"
        )


def test_benchmark_runner_smoke():
    proc = subprocess.run(
        [
            sys.executable,
            str(_REPO / "benchmarks" / "run_black_swan_benchmark.py"),
            "--config",
            str(_REPO / "benchmarks" / "configs" / "black_swan_replay.json"),
        ],
        cwd=_REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout

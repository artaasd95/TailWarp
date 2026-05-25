"""Unit tests for S5 posture heuristics (CPU replay path)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from benchmarks.posture_metrics import (  # noqa: E402
    EXCLUDED_FROM_HEADLINE,
    compute_antifragility_posture,
    compute_convexity_score,
    compute_posture_block,
)


class TestConvexityScore:
    def test_all_gains(self):
        assert compute_convexity_score([0.01, 0.02]) == pytest.approx(1.0)

    def test_all_losses(self):
        assert compute_convexity_score([-0.01, -0.02]) == pytest.approx(-1.0)

    def test_balanced(self):
        assert compute_convexity_score([0.01, -0.01]) == pytest.approx(0.0)


class TestPostureBlock:
    def test_schema_keys(self):
        block = compute_posture_block([-0.02, -0.01, 0.005, 0.01, 0.02])
        assert "convexity_score" in block
        assert "antifragility_posture" in block
        assert "complexity_regime" in block
        assert block["status"] == "cpu_replay_heuristic"
        assert set(block["excluded_from_headline"]) == set(EXCLUDED_FROM_HEADLINE)

    def test_insufficient_data(self):
        block = compute_posture_block([])
        assert block["antifragility_posture"] == "insufficient_data"
        assert block["complexity_regime"] == "insufficient_data"


def test_antifragility_labels():
    returns = [0.0] * 10 + [0.05, 0.04, 0.03]
    posture = compute_antifragility_posture(returns, compute_convexity_score(returns))
    assert posture in {"antifragile_lean", "neutral", "fragile", "insufficient_data"}

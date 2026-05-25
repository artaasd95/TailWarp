"""Tests for benchmark bundle discovery and parsing (S4-01 / S4-02)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from app.black_swan_loader import (  # noqa: E402
    ArtifactLoadError,
    discover_runs,
    load_results,
    results_root,
)

SAMPLE = _REPO / "benchmarks" / "results" / "sample_black_swan"


class TestDiscoverRuns:
    def test_sample_run_listed(self):
        runs = discover_runs()
        ids = {r.run_id for r in runs}
        assert "sample_black_swan" in ids

    def test_sample_has_scenario(self):
        runs = [r for r in discover_runs() if r.run_id == "sample_black_swan"]
        assert runs
        assert runs[0].scenario_id == "sample_stress_2026q1"


class TestLoadResults:
    def test_contributions_present(self):
        results = load_results(SAMPLE)
        assert results.warning_state is not None
        assert "solvency_distance" in results.warning_state.contributions

    def test_missing_bundle_raises(self, tmp_path: Path):
        with pytest.raises(ArtifactLoadError, match="results.json"):
            load_results(tmp_path / "nonexistent")

    def test_missing_field_raises(self, tmp_path: Path):
        bundle = tmp_path / "bad_run"
        bundle.mkdir()
        (bundle / "results.json").write_text(
            json.dumps({"scenario_id": "x"}), encoding="utf-8"
        )
        with pytest.raises(ArtifactLoadError, match="missing required field"):
            load_results(bundle)

    def test_results_root_exists(self):
        assert results_root().is_dir()

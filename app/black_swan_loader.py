"""
Load Black Swan benchmark artifacts and replay sidecars.

Vault S2-03 replay record (CSV): timestamp, return, equity, exposure, optional label;
event windows live in a JSON sidecar.

Vault S2-03 lead time: baseline_first_alert_ts - tailwarp_first_alert_ts
(positive => TailWarp alerted earlier in time).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import pandas as pd


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


@dataclass
class EventWindow:
    label: str
    start: str
    end: str


@dataclass
class ReplayEventsSidecar:
    """JSON next to replay listing labeled event windows (ISO-8601 bounds)."""

    event_windows: list[EventWindow] = field(default_factory=list)

    @staticmethod
    def from_path(path: Path) -> "ReplayEventsSidecar":
        raw = json.loads(path.read_text(encoding="utf-8"))
        windows = [
            EventWindow(
                label=w.get("label", ""),
                start=w["start"],
                end=w["end"],
            )
            for w in raw.get("event_windows", [])
        ]
        return ReplayEventsSidecar(event_windows=windows)


@dataclass
class WarningStateArtifact:
    state: str
    reason: str
    triggered_metrics: list[str]
    contributions: dict[str, dict[str, Any]]

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "WarningStateArtifact":
        return WarningStateArtifact(
            state=str(d.get("state", "GREEN")),
            reason=str(d.get("reason", "")),
            triggered_metrics=list(d.get("triggered_metrics", [])),
            contributions=dict(d.get("contributions", {})),
        )


@dataclass
class BlackSwanResults:
    """Subset of results.json produced by benchmarks/run_black_swan_benchmark.py."""

    schema_version: int
    scenario_id: str
    tailwarp_first_alert_ts: str
    baseline_variance_ewma_first_alert_ts: str
    lead_time_seconds: float
    replay_relative: str
    event_windows_relative: str
    tailwarp_warning_index: Optional[int]
    solvency_distance: float
    cvar_95: float
    max_drawdown: float
    max_exposure: float
    plots: list[str] = field(default_factory=list)
    command: str = ""
    k_runs: int = 1
    aggregation_policy: str = "single_run"
    warning_state: Optional[WarningStateArtifact] = None

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "BlackSwanResults":
        risk = d.get("risk") or {}
        ws_raw = d.get("warning_state")
        return BlackSwanResults(
            schema_version=int(d.get("schema_version", 1)),
            scenario_id=str(d["scenario_id"]),
            tailwarp_first_alert_ts=str(d["tailwarp_first_alert_ts"]),
            baseline_variance_ewma_first_alert_ts=str(
                d["baseline_variance_ewma_first_alert_ts"]
            ),
            lead_time_seconds=float(d["lead_time_seconds"]),
            replay_relative=str(d["replay_relative"]),
            event_windows_relative=str(d["event_windows_relative"]),
            tailwarp_warning_index=(
                int(d["tailwarp_warning_index"])
                if d.get("tailwarp_warning_index") is not None
                else None
            ),
            solvency_distance=float(risk.get("solvency_distance", d.get("solvency_distance", 0.0))),
            cvar_95=float(risk.get("cvar_95", d.get("cvar_95", 0.0))),
            max_drawdown=float(risk.get("max_drawdown", d.get("max_drawdown", 0.0))),
            max_exposure=float(risk.get("max_exposure", d.get("max_exposure", 0.0))),
            plots=list(d.get("plots", [])),
            command=str(d.get("command", "")),
            k_runs=int(d.get("k_runs", 1)),
            aggregation_policy=str(d.get("aggregation_policy", "single_run")),
            warning_state=(
                WarningStateArtifact.from_dict(ws_raw) if ws_raw else None
            ),
        )


def load_results(bundle_dir: Path) -> BlackSwanResults:
    path = bundle_dir / "results.json"
    return BlackSwanResults.from_dict(json.loads(path.read_text(encoding="utf-8")))


def resolve_under_repo(relative: str) -> Path:
    p = Path(relative)
    if p.is_absolute():
        return p
    return repo_root() / p


def load_replay_csv(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    if "timestamp" not in df.columns:
        raise ValueError("replay CSV must include timestamp")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df


def load_tailwarp_vs_variance(bundle_dir: Path) -> pd.DataFrame:
    path = bundle_dir / "tailwarp_vs_variance.csv"
    df = pd.read_csv(path)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df


def load_environment(bundle_dir: Path) -> dict[str, Any]:
    path = bundle_dir / "environment.json"
    return json.loads(path.read_text(encoding="utf-8"))


def lead_time_seconds(
    tailwarp_first_alert_ts: str, baseline_first_alert_ts: str
) -> float:
    """S2-03: baseline_first - tailwarp_first (positive => TailWarp earlier)."""
    tw = datetime.fromisoformat(tailwarp_first_alert_ts.replace("Z", "+00:00"))
    bl = datetime.fromisoformat(baseline_first_alert_ts.replace("Z", "+00:00"))
    if tw.tzinfo is None:
        tw = tw.replace(tzinfo=timezone.utc)
    if bl.tzinfo is None:
        bl = bl.replace(tzinfo=timezone.utc)
    return (bl - tw).total_seconds()

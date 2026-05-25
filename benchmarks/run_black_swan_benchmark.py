#!/usr/bin/env python3
"""
Black Swan replay benchmark runner (CPU-safe).

Runs TailWarp warning-state scoring and a rolling-variance EWMA baseline on the
same replay stream; writes results.json, summary.md, comparison CSV, plots, and
environment metadata per the S2 artifact contract.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from benchmarks.posture_metrics import compute_posture_block  # noqa: E402
from benchmarks.risk_metrics import (  # noqa: E402
    WarningState,
    WarningStateParams,
    compute_cvar,
    compute_solvency_distance,
    compute_warning_state,
    ewma_variance,
    max_drawdown_from_equity,
    replay_composite_score,
)

SCHEMA_VERSION_DEFAULT = 2
MEASUREMENT_LABEL_CPU = "cpu_sample"
MEASUREMENT_LABEL_CUDA = "cuda_measured"


def repo_root() -> Path:
    return _REPO_ROOT


def load_config(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_path(relative: str) -> Path:
    p = Path(relative)
    return p if p.is_absolute() else repo_root() / p


def _parse_state(name: str) -> WarningState:
    return WarningState[name.upper()]


def _iso(ts: pd.Timestamp) -> str:
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def _first_score_alert(
    scores: list[float], threshold: float, min_obs: int
) -> Optional[int]:
    for i, score in enumerate(scores):
        if i + 1 < min_obs:
            continue
        if score >= threshold:
            return i
    return None


def _first_tailwarp_alert(
    scores: list[float],
    threshold: float,
    min_state: WarningState,
    states: list[WarningState],
    min_obs: int,
) -> Optional[int]:
    for i, (score, state) in enumerate(zip(scores, states)):
        if i + 1 < min_obs:
            continue
        if score >= threshold or state.value >= min_state.value:
            return i
    return None


def run_replay(config: dict[str, Any]) -> dict[str, Any]:
    replay_path = resolve_path(config["replay_csv"])
    df = pd.read_csv(replay_path)
    if "timestamp" not in df.columns:
        raise ValueError(f"{replay_path}: replay CSV must include timestamp")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    returns = df["return"].astype(float).tolist()
    equity = df["equity"].astype(float).tolist()
    exposure = df["exposure"].astype(float).tolist()
    initial_equity = equity[0]

    tw_cfg = config["tailwarp"]
    bl_cfg = config["baseline"]
    window = int(tw_cfg.get("window_size", 4))
    alpha = float(tw_cfg.get("cvar_alpha", 0.95))
    ruin_fraction = float(tw_cfg.get("ruin_fraction", 0.5))
    alert_threshold = float(tw_cfg["alert_threshold"])
    min_state = _parse_state(tw_cfg.get("alert_min_state", "YELLOW"))
    bl_threshold = float(bl_cfg["alert_threshold"])
    bl_lambda = float(bl_cfg.get("ewma_lambda", 0.94))
    bl_min_obs = int(bl_cfg.get("min_observations", 3))

    tailwarp_scores: list[float] = []
    warning_states: list[WarningState] = []
    solvency_series: list[float] = []
    cvar_series: list[float] = []
    dd_series: list[float] = []
    exposure_series: list[float] = []
    reasons: list[str] = []

    for i in range(len(df)):
        start = max(0, i - window + 1)
        window_returns = returns[start : i + 1]
        window_equity = equity[: i + 1]
        rolling_std = (
            float(pd.Series(window_returns).std(ddof=0))
            if len(window_returns) > 1
            else abs(returns[i])
        )
        if math.isnan(rolling_std):
            rolling_std = 0.0

        cvar = compute_cvar(window_returns, alpha)
        max_dd = max_drawdown_from_equity(window_equity)
        gross_exp = exposure[i]
        solvency = compute_solvency_distance(
            equity[i], initial_equity, rolling_std, ruin_fraction
        )

        params = WarningStateParams(
            solvency_distance=solvency,
            max_drawdown=max_dd,
            gross_exposure=gross_exp,
            cvar_95=cvar,
        )
        ws = compute_warning_state(params)
        score = replay_composite_score(params, rolling_std)

        tailwarp_scores.append(score)
        warning_states.append(ws.state)
        solvency_series.append(solvency)
        cvar_series.append(cvar)
        dd_series.append(max_dd)
        exposure_series.append(gross_exp)
        reasons.append(ws.reason)

    if "variance_baseline" in df.columns and bl_cfg.get("use_replay_column", True):
        variance_baseline = df["variance_baseline"].astype(float).tolist()
    else:
        variance_baseline = ewma_variance(returns, bl_lambda)

    tw_idx = _first_tailwarp_alert(
        tailwarp_scores, alert_threshold, min_state, warning_states, window
    )
    bl_idx = _first_score_alert(variance_baseline, bl_threshold, bl_min_obs)

    if tw_idx is None:
        tw_alert_ts = _iso(df["timestamp"].iloc[-1])
    else:
        tw_alert_ts = _iso(df["timestamp"].iloc[tw_idx])

    if bl_idx is None:
        bl_alert_ts = _iso(df["timestamp"].iloc[-1])
    else:
        bl_alert_ts = _iso(df["timestamp"].iloc[bl_idx])

    tw_dt = datetime.fromisoformat(tw_alert_ts.replace("Z", "+00:00"))
    bl_dt = datetime.fromisoformat(bl_alert_ts.replace("Z", "+00:00"))
    lead_time = (bl_dt - tw_dt).total_seconds()

    final_ws = compute_warning_state(
        WarningStateParams(
            solvency_distance=solvency_series[-1],
            max_drawdown=dd_series[-1],
            gross_exposure=exposure_series[-1],
            cvar_95=cvar_series[-1],
        )
    )

    comparison_rows = []
    for i in range(len(df)):
        comparison_rows.append(
            {
                "timestamp": _iso(df["timestamp"].iloc[i]),
                "tailwarp_score": round(tailwarp_scores[i], 6),
                "variance_baseline": round(variance_baseline[i], 6),
                "delta": round(tailwarp_scores[i] - variance_baseline[i], 6),
                "warning_state": warning_states[i].name,
                "solvency_distance": round(solvency_series[i], 4),
                "cvar_95": round(cvar_series[i], 6),
                "max_drawdown": round(dd_series[i], 6),
                "gross_exposure": round(exposure_series[i], 4),
            }
        )

    headline_risk = {
        "solvency_distance": round(solvency_series[-1], 4),
        "cvar_95": round(cvar_series[-1], 6),
        "max_drawdown": round(-dd_series[-1], 6),
        "max_exposure": round(max(exposure_series), 4),
    }

    return {
        "df": df,
        "comparison_rows": comparison_rows,
        "tailwarp_first_alert_ts": tw_alert_ts,
        "baseline_first_alert_ts": bl_alert_ts,
        "lead_time_seconds": lead_time,
        "tailwarp_warning_index": tw_idx,
        "headline_risk": headline_risk,
        "warning_state": final_ws.to_dict(),
        "tailwarp_scores": tailwarp_scores,
        "variance_baseline": variance_baseline,
    }


def write_plots(
    out_dir: Path,
    df: pd.DataFrame,
    tailwarp_scores: list[float],
    variance_baseline: list[float],
) -> list[str]:
    plots_dir = out_dir / "artifacts" / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    rel_paths: list[str] = []

    ts = df["timestamp"]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(ts, tailwarp_scores, label="TailWarp score", color="#d62728")
    ax.plot(ts, variance_baseline, label="Variance EWMA", color="#9467bd")
    ax.set_title("TailWarp vs variance baseline")
    ax.set_xlabel("timestamp")
    ax.legend()
    fig.autofmt_xdate()
    signals_path = plots_dir / "signals.png"
    fig.tight_layout()
    fig.savefig(signals_path, dpi=120)
    plt.close(fig)
    rel_paths.append("artifacts/plots/signals.png")

    fig, ax1 = plt.subplots(figsize=(8, 4))
    ax1.plot(ts, df["equity"], color="#1f77b4", label="equity")
    ax1.set_ylabel("equity")
    ax1.set_title("Equity under stress replay")
    if "exposure" in df.columns:
        ax2 = ax1.twinx()
        ax2.plot(ts, df["exposure"], color="#ff7f0e", label="exposure", alpha=0.7)
        ax2.set_ylabel("exposure")
    fig.autofmt_xdate()
    equity_path = plots_dir / "equity_stress.png"
    fig.tight_layout()
    fig.savefig(equity_path, dpi=120)
    plt.close(fig)
    rel_paths.append("artifacts/plots/equity_stress.png")

    return rel_paths


def _git_commit() -> Optional[str]:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root(),
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        if proc.returncode == 0:
            return proc.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def _cuda_environment() -> dict[str, Any]:
    """Best-effort GPU metadata (null when CUDA unavailable)."""
    meta: dict[str, Any] = {
        "gpu_model": None,
        "driver_version": None,
        "cuda_version": None,
        "build_json": None,
    }
    build_path = repo_root() / "build.json"
    if build_path.is_file():
        try:
            meta["build_json"] = json.loads(build_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            meta["build_json"] = str(build_path)
    try:
        proc = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version",
                "--format=csv,noheader",
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            parts = [p.strip() for p in proc.stdout.strip().split(",", 1)]
            meta["gpu_model"] = parts[0] if parts else None
            meta["driver_version"] = parts[1] if len(parts) > 1 else None
    except (OSError, subprocess.TimeoutExpired):
        pass
    try:
        import torch  # type: ignore

        if torch.cuda.is_available():
            meta["cuda_version"] = getattr(torch.version, "cuda", None)
            if meta["gpu_model"] is None and torch.cuda.device_count() > 0:
                meta["gpu_model"] = torch.cuda.get_device_name(0)
    except ImportError:
        pass
    return meta


def write_environment(out_dir: Path, *, cuda_measured: bool = False) -> dict[str, Any]:
    cuda_meta = _cuda_environment()
    has_gpu = cuda_meta.get("gpu_model") is not None
    env: dict[str, Any] = {
        "hostname": platform.node(),
        "os": platform.platform(),
        "python": platform.python_version(),
        "git_commit": _git_commit(),
        "gpu": cuda_meta.get("gpu_model"),
        "gpu_model": cuda_meta.get("gpu_model"),
        "driver_version": cuda_meta.get("driver_version"),
        "cuda_version": cuda_meta.get("cuda_version"),
        "build_json": cuda_meta.get("build_json"),
        "cpu_only": not cuda_measured and not has_gpu,
        "measurement_label": (
            MEASUREMENT_LABEL_CUDA if cuda_measured else MEASUREMENT_LABEL_CPU
        ),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "notes": (
            "CUDA Black Swan replay reproduction."
            if cuda_measured
            else "CPU-safe Black Swan replay benchmark; no CUDA required."
        ),
    }
    (out_dir / "environment.json").write_text(
        json.dumps(env, indent=2) + "\n", encoding="utf-8"
    )
    return env


def default_limitations(*, cuda_measured: bool) -> list[str]:
    lines = [
        "Composite replay score uses softer normalization than formal S2-02 bands on short series.",
        "Student-t scenario refresh is optional and disabled in the default config.",
        "SPD manifold and robust covariance are excluded from headline posture metrics.",
    ]
    if cuda_measured:
        lines.insert(
            0,
            "CUDA-measured row: GPU-sorted CVaR may differ from CPU historical quantile.",
        )
    else:
        lines.insert(
            0,
            "CPU-only replay benchmark; CUDA reproduction may differ on GPU-sorted CVaR.",
        )
    return lines


def write_summary(
    out_dir: Path,
    scenario_id: str,
    tw_alert: str,
    bl_alert: str,
    lead_time: float,
    *,
    posture: Optional[dict[str, Any]] = None,
    measurement_label: str = MEASUREMENT_LABEL_CPU,
    k_runs: int = 1,
    aggregation_policy: str = "single_run",
) -> None:
    lead_h = lead_time / 3600.0
    posture_rows = ""
    if posture:
        posture_rows = f"""
| Convexity score | {posture.get("convexity_score", "—")} |
| Antifragility posture | {posture.get("antifragility_posture", "—")} |
| Complexity regime | {posture.get("complexity_regime", "—")} |
| Posture status | {posture.get("status", "—")} |
"""
    text = f"""# Black Swan benchmark — {scenario_id}

Synthetic **stress** replay. TailWarp triggers on warning-state composite score;
the variance EWMA baseline uses the **same** return stream.

## Headline

| Field | Value |
|-------|-------|
| Measurement | {measurement_label} |
| Scenario | {scenario_id} |
| K runs | {k_runs} |
| Aggregation | {aggregation_policy} |
| TailWarp first alert | {tw_alert} |
| Baseline first alert | {bl_alert} |
| Lead time | {lead_h:+.1f} h |
{posture_rows}
## Limitations

- Thresholds are deterministic per docs/VALIDATION.md (S2-02).
- Posture metrics use CPU replay heuristics until Lens-5 kernels ship.
- SPD / robust covariance excluded from headline rows.
"""
    (out_dir / "summary.md").write_text(text, encoding="utf-8")


def run_benchmark(config_path: Path) -> Path:
    config = load_config(config_path)
    out_dir = resolve_path(config["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    result = run_replay(config)
    df = result["df"]

    cfg_rel = config_path.resolve().relative_to(repo_root().resolve()).as_posix()
    command = f"python benchmarks/run_black_swan_benchmark.py --config {cfg_rel}"

    replay_rel = Path(config["replay_csv"]).as_posix()
    events_rel = Path(config["event_windows_json"]).as_posix()

    returns = result["df"]["return"].astype(float).tolist()
    posture = compute_posture_block(returns)
    cuda_measured = bool(config.get("cuda_measured", False))
    measurement_label = str(
        config.get(
            "measurement_label",
            MEASUREMENT_LABEL_CUDA if cuda_measured else MEASUREMENT_LABEL_CPU,
        )
    )
    limitations = config.get("limitations") or default_limitations(
        cuda_measured=cuda_measured
    )

    results_doc = {
        "schema_version": int(config.get("schema_version", SCHEMA_VERSION_DEFAULT)),
        "scenario_id": config["scenario_id"],
        "measurement_label": measurement_label,
        "tailwarp_first_alert_ts": result["tailwarp_first_alert_ts"],
        "baseline_variance_ewma_first_alert_ts": result["baseline_first_alert_ts"],
        "lead_time_seconds": result["lead_time_seconds"],
        "replay_relative": replay_rel,
        "event_windows_relative": events_rel,
        "tailwarp_warning_index": result["tailwarp_warning_index"],
        "k_runs": int(config.get("k_runs", 1)),
        "aggregation_policy": config.get("aggregation_policy", "single_run"),
        "risk": result["headline_risk"],
        "warning_state": result["warning_state"],
        "posture": posture,
        "limitations": limitations,
        "plots": [],
        "command": command,
    }

    plot_paths = write_plots(
        out_dir, df, result["tailwarp_scores"], result["variance_baseline"]
    )
    results_doc["plots"] = plot_paths

    (out_dir / "results.json").write_text(
        json.dumps(results_doc, indent=2) + "\n", encoding="utf-8"
    )

    pd.DataFrame(result["comparison_rows"]).to_csv(
        out_dir / "tailwarp_vs_variance.csv", index=False
    )

    write_environment(out_dir, cuda_measured=cuda_measured)
    write_summary(
        out_dir,
        config["scenario_id"],
        result["tailwarp_first_alert_ts"],
        result["baseline_first_alert_ts"],
        result["lead_time_seconds"],
        posture=posture,
        measurement_label=measurement_label,
        k_runs=int(config.get("k_runs", 1)),
        aggregation_policy=str(config.get("aggregation_policy", "single_run")),
    )

    return out_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Black Swan replay benchmark")
    parser.add_argument(
        "--config",
        type=Path,
        default=repo_root() / "benchmarks/configs/black_swan_replay.json",
        help="Path to replay config JSON",
    )
    args = parser.parse_args()

    if not args.config.exists():
        print(f"Config not found: {args.config}", file=sys.stderr)
        return 1

    out_dir = run_benchmark(args.config)
    print(f"Wrote benchmark bundle to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

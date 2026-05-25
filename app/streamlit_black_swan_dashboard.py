"""
Black Swan replay dashboard: reads benchmark artifact bundle (no GPU).

Run from repository root:
  streamlit run app/streamlit_black_swan_dashboard.py

Run selection: sidebar lists every benchmarks/results/<run_id>/ with results.json.
See dashboard/README.md for the artifact contract.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from black_swan_loader import (
    ArtifactLoadError,
    BlackSwanResults,
    DRIVER_METRIC_COLUMNS,
    ReplayEventsSidecar,
    discover_runs,
    lead_time_seconds,
    load_environment,
    load_replay_csv,
    load_results,
    load_tailwarp_vs_variance,
    repo_root,
    resolve_under_repo,
    results_root,
)


def _replay_path(results: BlackSwanResults, override: Optional[str]) -> Path:
    if override and override.strip():
        p = Path(override.strip())
        return p if p.is_absolute() else repo_root() / p
    return resolve_under_repo(results.replay_relative)


def _events_path(results: BlackSwanResults, override: Optional[str]) -> Path:
    if override and override.strip():
        p = Path(override.strip())
        return p if p.is_absolute() else repo_root() / p
    return resolve_under_repo(results.event_windows_relative)


def _equity_drawdown(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "equity" not in out.columns:
        return out
    cummax = out["equity"].cummax()
    out["drawdown"] = out["equity"] / cummax - 1.0
    return out


def _fig_replay(df: pd.DataFrame, events: ReplayEventsSidecar) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["equity"],
            name="equity",
            line=dict(color="#1f77b4"),
        )
    )
    if "exposure" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["exposure"],
                name="exposure",
                yaxis="y2",
                line=dict(color="#ff7f0e"),
            )
        )
    fig.update_layout(
        title="Replay stream",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        yaxis=dict(title="equity"),
        yaxis2=dict(title="exposure", overlaying="y", side="right", showgrid=False),
        margin=dict(l=48, r=48, t=56, b=48),
    )
    for w in events.event_windows:
        fig.add_vrect(
            x0=w.start,
            x1=w.end,
            fillcolor="rgba(128,128,128,0.15)",
            layer="below",
            line_width=0,
            annotation_text=w.label,
            annotation_position="top left",
        )
    return fig


def _fig_returns(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if "return" in df.columns:
        fig.add_trace(
            go.Bar(x=df["timestamp"], y=df["return"], name="return", marker_color="#2ca02c")
        )
    fig.update_layout(title="Returns", margin=dict(l=48, r=24, t=48, b=48))
    return fig


def _fig_variance_baseline(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if "variance_baseline" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["variance_baseline"],
                name="variance EWMA (baseline)",
                line=dict(color="#9467bd"),
            )
        )
    fig.update_layout(
        title="Variance baseline (replay column)",
        margin=dict(l=48, r=24, t=48, b=48),
    )
    return fig


def _fig_tailwarp_vs_var(dfc: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if "tailwarp_score" in dfc.columns:
        fig.add_trace(
            go.Scatter(
                x=dfc["timestamp"],
                y=dfc["tailwarp_score"],
                name="TailWarp score",
                line=dict(color="#d62728"),
            )
        )
    if "variance_baseline" in dfc.columns:
        fig.add_trace(
            go.Scatter(
                x=dfc["timestamp"],
                y=dfc["variance_baseline"],
                name="variance baseline",
                line=dict(color="#9467bd"),
            )
        )
    fig.update_layout(
        title="TailWarp vs variance (artifact CSV)",
        hovermode="x unified",
        margin=dict(l=48, r=24, t=48, b=48),
    )
    return fig


def _fig_metric_drivers(dfc: pd.DataFrame) -> Optional[go.Figure]:
    cols = [c for c in DRIVER_METRIC_COLUMNS if c in dfc.columns]
    if not cols or "timestamp" not in dfc.columns:
        return None
    fig = go.Figure()
    for col in cols:
        fig.add_trace(
            go.Scatter(x=dfc["timestamp"], y=dfc[col], name=col, mode="lines")
        )
    fig.update_layout(
        title="Warning-state metric drivers (per timestamp)",
        hovermode="x unified",
        margin=dict(l=48, r=24, t=48, b=48),
    )
    return fig


def _contributions_dataframe(results: BlackSwanResults) -> Optional[pd.DataFrame]:
    if results.warning_state is None or not results.warning_state.contributions:
        return None
    rows = []
    for name, detail in results.warning_state.contributions.items():
        rows.append(
            {
                "metric": name,
                "level": detail.get("level", ""),
                "value": detail.get("value"),
                "message": detail.get("message", ""),
            }
        )
    return pd.DataFrame(rows)


def _resolve_bundle_from_sidebar(
    discovered: list,
    override_path: str,
) -> Optional[Path]:
    if override_path.strip():
        p = Path(override_path.strip())
        return p if p.is_absolute() else repo_root() / p
    if not discovered:
        return None
    labels = [r.label for r in discovered]
    choice = st.session_state.get("run_select")
    if choice in labels:
        return discovered[labels.index(choice)].bundle_dir
    return discovered[0].bundle_dir


def main() -> None:
    st.set_page_config(page_title="TailWarp Black Swan", layout="wide")
    st.title("Black Swan defense calibration (replay)")

    discovered = discover_runs()

    with st.sidebar:
        st.header("Artifact bundle")
        st.caption(
            f"Scans `{results_root().relative_to(repo_root())}/` for folders containing "
            "`results.json`. Pick a run or enter a custom path."
        )
        if discovered:
            run_labels = [r.label for r in discovered]
            st.selectbox(
                "Run",
                options=run_labels,
                key="run_select",
                help="Most recently modified bundles appear first.",
            )
        else:
            st.warning(
                f"No runs found under {results_root()}. "
                "Run the benchmark runner to generate a bundle."
            )

        override_path = st.text_input(
            "Custom bundle path (optional)",
            value="",
            help="Overrides Run when set. Absolute path or repo-relative.",
        )
        if discovered and not override_path.strip():
            idx = 0
            if st.session_state.get("run_select") in [r.label for r in discovered]:
                idx = [r.label for r in discovered].index(st.session_state["run_select"])
            st.caption(f"Using: `{discovered[idx].bundle_dir}`")

        replay_override = st.text_input(
            "Optional replay CSV override",
            value="",
            help="Leave empty to use replay_relative from results.json",
        )
        events_override = st.text_input(
            "Optional events JSON override",
            value="",
            help="Leave empty to use event_windows_relative from results.json",
        )

        with st.expander("Help"):
            st.markdown(
                """
**Generate a bundle**

```bash
python benchmarks/run_black_swan_benchmark.py \\
  --config benchmarks/configs/black_swan_replay.json
```

**Layout** — each run is a directory under `benchmarks/results/<run_id>/` with
`results.json`, `tailwarp_vs_variance.csv`, `environment.json`, and plots.

**CUDA reproduction** — use a separate output directory and set
`cuda_measured: true` in config when GPU CI is available (next sprint).
"""
            )

    bundle = _resolve_bundle_from_sidebar(discovered, override_path)
    if bundle is None:
        st.error(
            f"No benchmark bundles under {results_root()}. "
            "Run `benchmarks/run_black_swan_benchmark.py` first."
        )
        st.stop()

    if not bundle.exists():
        st.error(f"Bundle directory not found: {bundle}")
        st.stop()

    try:
        results = load_results(bundle)
    except ArtifactLoadError as exc:
        st.error(str(exc))
        if exc.path:
            st.caption(f"Path: {exc.path}")
        st.stop()

    env = load_environment(bundle)

    try:
        dfcmp = load_tailwarp_vs_variance(bundle)
    except ArtifactLoadError as exc:
        st.error(str(exc))
        st.stop()

    replay_path = _replay_path(results, replay_override or None)
    try:
        df = load_replay_csv(replay_path)
    except ArtifactLoadError as exc:
        st.error(str(exc))
        st.stop()

    events_path = _events_path(results, events_override or None)
    if not events_path.exists():
        st.error(f"Events JSON not found: {events_path}")
        st.stop()

    events = ReplayEventsSidecar.from_path(events_path)
    df = _equity_drawdown(df)

    st.caption(
        f"Bundle: `{bundle}` · scenario **{results.scenario_id}** · "
        f"schema v{results.schema_version} · {results.measurement_label} · "
        f"k={results.k_runs} · {results.aggregation_policy}"
    )

    recomputed = lead_time_seconds(
        results.tailwarp_first_alert_ts,
        results.baseline_variance_ewma_first_alert_ts,
    )
    if abs(recomputed - results.lead_time_seconds) > 1.0:
        st.warning(
            "Stored lead_time_seconds differs from recomputed value "
            f"({results.lead_time_seconds} vs {recomputed}); showing stored value."
        )

    warn_idx = results.tailwarp_warning_index
    in_alert = False
    if warn_idx is not None and warn_idx < len(df):
        last_i = len(df) - 1
        in_alert = last_i >= warn_idx

    st.subheader("Warning state")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "TailWarp first alert (UTC)",
        results.tailwarp_first_alert_ts[:19].replace("T", " "),
    )
    c2.metric(
        "Baseline first alert (UTC)",
        results.baseline_variance_ewma_first_alert_ts[:19].replace("T", " "),
    )
    lead_h = results.lead_time_seconds / 3600.0
    c3.metric(
        "Lead time (baseline − TailWarp)",
        f"{lead_h:+.1f} h",
        help="Positive => TailWarp earlier",
    )
    terminal_state = (
        results.warning_state.state if results.warning_state else "—"
    )
    c4.metric("Terminal warning state", terminal_state)

    if results.warning_state is not None:
        ws = results.warning_state
        st.caption(f"**{ws.state}** — {ws.reason}")
        if ws.triggered_metrics:
            st.caption(f"Triggered metrics: {', '.join(ws.triggered_metrics)}")

        contrib_df = _contributions_dataframe(results)
        if contrib_df is not None:
            st.subheader("Metric drivers (terminal)")
            st.dataframe(
                contrib_df,
                use_container_width=True,
                column_config={
                    "level": st.column_config.TextColumn("level"),
                    "value": st.column_config.NumberColumn("value", format="%.4f"),
                },
            )

    driver_fig = _fig_metric_drivers(dfcmp)
    if driver_fig is not None:
        st.subheader("Metric drivers (time series)")
        st.plotly_chart(driver_fig, use_container_width=True)

    if results.posture is not None:
        st.subheader("Posture (S5 heuristics)")
        p = results.posture
        pc1, pc2, pc3 = st.columns(3)
        if p.convexity_score is not None:
            pc1.metric("Convexity score", f"{p.convexity_score:+.3f}")
        else:
            pc1.metric("Convexity score", "—")
        pc2.metric("Antifragility posture", p.antifragility_posture)
        pc3.metric("Complexity regime", p.complexity_regime)
        if p.excluded_from_headline:
            st.caption(
                "Excluded from headline: "
                + ", ".join(p.excluded_from_headline)
                + f" · status: {p.status}"
            )

    st.info(
        "**Replay tail state:** "
        + (
            "**WARNING** (at or past TailWarp first alert)"
            if in_alert
            else "**CALM** (before first alert)"
        )
    )

    st.subheader("Lead time delta")
    st.write(
        f"Lead time = baseline first-alert time minus TailWarp first-alert time "
        f"= **{results.lead_time_seconds:,.0f} s** ({lead_h:+.2f} h)."
    )

    st.subheader("Replay stream and event windows")
    st.plotly_chart(_fig_replay(df, events), use_container_width=True)
    c5, c6 = st.columns(2)
    with c5:
        st.plotly_chart(_fig_returns(df), use_container_width=True)
    with c6:
        st.plotly_chart(_fig_variance_baseline(df), use_container_width=True)

    st.subheader("Variance baseline vs comparison CSV")
    st.plotly_chart(_fig_tailwarp_vs_var(dfcmp), use_container_width=True)

    st.subheader("Solvency / CVaR / drawdown / exposure (headline)")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Solvency distance", f"{results.solvency_distance:.2f}")
    m2.metric("CVaR (95%)", f"{results.cvar_95:.3f}")
    m3.metric("Max drawdown", f"{results.max_drawdown:.3f}")
    m4.metric("Max exposure", f"{results.max_exposure:.2f}")
    if "drawdown" in df.columns:
        st.caption(f"Replay terminal drawdown (last bar): {df['drawdown'].iloc[-1]:.4f}")

    st.subheader("Committed plots (from bundle)")
    plot_cols = st.columns(max(1, len(results.plots)))
    for i, rel in enumerate(results.plots):
        img_path = bundle / rel
        with plot_cols[i % len(plot_cols)]:
            if img_path.exists():
                st.image(str(img_path), caption=rel)
            else:
                st.warning(f"Missing plot: {img_path}")

    st.subheader("Explanation")
    summary_path = bundle / "summary.md"
    if summary_path.exists():
        st.markdown(summary_path.read_text(encoding="utf-8"))
    else:
        st.warning(f"Missing summary.md in bundle: {summary_path}")

    limitations = list(results.limitations)
    if env.get("notes"):
        limitations.append(str(env["notes"]))

    with st.expander("Limitations"):
        if limitations:
            for line in limitations:
                st.markdown(f"- {line}")
        else:
            st.caption("No limitations recorded in results.json.")

    with st.expander("Environment metadata (environment.json)"):
        if "_error" in env:
            st.warning(env["_error"])
        else:
            st.json(env)

    with st.expander("Command (from results.json)"):
        st.code(results.command or "(not recorded)", language="text")

    with st.expander("Optional labels (last rows)"):
        if "label" in df.columns:
            st.dataframe(
                df[["timestamp", "label", "equity", "exposure"]].tail(8),
                use_container_width=True,
            )
        else:
            st.caption("No label column in replay CSV.")


if __name__ == "__main__":
    main()

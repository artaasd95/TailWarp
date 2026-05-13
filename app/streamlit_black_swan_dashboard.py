"""
Black Swan replay dashboard: reads benchmark artifact bundle (no GPU).

Run from repository root:
  streamlit run app/streamlit_black_swan_dashboard.py
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from black_swan_loader import (
    BlackSwanResults,
    ReplayEventsSidecar,
    lead_time_seconds,
    load_environment,
    load_replay_csv,
    load_results,
    load_tailwarp_vs_variance,
    repo_root,
    resolve_under_repo,
)


def _default_bundle() -> Path:
    return repo_root() / "benchmarks" / "results" / "sample_black_swan"


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
        title="Replay stream (same series drives TailWarp and variance baseline in sample)",
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
        title="Variance baseline (same replay timestamps)",
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


def main() -> None:
    st.set_page_config(page_title="TailWarp Black Swan", layout="wide")
    st.title("Black Swan defense calibration (replay)")
    root = repo_root()

    with st.sidebar:
        st.header("Artifact bundle")
        bundle_str = st.text_input(
            "Bundle directory",
            value=str(_default_bundle()),
            help="Folder containing results.json, summary.md, tailwarp_vs_variance.csv, environment.json",
        )
        bundle = Path(bundle_str)
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

    if not bundle.exists():
        st.error(f"Bundle not found: {bundle}")
        st.stop()

    results = load_results(bundle)
    env = load_environment(bundle)
    dfcmp = load_tailwarp_vs_variance(bundle)

    replay_path = _replay_path(results, replay_override or None)
    if not replay_path.exists():
        st.error(f"Replay CSV not found: {replay_path}")
        st.stop()

    events_path = _events_path(results, events_override or None)
    if not events_path.exists():
        st.error(f"Events JSON not found: {events_path}")
        st.stop()

    df = load_replay_csv(replay_path)
    events = ReplayEventsSidecar.from_path(events_path)
    df = _equity_drawdown(df)

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
    c1, c2, c3 = st.columns(3)
    c1.metric("TailWarp first alert (UTC)", results.tailwarp_first_alert_ts[:19].replace("T", " "))
    c2.metric("Baseline first alert (UTC)", results.baseline_variance_ewma_first_alert_ts[:19].replace("T", " "))
    lead_h = results.lead_time_seconds / 3600.0
    c3.metric("Lead time (baseline − TailWarp)", f"{lead_h:+.1f} h", help="Positive => TailWarp earlier")

    st.info(
        "**Replay tail state:** "
        + ("**WARNING** (at or past TailWarp first alert)" if in_alert else "**CALM** (before first alert)")
    )

    st.subheader("Lead time delta")
    st.write(
        f"Lead time = baseline first-alert time minus TailWarp first-alert time "
        f"= **{results.lead_time_seconds:,.0f} s** ({lead_h:+.2f} h)."
    )

    st.subheader("Replay stream and event windows")
    st.plotly_chart(_fig_replay(df, events), use_container_width=True)
    c4, c5 = st.columns(2)
    with c4:
        st.plotly_chart(_fig_returns(df), use_container_width=True)
    with c5:
        st.plotly_chart(_fig_variance_baseline(df), use_container_width=True)

    st.subheader("Variance baseline (replay column) vs comparison CSV")
    st.plotly_chart(_fig_tailwarp_vs_var(dfcmp), use_container_width=True)

    st.subheader("Solvency / CVaR / drawdown / exposure")
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
    with st.expander("Environment metadata (environment.json)"):
        st.json(env)
    with st.expander("Limitations (sample bundle)"):
        st.markdown(
            """
- Synthetic CSV only; not produced by `run_black_swan_benchmark.py` yet.
- Thresholds and scores are illustrative.
- No GPU or CUDA dependency in this dashboard path.
"""
        )
    with st.expander("Command (from results.json)"):
        st.code(results.command or "(not recorded)", language="text")

    with st.expander("Optional labels (last rows)"):
        if "label" in df.columns:
            st.dataframe(df[["timestamp", "label", "equity", "exposure"]].tail(8), use_container_width=True)
        else:
            st.caption("No label column in replay CSV.")


if __name__ == "__main__":
    main()

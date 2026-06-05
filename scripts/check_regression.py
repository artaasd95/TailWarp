#!/usr/bin/env python3
"""
Regression gate vs benchmarks/baselines/*.json (SP-BENCH-04).

Compares throughput (samples_per_sec) and mean_ms from run_benchmarks.py output.
Default threshold: 20% regression (current worse than baseline by >20%).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parent.parent
_BASELINES = _REPO / "benchmarks" / "baselines"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def benchmark_index(doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in doc.get("benchmarks", []):
        name = row.get("name")
        if name:
            out[str(name)] = row
    return out


def check_metric(
    name: str,
    metric: str,
    current: float,
    baseline: float,
    threshold: float,
    higher_is_better: bool,
) -> tuple[bool, str]:
    if baseline <= 0:
        return True, f"{name}.{metric}: baseline non-positive, skip"
    if higher_is_better:
        ratio = current / baseline
        ok = ratio >= (1.0 - threshold)
        delta_pct = (ratio - 1.0) * 100.0
    else:
        ratio = current / baseline
        ok = ratio <= (1.0 + threshold)
        delta_pct = (ratio - 1.0) * 100.0
    msg = f"{name}.{metric}: current={current:.4g} baseline={baseline:.4g} delta={delta_pct:+.1f}%"
    return ok, msg


def compare(
    current_doc: dict[str, Any],
    baseline_doc: dict[str, Any],
    threshold: float,
) -> list[str]:
    cur = benchmark_index(current_doc)
    base = benchmark_index(baseline_doc)
    messages: list[str] = []
    failed = False

    for name, base_row in base.items():
        if base_row.get("status") not in (None, "ok"):
            continue
        cur_row = cur.get(name)
        if not cur_row or cur_row.get("status") != "ok":
            messages.append(f"FAIL {name}: missing or not ok in current results")
            failed = True
            continue

        if "samples_per_sec" in base_row and "samples_per_sec" in cur_row:
            ok, msg = check_metric(
                name,
                "samples_per_sec",
                float(cur_row["samples_per_sec"]),
                float(base_row["samples_per_sec"]),
                threshold,
                higher_is_better=True,
            )
            messages.append(("FAIL " if not ok else "OK ") + msg)
            failed = failed or not ok

        if "mean_ms" in base_row and "mean_ms" in cur_row:
            ok, msg = check_metric(
                name,
                "mean_ms",
                float(cur_row["mean_ms"]),
                float(base_row["mean_ms"]),
                threshold,
                higher_is_better=False,
            )
            messages.append(("FAIL " if not ok else "OK ") + msg)
            failed = failed or not ok

    if failed:
        messages.append(f"Regression threshold exceeded ({threshold * 100:.0f}%)")
    return messages


def main() -> int:
    parser = argparse.ArgumentParser(description="TailWarp benchmark regression check")
    parser.add_argument(
        "--results",
        type=Path,
        required=True,
        help="Path to benchmarks/results/<run_id>/results.json",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=None,
        help="Baseline JSON (default: benchmarks/baselines/cpu_smoke.json)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.20,
        help="Allowed relative regression (default 0.20 = 20%%)",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Always exit 0 but print failures",
    )
    args = parser.parse_args()

    baseline_path = args.baseline or (_BASELINES / "cpu_smoke.json")
    if not args.results.is_file():
        print(f"Results file not found: {args.results}", file=sys.stderr)
        return 2
    if not baseline_path.is_file():
        print(f"Baseline not found: {baseline_path}", file=sys.stderr)
        return 2

    current_doc = load_json(args.results)
    baseline_doc = load_json(baseline_path)
    messages = compare(current_doc, baseline_doc, args.threshold)
    for m in messages:
        print(m)

    any_fail = any(m.startswith("FAIL") for m in messages)
    if any_fail and not args.warn_only:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Canonical benchmark runner (wiring only — SP-BENCH-01).

Runs the matrix defined in docs/EXECUTION_MANIFEST.md without executing S7 GPU
full matrix unless --profile cuda_full and a built tree exist.

Writes benchmarks/results/<run_id>/results.json
"""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

_REPO = Path(__file__).resolve().parent.parent
_SCHEMA_VERSION = 1


def repo_root() -> Path:
    return _REPO


def git_commit() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root(),
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def nvidia_metadata() -> dict[str, Any]:
    meta: dict[str, Any] = {}
    if not shutil.which("nvidia-smi"):
        return meta
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version",
                "--format=csv,noheader",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        line = out.strip().splitlines()[0] if out.strip() else ""
        if "," in line:
            name, driver = [p.strip() for p in line.split(",", 1)]
            meta["gpu_model"] = name
            meta["driver_version"] = driver
    except subprocess.CalledProcessError:
        pass
    try:
        nvcc = subprocess.check_output(
            ["nvcc", "--version"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        for row in nvcc.splitlines():
            if "release" in row.lower():
                meta["cuda_version"] = row.strip()
                break
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return meta


def build_dir() -> Path:
    return repo_root() / "build"


def bench_binary(name: str) -> Optional[Path]:
    candidates = [
        build_dir() / name,
        build_dir() / "Release" / name,
        build_dir() / "Debug" / name,
    ]
    if sys.platform == "win32":
        candidates = [p.with_suffix(".exe") for p in candidates]
    for path in candidates:
        if path.is_file():
            return path
    return None


def run_bench_exe(exe: Path, extra: list[str]) -> dict[str, Any]:
    cmd = [str(exe), "--json", *extra]
    proc = subprocess.run(
        cmd,
        cwd=repo_root(),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return {
            "name": exe.stem,
            "status": "error",
            "stderr": proc.stderr.strip() or proc.stdout.strip(),
        }
    line = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "{}"
    try:
        row = json.loads(line)
    except json.JSONDecodeError:
        row = {"name": exe.stem, "status": "error", "raw": line}
    row["status"] = row.get("status", "ok")
    return row


def run_ctest() -> dict[str, Any]:
    if not (build_dir() / "CTestTestfile.cmake").is_file():
        return {"name": "ctest", "status": "skipped", "reason": "build/ not configured"}
    proc = subprocess.run(
        ["ctest", "--test-dir", str(build_dir()), "--output-on-failure"],
        cwd=repo_root(),
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "name": "ctest",
        "status": "ok" if proc.returncode == 0 else "failed",
        "returncode": proc.returncode,
    }


def run_black_swan_smoke() -> dict[str, Any]:
    cfg = repo_root() / "benchmarks/configs/black_swan_replay.json"
    runner = repo_root() / "benchmarks/run_black_swan_benchmark.py"
    if not cfg.is_file() or not runner.is_file():
        return {
            "name": "black_swan_replay",
            "status": "skipped",
            "reason": "config or runner missing",
        }
    proc = subprocess.run(
        [sys.executable, str(runner), "--config", str(cfg)],
        cwd=repo_root(),
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "name": "black_swan_replay",
        "status": "ok" if proc.returncode == 0 else "failed",
        "measurement_label": "cpu_sample",
        "returncode": proc.returncode,
    }


def assemble_results(
    run_id: str,
    profile: str,
    k_runs: int,
    warmup: int,
    benchmarks: list[dict[str, Any]],
) -> dict[str, Any]:
    env = {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "measurement_label": "cpu_sample" if profile == "cpu_smoke" else "cuda_measured",
        **nvidia_metadata(),
    }
    return {
        "schema_version": _SCHEMA_VERSION,
        "run_id": run_id,
        "profile": profile,
        "commit_sha": git_commit(),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "warmup_runs": warmup,
        "k_runs": k_runs,
        "environment": env,
        "benchmarks": benchmarks,
        "manifest": "docs/EXECUTION_MANIFEST.md",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="TailWarp benchmark runner")
    parser.add_argument(
        "--profile",
        choices=("cpu_smoke", "cuda_full"),
        default="cpu_smoke",
        help="cpu_smoke: ctest + optional microbenches; cuda_full: include GPU benches",
    )
    parser.add_argument("--run-id", default=None, help="Output directory name under benchmarks/results/")
    parser.add_argument("--k", type=int, default=1, help="K runs for microbenches (passed to --k)")
    parser.add_argument("--warmup", type=int, default=0, help="Warm-up runs for microbenches")
    parser.add_argument(
        "--skip-black-swan",
        action="store_true",
        help="Do not invoke run_black_swan_benchmark.py",
    )
    args = parser.parse_args()

    run_id = args.run_id or f"bench_{args.profile}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    out_dir = repo_root() / "benchmarks/results" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    rows.append(run_ctest())

    if args.profile == "cuda_full" or bench_binary("bench_student_t"):
        exe = bench_binary("bench_student_t")
        if exe:
            rows.append(
                run_bench_exe(
                    exe,
                    ["--k", str(args.k), "--warmup", str(args.warmup), "--samples", "100000"],
                )
            )
        else:
            rows.append(
                {
                    "name": "student_t_sample",
                    "status": "skipped",
                    "reason": "build bench_student_t first (cmake -DBUILD_BENCHMARKS=ON)",
                }
            )

    if args.profile == "cuda_full":
        exe_g = bench_binary("bench_gaussian")
        if exe_g:
            rows.append(
                run_bench_exe(
                    exe_g,
                    ["--k", str(args.k), "--warmup", str(args.warmup), "--samples", "100000"],
                )
            )
        else:
            rows.append(
                {
                    "name": "gaussian_sample",
                    "status": "skipped",
                    "reason": "build bench_gaussian first",
                }
            )

    if not args.skip_black_swan and args.profile == "cpu_smoke":
        rows.append(run_black_swan_smoke())

    doc = assemble_results(run_id, args.profile, args.k, args.warmup, rows)
    out_path = out_dir / "results.json"
    out_path.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    failed = [r for r in rows if r.get("status") == "failed"]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

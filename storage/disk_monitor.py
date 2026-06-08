"""Disk usage monitor for triggering FTP sync at configurable threshold."""

from __future__ import annotations

import shutil
from pathlib import Path


def disk_usage_percent(path: str | Path = ".") -> float:
    """Return disk usage percentage for the filesystem containing ``path``."""
    usage = shutil.disk_usage(Path(path).resolve())
    if usage.total == 0:
        return 0.0
    return (usage.used / usage.total) * 100.0


def exceeds_threshold(path: str | Path = ".", threshold: float = 80.0) -> bool:
    """Return True when disk usage exceeds ``threshold`` percent."""
    return disk_usage_percent(path) >= threshold


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Report disk usage percentage.")
    parser.add_argument("--path", default=".", help="Path on target filesystem")
    parser.add_argument(
        "--threshold",
        type=float,
        default=80.0,
        help="Threshold percent; exit 1 if exceeded",
    )
    args = parser.parse_args()
    pct = disk_usage_percent(args.path)
    print(f"{pct:.1f}")
    raise SystemExit(1 if pct >= args.threshold else 0)

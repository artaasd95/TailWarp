#!/usr/bin/env python3
"""
Validate experiment output structure and metadata.
Checks for required files and minimal schema compliance.
"""

import sys
import json
from pathlib import Path

REQUIRED_FILES = [
    "manifest.json",
    "config.json",
    "environment.json",
    "build.json",
    "metrics.json",
    "validation.json",
    "performance.json",
    "summary.md",
]


def validate_experiment(exp_dir):
    """Validate experiment folder structure."""
    exp_path = Path(exp_dir)

    if not exp_path.exists():
        print(f"Error: {exp_dir} does not exist")
        return False

    missing = [f for f in REQUIRED_FILES if not (exp_path / f).exists()]
    if missing:
        print(f"Missing required files: {missing}")
        return False

    artifacts = exp_path / "artifacts"
    if not artifacts.is_dir():
        print("Error: artifacts/ directory missing")
        return False

    try:
        with open(exp_path / "manifest.json", encoding="utf-8") as f:
            manifest = json.load(f)
        if "files" not in manifest:
            print("Error: manifest.json missing 'files'")
            return False
    except Exception as e:
        print(f"Error reading manifest.json: {e}")
        return False

    for name in ("metrics.json", "validation.json", "performance.json", "environment.json"):
        try:
            with open(exp_path / name, encoding="utf-8") as f:
                json.load(f)
        except Exception as e:
            print(f"Error reading {name}: {e}")
            return False

    try:
        with open(exp_path / "metrics.json", encoding="utf-8") as f:
            metrics = json.load(f)
        for key in ("n_samples", "cvar"):
            if key not in metrics:
                print(f"Error: metrics.json missing required field '{key}'")
                return False
    except Exception as e:
        print(f"Error reading metrics.json: {e}")
        return False

    print(f"Validation passed: {exp_dir}")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: validate_experiment.py <experiment_dir>")
        sys.exit(1)

    success = validate_experiment(sys.argv[1])
    sys.exit(0 if success else 1)

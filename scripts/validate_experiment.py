#!/usr/bin/env python3
"""
Validate experiment output structure and metadata.
Checks for required files and schema compliance.
"""

import sys
import json
from pathlib import Path

def validate_experiment(exp_dir):
    """Validate experiment folder structure."""
    exp_path = Path(exp_dir)
    
    if not exp_path.exists():
        print(f"Error: {exp_dir} does not exist")
        return False
    
    required_files = [
        "manifest.json",
        "config.json",
        "environment.json",
        "metrics.json",
        "summary.md"
    ]
    
    missing = []
    for fname in required_files:
        if not (exp_path / fname).exists():
            missing.append(fname)
    
    if missing:
        print(f"Missing required files: {missing}")
        return False
    
    # Validate JSON structure
    try:
        with open(exp_path / "metrics.json") as f:
            metrics = json.load(f)
            # TODO: Check for required metric fields
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


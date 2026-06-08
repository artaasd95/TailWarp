#!/usr/bin/env bash
# Build and run TailWarp benchmarks on RunPod GPU pods.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

CONFIG="${REPO_ROOT}/runpod/config.json"
BUILD_DIR="${REPO_ROOT}/build"

echo "[runpod] building TailWarp"
cmake -S . -B "${BUILD_DIR}" -DCMAKE_BUILD_TYPE=Release
cmake --build "${BUILD_DIR}" --config Release -j"$(nproc 2>/dev/null || echo 4)"

echo "[runpod] running benchmarks"
python benchmarks/run_benchmarks.py --config "${CONFIG}" --output benchmarks/results/runpod

#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

echo "[setup] installing Python deps"
pip install -e ".[dev]" 2>/dev/null || pip install -e .

if command -v cmake >/dev/null 2>&1; then
  cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
  cmake --build build --config Release -j"$(nproc 2>/dev/null || echo 4)"
else
  echo "[setup] cmake not found — install CUDA toolkit + cmake before benchmarks"
fi

mkdir -p benchmarks/results/runpod
echo "[setup] done — bash runpod/run_benchmarks.sh"

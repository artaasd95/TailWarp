#!/usr/bin/env bash
# Local / self-hosted host-only GTest subset (TD-TW-04).
# Requires CUDA toolkit for build; GPU sampler tests may skip without device.

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

cmake -B build -DBUILD_TESTS=ON -DBUILD_BENCHMARKS=ON
cmake --build build -j"$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)"

ctest --test-dir build -R "Cvar|WarningState|KernelParity.Cvar|GpuSmoke" --output-on-failure

echo "Host test subset OK"

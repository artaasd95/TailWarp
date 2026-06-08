#!/usr/bin/env bash
# Collect benchmark results and upload via FTP.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

RESULTS_DIR="${REPO_ROOT}/benchmarks/results/runpod"
ARCHIVE="${REPO_ROOT}/benchmarks/results/runpod_$(date -u +%Y%m%dT%H%M%SZ).tar.gz"

mkdir -p "${RESULTS_DIR}"
tar -czf "${ARCHIVE}" -C "${REPO_ROOT}/benchmarks/results" runpod 2>/dev/null || true

echo "[runpod] uploading results"
python storage/ftp_sync.py --local-root "${REPO_ROOT}"
echo "[runpod] archive: ${ARCHIVE}"

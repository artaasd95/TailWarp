#!/usr/bin/env bash
# Poll disk usage every 10 minutes and trigger FTP sync when above threshold.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
INTERVAL="${SYNC_INTERVAL_SEC:-600}"
THRESHOLD="${SYNC_THRESHOLD:-80}"

cd "${REPO_ROOT}"

while true; do
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] checking disk usage (threshold=${THRESHOLD}%)"
  python "${SCRIPT_DIR}/ftp_sync.py" --check-threshold "${THRESHOLD}" --local-root "${REPO_ROOT}" || true
  sleep "${INTERVAL}"
done

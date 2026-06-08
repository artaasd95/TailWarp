# Storage sync (FTP/SFTP)

Mirror experiment artifacts to remote storage when local disk usage exceeds a threshold (default **80%**).

## Environment variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FTP_HOST` | FTP/SFTP host | *(required)* |
| `FTP_PORT` | Port | `21` (FTP) / `22` (SFTP) |
| `FTP_USER` | Username | *(required)* |
| `FTP_PASS` | Password | *(optional for key-based SFTP)* |
| `FTP_ROOT_DIR` | Remote base directory | `/runpod-backups` |

Remote layout: `{FTP_ROOT_DIR}/{repo_name}/{YYYY-MM-DD}/...`

## Upload directories

- `experiments/results/`
- `experiments/adapters/`
- `data/distilled/`
- `benchmarks/results/`

Files already present on the remote with matching size are skipped.

## Usage

```bash
# One-shot sync (always)
python storage/ftp_sync.py

# Sync only when disk >= 80%
python storage/ftp_sync.py --check-threshold 80

# Background daemon (10 min poll)
bash storage/sync_daemon.sh

# SFTP (requires paramiko)
python storage/ftp_sync.py --protocol sftp
```

## Disk monitor

```bash
python storage/disk_monitor.py --path . --threshold 80
echo $?   # 1 if threshold exceeded
```

"""Mirror local experiment directories to FTP/SFTP remote storage."""

from __future__ import annotations

import argparse
import ftplib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_UPLOAD_DIRS = [
    "experiments/results",
    "experiments/adapters",
    "data/distilled",
    "benchmarks/results",
]


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def _repo_name() -> str:
    return Path(__file__).resolve().parents[1].name


def _remote_date_prefix(remote_root: str, repo: str) -> str:
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"{remote_root.rstrip('/')}/{repo}/{date}"


def _ensure_ftp_dirs(ftp: ftplib.FTP, remote_path: str) -> None:
    parts = [p for p in remote_path.split("/") if p]
    current = ""
    for part in parts:
        current = f"{current}/{part}" if current else part
        try:
            ftp.cwd(current)
        except ftplib.error_perm:
            ftp.mkd(current)
            ftp.cwd(current)


def _remote_file_size(ftp: ftplib.FTP, remote_file: str) -> int | None:
    try:
        return int(ftp.size(remote_file))
    except ftplib.error_perm:
        return None


def _upload_file_ftp(ftp: ftplib.FTP, local: Path, remote_file: str) -> bool:
    remote_size = _remote_file_size(ftp, remote_file)
    local_size = local.stat().st_size
    if remote_size is not None and remote_size == local_size:
        return False
    parent = "/".join(remote_file.split("/")[:-1])
    if parent:
        _ensure_ftp_dirs(ftp, parent)
    with local.open("rb") as handle:
        ftp.storbinary(f"STOR {remote_file}", handle)
    return True


def sync_ftp(
    local_root: Path,
    upload_dirs: list[str],
    *,
    host: str,
    port: int,
    user: str,
    password: str,
    remote_root: str,
    repo: str | None = None,
) -> dict[str, int]:
    repo = repo or _repo_name()
    prefix = _remote_date_prefix(remote_root, repo)
    uploaded = 0
    skipped = 0

    with ftplib.FTP() as ftp:
        ftp.connect(host, port, timeout=60)
        ftp.login(user, password)
        _ensure_ftp_dirs(ftp, prefix)

        for rel in upload_dirs:
            local_dir = local_root / rel
            if not local_dir.is_dir():
                continue
            for local_file in local_dir.rglob("*"):
                if not local_file.is_file():
                    continue
                rel_path = local_file.relative_to(local_root).as_posix()
                remote_file = f"{prefix}/{rel_path}"
                if _upload_file_ftp(ftp, local_file, remote_file):
                    uploaded += 1
                    print(f"uploaded {rel_path}")
                else:
                    skipped += 1

    return {"uploaded": uploaded, "skipped": skipped}


def sync_sftp(
    local_root: Path,
    upload_dirs: list[str],
    *,
    host: str,
    port: int,
    user: str,
    password: str,
    remote_root: str,
    repo: str | None = None,
) -> dict[str, int]:
    try:
        import paramiko
    except ImportError as exc:
        raise ImportError("SFTP requires paramiko: pip install paramiko") from exc

    repo = repo or _repo_name()
    prefix = _remote_date_prefix(remote_root, repo)
    uploaded = 0
    skipped = 0

    transport = paramiko.Transport((host, port))
    transport.connect(username=user, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    assert sftp is not None

    def ensure_remote_dir(remote_path: str) -> None:
        parts = [p for p in remote_path.split("/") if p]
        current = ""
        for part in parts:
            current = f"{current}/{part}" if current else part
            try:
                sftp.stat(current)
            except OSError:
                sftp.mkdir(current)

    ensure_remote_dir(prefix)

    for rel in upload_dirs:
        local_dir = local_root / rel
        if not local_dir.is_dir():
            continue
        for local_file in local_dir.rglob("*"):
            if not local_file.is_file():
                continue
            rel_path = local_file.relative_to(local_root).as_posix()
            remote_file = f"{prefix}/{rel_path}"
            remote_parent = "/".join(remote_file.split("/")[:-1])
            if remote_parent:
                ensure_remote_dir(remote_parent)
            try:
                remote_size = sftp.stat(remote_file).st_size
            except OSError:
                remote_size = None
            local_size = local_file.stat().st_size
            if remote_size is not None and remote_size == local_size:
                skipped += 1
                continue
            sftp.put(str(local_file), remote_file)
            uploaded += 1
            print(f"uploaded {rel_path}")

    sftp.close()
    transport.close()
    return {"uploaded": uploaded, "skipped": skipped}


def main(argv: list[str] | None = None) -> int:
    from disk_monitor import exceeds_threshold

    parser = argparse.ArgumentParser(description="Sync local dirs to FTP/SFTP storage.")
    parser.add_argument("--local-root", default=".", help="Repository root")
    parser.add_argument("--check-threshold", type=float, default=None, help="Skip sync below threshold")
    parser.add_argument("--protocol", choices=("ftp", "sftp"), default="ftp")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    local_root = Path(args.local_root).resolve()
    if args.check_threshold is not None and not exceeds_threshold(local_root, args.check_threshold):
        print(f"disk below {args.check_threshold}% — skipping sync")
        return 0

    host = _env("FTP_HOST")
    user = _env("FTP_USER")
    password = _env("FTP_PASS")
    remote_root = _env("FTP_ROOT_DIR", "/runpod-backups")
    port = int(_env("FTP_PORT", "21" if args.protocol == "ftp" else "22"))

    if not host or not user:
        print("FTP_HOST and FTP_USER must be set", file=sys.stderr)
        return 2

    if args.dry_run:
        print(f"would sync {DEFAULT_UPLOAD_DIRS} to {remote_root}")
        return 0

    sync_fn = sync_ftp if args.protocol == "ftp" else sync_sftp
    stats = sync_fn(
        local_root,
        DEFAULT_UPLOAD_DIRS,
        host=host,
        port=port,
        user=user,
        password=password,
        remote_root=remote_root,
    )
    print(f"done: uploaded={stats['uploaded']} skipped={stats['skipped']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

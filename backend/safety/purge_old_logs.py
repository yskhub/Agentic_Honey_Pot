"""Purge and redact old audit/log files according to retention policy.

This script is intentionally safe and conservative: it rewrites audit/log
files by redacting long digit sequences and optionally removes files older
than `max_age_days`.

Usage (from repo root):
    python -m backend.safety.purge_old_logs --log-dir logs --max-age-days 90 --dry-run
"""
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta
import re

_PII_DIGITS_RE = re.compile(r"(\d{6,})")


def redact_content(s: str) -> str:
    def _mask(m):
        v = m.group(1)
        if len(v) <= 4:
            return 'X' * len(v)
        return 'X' * (len(v) - 4) + v[-4:]
    return _PII_DIGITS_RE.sub(_mask, s)


def purge_logs(log_dir: Path, max_age_days: int = 90, dry_run: bool = True):
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=max_age_days)
    log_dir = Path(log_dir)
    if not log_dir.exists():
        print(f"Log directory {log_dir} not found")
        return

    for p in log_dir.iterdir():
        if not p.is_file():
            continue
        stat = p.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime, timezone.utc)
        action = []
        if mtime < cutoff:
            action.append('delete')
        # Always redact file content in-place (or in dry-run show diff)
        with open(p, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        redacted = redact_content(content)
        if content != redacted:
            action.append('redact')

        print(f"{p.name}: mtime={mtime.isoformat()} actions={action}")
        if dry_run:
            continue
        if 'redact' in action:
            with open(p, 'w', encoding='utf-8') as f:
                f.write(redacted)
        if 'delete' in action:
            try:
                p.unlink()
            except Exception as e:
                print(f"Failed to delete {p}: {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--log-dir', default='logs')
    ap.add_argument('--max-age-days', type=int, default=90)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    purge_logs(Path(args.log_dir), args.max_age_days, args.dry_run)


if __name__ == '__main__':
    main()

#!/usr/bin/env bash
# Simple helper to generate a new AUDIT_HMAC_KEY and prepare dual-key rotation
# Usage:
#   ./dev-scripts/rotate_audit_key.sh --generate --env-file .env
#   ./dev-scripts/rotate_audit_key.sh --new-key-file /path/to/keyfile --env-file .env

set -euo pipefail

ENV_FILE=".env"
NEW_KEY_FILE=""
GENERATE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env-file) ENV_FILE="$2"; shift 2;;
    --new-key-file) NEW_KEY_FILE="$2"; shift 2;;
    --generate) GENERATE=1; shift;;
    -h|--help) echo "Usage: $0 [--generate] [--new-key-file PATH] [--env-file FILE]"; exit 0;;
    *) echo "Unknown arg: $1"; exit 1;;
  esac
done

if [[ -n "$NEW_KEY_FILE" && $GENERATE -eq 1 ]]; then
  echo "Specify either --generate or --new-key-file, not both." >&2
  exit 1
fi

if [[ -n "$NEW_KEY_FILE" ]]; then
  if [[ ! -f "$NEW_KEY_FILE" ]]; then
    echo "New key file not found: $NEW_KEY_FILE" >&2
    exit 1
  fi
  NEW_KEY=$(cat "$NEW_KEY_FILE")
elif [[ $GENERATE -eq 1 ]]; then
  # Try to generate using openssl, fallback to python
  if command -v openssl >/dev/null 2>&1; then
    NEW_KEY=$(openssl rand -base64 32)
  else
    NEW_KEY=$(python - <<'PY'
import os,base64
print(base64.b64encode(os.urandom(32)).decode())
PY
)
  fi
else
  echo "Either --generate or --new-key-file must be provided." >&2
  exit 1
fi

echo "Generated/loaded new AUDIT HMAC key (first 8 chars): ${NEW_KEY:0:8}..."

echo "Writing dual-key entries to $ENV_FILE (appends)."
cat >> "$ENV_FILE" <<EOF
# Added by dev-scripts/rotate_audit_key.sh - next audit HMAC key
AUDIT_HMAC_KEY_NEXT=${NEW_KEY}
EOF

echo "Done. Next steps:
1) Deploy application instances with both AUDIT_HMAC_KEY (current) and AUDIT_HMAC_KEY_NEXT set in environment or secret manager.
2) Allow traffic for a short transition period so running instances verify existing entries and sign new ones with the new key once flipped.
3) When ready, rotate: set AUDIT_HMAC_KEY to the value of AUDIT_HMAC_KEY_NEXT in your secret manager, remove AUDIT_HMAC_KEY_NEXT, and redeploy.
4) Revoke the old key from your secret store and log the rotation event in your KMS audit logs.
"

echo "If you want, commit $ENV_FILE to your deploy pipeline or copy the new key into your secret manager now."

exit 0

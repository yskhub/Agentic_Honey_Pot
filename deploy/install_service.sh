#!/usr/bin/env bash
# Installer helper for Linux hosts. Run from project root on the target host.
set -euo pipefail

INSTALL_DIR=/opt/agentic_honey_pot
VENV_DIR=/opt/venv_agentic
SERVICE_PATH=/etc/systemd/system/sentinel.service

echo "Installing Agentic Honey Pot into $INSTALL_DIR"

if [ "$EUID" -ne 0 ]; then
  echo "This script requires sudo/root. Re-run as root." >&2
  exit 1
fi

mkdir -p $INSTALL_DIR
rsync -a --exclude '.git' --exclude 'data' --exclude 'logs' ./ $INSTALL_DIR/

python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate
pip install --upgrade pip
if [ -f $INSTALL_DIR/requirements.txt ]; then
  pip install -r $INSTALL_DIR/requirements.txt
fi

useradd -r -s /sbin/nologin sentinel || true
chown -R sentinel:sentinel $INSTALL_DIR
chown -R sentinel:sentinel $VENV_DIR

cp deploy/sentinel.service $SERVICE_PATH
systemctl daemon-reload
systemctl enable --now sentinel

echo "Service installed and started. Check status with: systemctl status sentinel"

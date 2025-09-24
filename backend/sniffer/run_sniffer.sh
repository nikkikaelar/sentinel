#!/usr/bin/env bash
# Wrapper to run sniffer with the same venv/env as the backend.
# Requires sudo for pcap. It respects .env for iface/filter settings.

set -euo pipefail

# Discover repo root from this script location
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
export PYTHONPATH="$ROOT/backend"

# Source .env if present
if [ -f "$ROOT/.env" ]; then
  set -a
  source "$ROOT/.env"
  set +a
fi

# Use system python if not in venv
PY=${PYTHON:-python3}

echo "[run_sniffer] using iface=${PSN_IFACE:-eth0} filter=${PSN_BPF_FILTER}"
exec sudo -E $PY "$ROOT/backend/sniffer/sniffer.py"

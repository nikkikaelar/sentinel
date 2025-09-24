#!/usr/bin/env bash
set -euo pipefail
# Install system deps and Python venv on Raspberry Pi
sudo apt update
sudo apt install -y python3-pip python3-venv libpcap0.8
cd "$(dirname "$0")/.."
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip wheel
pip install -r requirements.txt

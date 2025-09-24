"""
settings.py — central configuration loaded from environment variables.

We read .env in development for convenience. On production, set actual env vars.
"""
from __future__ import annotations
import os
from dotenv import load_dotenv

# Load .env if present (dev convenience)
load_dotenv()

PSN_DB = os.getenv("PSN_DB", "./pi_sentinel.db")
PSN_HOST = os.getenv("PSN_HOST", "0.0.0.0")
PSN_PORT = int(os.getenv("PSN_PORT", "8088"))
PSN_RETENTION_DAYS = int(os.getenv("PSN_RETENTION_DAYS", "14"))

# Sniffer config
PSN_IFACE = os.getenv("PSN_IFACE", "eth0")
PSN_BPF_FILTER = os.getenv(
    "PSN_BPF_FILTER",
    "(arp or (udp and (port 67 or port 68 or port 53 or port 5353)))"
)
PSN_WIFI_PROBE_ENABLED = os.getenv("PSN_WIFI_PROBE_ENABLED", "false").lower() == "true"
PSN_WIFI_MON_IFACE = os.getenv("PSN_WIFI_MON_IFACE", "wlan1mon")

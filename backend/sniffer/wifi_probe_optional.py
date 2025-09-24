"""
wifi_probe_optional.py — OPTIONAL 802.11 probe request sniffer.

⚠️ Requires:
- Compatible Wi‑Fi adapter that supports monitor mode
- Interface (e.g., wlan1mon) placed in monitor mode (airmon-ng or iw)
- Local laws permitting passive reception of management frames

This module demonstrates *how* you might capture probe requests. It is NOT
wired into the main service by default to keep the legal footprint conservative.
"""
from __future__ import annotations
from scapy.all import sniff, Dot11, Dot11ProbeReq  # type: ignore
from app.db import insert_event
import time, json

EV_STREAM = "/tmp/pi_sentinel_events.ndjson"
open(EV_STREAM, "a").close()

MON_IFACE = "wlan1mon"  # override via env or CLI in real use

async def write_probe(mac: str, ssid: str | None):
    ts = int(time.time() * 1000)
    await insert_event("./pi_sentinel.db", ts, "WIFI_PROBE", None, None, mac, {"ssid": ssid})
    with open(EV_STREAM, "a") as f:
        f.write(json.dumps({"ts": ts, "proto": "WIFI_PROBE", "mac": mac, "extra": {"ssid": ssid}}) + "\n")

def _handle(pkt):
    if pkt.haslayer(Dot11ProbeReq):
        mac = pkt.addr2
        ssid = None
        # Attempt to extract SSID from information elements if present
        try:
            ssid = pkt.info.decode(errors='ignore') if hasattr(pkt, 'info') else None
        except Exception:
            ssid = None
        # Run async writer synchronously for brevity
        import asyncio
        asyncio.run(write_probe(mac, ssid))

if __name__ == "__main__":
    print(f"[wifi-probe] monitor iface={MON_IFACE}")
    sniff(iface=MON_IFACE, prn=_handle, store=False)

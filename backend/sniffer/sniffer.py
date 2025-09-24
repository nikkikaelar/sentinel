"""
sniffer.py — LAN metadata sniffer using scapy.

Captures ARP, DHCP, DNS, and mDNS on PSN_IFACE. For each packet, we extract minimal
metadata and append an event to SQLite AND write a line to /tmp/pi_sentinel_events.ndjson
for real-time dashboard updates.

Run with sudo (pcap requires elevated privileges) and a Python venv that has scapy.
"""
from __future__ import annotations
import os
import time
import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional

from scapy.all import sniff, ARP, DHCP, DNS, DNSQR, Ether, IP, UDP  # type: ignore

from app.settings import PSN_IFACE, PSN_BPF_FILTER, PSN_DB, PSN_RETENTION_DAYS
from app.db import insert_event

EV_STREAM = "/tmp/pi_sentinel_events.ndjson"

# Ensure stream file exists
open(EV_STREAM, "a").close()

async def write_event(proto: str, src: Optional[str], dst: Optional[str], mac: Optional[str], extra: dict):
    ts = int(time.time() * 1000)
    await insert_event(PSN_DB, ts, proto, src, dst, mac, extra)
    # also append to ndjson stream for WS broadcast
    with open(EV_STREAM, "a") as f:
        f.write(json.dumps({
            "ts": ts, "proto": proto, "src": src, "dst": dst, "mac": mac, "extra": extra
        }) + "\n")

def handle_packet(pkt):
    # Minimal extraction helpers
    mac = pkt[Ether].src if Ether in pkt else None
    src_ip = pkt[IP].src if IP in pkt else None
    dst_ip = pkt[IP].dst if IP in pkt else None

    # ARP (address resolution)
    if ARP in pkt:
        extra = {
            "op": "request" if pkt[ARP].op == 1 else "reply",
            "hwsrc": pkt[ARP].hwsrc,
            "hwdst": pkt[ARP].hwdst,
            "psrc": pkt[ARP].psrc,
            "pdst": pkt[ARP].pdst,
        }
        asyncio.run(write_event("ARP", pkt[ARP].psrc, pkt[ARP].pdst, mac, extra))
        return

    # DHCP (IP lease negotiation)
    if DHCP in pkt:
        opts = {k: v for k, v in pkt[DHCP].options if isinstance(k, str)}
        msg_type = opts.get("message-type")
        extra = {"msg_type": msg_type, "opts": {k: str(v) for k, v in opts.items() if k != "message-type"}}
        asyncio.run(write_event("DHCP", src_ip, dst_ip, mac, extra))
        return

    # DNS/mDNS (name resolution queries)
    if DNS in pkt:
        qname = None
        try:
            if pkt[DNS].qd and isinstance(pkt[DNS].qd, DNSQR):
                qname = pkt[DNS].qd.qname.decode(errors='ignore').rstrip('.')
        except Exception:
            pass
        extra = {"qname": qname, "qr": pkt[DNS].qr}
        proto = "MDNS" if UDP in pkt and pkt[UDP].dport == 5353 else "DNS"
        asyncio.run(write_event(proto, src_ip, dst_ip, mac, extra))
        return

async def retention_job():
    """Optional retention cleaner (simple approach: rewrite DB keeping N days).
    For MVP this is left as documentation; SQLite VACUUM/DELETE can be run via cron.
    """
    pass

if __name__ == "__main__":
    print(f"[sniffer] iface={PSN_IFACE} filter={PSN_BPF_FILTER}")
    sniff(iface=PSN_IFACE, filter=PSN_BPF_FILTER, prn=handle_packet, store=False)

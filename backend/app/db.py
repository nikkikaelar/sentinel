"""
db.py — SQLite schema and helpers.

We store minimal metadata:
- ts (integer epoch ms)
- proto ("ARP" | "DHCP" | "DNS" | "MDNS" | "WIFI_PROBE")
- src, dst (IP strings when applicable; for ARP, use IPs; for probes, None)
- mac (source MAC when available)
- extra (JSON string for small key/values like qname, op, hwsrc/hwdst, hostname)

Privacy: We do not store payloads; only header-derived metadata.
"""
from __future__ import annotations
import aiosqlite
import json
from typing import Any, Dict, List

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts INTEGER NOT NULL,
  proto TEXT NOT NULL,
  src TEXT,
  dst TEXT,
  mac TEXT,
  extra TEXT
);
CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts);
CREATE INDEX IF NOT EXISTS idx_events_proto ON events(proto);
"""

async def init_db(db_path: str):
    async with aiosqlite.connect(db_path) as db:
        await db.executescript(SCHEMA)
        await db.commit()

async def insert_event(db_path: str, ts: int, proto: str, src: str | None, dst: str | None, mac: str | None, extra: Dict[str, Any]):
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            "INSERT INTO events (ts, proto, src, dst, mac, extra) VALUES (?, ?, ?, ?, ?, ?)",
            (ts, proto, src, dst, mac, json.dumps(extra) if extra else None)
        )
        await db.commit()

async def recent_events(db_path: str, limit: int = 200) -> List[Dict[str, Any]]:
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM events ORDER BY ts DESC LIMIT ?", (limit,)) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

async def stats_counts(db_path: str) -> Dict[str, int]:
    out: Dict[str, int] = {}
    async with aiosqlite.connect(db_path) as db:
        async with db.execute("SELECT proto, COUNT(*) FROM events GROUP BY proto") as cur:
            async for proto, count in cur:
                out[proto] = count
    return out

"""
main.py — FastAPI app exposing:
- GET /api/events?limit=N  -> recent events
- GET /api/counts          -> counts by protocol
- WS  /ws                  -> pushes new events in real-time to connected clients
- Static frontend          -> served from ./static after frontend build

The sniffer process writes to SQLite. This API reads from it and broadcasts via WS.
"""
from __future__ import annotations
import asyncio
import json
import os
from typing import List, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .settings import PSN_DB, PSN_HOST, PSN_PORT
from .db import init_db, recent_events, stats_counts
from .models import Event, Counts

app = FastAPI(title="Pi Sentinel Net")

# Connected WS clients for push
clients: Set[WebSocket] = set()

@app.on_event("startup")
async def _startup():
    await init_db(PSN_DB)

@app.get("/api/events", response_model=List[Event])
async def api_events(limit: int = 200):
    return await recent_events(PSN_DB, limit)

@app.get("/api/counts", response_model=Counts)
async def api_counts():
    return {"counts": await stats_counts(PSN_DB)}

@app.websocket("/ws")
async def ws_stream(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        # Keep the connection open; we don't read from client (one-way stream)
        while True:
            await asyncio.sleep(3600)
    except WebSocketDisconnect:
        pass
    finally:
        clients.discard(ws)

# Broadcast helper used by sniffer via UDP localhost or file watch (simple option below)
# For simplicity, we implement a naive file-based notifier: sniffer writes newline-delimited
# JSON events to /tmp/pi_sentinel_events.ndjson; the API tails the file and pushes lines.
# This decouples processes without Redis/MQTT.

EV_STREAM = "/tmp/pi_sentinel_events.ndjson"

async def tail_and_broadcast():
    """Tail EV_STREAM and push each line to all websockets."""
    # Ensure file exists
    open(EV_STREAM, "a").close()
    with open(EV_STREAM, "r") as f:
        # Seek to end to only stream new events
        f.seek(0, os.SEEK_END)
        loop = asyncio.get_event_loop()
        while True:
            line = await loop.run_in_executor(None, f.readline)
            if not line:
                await asyncio.sleep(0.5)
                continue
            # Broadcast raw event JSON; frontend knows how to parse
            dead: List[WebSocket] = []
            for c in clients:
                try:
                    await c.send_text(line.strip())
                except Exception:
                    dead.append(c)
            for d in dead:
                clients.discard(d)

@app.on_event("startup")
async def _start_tailer():
    asyncio.create_task(tail_and_broadcast())

# Serve frontend static build if present
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

# For dev convenience
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=PSN_HOST, port=PSN_PORT, reload=True)

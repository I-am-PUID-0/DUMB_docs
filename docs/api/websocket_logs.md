---
title: WebSocket Logs API
icon: lucide/waves
---

# WebSocket Logs API

The WebSocket Logs API provides a real-time streaming interface for receiving logs from all DUMB-managed subprocesses. It is primarily used by the DUMB Frontend to power the live log viewer.

---

## WebSocket Endpoint

```
/ws/logs
```

Connect to this endpoint using a WebSocket client (e.g., browser or Python client) to receive log lines as plain text.

---

## Message Format

Each log entry is sent as a plain text line formatted by DUMB’s logger, for example:

```
Apr 12, 2025 10:04:01 - INFO - Riven Backend started
```

---

## Filtering Logs (Client-side)

The server pushes all logs to connected clients. It is up to the client to filter based on:

- **Process Name**
- **Log Level**
- **Search Term**

The DUMB Frontend implements dropdowns and search bars for this purpose.

---

## Connection Behavior

- The server **broadcasts logs** to all connected WebSocket clients.
- If the connection is dropped, reconnect using `/ws/logs`.
- Log history is **not buffered**, so missed logs are not resent on reconnect.
- Sending `{"type":"ping"}` will return `pong`.

---

## Example (Python Client)

```python
import websockets
import asyncio
import json

async def consume_logs():
    uri = "ws://localhost:8000/ws/logs"
    async with websockets.connect(uri) as websocket:
        async for message in websocket:
            print(message)

asyncio.run(consume_logs())
```

---

## Related Modules
- [`websocket_logs.py`](https://github.com/I-am-PUID-0/DUMB/blob/master/api/routers/websocket_logs.py)
- [Logs API](logs.md) for historical log file access
- [Frontend Log Viewer](../services/dumb/dumb-frontend.md#real-time-logs)

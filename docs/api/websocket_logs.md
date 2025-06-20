---
title: WebSocket Logs API
---

# WebSocket Logs API

The WebSocket Logs API provides a real-time streaming interface for receiving logs from all DMB-managed subprocesses. It is primarily used by the DMB Frontend to power the live log viewer.

---

## 📡 WebSocket Endpoint

```
/ws/logs
```

Connect to this endpoint using a WebSocket client (e.g., browser or Python client) to receive structured log entries in JSON format.

---

## 🔁 Message Format

Each log entry sent through the WebSocket has the following structure:

```json
{
  "message": "[INFO] riven_backend: Startup complete",
  "level": "INFO",
  "process_name": "riven_backend",
  "timestamp": "2025-04-01T12:34:56.789Z"
}
```

### Fields:
- **message**: Raw log message as a string
- **level**: Log level (`DEBUG`, `INFO`, `WARNING`, etc.)
- **process_name**: Name of the subprocess that generated the log
- **timestamp**: ISO 8601 formatted UTC timestamp

---

## 🔍 Filtering Logs (Client-side)

The server pushes all logs to connected clients. It is up to the client to filter based on:

- **Process Name**
- **Log Level**
- **Search Term**

The DMB Frontend implements dropdowns and search bars for this purpose.

---

## 🛑 Connection Behavior

- The server **broadcasts logs** to all connected WebSocket clients.
- If the connection is dropped, reconnect using `/ws/logs`.
- Log history is **not buffered**, so missed logs are not resent on reconnect.

---

## 🧪 Example (Python Client)

```python
import websockets
import asyncio
import json

async def consume_logs():
    uri = "ws://localhost:8000/ws/logs"
    async with websockets.connect(uri) as websocket:
        async for message in websocket:
            log = json.loads(message)
            print(f"[{log['level']}] {log['process_name']}: {log['message']}")

asyncio.run(consume_logs())
```

---

## 📎 Related Modules
- [`websocket_logs.py`](https://github.com/I-am-PUID-0/DMB/blob/master/api/routers/websocket_logs.py)
- [Logs API](logs.md) for historical log file access
- [Frontend Log Viewer](../services/dmb-frontend.md#real-time-logs)


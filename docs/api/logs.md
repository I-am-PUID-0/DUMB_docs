---
title: Logs API
---

# Logs API

The **Logs API** allows clients to retrieve recent logs captured by DMB and served through the API.

---

## 🔍 Endpoint

```
GET /logs
```

---

## 🧾 Query Parameters

| Parameter | Type   | Description                                                                 |
|-----------|--------|-----------------------------------------------------------------------------|
| `lines`   | int    | Number of recent log lines to return (default: 100).                        |
| `level`   | string | Optional filter by log level (e.g., `INFO`, `ERROR`, `DEBUG`).              |
| `name`    | string | Optional filter by process or service name (e.g., `riven`, `postgres`).     |

---

## 🧪 Example Request

```
GET /logs?lines=50&level=ERROR&name=zilean
```

This request fetches the last 50 lines of logs for the `zilean` service that have an `ERROR` log level.

---

## ✅ Response Format

Returns a JSON array of log entries:

```json
[
  "2024-04-01 12:00:01 INFO rclone: Mount started successfully",
  "2024-04-01 12:01:02 ERROR zilean: Failed to connect to database"
]
```

---

## ⚠️ Notes
- This endpoint provides logs captured by DMB's internal logger and may not reflect stdout/stderr of subprocesses unless specifically routed.
- Filtering by `name` is useful to narrow down issues with a specific subprocess.

---

## 🧱 Related
- [Real-Time WebSocket Logs](websocket_logs.md) for live streaming logs.
- [Process Management](process.md) for interacting with services whose logs may be captured here.


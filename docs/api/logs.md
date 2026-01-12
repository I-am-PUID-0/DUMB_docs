---
title: Logs API
icon: lucide/file-text
---

# Logs API

The **Logs API** allows clients to retrieve recent logs captured by DUMB and served through the API.

---

## Endpoint

```
GET /logs
```

---

## Query Parameters

| Parameter      | Type   | Description                                                                 |
|----------------|--------|-----------------------------------------------------------------------------|
| `process_name` | string | Required process name (e.g., `Riven Backend`, `Zurg w/ RealDebrid`).        |
| `cursor`       | int    | Last byte offset returned by the API (omit for first request).              |
| `tail_bytes`   | int    | Initial bytes to read from the end when no cursor (default: 131072).        |

---

## Example Request

```
GET /logs?process_name=Riven%20Backend
```

This request fetches the latest log chunk for the specified service.

---

## Response Format

Returns a JSON object containing the log chunk and cursor:

```json
{
  "process_name": "Riven Backend",
  "cursor": 123456,
  "chunk": "Apr 12, 2025 10:04:01 - INFO - Riven Backend started\n",
  "reset": true,
  "log": "Apr 12, 2025 10:04:01 - INFO - Riven Backend started\n"
}
```

---

!!! note "Important Notes"
    - When `reset` is `true`, clients should replace their log buffer with `chunk`.
    - On incremental requests, pass the returned `cursor` to get only new bytes.

---

## Related
- [Real-Time WebSocket Logs](websocket_logs.md) for live streaming logs.
- [Process Management](process.md) for interacting with services whose logs may be captured here.

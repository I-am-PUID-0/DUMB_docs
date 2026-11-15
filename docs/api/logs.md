---
title: Logs API
description: Read retained DUMB service logs with byte cursors and file identities, handle rotation safely, and interpret redacted log chunks and reset responses.
icon: lucide/file-text
---

# Logs API

The **Logs API** allows clients to retrieve recent logs captured by DUMB and served through the API.

## Endpoint

```
GET /logs
```

## Query Parameters

| Parameter      | Type   | Description                                                                 |
|----------------|--------|-----------------------------------------------------------------------------|
| `process_name` | string | Required process name (e.g., `Riven Backend`, `Zurg w/ RealDebrid`).        |
| `cursor`       | int    | Last byte offset returned by the API (omit for first request).              |
| `tail_bytes` | int | Initial tail size, default `131072`; accepted range `1024` to `8388608` bytes. |
| `file_id` | string | Opaque identity returned by the previous request; send with `cursor` to detect file rotation. |

## Example Request

```
GET /logs?process_name=Riven%20Backend
```

This request fetches the latest log chunk for the specified service.

## Response Format

Returns a JSON object containing the log chunk and cursor:

```json
{
  "process_name": "Riven Backend",
  "size": 123456,
  "cursor": 123456,
  "chunk": "Apr 12, 2025 10:04:01 - INFO - Riven Backend started\n",
  "reset": true,
  "file_id": "opaque-file-generation",
  "log": "Apr 12, 2025 10:04:01 - INFO - Riven Backend started\n"
}
```

!!! note "Important Notes"
    - When `reset` is `true`, clients should replace their log buffer with `chunk`.
    - On incremental requests, pass the returned `cursor` and `file_id`. A changed file identity or truncated file resets the tail, even when a new file has already grown larger than the old cursor.
    - An initial DUMB API log read returns the current startup section; other services start with a bounded tail. Missing logs return an empty chunk with `reset: true`.
    - Log content passes through DUMB's sensitive-data redactor before it is returned. This covers credential-bearing HTTP headers, session cookies, common URL/config secrets, email addresses, and Plex account/server identifiers.
    - DUMB returns only complete log lines so a sensitive value split across two polling responses cannot bypass redaction.
    - Prefer logs viewed or downloaded through DUMB when sharing diagnostics. An application's native log file on disk is owned by that application and may not have DUMB's response-time redaction applied.

## Related
- [Real-Time WebSocket Logs](websocket_logs.md) for live streaming logs.
- [Process Management](process.md) for interacting with services whose logs may be captured here.

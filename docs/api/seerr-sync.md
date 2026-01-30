---
title: Seerr Sync
icon: lucide/refresh-ccw
---

# Seerr Sync API

Seerr Sync provides one-way request replication from a **primary** Seerr instance to one or more **subordinates**.

It polls the primary at a configurable interval, fingerprints requests using `{mediaType}:{tmdbId}:{is4k}`, and persists sync state in `/config/seerr_sync_state.json` to survive restarts.

---

## Endpoints

### GET `/api/seerr-sync/status`

Summary status of the sync service.

Response (disabled):

```json
{
  "enabled": false,
  "status": "disabled"
}
```

Response (active):

```json
{
  "enabled": true,
  "status": "active",
  "last_poll": "2026-01-29T21:32:46Z",
  "next_poll": "2026-01-29T21:33:46Z",
  "poll_interval_seconds": 60,
  "total_requests_tracked": 1284,
  "total_failed": 9,
  "subordinates": {
    "internal:Sync1": { "synced": 1280, "failed": 5 },
    "internal:Sync2": { "synced": 1281, "failed": 4 }
  }
}
```

Response (initializing):

```json
{
  "enabled": true,
  "status": "initializing",
  "message": "Sync state not yet created"
}
```

---

### GET `/api/seerr-sync/failed`

List failed sync attempts with details.

```json
{
  "count": 9,
  "failed_requests": [
    {
      "fingerprint": "movie:1403290:False",
      "subordinate": "internal:Sync1",
      "media_type": "movie",
      "tmdb_id": 1403290,
      "error": "[TMDB] Failed to fetch movie details: Request failed with status code 404",
      "failed_at": "2026-01-29T21:29:37Z"
    }
  ]
}
```

---

### GET `/api/seerr-sync/state`

Raw sync state (debugging).

```json
{
  "last_poll_ts": "2026-01-29T21:32:46Z",
  "requests": {
    "movie:12345:False": {
      "primary_id": 42,
      "subordinates": {
        "internal:Sync1": { "id": 15, "status": 2, "synced_at": "2026-01-29T21:10:00Z" }
      }
    }
  },
  "failed": {
    "movie:1403290:False||internal:Sync1": {
      "failed_at": "2026-01-29T21:29:37Z",
      "error": "[TMDB] Failed to fetch movie details...",
      "media_type": "movie",
      "tmdb_id": 1403290
    }
  }
}
```

---

### POST `/api/seerr-sync/test`

Test connectivity to a Seerr instance using a URL and API key.

Request body:

```json
{
  "url": "https://seerr.example.com",
  "api_key": "your_api_key"
}
```

Response (success):

```json
{
  "ok": true,
  "status": {
    "version": "1.0.0"
  }
}
```

Response (failure):

```json
{
  "detail": "Seerr responded with HTTP 401"
}
```

---

### DELETE `/api/seerr-sync/failed`

Clear failed requests so they are retried on the next poll.

Query parameters:

- `fingerprint` (optional) – Clear only a specific request.

Response:

```json
{
  "message": "Cleared 9 failed request(s)",
  "cleared": 9
}
```

---

## Notes

- Timestamps are ISO 8601 UTC (`YYYY-MM-DDTHH:MM:SSZ`).
- Failed requests are retried after the configured delay.
- Subordinate identifiers use `internal:<InstanceName>` or external labels when configured.

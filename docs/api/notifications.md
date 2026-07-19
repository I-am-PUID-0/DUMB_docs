---
title: Notifications API
icon: lucide/bell
---

# Notifications API

Notification endpoints are available under `/api/notifications`. They follow the same optional authentication behavior as the other protected DUMB API routes.

If the persistent notification SQLite database is temporarily locked, DUMB
continues running and retries storage initialization in the background. Endpoints
that require queue or history access return HTTP `503` until storage recovers;
configuration and supported-event discovery remain available.

## Configuration

### `GET /api/notifications/config`

Returns notification settings with destination URLs and headers removed. Each destination includes `url_configured` and `headers_configured` booleans.

### `POST /api/notifications/config`

```json
{
  "config": {
    "enabled": true,
    "monitor_interval_sec": 30,
    "history_retention_days": 30,
    "max_attempts": 3,
    "retry_base_sec": 30,
    "destinations": [],
    "thresholds": {
      "cpu_percent": 85,
      "memory_percent": 85,
      "disk_percent": 90,
      "inode_percent": 90,
      "database_pressure": "high",
      "duration_sec": 60
    }
  }
}
```

A blank URL or headers object preserves an existing saved secret for the same destination ID. Destination `service_names` must contain exact process names that are currently enabled in DUMB; disabled template services and unknown names are rejected with `400` rather than retained as hidden filters. An empty list matches all events.

## Supported events

### `GET /api/notifications/events`

Returns the backend-supported event types and severity values. Frontends should use this endpoint instead of hard-coding future event support.

## Test a destination

### `POST /api/notifications/test`

```json
{
  "destination_id": "destination-id",
  "title": "Optional test title",
  "body": "Optional test body"
}
```

Tests bypass the global enable switch, destination enable switch, severity filters, event filters, and cooldowns.

## Send a manual notification

### `POST /api/notifications/send`

```json
{
  "title": "Maintenance starting",
  "body": "DUMB services will be restarted.",
  "severity": "info",
  "destination_ids": ["destination-id"]
}
```

Omit `destination_ids` or set it to `null` to send to every enabled destination with a configured URL. Manual sends bypass the global notification switch and routing/cooldown filters, but they do not override an individual destination's disabled state. Use the explicit destination test endpoint when validating a disabled destination.

## Delivery history

### `GET /api/notifications/history`

Query parameters:

| Parameter | Description |
|-----------|-------------|
| `limit` | 1-500 records; default 100 |
| `status` | Optional exact status filter |
| `event_type` | Optional exact event-type filter |

History responses never contain destination URLs or request headers.

### `DELETE /api/notifications/history`

Deletes completed, failed, and suppressed records. Queued and retrying deliveries are preserved.

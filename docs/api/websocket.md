---
title: WebSocket API
icon: lucide/radio
---

# WebSocket API

DUMB provides three WebSocket endpoints for real-time streaming of logs, service status, and system metrics.

---

## Overview

| Endpoint | Purpose | Data Type |
|----------|---------|-----------|
| `/ws/logs` | Real-time log streaming | Text lines |
| `/ws/status` | Service status updates | JSON |
| `/ws/metrics` | System metrics updates | JSON |

All WebSocket endpoints support authentication via query parameter when auth is enabled.

---

## Authentication

When authentication is enabled, include the access token as a query parameter:

```
ws://localhost:3005/ws/status?token=eyJhbGciOiJIUzI1NiIs...
```

If the token is missing or invalid, the connection will be rejected with a close code.

---

## Status WebSocket

### Endpoint

```
/ws/status
```

Streams the names of tracked running services. Add `health=true` to request the
expanded health and restart-state objects.

### Query parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `interval` | float | `2` | Update interval in seconds (0.5-10) |
| `health` | boolean | `false` | Include health and restart-state details |
| `token` | string | - | JWT access token (required if auth enabled) |

### Connection example

```javascript
const ws = new WebSocket('ws://localhost:3005/ws/status?interval=2&health=true&token=...');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

### Default message format

Without `health=true`, the payload contains only the current running-process
names:

```json
{
  "type": "status",
  "running": ["DUMB Frontend", "Riven Backend"]
}
```

### Expanded message format

With `health=true`, the payload uses `processes`:

```json
{
  "type": "status",
  "processes": [
    {
      "process_name": "Riven Backend",
      "status": "running",
      "healthy": true,
      "health_reason": null,
      "restart": {
        "restart_attempts": 0,
        "restart_successes": 0,
        "restart_failures": 0,
        "recent_restart_attempts": 0,
        "pending": false,
        "next_restart_time": null,
        "disabled": false,
        "last_restart_time": null,
        "last_failure_reason": null,
        "last_exit_time": null,
        "last_exit_reason": null,
        "unhealthy_count": 0,
        "unhealthy_threshold": 3
      }
    }
  ]
}
```

### Field descriptions

| Field | Type | Description |
|-------|------|-------------|
| `process_name` | string | Service display name |
| `status` | string | `running` for entries in this running-process snapshot |
| `healthy` | boolean | Health check result |
| `health_reason` | string | Reason if unhealthy |
| `restart` | object | Current auto-restart counters, pending/disabled state, timestamps, and health threshold |

---

## Metrics WebSocket

### Endpoint

```
/ws/metrics
```

Streams real-time system metrics including CPU, memory, selected filesystem, and selected network-interface usage. Each snapshot's `system.filesystems` array contains the configured container-visible paths; `system.disk` and `system.inode` alias the first path for older clients. `system.network_interfaces` contains per-interface counters and metadata, while `system.net_io` is their compatibility aggregate.

### Query parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `interval` | float | `2` | Update interval in seconds (0.5-10) |
| `history` | boolean | `false` | Include historical metrics on connect |
| `bootstrap` | boolean | `false` | Send a snapshot plus prepared history in one initial message |
| `history_full` | boolean | `false` | Request the full retained history window rather than the default window |
| `history_limit` | integer | `5000` | Maximum raw history rows read for the initial payload |
| `history_since` | number | - | Unix timestamp lower bound for history |
| `history_bucket` | integer | automatic | Requested history bucket size in seconds |
| `history_points` | integer | `600` | Maximum prepared series points in a bootstrap payload |
| `token` | string | - | JWT access token (required if auth enabled) |

### Connection example

```javascript
const ws = new WebSocket('ws://localhost:3005/ws/metrics?interval=2&bootstrap=true&token=...');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'bootstrap') {
    initializeCharts(data.items);
    updateDashboard(data.snapshot);
  } else if (data.type === 'snapshot') {
    // Current metrics
    updateDashboard(data.data);
  } else if (data.type === 'history') {
    // Historical data for charts
    initializeCharts(data.items);
  }
};
```

### Live snapshot message format

```json
{
  "type": "snapshot",
  "data": {
    "timestamp": 1752575400.0,
    "system": {
      "scope": "cgroup",
      "cpu_percent": 45.2,
      "cpu_count": 8,
      "load_avg": [1.5, 1.2, 0.9],
      "mem": {
        "total": 17179869184,
        "used": 8589934592,
        "percent": 50.0
      },
      "disk": {
        "path": "/",
        "total": 500107862016,
        "used": 250053931008,
        "free": 250053931008,
        "percent": 50.0
      },
      "inode": {"path": "/", "percent": 4.2},
      "filesystems": [],
      "net_io": {"sent_bytes": 1073741824, "recv_bytes": 2147483648},
      "network_interfaces": []
    },
    "dumb_managed": [
      {
        "pid": 1234,
        "name": "Riven Backend",
        "cpu_percent": 5.2,
        "rss": 134217728
      }
    ],
    "external": [],
    "database_health": {}
  }
}
```

### History message format

Sent once on connection when `history=true` and `bootstrap` is false:

```json
{
  "type": "history",
  "items": [
    {
      "timestamp": "2025-01-15T10:29:00Z",
      "cpu": { "percent": 44.1 },
      "memory": { "percent": 49.5 }
    },
    {
      "timestamp": "2025-01-15T10:29:05Z",
      "cpu": { "percent": 45.0 },
      "memory": { "percent": 49.8 }
    }
  ],
  "truncated": false
}
```

When `bootstrap=true`, the initial message has `type: "bootstrap"` and includes
`snapshot`, `items`, prepared `series`, `timestamps`, `truncated`, `stats`, and
`bucket_seconds`. Live updates after either initial mode still use
`type: "snapshot"`.

### Metric field descriptions

| Category | Field | Description |
|----------|-------|-------------|
| **CPU** | `system.cpu_percent` | CPU usage for the configured host/cgroup scope |
| **CPU** | `system.cpu_count` | Logical host CPUs or effective cgroup CPU limit |
| **CPU** | `system.load_avg` | 1, 5, 15 minute host load averages |
| **Memory** | `system.mem` | Total, used, and percent for the selected scope |
| **Filesystem** | `system.filesystems` | Per-selected-path capacity, type, availability, and inode data |
| **Filesystem** | `system.disk` / `system.inode` | Compatibility aliases for the first selected path |
| **Network** | `system.network_interfaces` | Per-selected-interface counters and link metadata |
| **Network** | `system.net_io` | Compatibility aggregate across selected interfaces |
| **Processes** | `dumb_managed` / `external` | Managed and bounded external process metrics |
| **Database** | `database_health` | Opt-in database/store health snapshot |

---

## Logs WebSocket

### Endpoint

```
/ws/logs
```

Streams real-time log output from all DUMB-managed services.

### Query parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `token` | string | - | JWT access token (required if auth enabled) |

### Connection example

```javascript
const ws = new WebSocket('ws://localhost:3005/ws/logs?token=...');

ws.onmessage = (event) => {
  // Each message is a log line
  appendToLogViewer(event.data);
};
```

### Message format

Log messages are sent as plain text lines:

```
Apr 12, 2025 10:04:01 - INFO - Riven Backend started
Apr 12, 2025 10:04:02 - DEBUG - Processing request...
Apr 12, 2025 10:04:03 - ERROR - Connection failed: timeout
```

!!! info "Client-side filtering"

    The server broadcasts all logs to connected clients. Filtering by process name, log level, or search term should be implemented client-side.

### Ping/pong heartbeat

Send a ping message to keep the connection alive:

```json
{"type": "ping"}
```

Response (the plain-text `ping` input is also accepted):

```
pong
```

---

## Connection management

### Reconnection strategy

WebSocket connections may drop due to network issues. Implement automatic reconnection:

```javascript
function connectWebSocket() {
  const ws = new WebSocket('ws://localhost:3005/ws/status?token=...');

  ws.onclose = () => {
    // Reconnect after delay with exponential backoff
    setTimeout(connectWebSocket, Math.min(reconnectDelay * 2, 10000));
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    ws.close();
  };
}
```

### Multiple connections

The frontend typically maintains separate connections for each WebSocket endpoint:

- One connection for `/ws/status` (service monitoring)
- One connection for `/ws/metrics` (system charts)
- One connection for `/ws/logs` (log viewer, when active)

---

## Error handling

### Connection errors

| Close Code | Reason |
|------------|--------|
| 1000 | Normal closure |
| 1001 | Server going away (shutdown) |
| 1006 | Abnormal closure (network error) |
| 1008 | Authentication required, invalid/expired token, or disabled user |

### Handling authentication errors

```javascript
ws.onclose = (event) => {
  if (event.code === 1008) {
    // Token expired or invalid - refresh and reconnect
    refreshToken().then(() => connectWebSocket());
  }
};
```

---

## Python client example

```python
import asyncio
import websockets
import json

async def monitor_status():
    uri = "ws://localhost:3005/ws/status?interval=2&health=true"

    async with websockets.connect(uri) as websocket:
        async for message in websocket:
            data = json.loads(message)
            for process in data.get("processes", []):
                print(f"{process['process_name']}: {process['status']}")

asyncio.run(monitor_status())
```

---

## Related pages

- [Authentication API](auth.md) - Token management for WebSocket auth
- [Logs API](logs.md) - REST endpoint for historical log access
- [Process Management API](process.md) - Service control endpoints
- [DUMB Frontend](../services/dumb/dumb-frontend.md) - Web interface using these endpoints

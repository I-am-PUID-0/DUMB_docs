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
ws://localhost:8000/ws/status?token=eyJhbGciOiJIUzI1NiIs...
```

If the token is missing or invalid, the connection will be rejected with a close code.

---

## Status WebSocket

### Endpoint

```
/ws/status
```

Streams real-time service status updates including running state, health status, and restart counts.

### Query parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `interval` | float | `2` | Update interval in seconds (0.5-10) |
| `health` | boolean | `true` | Include health check results |
| `token` | string | - | JWT access token (required if auth enabled) |

### Connection example

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/status?interval=2&health=true&token=...');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

### Message format

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
        "count": 0,
        "last_restart": null,
        "enabled": true
      }
    },
    {
      "process_name": "Zurg w/ RealDebrid",
      "status": "running",
      "healthy": true,
      "health_reason": null,
      "restart": {
        "count": 2,
        "last_restart": "2025-01-15T10:30:00Z",
        "enabled": true
      }
    }
  ]
}
```

### Field descriptions

| Field | Type | Description |
|-------|------|-------------|
| `process_name` | string | Service display name |
| `status` | string | `running`, `stopped`, or `unknown` |
| `healthy` | boolean | Health check result |
| `health_reason` | string | Reason if unhealthy |
| `restart.count` | integer | Number of auto-restarts |
| `restart.last_restart` | string | ISO timestamp of last restart |
| `restart.enabled` | boolean | Whether auto-restart is enabled |

---

## Metrics WebSocket

### Endpoint

```
/ws/metrics
```

Streams real-time system metrics including CPU, memory, disk, and network usage.

### Query parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `interval` | float | `2` | Update interval in seconds (0.5-10) |
| `history` | boolean | `false` | Include historical metrics on connect |
| `bootstrap` | boolean | `true` | Send initial snapshot immediately |
| `token` | string | - | JWT access token (required if auth enabled) |

### Connection example

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/metrics?interval=2&history=true&token=...');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'snapshot') {
    // Current metrics
    updateDashboard(data.data);
  } else if (data.type === 'history') {
    // Historical data for charts
    initializeCharts(data.items);
  }
};
```

### Snapshot message format

```json
{
  "type": "snapshot",
  "data": {
    "timestamp": "2025-01-15T10:30:00Z",
    "cpu": {
      "percent": 45.2,
      "count": 8,
      "load_avg": [1.5, 1.2, 0.9]
    },
    "memory": {
      "total": 17179869184,
      "available": 8589934592,
      "percent": 50.0,
      "used": 8589934592
    },
    "swap": {
      "total": 8589934592,
      "used": 1073741824,
      "percent": 12.5
    },
    "disk": {
      "total": 500107862016,
      "used": 250053931008,
      "free": 250053931008,
      "percent": 50.0
    },
    "network": {
      "bytes_sent": 1073741824,
      "bytes_recv": 2147483648,
      "packets_sent": 1000000,
      "packets_recv": 2000000
    },
    "processes": [
      {
        "pid": 1234,
        "name": "Riven Backend",
        "cpu_percent": 5.2,
        "memory_percent": 2.1,
        "memory_rss": 134217728
      }
    ],
    "boot_time": "2025-01-01T00:00:00Z"
  }
}
```

### History message format

Sent once on connection when `history=true`:

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
  "bucket_seconds": 5
}
```

### Metric field descriptions

| Category | Field | Description |
|----------|-------|-------------|
| **CPU** | `percent` | Overall CPU usage percentage |
| **CPU** | `count` | Number of CPU cores |
| **CPU** | `load_avg` | 1, 5, 15 minute load averages |
| **Memory** | `total` | Total RAM in bytes |
| **Memory** | `available` | Available RAM in bytes |
| **Memory** | `percent` | Memory usage percentage |
| **Disk** | `total` | Total disk space in bytes |
| **Disk** | `used` | Used disk space in bytes |
| **Disk** | `percent` | Disk usage percentage |
| **Network** | `bytes_sent` | Total bytes sent |
| **Network** | `bytes_recv` | Total bytes received |

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
const ws = new WebSocket('ws://localhost:8000/ws/logs?token=...');

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

Response:

```
pong
```

---

## Connection management

### Reconnection strategy

WebSocket connections may drop due to network issues. Implement automatic reconnection:

```javascript
function connectWebSocket() {
  const ws = new WebSocket('ws://localhost:8000/ws/status?token=...');

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
| 4001 | Authentication required |
| 4003 | Invalid or expired token |

### Handling authentication errors

```javascript
ws.onclose = (event) => {
  if (event.code === 4001 || event.code === 4003) {
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
    uri = "ws://localhost:8000/ws/status?interval=2&health=true"

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

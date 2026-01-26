---
title: Metrics Collection
icon: lucide/gauge
---

# Metrics Collection

DUMB includes a comprehensive metrics collection system that monitors system resources and provides both real-time updates and historical data for analysis.

---

## Overview

The metrics system provides:

- **Real-time monitoring** - Live CPU, memory, disk, and network stats
- **Historical tracking** - Time-series data storage for trend analysis
- **Per-process metrics** - Resource usage by individual service
- **WebSocket streaming** - Push updates to connected clients
- **cgroup awareness** - Accurate reporting in containerized environments

---

## Collected metrics

### System metrics

| Category | Metrics |
|----------|---------|
| **CPU** | Usage %, core count, load averages (1/5/15 min) |
| **Memory** | Total, used, available, percentage |
| **Swap** | Total, used, percentage |
| **Disk** | Total, used, free, percentage |
| **Network** | Bytes/packets sent and received |
| **System** | Boot time, uptime |

### Per-process metrics

| Metric | Description |
|--------|-------------|
| **PID** | Process identifier |
| **CPU %** | Process CPU utilization |
| **Memory %** | Process memory utilization |
| **Memory RSS** | Resident set size in bytes |

---

## Configuration

Metrics are configured in `dumb_config.json`:

```json
"dumb": {
  "metrics": {
    "system_scope": "auto",
    "history_enabled": true,
    "history_interval_sec": 5,
    "history_retention_days": 7,
    "history_max_file_mb": 50,
    "history_max_total_mb": 100,
    "history_dir": "/config/metrics"
  }
}
```

### Configuration options

| Option | Default | Description |
|--------|---------|-------------|
| `system_scope` | `auto` | Choose system scope for metrics (`auto`, `host`, `container`) |
| `history_enabled` | `true` | Store historical data |
| `history_interval_sec` | `5` | Seconds between samples |
| `history_retention_days` | `7` | Days to keep history |
| `history_max_file_mb` | `50` | Max size per history file |
| `history_max_total_mb` | `100` | Max total history storage |
| `history_dir` | `/config/metrics` | Directory for history files |

---

## Real-time streaming

Metrics are streamed via WebSocket at `/ws/metrics`:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/metrics?interval=2');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'snapshot') {
    updateDashboard(data.data);
  }
};
```

### Query parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `interval` | `2` | Update frequency (0.5-10 seconds) |
| `history` | `false` | Include historical data on connect |
| `bootstrap` | `true` | Send initial snapshot immediately |
| `token` | - | JWT token (if auth enabled) |

---

## Historical data

### Storage format

Historical metrics are stored as JSON files in `/config/metrics/`:

```
/config/metrics/
├── metrics_2025-01-15.json
├── metrics_2025-01-14.json
└── metrics_2025-01-13.json
```

### Data structure

Each history entry contains:

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "cpu": {
    "percent": 45.2,
    "count": 8,
    "load_avg": [1.5, 1.2, 0.9]
  },
  "memory": {
    "total": 17179869184,
    "available": 8589934592,
    "percent": 50.0
  },
  "disk": {
    "total": 500107862016,
    "used": 250053931008,
    "percent": 50.0
  },
  "network": {
    "bytes_sent": 1073741824,
    "bytes_recv": 2147483648
  }
}
```

### Querying history

Retrieve historical data via API:

```bash
# Get history with time range
curl "http://localhost:8000/api/metrics/history?start=2025-01-14&end=2025-01-15"

# Get history with bucket aggregation
curl "http://localhost:8000/api/metrics/history?bucket_seconds=300"
```

---

## cgroup awareness

DUMB automatically detects containerized environments and reports appropriate metrics:

### Container mode

When running in Docker/Kubernetes with resource limits:

- **CPU** - Reports usage relative to container limit
- **Memory** - Reports container memory limit, not host
- **Disk** - Reports container filesystem stats

### Host mode

When running without cgroup limits:

- Reports full host system resources

!!! info "Detection"

    cgroup detection is automatic. DUMB checks for cgroup v1 and v2 interfaces.

---

## API endpoints

### Current metrics

```bash
GET /api/metrics
```

Returns the current metrics snapshot.

### Historical metrics

```bash
GET /api/metrics/history
```

Query parameters:

| Parameter | Description |
|-----------|-------------|
| `start` | Start date (ISO format) |
| `end` | End date (ISO format) |
| `bucket_seconds` | Aggregation bucket size |
| `max_points` | Maximum data points to return |

---

## Frontend integration

### Metrics page

The frontend Metrics page displays:

- Real-time gauges for CPU, memory, disk
- Historical line charts
- Per-process resource table
- System information panel

### Dashboard alerts

Configure thresholds in Settings to show alerts:

| Resource | Default Threshold |
|----------|------------------|
| CPU | 85% |
| Memory | 85% |
| Disk | 90% |

Alerts appear as banners when thresholds are exceeded.

---

## Data retention

### Automatic cleanup

Old metrics files are automatically removed based on:

- `history_retention_days` - Files older than this are deleted
- `history_max_total_size_mb` - Oldest files deleted when exceeded

### Manual cleanup

To manually clear metrics history:

```bash
rm /config/metrics/metrics_*.json
```

---

## Performance considerations

### Collection overhead

Metrics collection has minimal performance impact:

- CPU sampling uses `/proc/stat`
- Memory from `/proc/meminfo`
- Non-blocking I/O operations

### Storage requirements

Estimate storage needs:

| Interval | Daily Size (approx) |
|----------|---------------------|
| 5 seconds | ~5 MB |
| 10 seconds | ~2.5 MB |
| 30 seconds | ~800 KB |

---

## Troubleshooting

### Metrics not updating

1. Check WebSocket connection status
2. Verify `metrics.enabled` is `true`
3. Check for JavaScript errors in browser console

### High storage usage

1. Reduce `history_retention_days`
2. Increase `history_interval`
3. Lower `history_max_total_size_mb`

### Incorrect resource values

1. Verify cgroup detection is working
2. Check container resource limits
3. Restart DUMB to refresh detection

---

## Related pages

- [Frontend Metrics](../frontend/metrics.md) - UI guide
- [WebSocket API](../api/websocket.md) - Streaming protocol
- [Dashboard](../frontend/dashboard.md) - Alert display

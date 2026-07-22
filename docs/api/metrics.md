---
title: Metrics API
icon: lucide/activity
---

# Metrics API

The Metrics API provides live snapshots, database-health observations, historical series, storage status, and legacy-history migration. Authentication follows the normal DUMB API configuration.

## Current snapshot

```http
GET /metrics
```

Returns current system, managed-process, external-process, and configured Database Health data. `system.filesystems` contains one entry per configured `dumb.metrics.filesystem_paths` value. `system.disk` and `system.inode` remain aliases for the first configured path for backward compatibility.

## Filesystem discovery

```http
GET /metrics/filesystems
```

Returns `configured_paths` plus eligible filesystem mount points visible inside the DUMB container. The response intentionally uses container paths; Docker host paths that are not mounted into the container cannot be discovered or monitored. Clients should gate this endpoint and the `filesystem_paths` setting on the `metrics_filesystem_selection` capability.

## Network interface discovery

```http
GET /metrics/network-interfaces
```

Returns `configured_interfaces` plus interfaces visible inside DUMB's network namespace. Candidate entries include interface name, availability/link state, speed, MTU, and cumulative byte/packet/error/drop counters; IP addresses are not returned. Clients should gate this endpoint and `dumb.metrics.network_interfaces` on the `metrics_network_interface_selection` capability.

In current snapshots, `system.network_interfaces` contains each selected visible interface. `system.net_io` remains the compatibility aggregate and sums only the selected available interfaces. The default `["all"]` selects every visible interface. Host interfaces cannot be discovered from a bridge-networked container merely by changing `system_scope`.

## Database Health

```http
GET /metrics/database-health
GET /metrics/database-health?process_name=NzbDAV&refresh=true
```

`process_name` limits the response to one managed service. `refresh=true` invalidates the cached bounded probe before collection.

## Raw history

```http
GET /metrics/history?since=1784300000&limit=5000
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `since` | Six hours ago | Earliest Unix timestamp |
| `full` | `false` | Read without the default lower time bound |
| `limit` | `5000` | Maximum snapshots returned |

The response contains ordered `items` and a `truncated` indicator. The configured database backend is transparent to clients.

## Chart history

```http
GET /metrics/history_series?since=1784300000&bucket_seconds=60&max_points=600
```

This endpoint returns compact items, timestamps, CPU/memory/disk/inode percentage series, per-selected-filesystem disk/inode series, per-selected-interface send/receive rate series, derived aggregate disk/network rate series, summary statistics, truncation state, and the effective bucket size. DUMB automatically increases the bucket size when necessary to honor `max_points`.

## Storage status

```http
GET /metrics/history/storage
GET /metrics/history/storage?probe_postgresql=true
```

The response reports:

- `configured_provider`: `sqlite` or `postgresql`;
- `active_provider`: provider currently serving history reads;
- `fallback_active`: whether PostgreSQL is configured but SQLite is active;
- `last_error` and `last_postgresql_success`;
- SQLite sample range, raw/compressed bytes, file allocation, and compression ratio;
- PostgreSQL sample range and relation allocation when reachable;
- preserved JSONL file count/size and import result.

`probe_postgresql=true` bypasses the reconnect backoff for a deliberate operator test. It does not disable SQLite fallback or expose PostgreSQL credentials.

## Import legacy JSONL

```http
POST /metrics/history/migrate
POST /metrics/history/migrate?force=true
```

The import reads legacy `metrics-YYYYMMDD-NNN.jsonl` files from the configured history directory and upserts snapshots into SQLite by timestamp. It is safe to repeat and preserves source files. DUMB records the migration as complete only when every line decodes and every batch writes successfully. A malformed JSONL record or partial write returns `completed: false` with a nonzero `skipped` count and remains retryable on the next import or DUMB startup. Without `force=true`, only a completed migration returns its recorded result without rescanning all files. When PostgreSQL is configured, a rescan requires a full idempotent SQLite-to-PostgreSQL reconciliation before PostgreSQL can resume serving history reads; this also backfills imported samples older than PostgreSQL's current newest row.

## Activate PostgreSQL storage

```http
POST /metrics/history/storage/activate-postgresql
```

After `dumb.metrics.storage.provider` has been saved as `postgresql`, this endpoint performs restart-free activation:

1. Enables DUMB-managed PostgreSQL and registers the configured Metrics database.
2. Starts PostgreSQL when stopped, or reuses the running process.
3. Creates enabled databases when needed.
4. Replays the retained SQLite continuity buffer into PostgreSQL.
5. Promotes PostgreSQL as the active history-read provider only after synchronization succeeds.

The response includes `status`, `provider`, `database`, `postgres_enabled`, `postgres_running`, `postgres_started`, `postgres_reused`, `synced_samples`, and the resulting provider status. `postgres_started` means this request launched PostgreSQL; `postgres_reused` means it was already running. Concurrent activation returns `409`. Provisioning or synchronization failure returns `503` with a safe stage description; detailed errors remain in DUMB logs, and SQLite remains active.

Clients should gate this call on the `metrics_history_hot_activation` process capability. Older backends require the normal DUMB restart to provision PostgreSQL.

## Failure behavior

In PostgreSQL mode, each new sample is committed to SQLite before PostgreSQL synchronization. PostgreSQL read/write failures change the active provider to SQLite. The complete retained SQLite window is idempotently reconciled after PostgreSQL recovers, and PostgreSQL is promoted only after that succeeds.

Notification persistence is separate and never moves to PostgreSQL. See [Notifications API](notifications.md).

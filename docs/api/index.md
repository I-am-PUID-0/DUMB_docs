---
title: DUMB API Overview
description: Reach the DUMB REST and WebSocket APIs through the dashboard gateway, authenticate clients, and find task-specific endpoint references.
icon: lucide/code
---

# DUMB API

Use the API to inspect configuration, control services, read logs and metrics, and run supported maintenance workflows.

**Visual guide:** [See how the dashboard and API exchange data](../architecture/frontend.md#data-flow).

## Connect through the dashboard

The dashboard server on port `3005` is also the normal API gateway.

| Client request | Backend-native route |
|---|---|
| `http://<host>:3005/api/health` | `/health` |
| `http://<host>:3005/api/process/processes` | `/process/processes` |
| `http://<host>:3005/api/auth/login` | `/auth/login` |
| `ws://<host>:3005/ws/status` | `/ws/status` |

**REST paths in this reference are backend-native.** Add `/api` when calling through the frontend. WebSockets keep `/ws/*` without that prefix.

```bash
curl http://localhost:3005/api/health
```

The native backend binds to `127.0.0.1:8000` inside DUMB by default. The maintained Compose file does not publish it. From inside the container, the equivalent request is:

```bash
curl http://127.0.0.1:8000/health
```

The gateway forwards requests; backend authentication still applies. It does not provide an alternate API with different permissions.

## Authenticate a client

Check `/api/auth/status` for the current mode. When authentication is enabled, obtain a DUMB access token through the configured login flow and send it as a bearer token:

```bash
curl -H "Authorization: Bearer $DUMB_ACCESS_TOKEN" \
  http://localhost:3005/api/process/processes
```

See [Authentication API](auth.md) for local login, OIDC, token refresh, and user management. See [WebSocket API](websocket.md#authentication) for socket authentication.

## Endpoint references

| Task | Reference |
|---|---|
| Inspect or control services; check capabilities | [Process management](process.md) |
| Change DUMB or application configuration | [Configuration](config.md) |
| Check process/listener readiness | [Health](health.md) |
| Read retained log chunks | [Logs](logs.md) |
| Receive live status, metrics, and logs | [WebSockets](websocket.md), [log stream](websocket_logs.md) |
| Read metrics history and manage its storage | [Metrics](metrics.md) |
| Configure destinations and inspect deliveries | [Notifications](notifications.md) |
| Configure AI providers or preview diagnostics | [AI Assistant](ai.md) |
| Inspect cross-instance Seerr sync | [Seerr Sync](seerr-sync.md) |
| Install updates or maintain the install cache | [Updates](updates.md) |
| Repair, snapshot, compare, or restore links | [Symlinks](symlinks.md) |
| Migrate a supported SQLite application | [PostgreSQL migration](postgres-migration.md) |
| Benchmark InfiniDysk-backed rclone | [Rclone optimizer](rclone-optimizer.md) |
| Review library protection incidents | [Media library protection](media-library-protection.md) |
<!-- dev:start -->
| Plan and complete application integration | [Setup](setup.md) |
| Back up or restore an installation | [Installation backups](installation-backups.md) |
| Register archive destinations | [Backup storage](backup-storage.md) |
| Install or migrate native InfiniDysk 2 | [InfiniDysk 2](infinidysk-v2.md) |
<!-- dev:end -->

## Use the running schema

The backend serves its OpenAPI schema at `/openapi.json`, Swagger UI at `/docs`, and Scalar at `/scalar`. These paths are available on the backend listener; they are separate from this website.

The running schema describes the exact installed API. Before offering optional actions, inspect `GET /process/capabilities` and require any workflow protocol/version fields. A newer dashboard or documentation channel cannot add support to an older backend.

## Source

API routing lives in [`api/api_service.py`](https://github.com/I-am-PUID-0/DUMB/blob/dev/api/api_service.py) and [`api/routers/`](https://github.com/I-am-PUID-0/DUMB/tree/dev/api/routers). The [architecture guide](../architecture/backend.md) explains configuration and process ownership.

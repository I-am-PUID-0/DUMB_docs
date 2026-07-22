---
title: DUMB API
icon: lucide/code
---

# DUMB API
The **DUMB API** is the central communication layer between the DUMB Frontend and the backend service. It handles requests for logs, service management (start/stop), configuration updates, and health checks.

## Access model

The maintained Compose file does not publish port `8000`. The API binds to `127.0.0.1:8000` inside the DUMB container and dmbdb proxies it through the normal frontend address:

| Use | URL |
|---|---|
| REST through dmbdb | `http://<host>:3005/api/<backend-path>` |
| WebSockets through dmbdb | `ws://<host>:3005/ws/<stream>` |
| Native API inside the container | `http://127.0.0.1:8000/<backend-path>` |

For example, native `/process/processes` is exposed as `/api/process/processes` through dmbdb. WebSocket routes do not gain an `/api` prefix.

The proxy is available to more than the dashboard itself. Scripts, integrations,
and other API clients can call `http://<host>:3005/api/...`; dmbdb removes the
gateway prefix and forwards the request to FastAPI. The backend performs the
same authentication and authorization checks regardless of which access path
was used.

!!! danger "Direct exposure"
    Setting `host` to `0.0.0.0` and publishing port `8000` exposes powerful lifecycle and configuration endpoints. Enable DUMB authentication and restrict the port to trusted networks before doing this.

---

## Configuration Settings in `dumb_config.json`
Located in `dumb.api_service`:
```json
"enabled": true,
"process_name": "DUMB API",
"log_level": "INFO",
"host": "127.0.0.1",
"port": 8000
```

### Configuration Key Descriptions
- **`enabled`** – Whether the API service should run.
- **`process_name`** – Used in process management and logs.
- **`log_level`** – Logging verbosity for the API.
- **`host`** – Address on which the backend listens. Keep the default loopback value when using dmbdb.

    !!! note "`0.0.0.0` allows access to the API from all addresses"

- **`port`** – Internal backend listener port. It is not automatically published to the Docker host.

## What the API owns

- Optional JWT authentication and user setup
- Service lifecycle, dependency graphs, update controls, and onboarding
- DUMB and service configuration validation/persistence
- Logs, current metrics, metrics history, Database Health, and notifications
- Symlink repair/snapshots and guarded SQLite-to-PostgreSQL migration jobs
- Optional AI diagnostic bundle preview and provider calls
- Real-time log, status, and metrics WebSockets

The backend advertises optional features through `GET /process/capabilities`. Frontends and automation should gate newer actions on these capability flags instead of assuming every DUMB version supports every endpoint.

## Health and interactive schema

- Native health check: `GET /health`
- OpenAPI JSON: `/openapi.json`
- Swagger UI: `/docs`
- Scalar UI: `/scalar`

The interactive documentation endpoints live on the native backend listener. See the [API overview](../../api/index.md) for access choices and the complete reference.

## Persistence and logs

API settings are stored with the main runtime configuration at `/config/dumb_config.json`. Authentication users and the generated JWT secret are stored separately at `/config/users.json`. DUMB logs are written below the configured `/log` directory.

## Related pages

- [API overview](../../api/index.md)
- [Authentication](../../features/authentication.md)
- [Configuration API](../../api/config.md)
- [Process Management API](../../api/process.md)
- [WebSocket API](../../api/websocket.md)

---

---
title: Configuration API
description: Read effective DUMB settings, validate and persist configuration updates, edit native service files, and inspect onboarding and embedded UI routes.
icon: lucide/settings
---

# Configuration API

Read and update DUMB's effective configuration, inspect its schema, or work with an application's native configuration file. These are different surfaces: a change to DUMB settings does not necessarily apply every native application change immediately.

## Choose the right surface

| Task | Endpoint |
|---|---|
| Read effective DUMB configuration | `GET /config` |
| Update a DUMB service or global settings | `POST /config` |
| Inspect the supported schema | `GET /config/schema` |
| Read or edit a native application config | `POST /config/service-config` |
| Inspect embedded UI routes | `GET /config/service-ui` |

Paths are backend-native. Add `/api` through the dashboard gateway and include a bearer token when authentication is enabled. Configuration responses can contain credentials; treat them as private.

## Endpoints

### `GET /config`
Returns the currently loaded in-memory configuration. You can optionally pass `process_name` to fetch a single service block.

Example:
```bash
curl http://localhost:3005/api/config
```

### `POST /config`
Updates config in memory. When `process_name` is provided, it updates only that service block and can optionally persist to disk. Without `process_name`, it performs a global update.

**Request Body:**
```json
{
  "process_name": "Riven Backend",
  "updates": {
    "log_level": "DEBUG"
  },
  "persist": true
}
```

Example:
```bash
curl -X POST http://localhost:3005/api/config \
  -H "Content-Type: application/json" \
  -d '{"process_name":"Riven Backend","updates":{"log_level":"DEBUG"},"persist":true}'
```

### `GET /config/schema`
Returns the JSON schema used for config validation.

Example:
```bash
curl http://localhost:3005/api/config/schema
```

### `POST /config/process-config/schema`
Returns the config schema subtree for a specific `process_name`.

**Request Body:**
```json
{
  "process_name": "Riven Backend"
}
```

Example:
```bash
curl -X POST http://localhost:3005/api/config/process-config/schema \
  -H "Content-Type: application/json" \
  -d '{"process_name":"Riven Backend"}'
```

### `POST /config/service-config`
Reads or updates a service-specific config file (JSON/YAML/CONF/Python/XML). If `updates` is omitted, the raw config is returned.

**Request Body:**
```json
{
  "service_name": "Zurg w/ RealDebrid",
  "updates": ""
}
```

Example:
```bash
curl -X POST http://localhost:3005/api/config/service-config \
  -H "Content-Type: application/json" \
  -d '{"service_name":"Zurg w/ RealDebrid"}'
```

### `GET /config/service-ui-map`

Returns the sanitized embedded-UI route name to backend `config_key` mapping used by the dmbdb proxy. Clients should treat this endpoint as the source of truth and use their local service-type fallback only when startup authentication prevents the map from loading.

```json
{
  "altmount": "altmount",
  "traefik_proxy_admin": "traefik_proxy_admin"
}
```

### `GET /config/service-ui`
Returns a list of enabled services with UI ports, proxied paths, and the current service UI toggle state. The list is dynamic and only includes services that are enabled and expose a UI.

**Response:**
```json
{
  "enabled": true,
  "services": [
    {
      "name": "Riven Frontend",
      "port": 3000,
      "path": "/service/ui/riven_frontend"
    },
    {
      "name": "pgAdmin 4",
      "port": 5050,
      "path": "/service/ui/pgadmin"
    },
    {
      "name": "AltMount",
      "port": 8088,
      "path": "/service/ui/altmount"
    },
    {
      "name": "Traefik Proxy Admin",
      "port": 3004,
      "path": "/service/ui/traefik_proxy_admin"
    }
  ]
}
```

### `POST /config/service-ui`
Enables or disables the embedded service UI feature. When enabled, DUMB writes Traefik routes for service UIs under `/service/ui/<service>` and the DUMB frontend can embed those routes through iframe-aware `/ui/<service>` paths.

**Request Body:**
```json
{
  "enabled": true
}
```

**Response:**
```json
{
  "enabled": true,
  "services": [],
  "traefik_config": "/config/traefik/dynamic/services.yaml"
}
```

### `GET /config/onboarding-status`
Returns whether onboarding is required.

### `POST /config/onboarding-completed`
Marks onboarding as complete.

### `POST /config/reset-onboarding`
Resets onboarding to incomplete.

## Validation and persistence

Updates are validated against DUMB's schema. Service updates can be kept in memory with `persist: false`; they still change effective settings and are not a dry-run preview. A restart discards an unpersisted change. Global updates follow the route's persistence behavior; review the response rather than treating every config request as an inspection.

When native application settings are regenerated during service setup, DUMB-owned fields may be reconciled again. Use the application's own UI for fields its service guide leaves operator-managed.

## Related Pages
- [Services Overview](../services/index.md)
- [Logs](logs.md)

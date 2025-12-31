---
title: Configuration API
---

# Configuration API

The Configuration API is responsible for exposing endpoints that manage and manipulate DUMB's configuration settings (`dumb_config.json`). These endpoints provide tools for loading, updating, saving, and validating configuration data for all DUMB services.

---

## Module: `config.py`
Located in: `api/routers/config.py`

---

## Endpoints

### `GET /config`
**Description:**
Returns the currently loaded in-memory configuration. You can optionally pass `process_name` to fetch a single service block.

**Usage Example:**
```bash
curl http://localhost:8000/config
```

---

### `POST /config`
**Description:**
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

**Usage Example:**
```bash
curl -X POST http://localhost:8000/config \
  -H "Content-Type: application/json" \
  -d '{"process_name":"Riven Backend","updates":{"log_level":"DEBUG"},"persist":true}'
```

---

### `GET /config/schema`
**Description:**
Returns the JSON schema used for config validation.

**Usage Example:**
```bash
curl http://localhost:8000/config/schema
```

---

### `POST /config/process-config/schema`
**Description:**
Returns the config schema subtree for a specific `process_name`.

**Request Body:**
```json
{
  "process_name": "Riven Backend"
}
```

**Usage Example:**
```bash
curl -X POST http://localhost:8000/config/process-config/schema \
  -H "Content-Type: application/json" \
  -d '{"process_name":"Riven Backend"}'
```

---

### `POST /config/service-config`
**Description:**
Reads or updates a service-specific config file (JSON/YAML/CONF/Python/XML). If `updates` is omitted, the raw config is returned.

**Request Body:**
```json
{
  "service_name": "Zurg w/ RealDebrid",
  "updates": ""
}
```

**Usage Example:**
```bash
curl -X POST http://localhost:8000/config/service-config \
  -H "Content-Type: application/json" \
  -d '{"service_name":"Zurg w/ RealDebrid"}'
```

---

### `GET /config/service-ui`
**Description:**
Returns a list of enabled services with UI ports and writes a Traefik dynamic config file.

---

### `GET /config/onboarding-status`
**Description:**
Returns whether onboarding is required.

---

### `POST /config/onboarding-completed`
**Description:**
Marks onboarding as complete.

---

### `POST /config/reset-onboarding`
**Description:**
Resets onboarding to incomplete.

---

## Developer Notes

- The config is held in memory for fast access and allows the user to experiment or preview changes before committing them to file.
- Validation uses internal DUMB schema checks to ensure required keys and structure.
- Routes include error handling for malformed config data.

---

## Related Pages
- [Services Overview](../services/index.md)
- [Logs](logs.md)

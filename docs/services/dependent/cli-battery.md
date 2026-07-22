---
title: CLI Battery
icon: lucide/battery-charging
---

# CLI Battery Configuration

In the CLI Debrid layout currently managed by DUMB, **CLI Battery** is a separate
Flask-based companion application. It provides metadata services and background
processing, integrates with Trakt, and exposes a lightweight web API for managing
movies and TV shows. This service must be running for the current DUMB-supported
CLI Debrid layout to operate properly.

!!! info "Upstream pre-release architecture change"

    [CLI Debrid v0.7.29](https://github.com/godver3/cli_debrid/releases/tag/v0.7.29)
    is an upstream pre-release. Commit
    [`ef4deb5`](https://github.com/godver3/cli_debrid/commit/ef4deb5bbed60826ef2aaa48be0ecb17250ea87e)
    replaces the standalone Flask/HTTP service with an in-process Python module,
    removing the separate port and process from that upstream layout.

    DUMB has not yet made its dependency graph version-aware: its configuration
    still contains `cli_battery/main.py`, port `5001`, and CLI Battery as a
    prerequisite. Keep this service enabled for stable/older CLI Debrid releases.
    If you intentionally use v0.7.29 or a newer pre-release with the in-process
    rewrite, manually disable the standalone CLI Battery service.

    Normal DUMB startup skips a disabled CLI Battery. A guided **Start Core
    Service** or onboarding action may re-enable it from the current static
    dependency map, so re-check the toggle after using those flows.

## Service relationships

| Classification | Role |
| -------------- | ---- |
| Dependent | CLI Debrid companion service |
| Used By | Stable/older [CLI Debrid](../core/cli-debrid.md) layouts that use the separate port-5001 service |
| Exposes UI | Yes |

---

## Configuration settings in `dumb_config.json`

```json
"cli_battery": {
  "enabled": false,
  "process_name": "CLI Battery",
  "suppress_logging": false,
  "log_level": "INFO",
  "port": 5001,
  "platforms": ["python"],
  "command": [
    "/cli_debrid/venv/bin/python",
    "cli_battery/main.py"
  ],
  "config_dir": "/cli_debrid",
  "config_file": "/cli_debrid/data/config/settings.json",
  "log_file": "/cli_debrid/data/logs/battery_debug.log",
  "env": {
    "PYTHONPATH": "/cli_debrid",
    "USER_CONFIG": "/cli_debrid/data/config/",
    "USER_LOGS": "/cli_debrid/data/logs/",
    "USER_DB_CONTENT": "/cli_debrid/data/db_content/",
    "CLI_DEBRID_BATTERY_PORT": "{port}"
  }
},
```

### Configuration Key Descriptions

* **`enabled`**: Enables the CLI Battery service.
* **`process_name`**: Display name in logs and process manager.
* **`suppress_logging`**: Suppresses CLI Battery logs in the main DUMB output.
* **`log_level`**: Controls verbosity of logging.
* **`port`**: CLI Battery service port.
* **`command`**: How the service is started.
* **`config_dir`** / **`config_file`**: Configuration paths used by the battery.
* **`log_file`**: Path to the CLI Battery log file.
* **`env`**: Environment variables passed to the subprocess.

### Environment variables

* `CLI_DEBRID_BATTERY_PORT`: Port the Flask app binds to (defaults to `port`).
* `USER_CONFIG`: Config directory (`/cli_debrid/data/config/`).
* `USER_LOGS`: Log directory (`/cli_debrid/data/logs/`).
* `USER_DB_CONTENT`: Metadata database directory (`/cli_debrid/data/db_content/`).
* `PYTHONPATH`: Module lookup path (`/cli_debrid`).

!!! warning "Trakt authorization"

    CLI Battery handles Trakt OAuth flows. Make sure the callback URL you authorize matches the port you expose.

---

## Required by stable/older CLI Debrid layouts

CLI Battery must be running **before** a CLI Debrid release that depends on its
standalone API launches. This ordering does not apply to the in-process v0.7.29+
pre-release design; disable this separate DUMB service for that layout.

---

## Web interface and API

CLI Battery is a Flask web app exposing a browser UI and REST API:

### Web Dashboard

* `/` — Home dashboard with metadata stats
* `/debug` — Debug view of all metadata items
* `/metadata` — Full metadata list
* `/providers` — Enable/disable metadata providers
* `/settings` — View and update settings

### API Endpoints

* `/api/metadata/<imdb_id>` — Fetch metadata for a specific movie or show
* `/api/seasons/<imdb_id>` — Fetch seasons for a show
* `/authorize_trakt` — Start Trakt OAuth authorization
* `/trakt_callback` — Handle the Trakt OAuth callback

---

## Access

- Navigate to: `http://<host>:<port>` (default `5001`)

---

## Access via Traefik

If Traefik is enabled in DUMB, CLI Battery can be reached via the proxy path:

```
http://<host>:18080/service/ui/cli_battery/
```

---

## Logs and data paths

- Logs: `/cli_debrid/data/logs/battery_debug.log`
- Config: `/cli_debrid/data/config/settings.json`
- Metadata DB: `/cli_debrid/data/db_content/`

---

## Additional Resources

* [CLI Debrid GitHub Repository](https://github.com/godver3/cli_debrid)
* [CLI Battery Source Code](https://github.com/godver3/cli_debrid/tree/main/cli_battery)

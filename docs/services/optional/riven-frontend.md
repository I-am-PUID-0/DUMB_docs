---
title: Riven Frontend
icon: lucide/layout-dashboard
---

# Riven Frontend

The **Riven Frontend** is the web-based interface for interacting with the Riven Backend. It allows users to manage settings, content, and integrations from a clean and modern UI.

DUMB handles automatic installation and updates of the frontend, including versioning and branch targeting. It is served by a lightweight web server and pre-configured to communicate with the backend at startup.

---

## Configuration Settings in `dumb_config.json`

```json
"riven_frontend": {
    "enabled": false,
    "process_name": "Riven Frontend",
    "repo_owner": "rivenmedia",
    "repo_name": "riven-frontend",
    "release_version_enabled": false,
    "release_version": "v0.17.0",
    "branch_enabled": false,
    "branch": "release-please--branches--main",
    "suppress_logging": false,
    "log_level": "INFO",
    "host": "0.0.0.0",
    "port": 3000,
    "auto_update": false,
    "auto_update_interval": 24,
    "origin": "",
    "clear_on_update": true,
    "exclude_dirs": [],
    "platforms": [
        "pnpm"
    ],
    "command": [
        "node",
        "build"
    ],
    "config_dir": "/riven/frontend",
    "log_file": "/log/riven_frontend.log",
    "env": {}
},
```

!!! warning "Port conflicts and auto-shift"

    Riven defaults (`3000`/`8080`) overlap with NzbDAV defaults. DUMB can auto-shift
    conflicting ports at container startup or during the onboarding core-service
    start flow, updating `dumb_config.json` accordingly.
    Per-service stop/start/restart does not re-run port conflict resolution, so fix
    conflicts manually before restarting a single service.

### Configuration Key Descriptions

- **`enabled`**: Whether to start the Riven Frontend service.
- **`process_name`**: Used in logs and process tracking.
- **`repo_owner`** / **`repo_name`**: GitHub repo to pull from.
- **`release_version_enabled`** / **`release_version`**: Use a tagged GitHub release if enabled.
- **`branch_enabled`** / **`branch`**: Pull a specific GitHub branch if enabled.
- **`suppress_logging`**: If `true`, disables log output for this service.
- **`log_level`**: Logging verbosity level (e.g., `DEBUG`, `INFO`).
- **`host`**: IP address the frontend should bind to.
- **`port`**: Port the frontend is served on.
- **`auto_update`**: Enables automatic self-updates.
- **`auto_update_interval`**: How often (in hours) to check for updates.
- **`origin`**: CORS origin for the service. 
- **`clear_on_update`**: Clears build artifacts or cache during updates.
- **`exclude_dirs`**: Prevents specific directories from being affected by updates when using `clear_on_update`
- **`platforms`**: Expected runtime environment (e.g., `pnpm`).
- **`command`**: Command used to build or start the frontend service.
- **`config_dir`**: Directory where the frontend files are stored.
- **`log_file`**: Path to the Riven frontend log file.
- **`env`**: Dictionary of environment variables passed to the process (e.g., `PORT`, `ORIGIN`, `HOST`).

---

## ORIGIN Variable
The `ORIGIN` key must match the public-facing URL used to access the frontend. It ensures correct behavior for authentication, saving settings, and API communication.

---

## Branch / Version Targeting
You can control which version or branch of the frontend is deployed by setting:

- `branch_enabled: true` and specifying a `branch`
- or `release_version_enabled: true` and specifying a `release_version`

---

## Access
- Navigate to: `http://<host>:<port>` 
    - default port `3000`

!!! note " If using a reverse proxy, ensure the `ORIGIN` environment variable matches the external URL."

---

## Tips
- The frontend depends on the backend being reachable at `http://<host>:<port>` defined in the `dumb_config.json` for the [Riven Backend](../core/riven-backend.md)
- Use Docker port mappings if needed to expose the frontend
- Check `PORT` and `ORIGIN` values if the UI fails to load

---

## Resources
- [Riven Frontend GitHub](https://github.com/rivenmedia/riven-frontend)

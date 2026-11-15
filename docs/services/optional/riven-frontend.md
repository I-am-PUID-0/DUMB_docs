---
title: Riven Frontend
description: Enable Riven Frontend after its backend, open its web interface, configure the browser origin, and review source selection and connection issues.
icon: lucide/layout-dashboard
---

# Riven Frontend

Riven Frontend is an optional interface for Riven Backend. Use it to configure Riven and manage its content; the backend and its database must be running first.

DUMB handles automatic installation and updates of the frontend, including versioning and branch targeting. It is served by a lightweight web server and pre-configured to communicate with the backend at startup.

---

## First start

1. Select **Riven Backend** and **Riven Frontend** in DUMB onboarding. The backend's supporting services must be running before the frontend can manage it.
2. Open the Riven Frontend service card. On **DUMB Config**, choose **Start** if stopped, then select **Embedded UI**.
3. Open **Settings** in Riven Frontend. Configure your provider account, at least one **Content** source, at least one suitable **Scraper**, and the library paths. Review **Ranking** before adding a large list.
4. Review the **Media Server** connection and choose whether its updater should run. Saving server credentials alone does not enable that updater.
5. Add one intended request through your chosen source, follow it in Riven, then scan the media-server library and play the result. The [Riven Backend setup guide](../core/riven-backend.md#initial-setup-riven-backend) includes the complete workflow and diagrams.

!!! warning "Port conflicts and auto-shift"

    Riven defaults (`3000`/`8080`) overlap with InfiniDysk defaults. DUMB can auto-shift
    conflicting ports at container startup or during the onboarding core-service
    start flow, updating `dumb_config.json` accordingly.
    Per-service stop/start/restart does not re-run port conflict resolution, so fix
    conflicts manually before restarting a single service.

<details class="geek-details" markdown="1">
<summary>Technical details: configuration reference</summary>

## Configuration Settings in `dumb_config.json`

```json
{
"riven_frontend": {
    "enabled": false,
    "process_name": "Riven Frontend",
    "repo_owner": "rivenmedia",
    "repo_name": "riven-frontend",
    "release_version_enabled": false,
    "release_version": "v0.17.0",
    "commit_sha": "",
    "branch_enabled": false,
    "branch": "release-please--branches--main",
    "suppress_logging": false,
    "log_level": "INFO",
    "host": "0.0.0.0",
    "port": 3000,
    "auto_update": false,
    "auto_update_interval": 24,
    "auto_update_start_time": "04:00",
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
}
}
```

### Configuration Key Descriptions

- **`enabled`**: Whether to start the Riven Frontend service.
- **`process_name`**: Used in logs and process tracking.
- **`repo_owner`** / **`repo_name`**: GitHub repo to pull from.
- **`release_version_enabled`** / **`release_version`**: Use a tagged GitHub release if enabled.
- **`commit_sha`**: Builds an exact frontend revision from its full 40-character GitHub SHA.
- **`branch_enabled`** / **`branch`**: Pull a specific GitHub branch if enabled.
- **`suppress_logging`**: Suppresses service messages in the main DUMB output.
- **`log_level`**: Logging verbosity level (e.g., `DEBUG`, `INFO`).
- **`host`**: IP address the frontend should bind to.
- **`port`**: Port the frontend is served on.
- **`auto_update`**: Enables DUMB's scheduled update checks; `auto_update_mode` determines whether a detected update is installed.
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

</details>

## ORIGIN Variable
The `ORIGIN` key must match the public-facing URL used to access the frontend. It ensures correct behavior for authentication, saving settings, and API communication.

---

## Commit / Branch / Version Targeting

Choose a full `commit_sha`, a release selector, or an enabled branch in this service's DUMB settings. A commit pin takes precedence over the other selectors and disables automatic updates until you clear it. Review [source selection and update modes](../../features/auto-update.md) before changing a running service.

## Access

Open the service from DUMB's **Embedded UI** tab when available. The native URLs below require the corresponding Docker host port to be published; use the port saved in your running configuration.
- Navigate to: `http://<host>:<port>` 
    - default port `3000`

!!! note " If using a reverse proxy, ensure the `ORIGIN` environment variable matches the external URL."

---

## Tips
- The frontend depends on the backend being reachable at `http://<host>:<port>` defined in the `dumb_config.json` for the [Riven Backend](../core/riven-backend.md)
- Use Docker port mappings if needed to expose the frontend
- Check `PORT` and `ORIGIN` values if the UI fails to load
- DUMB verifies that the runnable frontend build exists before accepting an
  installation. If retained source contains `package.json` but the `build`
  output is missing, DUMB downloads and rebuilds the frontend automatically
  instead of launching an incomplete installation.

---

## Resources
- [Riven Frontend GitHub](https://github.com/rivenmedia/riven-frontend)

---
title: Pulsarr
icon: lucide/radio-tower
---

# Pulsarr

Pulsarr monitors Plex watchlists and routes requested movies and shows to Sonarr and Radarr. It is useful when Plex is the front door for requests and you want watchlist-driven automation, approvals, quotas, and notifications without running a separate request portal.

---

## Overview

Pulsarr provides:

- **Plex watchlist monitoring** - Syncs watched Plex account activity into media requests.
- **Sonarr/Radarr routing** - Sends shows and movies to configured Arr instances.
- **Approvals and quotas** - Supports controlled request workflows for users.
- **Notifications** - Supports Discord, Plex mobile push, webhooks, and Apprise.
- **Multi-user support** - Tracks Plex users and watchlist permissions.

---

## Default port

| Service | Port |
|---------|------|
| Pulsarr | 3003 |

---

## Configuration settings in `dumb_config.json`

```json
"pulsarr": {
  "enabled": false,
  "process_name": "Pulsarr",
  "repo_owner": "jamcalli",
  "repo_name": "Pulsarr",
  "release_version_enabled": false,
  "release_version": "latest",
  "branch_enabled": false,
  "branch": "master",
  "suppress_logging": false,
  "log_level": "INFO",
  "port": 3003,
  "auto_update": false,
  "auto_update_interval": 24,
  "auto_update_start_time": "04:00",
  "clear_on_update": true,
  "exclude_dirs": [
    "/pulsarr/data"
  ],
  "platforms": [
    "bun"
  ],
  "command": [
    "/config/.bun/bin/bun",
    "run",
    "--bun",
    "dist/server.js"
  ],
  "config_dir": "/pulsarr",
  "config_file": "/pulsarr/data/db/pulsarr.db",
  "log_file": "/pulsarr/data/logs/pulsarr.log",
  "env": {
    "NODE_ENV": "production",
    "listenPort": "{port}",
    "dbPath": "/pulsarr/data/db/pulsarr.db",
    "allowIframes": "true"
  }
}
```

### Configuration key descriptions

- **`enabled`**: Whether to start Pulsarr.
- **`repo_owner`** / **`repo_name`**: GitHub repository DUMB downloads from.
- **`release_version_enabled`** / **`release_version`**: Use a tagged release if enabled, or the latest release by default.
- **`branch_enabled`** / **`branch`**: Use a source branch instead of a release.
- **`port`**: Pulsarr web UI port.
- **`platforms`**: Uses DUMB's Bun setup path.
- **`config_dir`**: Pulsarr source and runtime directory.
- **`exclude_dirs`**: Keeps the persistent `/pulsarr/data` directory during updates.
- **`env.listenPort`**: Internal Pulsarr bind port.
- **`env.dbPath`**: SQLite database path.
- **`env.allowIframes`**: Allows Pulsarr to be embedded in the DUMB frontend.

---

## Initial setup

After enabling and starting Pulsarr:

1. Open Pulsarr from the DUMB service page or at `http://<host>:3003`.
2. Create the Pulsarr admin account.
3. Add your Plex token.
4. Configure Sonarr and Radarr connections with their DUMB internal URLs and API keys.
5. Start the main workflow from Pulsarr's dashboard and enable auto-start if desired.

---

## Notes

- Pulsarr uses SQLite by default at `/pulsarr/data/db/pulsarr.db`.
- DUMB installs Bun under `/config/.bun` when Pulsarr is built from source.
- If you intentionally serve Pulsarr behind a separate subfolder reverse proxy, set Pulsarr's own `basePath` environment variable for that external proxy. DUMB's embedded UI route strips its service prefix and does not need `basePath`.

---

## Related links

- [Pulsarr repository](https://github.com/jamcalli/Pulsarr)
- [Pulsarr documentation](https://jamcalli.github.io/Pulsarr/)
- [Pulsarr environment variables](https://jamcalli.github.io/Pulsarr/docs/development/environment-variables)

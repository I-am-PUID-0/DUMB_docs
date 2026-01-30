---
title: Seerr
icon: lucide/clapperboard
---

# Seerr

Seerr (Overseerr/Jellyseerr) is a media request and discovery platform that integrates with Plex, Jellyfin, Radarr, and Sonarr. It allows users to browse, request, and track media content through an intuitive web interface.

---

## Overview

Seerr provides:

- **Media discovery** - Browse trending, popular, and upcoming content
- **Request management** - Users can request movies and TV shows
- **Integration with Arr services** - Automatically sends requests to Radarr/Sonarr
- **User management** - Multiple users with different permission levels
- **Notifications** - Alerts when requests are fulfilled

---

## Default port

| Service | Port |
|---------|------|
| Seerr | 5055 |

---

## Configuration settings in `dumb_config.json`

### Seerr instance configuration

```json
"seerr": {
  "instances": {
    "Default": {
      "enabled": false,
      "sync_role": "disabled",
      "core_service": "",
      "process_name": "Seerr",
      "repo_owner": "seerr-team",
      "repo_name": "seerr",
      "release_version_enabled": false,
      "release_version": "latest",
      "branch_enabled": false,
      "branch": "main",
      "suppress_logging": false,
      "log_level": "INFO",
      "port": 5055,
      "auto_update": false,
      "auto_update_interval": 24,
      "clear_on_update": true,
      "exclude_dirs": [
        "/seerr/default/config"
      ],
      "platforms": [
        "pnpm"
      ],
      "command": ["node", "dist/index.js"],
      "config_dir": "/seerr/default",
      "config_file": "/seerr/default/config/settings.json",
      "log_file": "/seerr/default/config/logs/jellyseerr.log",
      "env": {
        "NODE_ENV": "production",
        "PORT": "{port}"
      }
    }
  }
}
```

#### Seerr instance keys

- **`enabled`**: Whether to start this Seerr instance.
- **`sync_role`**: `disabled`, `primary`, or `subordinate`.
- **`process_name`**: Display name used in logs and the frontend.
- **`repo_owner`** / **`repo_name`**: GitHub repository to pull from.
- **`release_version_enabled`** / **`release_version`**: Use a tagged release if enabled.
- **`branch_enabled`** / **`branch`**: Use a specific branch if enabled.
- **`suppress_logging`**: If `true`, disables log output for this service.
- **`log_level`**: Logging verbosity (e.g., `debug`, `info`, `warn`).
- **`port`**: Port the Seerr web UI is exposed on.
- **`auto_update`**: Enables automatic self-updates from GitHub.
- **`auto_update_interval`**: How often (in hours) to check for updates.
- **`clear_on_update`**: Clears build artifacts or cache during updates.
- **`exclude_dirs`**: Prevents specific directories from being affected by updates.
- **`platforms`**: Required runtime (typically `pnpm`).
- **`command`**: The command used to launch Seerr.
- **`config_dir`** / **`config_file`**: Where configuration files are stored.
- **`log_file`**: Path to the Seerr log file.
- **`env`**: Environment variables passed at runtime.

---

## Seerr Sync

Seerr Sync replicates requests from one **primary** Seerr instance to one or more **subordinates**. It is one‑way and is designed for multi‑Seerr setups where the primary is the source of truth.

For a full overview and use‑case narrative, see [Seerr Sync](../../features/seerr-sync.md).

### High-level overview

Seerr Sync keeps multiple Seerr instances aligned by periodically polling the primary and applying changes to subordinates.

How it works:

- **Polling** - Periodically polls the primary for all requests (default 60s).
- **Fingerprinting** - Each request is identified by `{mediaType}:{tmdbId}:{is4k}`.
- **Sync actions** - New requests are created on subordinates, status changes propagate, and deletions are optionally mirrored.
- **State persistence** - Tracks synced requests in `/config/seerr_sync_state.json` so it survives restarts.
- **Failure handling** - Failed sync attempts are tracked separately and retried after a configurable delay.

Use case example:

Multiple Seerr instances (for example, one per household) can share the same request library. Users submit requests on the primary and they appear on all subordinates, each tied to its own Arr stack.

### Top-level `seerr_sync` settings

```json
"seerr_sync": {
  "enabled": false,
  "poll_interval_seconds": 60,
  "external_primary": {
    "enabled": false,
    "url": "",
    "api_key": ""
  },
  "external_subordinates": [
    { "url": "", "api_key": "" }
  ],
  "options": {
    "sync_pending": true,
    "sync_approved": true,
    "sync_declined": false,
    "sync_deletes": true,
    "sync_4k_separately": true,
    "user_mapping": "admin"
  }
}
```

#### Seerr Sync keys

- **`seerr_sync.enabled`**: Master toggle for Seerr Sync.
- **`seerr_sync.poll_interval_seconds`**: Poll interval in seconds (minimum 10).
- **`seerr_sync.external_primary.enabled`**: Use an external Seerr as primary.
- **`seerr_sync.external_primary.url`**: External primary base URL.
- **`seerr_sync.external_primary.api_key`**: API key for external primary.
- **`seerr_sync.external_subordinates`**: List of external subordinate URLs + API keys.
- **`seerr_sync.options.sync_pending`**: Sync pending requests.
- **`seerr_sync.options.sync_approved`**: Sync approved requests.
- **`seerr_sync.options.sync_declined`**: Sync declined requests.
- **`seerr_sync.options.sync_deletes`**: Delete subordinates when deleted on primary.
- **`seerr_sync.options.sync_4k_separately`**: Treat 4K as separate requests.
- **`seerr_sync.options.user_mapping`**: Owner mapping (`admin` or `email_match`).

Key fields:

- **`enabled`**: Master toggle for Seerr Sync.
- **`poll_interval_seconds`**: Minimum 10 seconds. How often to poll the primary.
- **`external_primary`**: Use an external Seerr as primary (URL + API key required).
- **`external_subordinates`**: External subordinate list (URL + API key required for each).
- **`options`**: Toggles for request types and ownership mapping.

### Per-instance `sync_role`

Each Seerr instance has a sync role:

```json
"seerr": {
  "instances": {
    "Default": {
      "enabled": true,
      "sync_role": "disabled"
    }
  }
}
```

Values:

- **`disabled`**: Not part of sync.
- **`primary`**: Source of truth.
- **`subordinate`**: Receives replicated requests.

!!! warning "Validation rules"

    - Only one internal primary is allowed.
    - If an external primary is enabled, no internal instance can be primary.
    - A primary must exist (internal or external).
    - At least one subordinate must exist (internal or external).
    - External entries require both URL and API key.

### Frontend integration

The Seerr service page includes a **Seerr Sync** panel with:

- Enable toggle and polling interval
- External primary + subordinates editor (API keys are hidden by default)
- Test buttons to validate external primary and subordinate connectivity
- Sync options toggles and user mapping
- Per-instance sync role selector
- Status + failed request reporting (with clear actions and scrollable list)

---

## Initial setup

After enabling Seerr and starting the service:

1. Access the Seerr UI at `http://<host>:5055`
2. Complete the setup wizard:
   - Sign in with your Plex account (or configure Jellyfin)
   - Connect to your Plex/Jellyfin server
   - Configure Radarr and Sonarr connections
   - Set up user permissions

---

## Connecting to media servers

### Plex configuration

Seerr can sync with your Plex server to:

- Show what content you already have
- Display watch status
- Allow Plex user authentication

### Jellyfin configuration

For Jellyfin users, Seerr (Jellyseerr variant) provides similar functionality:

- Library synchronization
- User authentication via Jellyfin

---

## Connecting to Arr services

Configure Radarr and Sonarr in Seerr settings:

| Setting | Description |
|---------|-------------|
| **Hostname** | `127.0.0.1` (internal to DUMB container) |
| **Port** | Radarr: `7878`, Sonarr: `8989` |
| **API Key** | Found in Arr service Settings :material-arrow-right: General |
| **Quality Profile** | Select default quality for requests |
| **Root Folder** | Default download location |

!!! tip "Multiple Arr instances"

    If you have multiple Radarr or Sonarr instances (e.g., for 4K content), you can add them all to Seerr and let users choose during requests.

---

## User management

Seerr supports multiple user types:

| User Type | Capabilities |
|-----------|--------------|
| **Admin** | Full access, manage settings and users |
| **User** | Request content, view request status |
| **Guest** | Browse only (configurable) |

Users can authenticate via:

- Plex account
- Jellyfin account
- Local Seerr account

---

## Request workflow

```mermaid
%%{ init: { "flowchart": { "curve": "basis" } } }%%
flowchart TD
    A([User browses content])
    B([User requests movie/show])
    C[Request approved]
    D[Sent to Radarr/Sonarr]
    E[Downloaded by Arr service]
    F([User notified])

    A ==> B
    B ==> C
    C ==> D
    D ==> E
    E ==> F
```

Requests can be configured for:

- **Auto-approval** - Requests are automatically sent to Arr services
- **Manual approval** - Admin must approve before processing
- **Request limits** - Limit requests per user per time period

---

## Accessing via DUMB frontend

When embedded service UIs are enabled, Seerr appears in the DUMB frontend with:

- An embedded UI tab on the Seerr service page
- A direct link that opens the proxied UI in a new browser tab

This provides a unified interface without exposing Seerr's port directly.

---

## Tips

- Configure request limits to prevent abuse in multi-user setups.
- Enable notifications (Discord, email, etc.) to alert users when content is available.
- Use quality profiles in your Arr services to control download quality.
- Seerr respects availability settings in Radarr/Sonarr for proper release monitoring.
- Logs can be viewed via DUMB's Frontend or at `/seerr/default/config/logs/jellyseerr.log`.

---

## Resources

- [Seerr GitHub Repository](https://github.com/seerr-team/seerr)
- [Seerr Documentation](https://docs.seerr.dev/)

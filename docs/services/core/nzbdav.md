---
title: NzbDAV
icon: lucide/cloud
---

# NzbDAV (Core Service)

**NzbDAV** is a combined backend + frontend WebDAV service for **Usenet** workflows. In DUMB it runs as a single service that exposes a Web UI, a WebDAV endpoint for browsing/serving content, and a backend API used for automation.

---

## Workflow diagram

```mermaid
%%{ init: { "flowchart": { "curve": "basis" } } }%%
flowchart TD
    A([Request Sources:<br/>Seerr, Trakt,<br/>Plex Watchlist,<br/>NeutArr])
    B[Arr Services:<br/>Sonarr, Radarr,<br/>Lidarr,<br/>Whisparr]
    C[[Prowlarr / Indexers]]
    D[NzbDAV]
    E@{shape: cloud, label: "Usenet Providers"}
    F[[Rclone]]
    G[(WebDAV Mount Root:<br/>/mnt/debrid/<br/>nzbdav)]
    H[(QBit Download Symlinks:<br/>/mnt/debrid/nzbdav/<br/>completed-symlinks)]
    I[Arr Rename + Link Step:<br/>Hard Link / Symlink]
    J[(Final Symlink Root:<br/>/mnt/debrid/<br/>nzbdav-symlinks)]
    K([Media Servers:<br/>Plex, Jellyfin,<br/>Emby])

    E === D
    D === F
    linkStyle 0 stroke:transparent,stroke-width:0;
    linkStyle 1 stroke:transparent,stroke-width:0;

    A ==> B
    C <==> B
    B <==> D
    D e1@==> E
    F e2@==> D
    F e3@==> G
    D ==> H
    H ==> G
    H ==> B
    B ==> I
    I ==> J
    J e4@==> G
    K e5@<==> J


    classDef animate stroke-dasharray: 9,5,stroke-dashoffset: 900,animation: dash 25s linear infinite;
    class e1,e2,e3,e4,e5 animate
```

---

## Service Relationships

| Classification | Role                                                     |
| -------------- | -------------------------------------------------------- |
| Core Service   | NZB WebDAV gateway                                       |
| Depends On     | [rclone](../dependent/rclone.md)                         |
| Optional       | Sonarr, Radarr, Lidarr, Whisparr, Prowlarr, NeutArr      |
| Exposes UI     | Yes (Web UI + WebDAV)                                    |

---

## What NzbDAV provides

| Endpoint | Purpose | Default |
|----------|---------|---------|
| Web UI + WebDAV | Primary UI and WebDAV endpoint | `http://<host>:3000/` |
| Backend API | Internal API for DUMB automation | `http://127.0.0.1:8080/` |

NzbDAV also exposes a **Usenet download client** path in Arr by emulating a Sabnzbd-compatible API. DUMB registers this client automatically when `core_service: nzbdav` (or `core_service` includes `nzbdav`) is set on Arr instances.

!!! info "WebDAV endpoint"

    rclone and Arr download clients point at the WebDAV endpoint on the frontend port.

---

## Configuration in `dumb_config.json`

!!! important "DUMB defaults to the NzbDAV fork"

    DUMB installs and updates NzbDAV from the maintained
    [`nzbdav/nzbdav`](https://github.com/nzbdav/nzbdav) **fork by default**.
    It does **not** default to the original
    [`nzbdav-dev/nzbdav`](https://github.com/nzbdav-dev/nzbdav) repository.
    The `repo_owner: "nzbdav"` and `repo_name: "nzbdav"` values below select
    that fork for release, branch, and update operations.

```json
"nzbdav": {
    "enabled": false,
    "process_name": "NzbDAV",
    "repo_owner": "nzbdav",
    "repo_name": "nzbdav",
    "release_version_enabled": false,
    "release_version": "latest",
    "commit_sha": "",
    "branch_enabled": false,
    "branch": "main",
    "suppress_logging": false,
    "log_level": "INFO",
    "frontend_port": 3000,
    "backend_port": 8080,
    "auto_update": false,
    "auto_update_interval": 24,
    "auto_update_start_time": "04:00",
    "symlink_backup_enabled": false,
    "symlink_backup_interval": 168,
    "symlink_backup_start_time": "04:00",
    "symlink_backup_path": "/config/symlink-repair/snapshots/nzbdav-{timestamp}.json",
    "symlink_backup_include_broken": true,
    "symlink_backup_retention_count": 1,
    "symlink_backup_roots": [
        "/mnt/debrid/nzbdav-symlinks"
    ],
    "clear_on_update": false,
    "exclude_dirs": [],
    "platforms": [
        "pnpm",
        "dotnet"
    ],
    "command": [],
    "config_dir": "/nzbdav",
    "log_file": "/log/nzbdav.log",
    "webdav_password": "",
    "env": {}
},
```

### Key Configuration Fields

* `enabled`: Toggle to run NzbDAV via DUMB.
* `frontend_port`: Port for the Web UI and WebDAV endpoint.
* `backend_port`: Port for the backend API.
* `commit_sha`: Optional full 40-character GitHub SHA. When set, DUMB builds
  that exact NzbDAV revision instead of selecting a release or branch.
* `webdav_password`: Default WebDAV password (overridden by `WEBDAV_PASSWORD`).
* `config_dir`: Path where NzbDAV data is stored.
* `log_file`: Path for the consolidated NzbDAV log.
* `env`: Optional environment variables (see below).

!!! warning "WebDAV credentials"

    If `webdav_password` is blank, DUMB generates one at startup and stores it in the config.
    Change the password before exposing NzbDAV outside your trusted network.

### Pinning an exact NzbDAV commit

Set `commit_sha` to the complete SHA from the configured `repo_owner` and
`repo_name`:

```json
"nzbdav": {
    "repo_owner": "nzbdav",
    "repo_name": "nzbdav",
    "commit_sha": "0123456789abcdef0123456789abcdef01234567"
}
```

The commit pin overrides `release_version_enabled` and `branch_enabled`.
Automatic updates stay disabled while the pin is present. Change the SHA to
move deliberately to another revision, or clear it to return to the configured
release/branch strategy.

After saving a new SHA, open **Updates** and select **Install configured
commit**. This installs and restarts NzbDAV on the saved commit. Do not use
**Override + latest** for this operation; that action intentionally installs the
latest moving release while leaving the saved pin in place for a later restart.

### Environment Variables

* `LOG_LEVEL`: Logging level for NzbDAV (defaults to `INFO`).
* `WEBDAV_USER`: Override the WebDAV username (defaults to `admin`).
* `WEBDAV_PASSWORD`: Override the WebDAV password.
* `CONFIG_PATH`: Override the NzbDAV config path (defaults to `config_dir`).
* `FRONTEND_BACKEND_API_KEY`: Backend API key shared with the frontend.
* `ASPNETCORE_URLS`: Backend bind address (defaults to `http://+:<backend_port>`).
* `PORT`: Frontend port (defaults to `frontend_port`).
* `BACKEND_URL`: Frontend-to-backend URL (defaults to `http://127.0.0.1:<backend_port>`).

!!! danger "Protect API keys"

    `FRONTEND_BACKEND_API_KEY` grants backend access. Treat it like a secret and avoid committing it to source control.

---

## Integration with DUMB

When NzbDAV starts, DUMB performs several automation steps:

- Syncs Arr instance details into the NzbDAV database
- Ensures API categories exist for Arr integrations
- Creates `/mnt/debrid/nzbdav-symlinks/<category>` roots
- Updates Arr permissions and root folders
- Adds or updates a download client named `nzbdav` in Arr

The Arr instance list is stored in NzbDAV’s SQLite config under `arr.instances`, so DUMB can merge user edits with auto-detected instances.

!!! info "Startup timing"

    If the NzbDAV backend is not reachable yet, DUMB retries the download-client setup shortly after startup.

### Database migration startup

DUMB starts the NzbDAV frontend before running the blocking database migration.
This is the default launch behavior and lets the Web UI show NzbDAV's live
**Database maintenance in progress** page, including migration steps, progress,
and elapsed time, even when a large database takes a long time to migrate.

After a successful migration, DUMB starts the normal backend and the page reloads
into NzbDAV when it becomes healthy. If migration fails, DUMB keeps the frontend
alive through NzbDAV's brief failure-display window, then stops it and exits the
NzbDAV process with the migration's non-zero exit code. No separate setting is
required.

### Arr `core_service` setting

For Sonarr/Radarr/Lidarr/Whisparr instances you want wired to NzbDAV, set
`core_service` to `nzbdav` or include it in a list:

```json
"core_service": "nzbdav"
```

```json
"core_service": ["decypharr", "nzbdav", "altmount"]
```

This tells DUMB to auto-configure Arr integration around NzbDAV’s WebDAV and download-client workflows.
See [Core Service Routing](../../reference/core-service.md) for how `core_service` affects automation.

### 1. rclone WebDAV Mount

Create a dedicated rclone instance for NzbDAV and point it at the WebDAV endpoint:

```json
"rclone": {
  "instances": {
    "NzbDAV": {
      "enabled": true,
      "core_service": "nzbdav",
      "process_name": "rclone w/ NzbDAV",
      "suppress_logging": false,
      "log_level": "INFO",
      "key_type": "NzbDAV",
      "zurg_enabled": false,
      "decypharr_enabled": false,
      "mount_dir": "/mnt/debrid",
      "mount_name": "nzbdav",
      "config_dir": "/config",
      "config_file": "/config/rclone.config",
      "log_file": "/log/rclone_w_nzbdav.log",
      "zurg_config_file": "",
      "cache_dir": "/cache",
      "command": [],
      "api_key": ""
    }
  }
}
```

When `key_type` is set to `NzbDAV`, DUMB configures rclone to use:

* `http://127.0.0.1:<frontend_port>/` as the WebDAV URL
* `WEBDAV_USER` / `WEBDAV_PASSWORD` (or the values stored in the NzbDAV DB)
* an rclone RC listener on the first available port starting at `5572`

DUMB reserves RC ports already assigned to other managed rclone instances and
AltMount, and also checks active listeners before selecting the port. On first
setup, DUMB enables **Settings -> Rclone Server** in NzbDAV and points it at the
local RC listener so WebDAV changes can invalidate rclone's VFS directory cache.
Later NzbDAV UI changes to the RC enablement, host, username, or password are
preserved. A saved `--rc-addr` and `--dir-cache-time` in the rclone command are
also retained when they remain valid.

Default rclone mount path (if not overridden) is:

```
/mnt/debrid/nzbdav
```

### 2. Arr Integration (Sonarr/Radarr)

Set `core_service` to `nzbdav` (or include `nzbdav` in a list) for the Sonarr and
Radarr instances you want wired to NzbDAV:

```json
"sonarr": {
  "instances": {
    "Default": {
      "enabled": true,
      "core_service": "nzbdav",
      "port": 8989
    }
  }
},
"radarr": {
  "instances": {
    "Default": {
      "enabled": true,
      "core_service": "nzbdav",
      "port": 7878
    }
  }
}
```

DUMB will:

* Create symlink roots at `/mnt/debrid/nzbdav-symlinks/<category>`
* Configure NzbDAV to recognize these paths
* Update Arr permissions (enable chmod + set folder/file modes)
* Attempt to add an `nzbdav` download client in the Arrs using their API keys

When `core_service` includes both `decypharr` and `nzbdav`, the root folder base
shifts to `/mnt/debrid/combined_symlinks/<category>`. Other multi-service
combinations keep the NzbDAV symlink root unless another workflow owns its own
root-folder setup.

!!! info "Automatic vs manual wiring"

    When `core_service` is set to `nzbdav` (or includes it), DUMB
    automatically configures download clients, root folders, and permissions.
    If `core_service` includes both `decypharr` and `nzbdav`, the Arr root folder
    base switches to `/mnt/debrid/combined_symlinks/<category>`.
    Manual setup is only needed when `core_service` is blank or you want to override
    the combined workflow wiring.

### Category mapping

By default, DUMB maps Arr types to categories:

| Arr service | Default category |
|-------------|------------------|
| Radarr | `movies` |
| Sonarr | `tv` |
| Lidarr | `music` |
| Whisparr | `whisparr` |

Instance names are slugified into categories if present (for example, `Radarr 4K` becomes `radarr-4k`).

---

## Accessing the UI

* Navigate to: `http://<host>:<frontend_port>` (default port `3000`)
* WebDAV endpoint: `http://<host>:<frontend_port>/`

!!! warning "Port conflicts and auto-shift"

    NzbDAV defaults (`3000`/`8080`) overlap with Riven defaults. DUMB can auto-shift
    conflicting ports at container startup or during the onboarding core-service
    start flow, updating `dumb_config.json` accordingly.
    Per-service stop/start/restart does not re-run port conflict resolution, so fix
    conflicts manually before restarting a single service.

---

## Troubleshooting Tips

### Compare NzbDAV performance

Open the NzbDAV service page's **AI Assist** tab and choose **Performance** to compare a selected window with the previous matching period or with the period before the latest DUMB-saved setting change.

In addition to generic logs and process metrics, DUMB can read the maintained fork's `metrics.sqlite` and `db.sqlite` in read-only mode. The evidence includes queue worker settings, segment success/missing/error/retry rates, provider latency, read-session activity, queue completion/failure timing, long-running queue processors, and busy-period throughput.

Use **Preview bundle** first to confirm native telemetry is available and check the exact coverage. These metrics do not measure Plex click-to-first-frame latency, so playback-start conclusions should remain qualified unless Plex-side timing is correlated separately.

See [AI Assistant](../../features/ai-assistant.md#nzbdav-native-evidence) for the full evidence and safety model.

### Assess SQLite pressure

NzbDAV currently stores its operational and metrics data in SQLite. DUMB can optionally monitor both databases from **Metrics → Settings → Database Health Monitoring** or the NzbDAV service page's **Database Health** panel.

Start with **Standard / passive** mode and collect through normal imports, health checks, and playback. Use **Enhanced / read-only probes** when you also want bounded SQLite metadata latency. Repeated lock/busy/timeout errors, sustained WAL growth, slow probes, or network-filesystem placement are stronger reasons to investigate PostgreSQL than database size alone. See [Metrics Collection](../../features/metrics.md#database-health-monitoring) for the safety boundary and interpretation guidance.

!!! warning "Permission changes"

    DUMB updates Arr media-management permissions to enable chmod operations (folder `777`, file `666`).
    If you manage permissions manually, review these settings after integration.

* If rclone fails to authenticate, verify `WEBDAV_USER`/`WEBDAV_PASSWORD` and restart the container.
* If Arr download clients are not created, confirm each Arr instance is enabled and has a readable `config.xml` for API key discovery.
* If Arr root folders are missing, verify `core_service` includes `nzbdav` and the Arr API is reachable.
* Runtime NzbDAV builds use an on-demand managed .NET SDK. DUMB merges the
  NzbDAV-specific build variables with the container environment so system tools
  remain available, and invokes `/bin/bash` explicitly when installing the SDK.
  An error such as `No such file or directory: 'bash'` indicates an image that
  predates this fix and should be retested after pulling a fixed tag and
  recreating the container.
* Check `/log` for NzbDAV startup errors, and ensure `frontend_port`/`backend_port` are not already in use.

---

## Resources

* [NzbDAV fork used by DUMB (default)](https://github.com/nzbdav/nzbdav)
* [Original NzbDAV repository (not the DUMB default)](https://github.com/nzbdav-dev/nzbdav)
* [Upstream migration progress integration issue](https://github.com/nzbdav/nzbdav/issues/268)

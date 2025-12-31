---
title: Decypharr
---

# Decypharr (Core Service)

**Decypharr** is a self-hosted, Go-based torrent manager and content orchestrator that integrates multiple Debrid services and acts as a mock Qbittorrent client for Arr applications like Sonarr and Radarr. It is a core component in DUMB for automating torrent-based downloads with native Debrid support and seamless library linking.

---

## Service Relationships

| Classification | Role                                                           |
| -------------- | -------------------------------------------------------------- |
| Core Service   | Debrid Torrent Orchestrator                                    |
| Depends On     | [rclone](../dependent/rclone.md)                               |
| Optional       | None                                                           |
| Exposes UI     | Yes (Web UI)                                                   |


---

## Configuration in `dumb_config.json`

```json
"decypharr": {
    "enabled": false,
    "process_name": "Decypharr",
    "repo_owner": "sirrobot01",
    "repo_name": "decypharr",
    "release_version_enabled": false,
    "release_version": "v1.0.0",
    "branch_enabled": false,
    "branch": "main",
    "suppress_logging": false,
    "log_level": "INFO",
    "port": 8282,
    "auto_update": false,
    "auto_update_interval": 24,
    "clear_on_update": false,
    "exclude_dirs": [],
    "command": [
        "/decypharr/decypharr",
        "--config",
        "/decypharr"
    ],
    "config_dir": "/decypharr",
    "config_file": "/decypharr/config.json",
    "log_file": "/decypharr/logs/decypharr.log",
    "env": {},
    "use_embedded_rclone": true,
    "api_keys": {}
},
```

### Key Configuration Fields

* `enabled`: Toggle to run Decypharr via DUMB.
* `process_name`: Used for display and logs.
* `repo_owner`, `repo_name`: GitHub repo to use for updates.
* `release_version_enabled`, `branch_enabled`: Target a specific tag or branch.
* `log_level`, `suppress_logging`: Logging controls.
* `port`: Web UI port.
* `env`: Environment variables passed to Decypharr.
* `use_embedded_rclone`: Enable the embedded rclone integration (recommended).
* `api_keys`: Per-provider API keys used by Decypharr.
* `clear_on_update`, `exclude_dirs`: Clean old files during update while protecting data dirs.

---

## What Decypharr does


### How It Works

Decypharr acts as both a torrent manager and a renaming/organizing engine:

* Handles torrent links via Debrid services
* Mimics Qbittorrent API for seamless \*Arr integration
* Renames and organizes files into structured symlink folders
* Provides a Web UI and WebDAV endpoints for remote management
* Ensures all changes propagate cleanly between containers using `rshared`/`rslave`

### Supported Features

*  Mock Qbittorrent API for Sonarr, Radarr, Lidarr, etc.
*  Full-featured UI for managing torrents
*  Proxy filtering for un-cached Debrid torrents
*  Multiple Debrid service support (Real Debrid, Torbox, Debrid Link, All Debrid)
*  WebDAV server per Debrid provider for mounting remote files
*  Repair Worker for missing files or symlinks

---

## Integration with DUMB

### Arr `core_service` Setting

For Sonarr/Radarr/Lidarr/Whisparr instances you want wired to Decypharr, set:

```json
"core_service": "decypharr"
```

This tells DUMB to auto-configure Arr integration around Decypharr’s WebDAV and symlink workflows.

To successfully run Decypharr with DUMB, the following configuration and mounting steps must be completed:

### 1. Bind Mount Setup

If you are passing the rclone mount to an **external** Arr or media server container, include the following bind mounts in both your `DUMB` and `arrs` docker-compose files (replace `...` with the full host path to your DUMB bind mount):

**DUMB Compose**:

```yaml
volumes:
  - .../DUMB/mnt/debrid:/mnt/debrid:rshared
```

**Arrs Compose (Sonarr/Radarr)**:

```yaml
volumes:
  - .../DUMB/mnt/debrid:/mnt/debrid:rslave
```

> These mounts are only required when Arrs or media servers run **outside** the DUMB container and need access to the rclone mount and Decypharr symlinks.

### 2. Configure Root Folders in Arrs

Inside the Sonarr and Radarr web UI:

* Navigate to **Settings > Media Management > Root Folders**
* Add the following paths:

  * **Radarr**: `/mnt/debrid/decypharr_symlinks/movies`
  * **Sonarr**: `/mnt/debrid/decypharr_symlinks/shows`

> These directories are managed by Decypharr and must be used for proper operation.

### 3. Connect Decypharr to Arrs

Follow the [official usage guide](https://sirrobot01.github.io/decypharr/usage/#connecting-to-sonarrradarr) for step-by-step instructions on connecting your Radarr and Sonarr instances to Decypharr.

> This includes setting the correct API keys and ensuring URL paths match the container environments.

### 4. Plex Library Setup

In Plex, add the Decypharr symlink folders as library sources:

* **Movies Library**: `/mnt/debrid/decypharr_symlinks/movies`
* **TV Shows Library**: `/mnt/debrid/decypharr_symlinks/shows`

> This ensures Plex indexes files processed and renamed by Decypharr, enabling clean and consistent playback.


---

## Troubleshooting Tips

* Ensure the bind mounts are correct and both containers see the same `/mnt/debrid` structure
* Make sure Decypharr has permission to write to and create symlinks in the target directory
* If media doesn't appear in Plex, check that the symlink folders are scanned and indexed
* Use `docker inspect` to verify correct mount propagation between DUMB and Arrs

---

## Supported Debrid Providers

* [Real Debrid](https://real-debrid.com)
* [Torbox](https://www.torbox.net)
* [Debrid Link](https://debrid-link.fr)
* [All Debrid](https://alldebrid.com)

---

## Resources

* [Decypharr GitHub](https://github.com/sirrobot01/decypharr)
* [Decypharr Docs](https://sirrobot01.github.io/decypharr/)

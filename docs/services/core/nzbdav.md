---
title: NzbDAV
---

# NzbDAV (Core Service)

**NzbDAV** is a combined backend + frontend WebDAV service for NZB access. In DUMB it runs as a single service that exposes a Web UI and a WebDAV endpoint for browsing and serving content.

---

## 🔗 Service Relationships

| Classification | Role                                  |
| -------------- | ------------------------------------- |
| Core Service   | NZB WebDAV gateway                    |
| Depends On     | [rclone](../dependent/rclone.md)      |
| Optional       | Sonarr, Radarr                        |
| Exposes UI     | Yes (Web UI + WebDAV)                 |

---

## 📦 Configuration in `dumb_config.json`

```json
"nzbdav": {
    "enabled": false,
    "process_name": "NzbDAV",
    "repo_owner": "nzbdav-dev",
    "repo_name": "nzbdav",
    "release_version_enabled": false,
    "release_version": "latest",
    "branch_enabled": false,
    "branch": "main",
    "suppress_logging": false,
    "log_level": "INFO",
    "frontend_port": 3000,
    "backend_port": 8080,
    "auto_update": false,
    "auto_update_interval": 24,
    "clear_on_update": false,
    "exclude_dirs": [],
    "platforms": [
        "pnpm",
        "dotnet"
    ],
    "command": [],
    "config_dir": "/nzbdav",
    "webdav_password": "1P@55w0rd",
    "env": {}
},
```

### 🔍 Key Configuration Fields

* `enabled`: Toggle to run NzbDAV via DUMB.
* `frontend_port`: Port for the Web UI and WebDAV endpoint.
* `backend_port`: Port for the backend API.
* `webdav_password`: Default WebDAV password (overridden by `WEBDAV_PASSWORD`).
* `config_dir`: Path where NzbDAV data is stored.
* `env`: Optional environment variables (see below).

### 🔧 Environment Variables

* `WEBDAV_USER`: Override the WebDAV username (defaults to `admin`).
* `WEBDAV_PASSWORD`: Override the WebDAV password.
* `CONFIG_PATH`: Override the NzbDAV config path (defaults to `config_dir`).
* `FRONTEND_BACKEND_API_KEY`: Backend API key shared with the frontend.

---

## ⚙️ Integration with DUMB

### 🧭 Arr `core_service` Setting

For Sonarr/Radarr/Lidarr/Whisparr instances you want wired to NzbDAV, set:

```json
"core_service": "nzbdav"
```

This tells DUMB to auto-configure Arr integration around NzbDAV’s WebDAV and download-client workflows.

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

### 2. Arr Integration (Sonarr/Radarr)

Set `core_service` to `nzbdav` for the Sonarr and Radarr instances you want wired to NzbDAV:

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

* Create symlink roots at `/mnt/debrid/nzbdav-symlinks/movies` and `/mnt/debrid/nzbdav-symlinks/shows`
* Configure NzbDAV to recognize these paths
* Attempt to add an `nzbdav` download client in the Arrs using their API keys

---

## 🌐 Accessing the UI

* Navigate to: `http://<host>:<frontend_port>` (default port `3000`)

---

## 🛠️ Troubleshooting Tips

* If rclone fails to authenticate, verify `WEBDAV_USER`/`WEBDAV_PASSWORD` and restart the container.
* If Arr download clients are not created, confirm each Arr instance is enabled and has a readable `config.xml` for API key discovery.
* Check `/log` for NzbDAV startup errors, and ensure `frontend_port`/`backend_port` are not already in use.

---

## 🔗 Resources

* [NzbDAV GitHub](https://github.com/nzbdav-dev/nzbdav)

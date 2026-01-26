---
title: Emby
icon: lucide/disc
---

# Emby (Core Service)

**Emby** is a media server for organizing and streaming your media library. It is a commercial alternative to Plex and Jellyfin.

---

## Service Relationships

| Classification | Role                               |
| -------------- | ---------------------------------- |
| Core Service   | Media server                       |
| Depends On     | Content in `/mnt/debrid`           |
| Optional       | None                               |
| Exposes UI     | Yes (Web UI)                       |

---

## What Emby provides

| Endpoint | Purpose | Default |
|----------|---------|---------|
| Web UI | Emby browser UI | `http://<host>:8096/` |

!!! info "Traefik access"

    If Traefik is enabled, the Emby UI is proxied at `http://<host>/emby/` (path prefix `/web`).

---

## Configuration in `dumb_config.json`

```json
"emby": {
  "enabled": false,
  "process_name": "Emby Media Server",
  "repo_owner": "MediaBrowser",
  "repo_name": "Emby.Releases",
  "release_version_enabled": false,
  "release_version": "4.8.11.0",
  "use_system_ffmpeg": true,
  "suppress_logging": false,
  "log_level": "INFO",
  "port": 8096,
  "auto_update": false,
  "auto_update_interval": 24,
  "config_dir": "/emby",
  "config_file": "/emby/config/system.xml",
  "log_file": "/emby/log/embyserver.txt",
  "command": [],
  "env": {}
}
```

### Key Configuration Fields

* `port`: Web UI port (default `8096`).
* `use_system_ffmpeg`: Use the system ffmpeg binary when available.
* `release_version_enabled`, `release_version`: Pin to a specific Emby release.
* `auto_update`: Enable scheduled update checks (disabled when pinning releases).
* `config_dir`, `config_file`, `log_file`: Paths for config and logs.

!!! warning "Release pinning"

    When `release_version_enabled` is set, DUMB treats the release as pinned and disables scheduled auto-updates for Emby.

---

## Accessing the UI

* Navigate to: `http://<host>:8096`
* Traefik proxy: `http://<host>/emby/`

---

## Logs and data paths

- Config: `/emby/config/system.xml`
- Logs: `/emby/log/embyserver.txt`

---

## Terms of Service

By enabling Emby, you confirm that you have read and agree to the Emby Terms of Service:
* [Emby Terms of Service](https://emby.media/terms.html)

---

## Resources

* [Emby Website](https://emby.media/)
* [Emby Releases](https://github.com/MediaBrowser/Emby.Releases)

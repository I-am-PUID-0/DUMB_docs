---
title: Jellyfin
---

# Jellyfin (Core Service)

**Jellyfin** is an open-source media server for organizing and streaming your media library. It can be used as an alternative to Plex or Emby.

---

## Service Relationships

| Classification | Role                               |
| -------------- | ---------------------------------- |
| Core Service   | Media server                       |
| Depends On     | Content in `/mnt/debrid`           |
| Optional       | None                               |
| Exposes UI     | Yes (Web UI)                       |

---

## Configuration in `dumb_config.json`

```json
"jellyfin": {
  "enabled": false,
  "process_name": "Jellyfin Media Server",
  "suppress_logging": false,
  "auto_update": false,
  "auto_update_interval": 24,
  "pinned_version": "",
  "config_dir": "/jellyfin",
  "config_file": "/jellyfin/config/system.xml",
  "log_file": "/jellyfin/log/jellyfin.log",
  "command": [],
  "env": {}
}
```

### Key Configuration Fields

* `pinned_version`: Optional version pin for Jellyfin updates.
* `config_dir`, `config_file`, `log_file`: Paths for config and logs.
* `command`: Override the default startup command if needed.

---

## Accessing the UI

* Navigate to: `http://<host>:8096` (default Jellyfin port)

---

## Resources

* [Jellyfin Website](https://jellyfin.org/)
* [Jellyfin GitHub](https://github.com/jellyfin/jellyfin)

---
title: Lidarr
icon: lucide/music
---

# Lidarr (Core Service)

**Lidarr** is a music manager that automates searching, grabbing, and organizing albums through indexers and download clients.

---

## Service Relationships

| Classification | Role                               |
| -------------- | ---------------------------------- |
| Core Service   | Music automation                   |
| Depends On     | None                               |
| Optional       | Decypharr, NzbDAV, Prowlarr         |
| Exposes UI     | Yes (Web UI)                       |

---

## Configuration in `dumb_config.json`

```json
"lidarr": {
  "instances": {
    "Default": {
      "enabled": false,
      "core_service": "",
      "process_name": "Lidarr",
      "suppress_logging": false,
      "auto_update": false,
      "auto_update_interval": 24,
      "pinned_version": "",
      "port": 8686,
      "config_dir": "/lidarr/default",
      "config_file": "/lidarr/default/config.xml",
      "log_file": "/lidarr/default/logs/lidarr.txt",
      "command": [],
      "env": {}
    }
  }
}
```

### Key Configuration Fields

* `core_service`: Set to `decypharr` or `nzbdav` to enable DUMB integration with those services.
* `port`: Web UI port (default `8686`).
* `pinned_version`: Optional version pin for Lidarr updates.
* `config_dir`, `config_file`, `log_file`: Paths for config and logs.

---

## Integration with DUMB

* For Decypharr integration, set `core_service` to `decypharr` and follow the [Decypharr guide](decypharr.md).
* For NzbDAV integration, set `core_service` to `nzbdav` and follow the [NzbDAV guide](nzbdav.md).
* Use [Prowlarr](prowlarr.md) to centrally manage indexers and sync them to Lidarr.

---

## Accessing the UI

* Navigate to: `http://<host>:8686`

---

## Resources

* [Lidarr Website](https://lidarr.audio/)
* [Lidarr GitHub](https://github.com/Lidarr/Lidarr)

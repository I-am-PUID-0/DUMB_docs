---
title: Radarr
icon: lucide/film
---

# Radarr (Core Service)

**Radarr** is a movie manager that automates searching, grabbing, and organizing movies through indexers and download clients.

---

## Service Relationships

| Classification | Role                               |
| -------------- | ---------------------------------- |
| Core Service   | Movie automation                   |
| Depends On     | None                               |
| Optional       | Decypharr, NzbDAV, Prowlarr         |
| Exposes UI     | Yes (Web UI)                       |

---

## Configuration in `dumb_config.json`

```json
"radarr": {
  "instances": {
    "Default": {
      "enabled": false,
      "core_service": "",
      "process_name": "Radarr",
      "suppress_logging": false,
      "auto_update": false,
      "auto_update_interval": 24,
      "pinned_version": "",
      "port": 7878,
      "config_dir": "/radarr/default",
      "config_file": "/radarr/default/config.xml",
      "log_file": "/radarr/default/logs/radarr.txt",
      "command": [],
      "env": {}
    }
  }
}
```

### Key Configuration Fields

* `core_service`: Set to `decypharr` or `nzbdav` to enable DUMB integration with those services.
* `port`: Web UI port (default `7878`).
* `pinned_version`: Optional version pin for Radarr updates.
* `config_dir`, `config_file`, `log_file`: Paths for config and logs.

---

## Integration with DUMB

* For Decypharr integration, set `core_service` to `decypharr` and follow the [Decypharr guide](decypharr.md).
* For NzbDAV integration, set `core_service` to `nzbdav` and follow the [NzbDAV guide](nzbdav.md).
* Use [Prowlarr](prowlarr.md) to centrally manage indexers and sync them to Radarr.

---

## Accessing the UI

* Navigate to: `http://<host>:7878`

---

## Resources

* [Radarr Website](https://radarr.video/)
* [Radarr GitHub](https://github.com/Radarr/Radarr)

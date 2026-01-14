---
title: Sonarr
icon: lucide/radio
---

# Sonarr (Core Service)

**Sonarr** is a TV series manager that automates monitoring, searching, and organizing episodes through configured indexers and download clients.

---

## Service Relationships

| Classification | Role                               |
| -------------- | ---------------------------------- |
| Core Service   | TV series automation               |
| Depends On     | None                               |
| Optional       | Decypharr, NzbDAV, Prowlarr         |
| Exposes UI     | Yes (Web UI)                       |

---

## Configuration in `dumb_config.json`

```json
"sonarr": {
  "instances": {
    "Default": {
      "enabled": false,
      "core_service": "",
      "process_name": "Sonarr",
      "suppress_logging": false,
      "auto_update": false,
      "auto_update_interval": 24,
      "pinned_version": "",
      "port": 8989,
      "config_dir": "/sonarr/default",
      "config_file": "/sonarr/default/config.xml",
      "log_file": "/sonarr/default/logs/sonarr.txt",
      "command": [],
      "env": {}
    }
  }
}
```

### Key Configuration Fields

* `core_service`: Set to `decypharr` or `nzbdav` to enable DUMB integration with those services.
* `port`: Web UI port (default `8989`).
* `pinned_version`: Optional version pin for Sonarr updates.
* `config_dir`, `config_file`, `log_file`: Paths for config and logs.

---

## Integration with DUMB

* For Decypharr integration, set `core_service` to `decypharr` and follow the [Decypharr guide](decypharr.md).
* For NzbDAV integration, set `core_service` to `nzbdav` and follow the [NzbDAV guide](nzbdav.md).
* Use [Prowlarr](prowlarr.md) to centrally manage indexers and sync them to Sonarr.

---

## Accessing the UI

* Navigate to: `http://<host>:8989`

---

## Resources

* [Sonarr Website](https://sonarr.tv/)
* [Sonarr GitHub](https://github.com/Sonarr/Sonarr)

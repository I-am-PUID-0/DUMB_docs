---
title: Whisparr
---

# Whisparr (Core Service)

**Whisparr** is an automation tool for managing adult content libraries, similar to Radarr/Sonarr workflows.

---

## 🔗 Service Relationships

| Classification | Role                               |
| -------------- | ---------------------------------- |
| Core Service   | Adult content automation           |
| Depends On     | None                               |
| Optional       | Decypharr, NzbDAV, Prowlarr         |
| Exposes UI     | Yes (Web UI)                       |

---

## 📦 Configuration in `dumb_config.json`

```json
"whisparr": {
  "instances": {
    "Default": {
      "enabled": false,
      "core_service": "",
      "process_name": "Whisparr",
      "suppress_logging": false,
      "auto_update": false,
      "auto_update_interval": 24,
      "pinned_version": "",
      "port": 6969,
      "config_dir": "/whisparr/default",
      "config_file": "/whisparr/default/config.xml",
      "log_file": "/whisparr/default/logs/whisparr.txt",
      "command": [],
      "env": {}
    }
  }
}
```

### 🔍 Key Configuration Fields

* `core_service`: Set to `decypharr` or `nzbdav` to enable DUMB integration with those services.
* `port`: Web UI port (default `6969`).
* `pinned_version`: Optional version pin for Whisparr updates.
* `config_dir`, `config_file`, `log_file`: Paths for config and logs.

---

## ⚙️ Integration with DUMB

* For Decypharr integration, set `core_service` to `decypharr` and follow the [Decypharr guide](decypharr.md).
* For NzbDAV integration, set `core_service` to `nzbdav` and follow the [NzbDAV guide](nzbdav.md).
* Use [Prowlarr](prowlarr.md) to centrally manage indexers and sync them to Whisparr.

---

## 🌐 Accessing the UI

* Navigate to: `http://<host>:6969`

---

## 🔗 Resources

* [Whisparr Website](https://whisparr.com/)
* [Whisparr GitHub](https://github.com/Whisparr/Whisparr)

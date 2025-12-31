---
title: Prowlarr
---

# Prowlarr (Core Service)

**Prowlarr** is an indexer manager for the Arr ecosystem. It centralizes indexer configuration and syncs them to Sonarr, Radarr, Lidarr, and Whisparr.

---

## Service Relationships

| Classification | Role                               |
| -------------- | ---------------------------------- |
| Core Service   | Indexer manager                    |
| Depends On     | None                               |
| Optional       | Sonarr, Radarr, Lidarr, Whisparr    |
| Exposes UI     | Yes (Web UI)                       |

---

## Configuration in `dumb_config.json`

```json
"prowlarr": {
  "instances": {
    "Default": {
      "enabled": false,
      "process_name": "Prowlarr",
      "suppress_logging": false,
      "auto_update": false,
      "auto_update_interval": 24,
      "pinned_version": "",
      "port": 9696,
      "config_dir": "/prowlarr/default",
      "config_file": "/prowlarr/default/config.xml",
      "log_file": "/prowlarr/default/logs/prowlarr.txt",
      "command": [],
      "env": {}
    }
  }
}
```

### Key Configuration Fields

* `port`: Web UI port (default `9696`).
* `pinned_version`: Optional version pin for Prowlarr updates.
* `config_dir`, `config_file`, `log_file`: Paths for config and logs.

---

## Integration with DUMB

* Connect Prowlarr to Sonarr/Radarr/Lidarr/Whisparr via their API keys and base URLs.
* Prowlarr can share indexers across all Arr instances to keep setups consistent.

### Automated Arr Sync

DUMB can auto-configure Prowlarr applications for enabled Arr instances. It reads each Arr API key from the Arr `config_file`, waits for the services to come up, and creates the matching Prowlarr app entries (full sync).

Requirements:

* Prowlarr instance is enabled
* Arr instances are enabled with a valid `port` and readable `config_file`
* Prowlarr API key is available in its `config_file`

---

## Accessing the UI

* Navigate to: `http://<host>:9696`

---

## Resources

* [Prowlarr Website](https://prowlarr.com/)
* [Prowlarr GitHub](https://github.com/Prowlarr/Prowlarr)

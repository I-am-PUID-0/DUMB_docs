---
title: Multi-instance configuration
icon: lucide/layers
---

# Multi-instance configuration

Several DUMB services support multiple instances (for example Sonarr, Radarr, Lidarr, Whisparr, and rclone). This guide shows how to configure instances safely.

---

## Instance pattern

Services that support instances use an `instances` map keyed by a friendly name:

```json
"sonarr": {
  "instances": {
    "Default": {
      "enabled": true,
      "process_name": "Sonarr Default",
      "port": 8989,
      "config_dir": "/sonarr/default",
      "config_file": "/sonarr/default/config.xml",
      "log_file": "/sonarr/default/logs/sonarr.txt"
    },
    "Anime": {
      "enabled": true,
      "process_name": "Sonarr Anime",
      "port": 8991,
      "config_dir": "/sonarr/anime",
      "config_file": "/sonarr/anime/config.xml",
      "log_file": "/sonarr/anime/logs/sonarr.txt"
    }
  }
}
```

---

## Best practices

- Assign unique ports per instance to avoid collisions.
- Use distinct `config_dir` and `log_file` paths.
- Keep `process_name` descriptive for clarity in the UI.
- Set `core_service` when integrating with Decypharr or NzbDAV (single value, list, or comma-separated).

---

## rclone instances

rclone also uses an `instances` map for different mount targets:

```json
"rclone": {
  "instances": {
    "Decypharr": {
      "enabled": true,
      "core_service": "decypharr",
      "mount_dir": "/mnt/debrid",
      "mount_name": "decypharr",
      "config_dir": "/config",
      "config_file": "/config/rclone.conf"
    }
  }
}
```

---

## Related pages

- [Services overview](../services/index.md)
- [Configuration guide](../features/configuration.md)

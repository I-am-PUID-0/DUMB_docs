---
title: Huntarr
icon: lucide/radar
---

# Huntarr

Huntarr is an automated content hunting service that continuously searches for missing or upgraded content in your Arr applications. It periodically triggers searches in Radarr, Sonarr, Lidarr, and Whisparr to find better quality releases or fill gaps in your library.

---

## Overview

Huntarr integrates with your Arr stack to automate the hunt for:

- **Missing content** - Movies, TV episodes, or music not yet downloaded
- **Quality upgrades** - Better releases that meet your quality profiles
- **Cutoff unmet** - Content below your configured quality cutoff

DUMB supports multiple Huntarr instances, allowing you to run separate hunters for different Arr configurations (e.g., one for Decypharr-linked services and one for NzbDAV-linked services).

---

## Service relationships

| Classification | Role                         |
| -------------- | ---------------------------- |
| Core service   | Automated Arr hunting engine |
| Depends on     | None                         |
| Integrates     | Sonarr, Radarr, Lidarr, Whisparr |
| Exposes UI     | Yes (Web UI)                 |

---

## Default ports

| Instance | Port |
|----------|------|
| Default | 9705 |

Additional Huntarr instances must use unique ports.

---

## Automation in DUMB

DUMB auto-populates Huntarr with Arr instances that opt in.

1. Set `use_huntarr: true` on the Arr instances you want Huntarr to manage.
2. (Optional) Set `core_service` on the Huntarr instance to filter which Arr instances it pulls in.

Example Arr instance:

```json
"radarr": {
  "instances": {
    "Decypharr": {
      "enabled": true,
      "core_service": "decypharr",
      "use_huntarr": true,
      "port": 7878,
      "config_file": "/radarr/decypharr/config.xml"
    }
  }
}
```

Example Huntarr instance filter:

```json
"huntarr": {
  "instances": {
    "Decypharr": {
      "core_service": ["decypharr", "nzbdav"]
    }
  }
}
```

With that filter in place, the Huntarr instance only receives Arr entries whose
core services overlap the Huntarr instance. If `core_service` is left blank on a
Huntarr instance, it can receive all Arr instances with `use_huntarr: true`.
For deeper behavior details, see [Core Service Routing](../../reference/core-service.md).

!!! info "Auto-configuration storage"

    DUMB writes Huntarr configuration into the Huntarr SQLite database (`huntarr.db`). You can still tune settings in the Huntarr UI, but DUMB will keep the Arr instance list in sync.

---

## Configuration settings in `dumb_config.json`

Below is a sample configuration for Huntarr within the `dumb_config.json` file:

```json
"huntarr": {
  "instances": {
    "Default": {
      "enabled": false,
      "core_service": "",
      "process_name": "Huntarr",
      "repo_owner": "plexguide",
      "repo_name": "Huntarr.io",
      "release_version_enabled": false,
      "release_version": "latest",
      "branch_enabled": false,
      "branch": "main",
      "suppress_logging": false,
      "log_level": "INFO",
      "port": 9705,
      "auto_update": false,
      "auto_update_interval": 24,
      "clear_on_update": false,
      "exclude_dirs": [
        "/huntarr/default/config"
      ],
      "platforms": [
        "python"
      ],
      "command": [
        "/huntarr/default/venv/bin/python",
        "main.py"
      ],
      "config_dir": "/huntarr/default",
      "config_file": "/huntarr/default/config/huntarr.db",
      "log_file": "/huntarr/default/config/logs/huntarr.log",
      "env": {
        "HUNTARR_CONFIG_DIR": "/huntarr/default/config",
        "HUNTARR_PORT": "{port}"
      }
    }
  }
}
```

### Configuration key descriptions

- **`enabled`**: Whether to start this Huntarr instance.
- **`process_name`**: Display name used in logs and the frontend.
- **`repo_owner`** / **`repo_name`**: GitHub repository to pull from.
- **`release_version_enabled`** / **`release_version`**: Use a tagged release if enabled.
- **`branch_enabled`** / **`branch`**: Use a specific branch if enabled.
- **`suppress_logging`**: If `true`, disables log output for this service.
- **`log_level`**: Logging verbosity (e.g., `DEBUG`, `INFO`).
- **`port`**: Port the Huntarr web UI is exposed on.
- **`auto_update`**: Enables automatic self-updates from GitHub.
- **`auto_update_interval`**: How often (in hours) to check for updates.
- **`clear_on_update`**: Clears build artifacts or cache during updates.
- **`exclude_dirs`**: Prevents specific directories from being affected by updates.
- **`platforms`**: Required runtime (typically `python`).
- **`command`**: The command used to launch Huntarr.
- **`config_dir`** / **`config_file`**: Where configuration files are stored.
- **`log_file`**: Path to the Huntarr log file.
- **`env`**: Environment variables passed at runtime.

---

## Multi-instance support

DUMB supports running multiple Huntarr instances to work with different Arr configurations.
The default config ships with a single `Default` instance.

| Instance | Use Case |
|----------|----------|
| `Default` | General use with any Arr instances you opt in |
| Custom instances | Separate hunters for different `core_service` values |

Each instance maintains its own:

- Configuration directory
- SQLite database
- Web UI port
- Log output

---

## Huntarr web UI

Huntarr provides a web interface for:

- Configuring which Arr services to monitor
- Setting search intervals and limits
- Viewing hunt status and history
- Manual search triggers

Access the UI at `http://<host>:<port>` or through the DUMB frontend's embedded service UI feature.

---

## Tips

- Start with conservative search intervals to avoid rate limiting from indexers.
- Use separate Huntarr instances when you have Arr services connected to different download clients.
- Monitor logs via the DUMB frontend or from the `log_file` path defined for each instance.
- Huntarr respects your Arr quality profiles, so configure those first.

---

## Resources

- [Huntarr GitHub Repository](https://github.com/plexguide/Huntarr)

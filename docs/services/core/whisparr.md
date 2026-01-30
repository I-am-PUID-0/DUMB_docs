---
title: Whisparr
icon: lucide/eye
---

# Whisparr (Core Service)

**Whisparr** is an automation tool for managing adult content libraries, similar to Radarr/Sonarr workflows.

---

## Service Relationships

| Classification | Role                               |
| -------------- | ---------------------------------- |
| Core Service   | Adult content automation           |
| Depends On     | None                               |
| Optional       | Decypharr, NzbDAV, Prowlarr         |
| Exposes UI     | Yes (Web UI)                       |

---

## Configuration in `dumb_config.json`

```json
"whisparr": {
  "instances": {
    "Default": {
      "enabled": false,
      "core_service": "",
      "use_huntarr": false,
      "process_name": "Whisparr",
      "repo_owner": "Whisparr",
      "repo_name": "Whisparr",
      "release_version_enabled": false,
      "release_version": "latest",
      "clear_on_update": false,
      "exclude_dirs": [],
      "platforms": [],
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

### Key Configuration Fields

* `core_service`: Set to `decypharr`, `nzbdav`, or a list of both to enable DUMB integration.
* `use_huntarr`: Opt this instance into Huntarr automation.
* `port`: Web UI port (default `6969`).
* `pinned_version`: Optional version pin for Whisparr updates.
* `repo_owner` / `repo_name`: GitHub repo used for releases or branch builds.
* `release_version_enabled` / `release_version`: Use GitHub releases (e.g., `latest`, `nightly`, `prerelease`, or a tag).
* `clear_on_update`: Clear the install directory before updating.
* `exclude_dirs`: Directories to preserve when clearing.
* `platforms`: Build platforms (auto‑defaults to `["dotnet"]` when using branches).
* `config_dir`, `config_file`, `log_file`: Paths for config and logs.

---

## Repo-based installs and updates

Whisparr now supports the same repo‑based controls as other DUMB services.

- **GitHub releases**: Set `release_version_enabled: true` with a valid `repo_owner`/`repo_name`.
- **Default updater**: Leave `release_version_enabled: false` to use the standard Arr updater.

GitHub sources take priority when enabled and are **not** a fallback. `pinned_version` only applies to the traditional Arr updater.

---

## Integration with DUMB

* For Decypharr integration, set `core_service` to `decypharr` and follow the [Decypharr guide](decypharr.md).
* For NzbDAV integration, set `core_service` to `nzbdav` and follow the [NzbDAV guide](nzbdav.md).
* For combined workflows, set `core_service` to `["decypharr", "nzbdav"]`.
* Use [Prowlarr](prowlarr.md) to centrally manage indexers and sync them to Whisparr.
* DUMB enables Arr folder permission updates and applies permissions to configured root folders during integration.
* See [Core Service Routing](../../reference/core-service.md) for how `core_service` affects automation.

---

## Accessing the UI

* Navigate to: `http://<host>:6969`

---

## Resources

* [Whisparr Website](https://whisparr.com/)
* [Whisparr GitHub](https://github.com/Whisparr/Whisparr)

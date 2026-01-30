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
      "use_huntarr": false,
      "process_name": "Sonarr",
      "repo_owner": "Sonarr",
      "repo_name": "Sonarr",
      "release_version_enabled": false,
      "release_version": "latest",
      "clear_on_update": false,
      "exclude_dirs": [],
      "platforms": [],
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

* `core_service`: Set to `decypharr`, `nzbdav`, or a list of both to enable DUMB integration.
* `use_huntarr`: Opt this instance into Huntarr automation.
* `port`: Web UI port (default `8989`).
* `pinned_version`: Optional version pin for Sonarr updates.
* `repo_owner` / `repo_name`: GitHub repo used for releases or branch builds.
* `release_version_enabled` / `release_version`: Use GitHub releases (e.g., `latest`, `nightly`, `prerelease`, or a tag).
* `clear_on_update`: Clear the install directory before updating.
* `exclude_dirs`: Directories to preserve when clearing.
* `platforms`: Build platforms (auto‑defaults to `["dotnet"]` when using branches).
* `config_dir`, `config_file`, `log_file`: Paths for config and logs.

---

## Repo-based installs and updates

Sonarr now supports the same repo‑based controls as other DUMB services.

- **GitHub releases**: Set `release_version_enabled: true` with a valid `repo_owner`/`repo_name`.
- **Default updater**: Leave `release_version_enabled: false` to use the standard Arr updater.

GitHub sources take priority when enabled and are **not** a fallback. `pinned_version` only applies to the traditional Arr updater.

---

## Integration with DUMB

* For Decypharr integration, set `core_service` to `decypharr` and follow the [Decypharr guide](decypharr.md).
* For NzbDAV integration, set `core_service` to `nzbdav` and follow the [NzbDAV guide](nzbdav.md).
* For combined workflows, set `core_service` to `["decypharr", "nzbdav"]`.
* Use [Prowlarr](prowlarr.md) to centrally manage indexers and sync them to Sonarr.
* DUMB enables Arr folder permission updates and applies permissions to configured root folders during integration.
* See [Core Service Routing](../../reference/core-service.md) for how `core_service` affects automation.

---

## Accessing the UI

* Navigate to: `http://<host>:8989`

---

## Resources

* [Sonarr Website](https://sonarr.tv/)
* [Sonarr GitHub](https://github.com/Sonarr/Sonarr)

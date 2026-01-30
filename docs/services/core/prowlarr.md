---
title: Prowlarr
icon: lucide/search
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
      "repo_owner": "Prowlarr",
      "repo_name": "Prowlarr",
      "release_version_enabled": false,
      "release_version": "latest",
      "clear_on_update": false,
      "exclude_dirs": [],
      "platforms": [],
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
* `repo_owner` / `repo_name`: GitHub repo used for releases or branch builds.
* `release_version_enabled` / `release_version`: Use GitHub releases (e.g., `latest`, `nightly`, `prerelease`, or a tag).
* `clear_on_update`: Clear the install directory before updating.
* `exclude_dirs`: Directories to preserve when clearing.
* `platforms`: Build platforms (auto‑defaults to `["dotnet"]` when using branches).
* `config_dir`, `config_file`, `log_file`: Paths for config and logs.

---

## Repo-based installs and updates

Prowlarr now supports the same repo‑based controls as other DUMB services.

- **GitHub releases**: Set `release_version_enabled: true` with a valid `repo_owner`/`repo_name`.
- **Default updater**: Leave `release_version_enabled: false` to use the standard Arr updater.

GitHub sources take priority when enabled and are **not** a fallback. `pinned_version` only applies to the traditional Arr updater.

---

## Integration with DUMB

* Connect Prowlarr to Sonarr/Radarr/Lidarr/Whisparr via their API keys and base URLs.
* Prowlarr can share indexers across all Arr instances to keep setups consistent.

### Automated Arr sync

DUMB can auto-configure Prowlarr applications for enabled Arr instances. It reads each Arr API key from the Arr `config_file`, waits for the services to come up, and creates the matching Prowlarr app entries (full sync). Apps are created using the Arr `process_name`.

Requirements:

* Prowlarr instance is enabled.
* Arr instances are enabled with a valid `port` and readable `config_file`.
* Prowlarr API key is available in its `config_file`.

### Core-service tags

DUMB tags Prowlarr application entries when the Arr instance has `core_service`
set (single value or list):

| Arr core service | Tag applied in Prowlarr |
|------------------|-------------------------|
| `decypharr` | `decypharr` |
| `nzbdav` | `nzbdav` |

These tags are created automatically if they do not exist.

### Indexer routing via tags

Prowlarr uses tags to decide which indexers sync into which Arr apps. DUMB links each Arr app
to the tag matching its core service(s), so Decypharr and NzbDAV indexers stay separated.

When you add custom indexers in Prowlarr, make sure the correct tag is applied so they sync to
the intended Arr apps.

### Custom indexer sync (Decypharr)

When Decypharr is enabled, DUMB also syncs custom indexer definitions and creates indexers:

- **Zilean** (Torznab) with a base URL that prefers the local Zilean instance when enabled, and
  defaults to `https://zileanfortheweebs.midnightignite.me` otherwise. You can override the URL
  in Prowlarr after it is created.
- **StremThru** (Torznab) using the hosted endpoint

If Decypharr is enabled, DUMB automatically enables the public StremThru indexer.

Custom definitions are pulled from the `Prowlarr-Indexers` repository and stored in
`<prowlarr_config_dir>/Definitions/Custom` (or `<prowlarr_config_dir>/indexer/Definitions/Custom` when present).

Other custom indexers in the definition repository are available to add manually in Prowlarr.

---

## Accessing the UI

* Navigate to: `http://<host>:9696`

---

## Resources

* [Prowlarr Website](https://prowlarr.com/)
* [Prowlarr GitHub](https://github.com/Prowlarr/Prowlarr)

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
| Optional       | Decypharr, NzbDAV, AltMount, Prowlarr |
| Exposes UI     | Yes (Web UI)                       |

---

## Configuration in `dumb_config.json`

```json
"lidarr": {
  "instances": {
    "Default": {
      "enabled": false,
      "core_service": "",
      "use_neutarr": false,
      "postgres_enabled": false,
      "postgres_main_db": "",
      "postgres_log_db": "",
      "process_name": "Lidarr",
      "repo_owner": "Lidarr",
      "repo_name": "Lidarr",
      "release_version_enabled": false,
      "release_version": "latest",
      "clear_on_update": false,
      "exclude_dirs": [],
      "platforms": [],
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

* `core_service`: Set to `decypharr`, `nzbdav`, `altmount`, or a list of workflow keys to enable DUMB integration.
* `use_neutarr`: Opt this instance into NeutArr automation.
* `postgres_enabled`: Opt this instance into DUMB-managed PostgreSQL config. SQLite is the default; set this to `true` only when you want Lidarr to use PostgreSQL.
* `postgres_main_db` / `postgres_log_db`: Optional database-name overrides. When blank, DUMB uses `lidarr-main` and `lidarr-log` for the default instance, or unique instance-scoped names for additional instances.
* `port`: Web UI port (default `8686`).
* `pinned_version`: Optional version pin for Lidarr updates.
* `repo_owner` / `repo_name`: GitHub repo used for releases or branch builds.
* `release_version_enabled` / `release_version`: Use GitHub releases (e.g., `latest`, `nightly`, `prerelease`, or a tag).
* `clear_on_update`: Clear the install directory before updating.
* `exclude_dirs`: Directories to preserve when clearing.
* `platforms`: Build platforms (auto‑defaults to `["dotnet"]` when using branches).
* `config_dir`, `config_file`, `log_file`: Paths for config and logs.

---

## PostgreSQL database mode

When `postgres_enabled` is `true`, DUMB:

* enables the bundled PostgreSQL service if needed;
* creates the Lidarr main/log databases in `postgres.databases`;
* starts PostgreSQL before Lidarr; and
* writes the required `PostgresUser`, `PostgresPassword`, `PostgresHost`, `PostgresPort`, `PostgresMainDb`, and `PostgresLogDb` entries to Lidarr's `config.xml`.

During onboarding, enabling `postgres_enabled` for Lidarr is enough; you do not need to separately select PostgreSQL as an optional service.

!!! danger "This does not migrate existing SQLite data"
    Setting `postgres_enabled: true` changes the database backend Lidarr starts with. It does **not** copy `lidarr.db` into PostgreSQL.

    If you enable this on an existing SQLite-backed Lidarr instance without doing a manual migration, Lidarr can start against fresh PostgreSQL databases and appear empty or newly initialized.

This mode is intended for new Lidarr databases unless you are deliberately following Lidarr's upstream community migration notes. Lidarr's upstream documentation says SQLite-to-PostgreSQL migration is not officially supported. Back up both `/lidarr/...` and `/postgres_data` before experimenting with an existing instance.

Manual migration, if you choose to attempt it, is outside DUMB automation. The rough upstream flow is: back up, stop Lidarr, enable PostgreSQL mode, let Lidarr initialize the PostgreSQL schema once, stop Lidarr again, then follow the Lidarr `pgloader` migration guide for the main database.

!!! warning "PostgreSQL is not a temporary toggle"
    There is no known supported migration path from PostgreSQL back to SQLite for Lidarr. Treat `postgres_enabled: true` as a long-term database choice unless you are willing to recreate the Lidarr instance from scratch.

    DUMB does not provide automatic SQLite-to-PostgreSQL or PostgreSQL-to-SQLite migration for Lidarr.

---

## Repo-based installs and updates

Lidarr now supports the same repo‑based controls as other DUMB services.

- **GitHub releases**: Set `release_version_enabled: true` with a valid `repo_owner`/`repo_name`.
- **Default updater**: Leave `release_version_enabled: false` to use the standard Arr updater.

GitHub sources take priority when enabled and are **not** a fallback. `pinned_version` only applies to the traditional Arr updater.

---

## Integration with DUMB

* For Decypharr integration, set `core_service` to `decypharr` and follow the [Decypharr guide](decypharr.md).
* For NzbDAV integration, set `core_service` to `nzbdav` and follow the [NzbDAV guide](nzbdav.md).
* For AltMount integration, set `core_service` to `altmount` and follow the [AltMount guide](altmount.md).
* For combined workflows, set `core_service` to a list such as `["decypharr", "nzbdav", "altmount"]`.
* Use [Prowlarr](prowlarr.md) to centrally manage indexers and sync them to Lidarr.
* DUMB enables Arr folder permission updates and applies permissions to configured root folders during integration.
* See [Core Service Routing](../../reference/core-service.md) for how `core_service` affects automation.

---

## Accessing the UI

* Navigate to: `http://<host>:8686`

---

## Resources

* [Lidarr Website](https://lidarr.audio/)
* [Lidarr GitHub](https://github.com/Lidarr/Lidarr)
* [Lidarr PostgreSQL setup](https://wiki.servarr.com/lidarr/postgres-setup)

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
| Optional       | Decypharr, NzbDAV, AltMount, Prowlarr |
| Exposes UI     | Yes (Web UI)                       |

---

## Configuration in `dumb_config.json`

```json
"sonarr": {
  "instances": {
    "Default": {
      "enabled": false,
      "core_service": "",
      "use_neutarr": false,
      "use_profilarr": false,
      "postgres_enabled": false,
      "postgres_main_db": "",
      "postgres_log_db": "",
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
      "auto_update_start_time": "04:00",
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

* `core_service`: Set to `decypharr`, `nzbdav`, `altmount`, or a list of workflow keys to enable DUMB integration.
* `use_neutarr`: Opt this instance into NeutArr automation.
* `use_profilarr`: Opt this instance into Profilarr auto‑linking.
* `postgres_enabled`: Opt this instance into DUMB-managed PostgreSQL config. SQLite is the default; set this to `true` only when you want Sonarr to use PostgreSQL.
* `postgres_main_db` / `postgres_log_db`: Optional database-name overrides. When blank, DUMB uses `sonarr-main` and `sonarr-log` for the default instance, or unique instance-scoped names for additional instances.
* `port`: Web UI port (default `8989`).
* `pinned_version`: Optional version pin for Sonarr updates.
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
* creates the Sonarr main/log databases in `postgres.databases`;
* starts PostgreSQL before Sonarr; and
* writes the required `PostgresUser`, `PostgresPassword`, `PostgresHost`, `PostgresPort`, `PostgresMainDb`, and `PostgresLogDb` entries to Sonarr's `config.xml`.

During onboarding, enabling `postgres_enabled` for Sonarr is enough; you do not need to separately select PostgreSQL as an optional service.

!!! danger "This does not migrate existing SQLite data"
    Setting `postgres_enabled: true` changes the database backend Sonarr starts with. It does **not** copy `sonarr.db` into PostgreSQL.

    If you enable this on an existing SQLite-backed Sonarr instance without doing a manual migration, Sonarr can start against fresh PostgreSQL databases and appear empty or newly initialized.

For an existing instance, use the **Database Migration** tool on its service page. Run a rehearsal first, review its table-count validation, and only then start guarded cutover. See [SQLite to PostgreSQL Migration](../../features/arr-postgres-migration.md).

Sonarr's upstream documentation still classifies existing SQLite migration as unsupported. Back up Sonarr's `/data/sonarr` persistence and PostgreSQL's `/data/postgres` persistence (internal paths `/sonarr/...` and `/postgres_data`) before proceeding, even when using DUMB's guarded workflow.

!!! warning "PostgreSQL is not a temporary toggle"
    There is no known supported migration path from PostgreSQL back to SQLite for Sonarr. Treat `postgres_enabled: true` as a long-term database choice unless you are willing to recreate the Sonarr instance from scratch.

    DUMB preserves the pre-cutover SQLite database and can restore its configuration, but it does not copy later PostgreSQL changes back into SQLite.

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
* For AltMount integration, set `core_service` to `altmount` and follow the [AltMount guide](altmount.md).
* For combined workflows, set `core_service` to a list such as `["decypharr", "nzbdav", "altmount"]`.
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
* [Sonarr PostgreSQL setup](https://wiki.servarr.com/en/sonarr/postgres-setup)

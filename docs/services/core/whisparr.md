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
| Optional       | Decypharr, NzbDAV, AltMount, Prowlarr |
| Exposes UI     | Yes (Web UI)                       |

---

## Configuration in `dumb_config.json`

```json
"whisparr": {
  "instances": {
    "Default": {
      "enabled": false,
      "core_service": "",
      "use_neutarr": false,
      "postgres_enabled": false,
      "postgres_main_db": "",
      "postgres_log_db": "",
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

* `core_service`: Set to `decypharr`, `nzbdav`, `altmount`, or a list of workflow keys to enable DUMB integration.
* `use_neutarr`: Opt this instance into NeutArr automation.
* `postgres_enabled`: Opt this instance into DUMB-managed PostgreSQL config. SQLite is the default; set this to `true` only when you want Whisparr to use PostgreSQL.
* `postgres_main_db` / `postgres_log_db`: Optional database-name overrides. When blank, DUMB uses `whisparr-main` and `whisparr-log` for the default instance, or unique instance-scoped names for additional instances.
* `port`: Web UI port (default `6969`).
* `pinned_version`: Optional version pin for Whisparr updates.
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
* creates the Whisparr main/log databases in `postgres.databases`;
* starts PostgreSQL before Whisparr; and
* writes the required `PostgresUser`, `PostgresPassword`, `PostgresHost`, `PostgresPort`, `PostgresMainDb`, and `PostgresLogDb` entries to Whisparr's `config.xml`.

During onboarding, enabling `postgres_enabled` for Whisparr is enough; you do not need to separately select PostgreSQL as an optional service.

!!! danger "This does not migrate existing SQLite data"
    Setting `postgres_enabled: true` changes the database backend Whisparr starts with. It does **not** copy `whisparr.db` into PostgreSQL.

    If you enable this on an existing SQLite-backed Whisparr instance without doing a manual migration, Whisparr can start against fresh PostgreSQL databases and appear empty or newly initialized.

For an existing instance, use **Database Migration** on the service page. DUMB requires a rehearsal, initializes an isolated Whisparr-owned PostgreSQL schema, imports and validates every table, and preserves SQLite for rollback. See [SQLite to PostgreSQL Migration](../../features/arr-postgres-migration.md).

!!! warning "PostgreSQL is not a temporary toggle"
    There is no known supported migration path from PostgreSQL back to SQLite for Whisparr. Treat `postgres_enabled: true` as a long-term database choice unless you are willing to recreate the Whisparr instance from scratch.

    DUMB can restore the preserved pre-cutover SQLite state, but it does not copy later PostgreSQL writes back into SQLite.

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
* For AltMount integration, set `core_service` to `altmount` and follow the [AltMount guide](altmount.md).
* For combined workflows, set `core_service` to a list such as `["decypharr", "nzbdav", "altmount"]`.
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
* [Whisparr PostgreSQL setup](https://wiki.servarr.com/whisparr/postgres-setup)

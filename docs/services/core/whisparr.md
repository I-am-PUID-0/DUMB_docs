---
title: Whisparr
description: Configure Whisparr in DUMB for automated library monitoring, indexers, download clients, root folders, profiles, and linked workflow services.
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
| Optional       | Decypharr, InfiniDysk, AltMount, Prowlarr |
| Exposes UI     | Yes (Web UI)                       |

---

## Configuration in `dumb_config.json`

```json
"whisparr": {
  "instances": {
    "Default": {
      "enabled": false,
      "whisparr_version": "",
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
      "branch_enabled": false,
      "branch": "",
      "commit_sha": "",
      "clear_on_update": false,
      "exclude_dirs": [],
      "platforms": [],
      "suppress_logging": false,
      "auto_update": false,
      "auto_update_interval": 24,
      "auto_update_start_time": "04:00",
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

* `whisparr_version`: Choose `v2` or `v3` (Eros), or leave blank to detect and preserve the existing version. A new instance with no existing version defaults to v2.
* `core_service`: Set to `decypharr`, `infinidysk`, `altmount`, or a list of workflow keys to enable DUMB integration.
* `use_neutarr`: Opt this instance into NeutArr automation.
* `postgres_enabled`: Opt this instance into DUMB-managed PostgreSQL config. SQLite is the default; set this to `true` only when you want Whisparr to use PostgreSQL.
* `postgres_main_db` / `postgres_log_db`: Optional database-name overrides. When blank, DUMB uses `whisparr-main` and `whisparr-log` for the default instance, or unique instance-scoped names for additional instances.
* `port`: Web UI port (default `6969`).
* `pinned_version`: Optional exact numeric release version, such as `3.6.4.1865`, within the selected major version. This applies when `release_version_enabled` is `false`.
* `repo_owner` / `repo_name`: GitHub release source. Official v2 releases use `Whisparr/Whisparr`; v3 releases use `Whisparr/Whisparr-Eros`.
* `release_version_enabled` / `release_version`: Select a GitHub release using `latest`, `prerelease`, or an exact tag. When disabled, an unpinned instance still installs the latest official release for its selected version.
* `branch_enabled` / `branch`: Select an update channel: `v2` or `v2-develop` for v2, and `eros` or `eros-develop` for v3. These select packaged releases; Whisparr source builds are not supported.
* `commit_sha`: Leave blank. Installing Whisparr from a specific source commit is not supported.
* `clear_on_update` / `exclude_dirs`: Generic install-cleanup settings. Whisparr stages a replacement of its managed binary directory; keep `config_dir` separate from that directory. These fields do not convert or relocate databases.
* `config_dir`, `config_file`, `log_file`: Paths for config and logs.

---

## Choosing v2 or v3 (Eros)

Choose **Whisparr v2**, **Whisparr v3 (Eros)**, or **Detect existing version** during onboarding. You can also set `whisparr_version` on the instance in DUMB Config.

Leaving the setting blank preserves the version indicated by the existing database, installed binary, repository, or update channel. It defaults to v2 only for a new instance without that existing version information.

| Version | Official release repository | Stable / development channel | SQLite main database |
| ------- | --------------------------- | ---------------------------- | -------------------- |
| v2 | [Whisparr/Whisparr](https://github.com/Whisparr/Whisparr/releases) | `v2` / `v2-develop` | `whisparr2.db`; older installs may use `whisparr.db` |
| v3 (Eros) | [Whisparr/Whisparr-Eros](https://github.com/Whisparr/Whisparr-Eros/releases) | `eros` / `eros-develop` | `whisparr3.db` |

Both versions use `logs.db` for SQLite logs. DUMB keeps each instance's binary separate under `/opt/whisparr/instances/<instance-slug>/Whisparr/Whisparr` and leaves the configured data directory in place.

!!! warning "Changing versions does not convert the database"
    v2 and v3 have different databases and library models. Create a separate instance with its own `config_dir` and port when installing the other version.

    DUMB refuses an installation or startup when the selected version conflicts with existing data, or when both version families are present in the same data directory. It does not rename, delete, or convert those databases.

!!! warning "Legacy v2 database filenames require a separate migration"
    Current v2 releases (2.2 and newer) open `whisparr2.db`; they do not automatically discover or rename a legacy `whisparr.db`. Starting a newer binary against only the legacy file could create an empty library. See the [upstream v2 database path](https://github.com/Whisparr/Whisparr/blob/v2.2.0-release.231/src/NzbDrone.Common/Extensions/PathExtensions.cs).

    DUMB keeps a compatible existing v2 installation working, but blocks an incompatible binary or an update or release pin that would change the expected database filename until you have completed a separately backed-up and validated database migration. It also blocks an older v2 binary against the newer filename and requires deliberate resolution if both filenames or their recovery files are present.

    Changing `whisparr_version`, clearing the install directory, or changing `exclude_dirs` does not perform this migration. Preserve the original database and recovery files while planning it.

For example, a separate v3 instance using the official stable releases can use:

```json
"whisparr": {
  "instances": {
    "Eros": {
      "enabled": true,
      "whisparr_version": "v3",
      "repo_owner": "Whisparr",
      "repo_name": "Whisparr-Eros",
      "release_version_enabled": true,
      "release_version": "latest",
      "port": 6970,
      "config_dir": "/whisparr/eros",
      "config_file": "/whisparr/eros/config.xml",
      "log_file": "/whisparr/eros/logs/whisparr.txt"
    }
  }
}
```

---

## PostgreSQL database mode

When `postgres_enabled` is `true`, DUMB:

* enables the bundled PostgreSQL service if needed;
* creates the Whisparr main/log databases in `postgres.databases`;
* starts PostgreSQL before Whisparr; and
* writes the required `PostgresUser`, `PostgresPassword`, `PostgresHost`, `PostgresPort`, `PostgresMainDb`, and `PostgresLogDb` entries to Whisparr's `config.xml`.

During onboarding, enabling `postgres_enabled` for Whisparr is enough; you do not need to separately select PostgreSQL as an optional service.

!!! danger "This does not migrate existing SQLite data"
    Setting `postgres_enabled: true` changes the database backend Whisparr starts with. It does **not** copy the existing SQLite database (`whisparr2.db`, legacy `whisparr.db`, or `whisparr3.db`) into PostgreSQL.

    If you enable this on an existing SQLite-backed Whisparr instance without doing a manual migration, Whisparr can start against fresh PostgreSQL databases and appear empty or newly initialized.

For an existing instance, use **Database Migration** on the service page. DUMB requires a rehearsal, initializes an isolated Whisparr-owned PostgreSQL schema, imports and validates every table, and preserves SQLite for rollback. See [SQLite to PostgreSQL Migration](../../features/arr-postgres-migration.md).

This changes the database backend for the installed Whisparr version. It does not convert a v2 library into a v3 library.

!!! warning "PostgreSQL is not a temporary toggle"
    There is no known supported migration path from PostgreSQL back to SQLite for Whisparr. Treat `postgres_enabled: true` as a long-term database choice unless you are willing to recreate the Whisparr instance from scratch.

    DUMB can restore the preserved pre-cutover SQLite state, but it does not copy later PostgreSQL writes back into SQLite.

---

## Repo-based installs and updates

DUMB installs ready-to-run official GitHub release archives for the selected Whisparr version. The default install and updater also use these archives; older Servarr `nightly` and `eros` download feeds are not used to find current Whisparr releases.

- **Default stable releases**: Leave `release_version_enabled: false` and `pinned_version` blank.
- **Explicit GitHub release**: Set `release_version_enabled: true` with the matching official repository, then choose `latest`, `prerelease`, or a release tag in `release_version`.
- **Exact numeric pin**: Leave `release_version_enabled: false` and set `pinned_version` to the exact release version from the selected major version.
- **Development channel**: Use `v2-develop` or `eros-develop` with `branch_enabled: true`. Use the corresponding stable channel to stay on stable releases.

An explicit GitHub release selection takes priority over `pinned_version`. Release tags and pins must match the selected Whisparr major version. Unavailable releases fail the install or update instead of silently switching versions or compiling from source.

Updates replace the managed binary directory after staging the selected release. Configuration and database directories remain separate, and DUMB checks their compatibility before stopping the running service or activating a replacement binary.

---

## Integration with DUMB

* For Decypharr integration, set `core_service` to `decypharr` and follow the [Decypharr guide](decypharr.md).
* For InfiniDysk integration, set `core_service` to `infinidysk` and follow the [InfiniDysk guide](infinidysk.md).
* For AltMount integration, set `core_service` to `altmount` and follow the [AltMount guide](altmount.md).
* For combined workflows, set `core_service` to a list such as `["decypharr", "infinidysk", "altmount"]`.
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
* [Whisparr v2 releases](https://github.com/Whisparr/Whisparr/releases)
* [Whisparr v3 (Eros) GitHub](https://github.com/Whisparr/Whisparr-Eros)
* [Whisparr v3 (Eros) releases](https://github.com/Whisparr/Whisparr-Eros/releases)
* [Whisparr PostgreSQL setup](https://wiki.servarr.com/whisparr/postgres-setup)

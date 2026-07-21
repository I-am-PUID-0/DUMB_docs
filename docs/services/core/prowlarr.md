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
      "postgres_enabled": false,
      "postgres_main_db": "",
      "postgres_log_db": "",
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

* `postgres_enabled`: Opt this instance into DUMB-managed PostgreSQL config. SQLite is the default; set this to `true` only when you want Prowlarr to use PostgreSQL.
* `postgres_main_db` / `postgres_log_db`: Optional database-name overrides. When blank, DUMB uses `prowlarr-main` and `prowlarr-log` for the default instance, or unique instance-scoped names for additional instances.
* `port`: Web UI port (default `9696`).
* `pinned_version`: Optional version pin for Prowlarr updates.
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
* creates the Prowlarr main/log databases in `postgres.databases`;
* starts PostgreSQL before Prowlarr; and
* writes the required `PostgresUser`, `PostgresPassword`, `PostgresHost`, `PostgresPort`, `PostgresMainDb`, and `PostgresLogDb` entries to Prowlarr's `config.xml`.

During onboarding, enabling `postgres_enabled` for Prowlarr is enough; you do not need to separately select PostgreSQL as an optional service.

!!! danger "This does not migrate existing SQLite data"
    Setting `postgres_enabled: true` changes the database backend Prowlarr starts with. It does **not** copy `prowlarr.db` into PostgreSQL.

    If you enable this on an existing SQLite-backed Prowlarr instance without doing a manual migration, Prowlarr can start against fresh PostgreSQL databases and appear empty or newly initialized.

For an existing instance, use **Database Migration** on the service page. DUMB requires a rehearsal, initializes an isolated Prowlarr-owned PostgreSQL schema, imports and validates every table, and preserves SQLite for rollback. Prowlarr's upstream guide still classifies migration as unsupported. See [SQLite to PostgreSQL Migration](../../features/arr-postgres-migration.md).

!!! warning "PostgreSQL is not a temporary toggle"
    There is no known supported migration path from PostgreSQL back to SQLite for Prowlarr. Treat `postgres_enabled: true` as a long-term database choice unless you are willing to recreate the Prowlarr instance from scratch.

    DUMB can restore the preserved pre-cutover SQLite state, but it does not copy later PostgreSQL writes back into SQLite.

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
to the tag matching its core service(s), so Decypharr, NzbDAV, and AltMount indexers stay separated.

When you add custom indexers in Prowlarr, make sure the correct tag is applied so they sync to
the intended Arr apps.

### Custom indexer sync (Decypharr)

When Decypharr is enabled, DUMB also syncs custom indexer definitions and creates indexers:

- **Zilean** (Torznab) with a base URL that prefers the local Zilean instance when enabled, and
  defaults to `https://zileanfortheweebs.midnightignite.me` otherwise. You can override the URL
  in Prowlarr after it is created.
- **StremThru** (Torznab) using the hosted endpoint

If Decypharr is enabled, DUMB automatically enables the public StremThru indexer.

For Whisparr applications, DUMB widens Prowlarr sync categories to include the Movie/TV roots used by the Zilean/StremThru custom definitions plus the common XXX categories. This lets the custom indexers sync to Whisparr while keeping the normal Decypharr/NzbDAV/AltMount tag separation.

Custom definitions are pulled from the `Prowlarr-Indexers` repository and stored in
`<prowlarr_config_dir>/Definitions/Custom` (or `<prowlarr_config_dir>/indexer/Definitions/Custom` when present).

Other custom indexers in the definition repository are available to add manually in Prowlarr.

---

## Accessing the UI

* Navigate to: `http://<host>:9696`

---

## Installation troubleshooting

Before extracting an Arr archive, DUMB validates that `tar` can read the full
gzip archive and logs both the downloaded archive size and free space in the
installation filesystem. If validation or extraction fails, the structured
DUMB error includes `tar`'s stderr, its exit status, the archive size, and the
available space. Messages such as `unexpected end of file`, `No space left on
device`, `Permission denied`, or `Read-only file system` therefore remain
visible even when `/opt/prowlarr` is ephemeral.

A Prowlarr preinstall failure no longer shuts down the DUMB API or Frontend.
DUMB records the failure, completes the remaining preinstall work, and retries
Prowlarr during normal service startup. If the retry also fails, Prowlarr stays
stopped while the DUMB control plane remains available for logs and service
management.

For repeated extraction failures, check the Docker host's storage and inode
capacity at its Docker root directory. A full container removal/recreation
deletes the failed archive under `/opt`, so preserve the complete DUMB log when
requesting support.

If extraction reports `Function not implemented`, the archive and available
space are not normally the cause. Ubuntu 26.04's security-hardened GNU tar uses
the Linux `openat2` interface to confine archive extraction. Older host kernels,
container runtimes, or seccomp profiles can return `ENOSYS` for that interface
even when the same installation worked with an older DUMB image. DUMB retries
these failures with Python's security-filtered archive extractor, which rejects
paths and links that escape `/opt/prowlarr`.

If both extractors fail, check the host's kernel, Docker, containerd, runc, and
seccomp versions. Do not permanently disable seccomp as a workaround; updating
the host runtime retains its security boundary and native GNU tar extraction.

---

## Resources

* [Prowlarr Website](https://prowlarr.com/)
* [Prowlarr GitHub](https://github.com/Prowlarr/Prowlarr)
* [Prowlarr PostgreSQL setup](https://wiki.servarr.com/prowlarr/postgres-setup)

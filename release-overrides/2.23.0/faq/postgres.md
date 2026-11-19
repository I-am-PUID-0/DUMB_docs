---
title: PostgreSQL FAQ
description: Troubleshoot PostgreSQL startup and connections in DUMB, understand which services use the database, and choose the correct listener and client settings.
icon: lucide/database
---

# PostgreSQL FAQ

**Visual guide:** [Follow the SQLite-to-PostgreSQL migration workflow](../features/arr-postgres-migration.md).

## How PostgreSQL is used in DUMB

PostgreSQL stores persistent data for services that require it and for optional SQLite-to-PostgreSQL cutovers. Current integrations include:

- **Riven Backend**, **Zilean**, **Traefik Proxy Admin**, and **mediastorm**
- Optional PostgreSQL modes for **Sonarr, Radarr, Lidarr, Prowlarr, Whisparr, Bazarr, Pulsarr, Seerr, and AltMount** after a guarded migration
- A fresh-install main-database option for **InfiniDysk v1.2.0+**, plus DUMB's separate guarded migration for official stable v1.2.0-or-newer runtimes whose source SQLite and staged PostgreSQL schemas exactly match DUMB's supported contract; upstream itself remains fresh-install-only
- Optional DUMB Metrics history storage
- **pgAdmin**'s own database when pgAdmin is enabled

Each service has its **own database**, created automatically when DUMB starts:

| Service        | Database Name |
|----------------|----------------|
| Riven          | `riven`        |
| Zilean         | `zilean`       |
| pgAdmin (optional) | `pgadmin`   |
| Traefik Proxy Admin | `traefik_proxy_admin` |
| mediastorm | `mediastorm` |
| InfiniDysk (fresh install or guarded DUMB cutover) | `infinidysk` by default |
| Metrics history (optional default) | `dumb_metrics` |

Additional databases are registered from service configuration. PostgreSQL's internal data directory defaults to `/postgres_data`; the maintained Compose layout persists it at `/data/postgres` through DUMB's managed data mapping.


## What happens if I delete the database?

If `/data/postgres` (or a directly mounted legacy `/postgres_data`) is deleted, **every database in that cluster is lost**.

This includes:

- Application data and settings for PostgreSQL-backed services
- Migrated Arr-family databases
- PostgreSQL Metrics history
- InfiniDysk's main database after a fresh PostgreSQL install or successful DUMB guarded cutover
- pgAdmin state stored in its database

Services may create empty schemas on their next launch, but this does not reconstruct the deleted application data.

!!! warning "A directory copy is not a complete running-database backup strategy"
    Schedule logical `pg_dump` backups for every important database and test restores. Also protect the mounted `/data` tree while the stack is stopped or with a PostgreSQL-aware physical-backup process.

    Follow the [scheduled pg_dump backups with pgAdmin and pgAgent](pgadmin.md#example-scheduled-backups-with-pgagent) example, including its retention and restore-test steps.

    For PostgreSQL-backed InfiniDysk, the application backup does not contain
    the PostgreSQL main database. Pair the logical database backup with a
    filesystem backup of the InfiniDysk configuration directory because
    `metrics.sqlite`, `warden.db`, `usenet-migration.db`, blobs, and
    `session.key` remain local.

## Can an existing InfiniDysk installation move to PostgreSQL?

Yes, through DUMB's guarded **Database Migration** workflow when the backend
advertises `infinidysk` in `postgres_migration_service_keys`. Upstream
InfiniDysk itself still documents PostgreSQL as new-install-only and tracks
native migration tooling separately in
[issue #1012](https://github.com/infinidysk/infinidysk/issues/1012). See the
[official InfiniDysk PostgreSQL guide](https://github.com/infinidysk/infinidysk/blob/main/docs/operations/postgresql.md).

DUMB requires a successful rehearsal before cutover, migrates and validates
only `db.sqlite`, preserves the SQLite/configuration rollback data, and leaves
`metrics.sqlite`, `warden.db`, and `usenet-migration.db` on SQLite. Keep an
independent filesystem backup before migration. After cutover, configure and
test a logical PostgreSQL backup; roll back promptly if validation fails
because PostgreSQL writes are not copied back into SQLite.

If DUMB still offers an NzbDAV-to-InfiniDysk identity or full namespace
migration, complete that before enabling PostgreSQL or opening Database
Migration. Do not try a direct provider toggle on an existing SQLite install:
DUMB fails closed and requires the guided workflow.


## Can I reset the database intentionally?

Yes, but deleting the whole cluster resets every PostgreSQL-backed service. For a disposable installation, stop DUMB and remove `/data/postgres` (or your explicitly mounted `/postgres_data`) only after confirming the exact path and preserving any required backups.

Alternatively, use **pgAdmin 4** (if enabled) to drop individual databases manually.

> See the [PostgreSQL Useful Commands](../services/dependent/postgres.md#useful-commands) section.

> Alternatively, see the [pgAdmin FAQ](pgadmin.md#drop-a-database-or-create-a-manual-backup-in-pgadmin) section.


## What are the default credentials?

- **Username**: `DUMB`
- **Password**: `postgres`
- **Port**: `5432`
- These values can be customized in the `postgres` section of `dumb_config.json`.


## Can I connect to PostgreSQL externally?

Use DUMB's embedded [pgAdmin](../services/optional/pgadmin.md) when browser-based inspection is enough; it avoids publishing a database port.

For a separate database client, an administrator must review PostgreSQL's actual `listen_addresses`, host-based access rules, the Docker port binding, and network protection. The `postgres.host` setting is the address DUMB uses to connect; changing it to `0.0.0.0` does not configure the server listener.

<details class="geek-details" markdown="1">
<summary>Technical details: external PostgreSQL access</summary>

Inspect `SHOW listen_addresses;` and `SHOW hba_file;` in pgAdmin or `psql`, then review the matching PostgreSQL configuration. If host access is required, bind a published port to a specific trusted interface or loopback, such as `127.0.0.1:5432:5432`, and use a protected tunnel or trusted network path. Authentication and host-based access rules must permit the intended client. Replace public bootstrap passwords before granting access.

</details>

## Is it safe to run queries against the databases?

Use read-only queries for inspection. Direct writes can bypass the application's validation and break relationships or migration state. Use the application's own controls where possible; take a restorable backup before intentional database changes.


## Related Pages

- [pgAdmin Service Guide](../services/optional/pgadmin.md)
- [Riven Backend](../services/core/riven-backend.md)
- [Zilean](../services/optional/zilean.md)
- [DUMB Configuration](../features/configuration.md)

---
title: SQLite to PostgreSQL Migration
---

# SQLite to PostgreSQL Migration

DUMB provides a guarded tool for moving an existing supported service from SQLite to DUMB-managed PostgreSQL. Open the service page and select **Database Migration**.

This tool is deliberately separate from `postgres_enabled`. Enabling PostgreSQL directly changes the database used at the next start; it does not copy existing SQLite data.

## Supported services

| Service | SQLite source | PostgreSQL target | Important note |
|---|---|---|---|
| Sonarr | `sonarr.db`, optional `logs.db` | Per-instance main/log databases | Requires Sonarr 4.0.0.615 or newer; Servarr calls migration unsupported |
| Radarr | `radarr.db`, optional `logs.db` | Per-instance main/log databases | Requires Radarr 4.1.0.6133 or newer; Servarr calls migration unsupported |
| Lidarr | `lidarr.db`, optional `logs.db` | Per-instance main/log databases | Requires Lidarr 1.1.2.2890 or newer; upstream guide is community/unsupported |
| Prowlarr | `prowlarr.db`, optional `logs.db` | Per-instance main/log databases | Upstream guide calls migration unsupported |
| Whisparr | `whisparr.db`, optional `logs.db` | Per-instance main/log databases | Follow the same guarded rehearsal and validation rules |
| Bazarr | `/bazarr/data/db/bazarr.db` | `bazarr` by default | The SQLite database must have been upgraded by Bazarr 1.1.5 or newer; timestamp columns require type conversion |
| Pulsarr | `/pulsarr/data/db/pulsarr.db` | `pulsarr` by default | DUMB runs Pulsarr's migration script in staging; migration metadata tables are recreated and are not copied |
| Seerr | `/seerr/config/db/db.sqlite3` | Per-instance database | Migration metadata is recreated by Seerr and is not copied |
| AltMount | Configured `database.path` | `altmount` by default | AltMount supports both providers; DUMB validates the data-only conversion against AltMount's current schema |

Services that use PostgreSQL only, such as MediaStorm, Riven Backend, Zilean, and Traefik Proxy Admin, do not have a SQLite source to migrate. Services without a confirmed PostgreSQL backend are not offered the tool.

## What DUMB automates

The workflow:

1. Confirms that the service is enabled, still configured for SQLite, and has a healthy SQLite source.
2. Verifies PostgreSQL connectivity, database-creation privileges, and storage for staging plus backups.
3. Creates consistent SQLite backups with SQLite's backup API and verifies each copy.
4. Starts the current application briefly against isolated PostgreSQL staging databases so the application creates its own current schema.
5. Imports data into that schema, converts values according to PostgreSQL target types, resets sequences, and compares every imported table's row count.
6. For cutover, clones the validated application schema into the named production databases, imports a fresh cold snapshot, and enables `postgres_enabled` only after validation succeeds.
7. Restores the saved application configuration and SQLite mode automatically if cutover fails.

Jobs and backups remain in the original compatibility location:

```text
/config/arr-postgres-migration/
├── jobs/
└── backups/
```

Existing Sonarr/Radarr job history and rollback backups therefore remain visible after upgrading. DUMB never deletes the source SQLite database.

## Recommended flow

### 1. Run preflight

Open **Database Migration** on the service page and review every check. A failure blocks the job. A warning requires review but may be expected, such as a version that cannot be detected or a target database that already contains data.

The panel shows the latest persisted job for the current service, including its service name and start time. Historical failed or completed jobs remain visible after navigation and restarts; opening a panel or running preflight does not start a migration.

Preflight does not change the service configuration.

### 2. Run a rehearsal

Rehearsal is required before dmbdb enables cutover. It:

- takes a consistent SQLite snapshot;
- briefly stops the application and lets it initialize isolated PostgreSQL staging databases;
- returns the production application to SQLite;
- performs the longer import against staging;
- validates all table counts and selected high-value tables; and
- removes the staging databases.

The schema-bootstrap interruption is normally short. Do not restart DUMB or manually start/stop the service while a job is active.

Closing the migration popup does not cancel an active job. dmbdb asks for confirmation, then keeps a **Database migration running in the background** indicator on the service page with current progress and an **Open progress** action. Reopen the panel at any time to resume the detailed event view. Do not restart the DUMB API or container while the job is active.

When a guarded cutover finishes, the panel displays **Migration completed successfully — PostgreSQL cutover is complete**. If it finishes while the popup is closed, the service page replaces the running indicator with a dismissible completion notice. This confirms that DUMB imported and validated the snapshot and switched the database configuration; still verify service health, application data, and integrations afterward.

When validation succeeds, the panel displays **Rehearsal passed — ready for PostgreSQL cutover** and automatically selects **Cut over to PostgreSQL**. The service is still using SQLite at this point. Review the safeguards, enter the confirmation text again, and click **Start guarded cutover** to perform the actual switch.

### 3. Run guarded cutover

Cutover stops the service, creates a fresh cold backup, resets the named PostgreSQL target databases, imports and validates the snapshot, switches the application configuration, and starts the service when it was running before the job.

Downtime depends mainly on SQLite size and storage speed.

### 4. Validate the application

Check the service's important objects and integrations, then perform a harmless write such as saving an unchanged setting. For an Arr, verify libraries, files, root folders, profiles, indexers, download clients, and history. For Bazarr, verify shows/movies, providers, history, and subtitle searches. For request services, verify users, requests, settings, and integrations.

Keep the SQLite backup until PostgreSQL and its
[backup schedule](../faq/pgadmin.md#example-scheduled-backups-with-pgagent) have
been proven with a test restore.

## Arr log databases are optional

The five Arr services have a separate `logs.db`. Leave **Migrate the service log database too** disabled unless old application log entries matter. The main database already contains application configuration, library state, and history; starting fresh for diagnostic logs shortens cutover.

The option is hidden for Bazarr, Pulsarr, Seerr, and AltMount because they have one migrated SQLite database.

## Rollback behavior

For a completed cutover, the panel can restore the preserved application configuration, set `postgres_enabled: false`, and restart against the untouched SQLite database.

!!! warning "Rollback is not reverse migration"
    Changes written after PostgreSQL cutover are not copied into SQLite. Roll back promptly if validation fails. A later rollback can lose settings, library changes, history, requests, or other PostgreSQL writes.

An active job is marked `interrupted` if the DUMB API restarts. Inspect its backup directory and restore SQLite before retrying.

## PostgreSQL backups after migration

Application-native backups generally do not contain PostgreSQL data. Configure
scheduled `pg_dump` backups for every migrated database by following the
[pgAdmin and pgAgent example](../faq/pgadmin.md#example-scheduled-backups-with-pgagent),
including retention and restore testing. Also protect the mounted data
directory's `postgres` subtree (container path `/data/postgres`, service path
`/postgres_data`) with the normal backup plan.

## Upstream references

- [Sonarr PostgreSQL setup](https://wiki.servarr.com/en/sonarr/postgres-setup)
- [Radarr PostgreSQL setup](https://wiki.servarr.com/radarr/postgres-setup)
- [Lidarr PostgreSQL setup](https://wiki.servarr.com/lidarr/postgres-setup)
- [Prowlarr PostgreSQL setup](https://wiki.servarr.com/prowlarr/postgres-setup)
- [Whisparr PostgreSQL setup](https://wiki.servarr.com/whisparr/postgres-setup)
- [Bazarr PostgreSQL database](https://wiki.bazarr.media/Additional-Configuration/PostgreSQL-Database/)
- [Pulsarr SQLite-to-PostgreSQL migration](https://jamcalli.github.io/Pulsarr/docs/installation/postgres-migration)
- [Seerr database configuration and migration](https://docs.seerr.dev/extending-seerr/database-config/)

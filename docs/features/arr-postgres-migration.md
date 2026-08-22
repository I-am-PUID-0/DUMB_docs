---
title: SQLite to PostgreSQL Migration
description: Rehearse, validate, cut over, and roll back supported DUMB services from SQLite to managed PostgreSQL with persistent backups and job status.
icon: lucide/database-backup
---

# SQLite to PostgreSQL Migration

DUMB provides a guarded tool for moving an existing supported service from SQLite to DUMB-managed PostgreSQL. Open the service page and select **Database Migration**.

This tool is deliberately separate from `postgres_enabled`. For most services,
enabling PostgreSQL directly changes the database used at the next start; it
does not copy existing SQLite data. InfiniDysk additionally blocks a direct
provider switch when an existing main SQLite database is present.

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
| InfiniDysk | Configured main `db.sqlite` | `infinidysk` by default | Migration requires an official stable v1.2.0-or-newer runtime whose source SQLite and staged PostgreSQL schemas exactly match DUMB's supported contract; after cutover, official releases, branches, and exact commits are allowed only at or after the recorded cutover commit; only the main store moves and auxiliary stores remain SQLite |

Services that use PostgreSQL only, such as mediastorm, Riven Backend, Zilean, and Traefik Proxy Admin, do not have a SQLite source to migrate. Services without a confirmed PostgreSQL backend are not offered the tool.

!!! info "InfiniDysk migration is DUMB-managed"

    InfiniDysk v1.2.0+ upstream supports selecting PostgreSQL only for a fresh
    installation and does not provide an in-place `db.sqlite` migration.
    DUMB's guarded workflow is separate. Official v1.2.0 commit
    [`8c960ffc39fc85fdf9166aafd6cb2846878ec3c2`](https://github.com/infinidysk/infinidysk/commit/8c960ffc39fc85fdf9166aafd6cb2846878ec3c2)
    is the audited contract baseline, not a runtime pin. DUMB accepts an
    official stable v1.2.0-or-newer runtime only when the live SQLite database
    and the migration-only staged PostgreSQL database exactly match that
    supported contract. A missing, extra, or changed table, column, index,
    trigger, foreign key, identity, function, or migration-history entry fails
    preflight until DUMB is updated. The workflow requires a successful
    rehearsal, imports and validates only the main store, and switches
    providers only after cutover validation. `metrics.sqlite`, `warden.db`, and
    `usenet-migration.db` remain local SQLite files.

    A successful cutover records the full InfiniDysk commit as the PostgreSQL
    runtime floor. Later official release tags, branch heads, and exact commit
    pins are accepted only when GitHub proves that their resolved commit is the
    recorded cutover commit or one of its descendants. Older, diverged, and
    unverifiable targets fail before DUMB saves the source change or launches
    InfiniDysk.

!!! warning "The cutover commit becomes the minimum InfiniDysk revision"

    The runtime installed when cutover begins becomes the permanent minimum
    revision for that PostgreSQL deployment. DUMB will not install a release,
    branch head, or exact commit that predates or diverges from it. Running an
    older build requires first using the guarded rollback to restore SQLite;
    later PostgreSQL writes are not copied back into the SQLite snapshot.

    If a legacy installation still needs either NzbDAV-to-InfiniDysk identity
    migration or the optional full namespace migration, complete that before
    selecting PostgreSQL or starting the database-migration workflow. DUMB
    blocks every namespace mode once PostgreSQL is selected: the full path
    rewrites the SQLite main store, while an identity rename would disconnect
    guarded rollback job lookup.

## What DUMB automates

The workflow:

1. Confirms that the service is enabled, still configured for SQLite, and has a healthy SQLite source.
2. Verifies PostgreSQL connectivity, database-creation privileges, and storage for staging plus backups.
3. Creates consistent SQLite backups with SQLite's backup API and verifies each copy.
4. Lets the service create its current schema in isolated PostgreSQL staging databases. For InfiniDysk, DUMB runs only the installed v1.2 backend's `--db-migration` maintenance command with an isolated configuration path; it never boots the normal application against staging.
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

!!! warning "Keep an independent backup"

    DUMB's job-specific recovery bundle is not a substitute for a verified
    backup stored outside the managed migration paths. For InfiniDysk, back up
    its complete configuration directory before rehearsal or cutover.

## Recommended flow

### 1. Run preflight

Open **Database Migration** on the service page and review every check. A failure blocks the job. A warning requires review but may be expected, such as a version that cannot be detected or a target database that already contains data.

The panel shows the latest persisted job for the current service, including its service name and start time. Historical failed or completed jobs remain visible after navigation and restarts; opening a panel or running preflight does not start a migration.

Preflight does not change the service configuration.

### 2. Run a rehearsal

Rehearsal is required before dmbdb enables cutover. It:

- takes a consistent SQLite snapshot;
- lets the service initialize isolated PostgreSQL staging databases;
- leaves InfiniDysk on its existing SQLite runtime throughout the rehearsal (a running instance stays running and a stopped instance stays stopped);
- performs the longer import against staging;
- validates all table counts and selected high-value tables; and
- removes the staging databases.

Other supported services may need a short schema-bootstrap interruption. InfiniDysk uses its migration-only maintenance command instead because its normal v1.2 runtime starts background cleanup and integration services. Do not restart DUMB or manually start/stop the service while a job is active.

Closing the migration popup does not cancel an active job. dmbdb asks for confirmation, then keeps a **Database migration running in the background** indicator on the service page with current progress and an **Open progress** action. For InfiniDysk, the 99% `finalizing` stage remains active while DUMB writes the durable PostgreSQL cutover authorization; the indicator and polling remain in place until the backend publishes a terminal result. Reopen the panel at any time to resume the detailed event view. Do not restart the DUMB API or container while the job is active.

When a guarded cutover finishes, the panel displays **Migration completed successfully — PostgreSQL cutover is complete**. If it finishes while the popup is closed, the service page replaces the running indicator with a dismissible completion notice. This confirms that DUMB imported and validated the snapshot and switched the database configuration; still verify service health, application data, and integrations afterward.

When validation succeeds, the panel displays **Rehearsal passed — ready for PostgreSQL cutover** and automatically selects **Cut over to PostgreSQL**. The service is still using SQLite at this point. Review the safeguards, enter the confirmation text again, and click **Start guarded cutover** to perform the actual switch.

### 3. Run guarded cutover

Cutover stops the service, creates a fresh cold backup, resets the named PostgreSQL target databases, imports and validates the snapshot, switches the application configuration, and starts the service when it was running before the job. InfiniDysk cutover is stricter: the SQLite service must already be running with healthy `/health` and `/ready` responses, and DUMB requires the PostgreSQL service to remain healthy after restart before declaring success.

Downtime depends mainly on SQLite size and storage speed.

### 4. Validate the application

Check the service's important objects and integrations, then perform a harmless write such as saving an unchanged setting. For an Arr, verify libraries, files, root folders, profiles, indexers, download clients, and history. For Bazarr, verify shows/movies, providers, history, and subtitle searches. For request services, verify users, requests, settings, and integrations.

For InfiniDysk, verify its UI plus provider, queue, and history state; confirm
WebDAV or rclone access and Arr category/download-client behavior; and test
representative playback and seeking. Confirm `metrics.sqlite`, `warden.db`,
and `usenet-migration.db` remain healthy local files.

Keep the SQLite backup until PostgreSQL and its
[backup schedule](../faq/pgadmin.md#example-scheduled-backups-with-pgagent) have
been proven with a test restore.

## Arr log databases are optional

The five Arr services have a separate `logs.db`. Leave **Migrate the service log database too** disabled unless old application log entries matter. The main database already contains application configuration, library state, and history; starting fresh for diagnostic logs shortens cutover.

The option is hidden for Bazarr, Pulsarr, Seerr, AltMount, and InfiniDysk because they have one migrated main SQLite database.

## Rollback behavior

For a completed cutover, the panel can restore the preserved application configuration, set `postgres_enabled: false`, and restart against the untouched SQLite database.

For InfiniDysk, rollback restores only the preserved main `db.sqlite` state;
the three auxiliary SQLite stores never move. DUMB blocks directly toggling
`postgres_enabled` off after a guarded cutover; use the migration job's
explicit rollback action so the preserved source is validated before restart.

!!! warning "Rollback is not reverse migration"
    Changes written after PostgreSQL cutover are not copied into SQLite. Roll back promptly if validation fails. A later rollback can lose settings, library changes, history, requests, or other PostgreSQL writes.

An active database-migration job is marked `interrupted` if the DUMB API
restarts. Do not toggle `postgres_enabled`, replace `db.sqlite`, or restore the
whole backup bundle manually. Reopen **Database Migration** and use the guarded
rollback action whenever the job exposes it. For InfiniDysk, an interrupted,
failed, or `rollback_failed` result remains visible as a red service-page
recovery banner after the popup closes or the page reloads. The banner reopens
the persisted job and does not disappear merely because background polling
reached a terminal error.

A terminal `rollback_failed` result has two distinct recovery meanings:

- `rollback.retry_safe: true` means DUMB stopped before changing saved data.
  The guarded rollback remains available and may be retried after fixing the
  reported blocker.
- `rollback.retry_safe: false` means rollback had already started changing
  state. DUMB treats this as manual-attention recovery and freezes InfiniDysk
  lifecycle/provider changes. Review the private job evidence and the precise
  failed recovery surface before taking a targeted action; do not blindly
  restore the complete bundle or force the provider toggle.

## PostgreSQL backups after migration

Application-native backups generally do not contain PostgreSQL data. Configure
scheduled `pg_dump` backups for every migrated database by following the
[pgAdmin and pgAgent example](../faq/pgadmin.md#example-scheduled-backups-with-pgagent),
including retention and restore testing. Also protect the mounted data
directory's `postgres` subtree (container path `/data/postgres`, service path
`/postgres_data`) with the normal backup plan.

For InfiniDysk, also retain an independent filesystem backup of its complete
configuration directory so the auxiliary SQLite stores, blobs, `session.key`,
and other local state are protected alongside the PostgreSQL logical backup.

## Upstream references

- [Sonarr PostgreSQL setup](https://wiki.servarr.com/en/sonarr/postgres-setup)
- [Radarr PostgreSQL setup](https://wiki.servarr.com/radarr/postgres-setup)
- [Lidarr PostgreSQL setup](https://wiki.servarr.com/lidarr/postgres-setup)
- [Prowlarr PostgreSQL setup](https://wiki.servarr.com/prowlarr/postgres-setup)
- [Whisparr PostgreSQL setup](https://wiki.servarr.com/whisparr/postgres-setup)
- [Bazarr PostgreSQL database](https://wiki.bazarr.media/Additional-Configuration/PostgreSQL-Database/)
- [Pulsarr SQLite-to-PostgreSQL migration](https://jamcalli.github.io/Pulsarr/docs/installation/postgres-migration)
- [Seerr database configuration and migration](https://docs.seerr.dev/extending-seerr/database-config/)
- [InfiniDysk PostgreSQL guide](https://github.com/infinidysk/infinidysk/blob/main/docs/operations/postgresql.md)
- [InfiniDysk native migration tracking issue #1012](https://github.com/infinidysk/infinidysk/issues/1012)

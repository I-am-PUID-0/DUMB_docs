---
title: Arr SQLite to PostgreSQL Migration
---

# Arr SQLite to PostgreSQL Migration

DUMB provides a guarded migration tool for moving an existing **Sonarr or Radarr** instance from SQLite to DUMB's PostgreSQL service. The tool is available from the instance's service page under **Database Migration**.

This is deliberately separate from `postgres_enabled`. Turning that setting on directly changes the database backend but does not copy existing data.

!!! danger "Servarr considers this unsupported"
    Sonarr and Radarr document SQLite-to-PostgreSQL migration as unsupported and may not assist with failures. DUMB adds backups, rehearsal, validation, and rollback controls, but it cannot turn the migration into an upstream-supported operation.

## What the tool automates

The workflow:

1. Confirms that the instance is enabled, currently uses SQLite, meets the supported version floor, and has healthy SQLite files.
2. Verifies PostgreSQL connectivity, database-creation privileges, and backup space.
3. Creates consistent SQLite backups with SQLite's backup API and verifies the copies.
4. Creates the instance's PostgreSQL main/log databases.
5. Briefly starts the Arr against PostgreSQL when the current binary needs to initialize its schema.
6. Imports data into that Arr-created schema using DUMB's native data-only importer.
7. Resets PostgreSQL sequences dynamically and compares every imported table's row count with SQLite.
8. During cutover, persists `postgres_enabled: true` only after import validation succeeds.
9. Automatically restores the original `config.xml` and SQLite mode if cutover fails.

Job state and backups are stored under:

```text
/config/arr-postgres-migration/
├── jobs/
└── backups/
```

The original SQLite databases are not deleted.

## Recommended flow

### 1. Run preflight

Open the Sonarr or Radarr service page, select **Database Migration**, and review every check. A failed check blocks the job. Warnings require review but may be expected, such as an Arr version that could not be read from its logs or PostgreSQL databases that already contain an initialized schema.

### 2. Run a rehearsal

Rehearsal is the default and is required by dmbdb before it enables cutover.

A rehearsal:

- takes a consistent SQLite snapshot;
- initializes the current Arr PostgreSQL schema in isolated staging databases;
- imports into temporary rehearsal databases;
- validates all table counts and important library counts;
- removes the rehearsal databases; and
- leaves the service using SQLite.

Schema initialization causes a short service interruption. The longer rehearsal import then runs against isolated staging databases while the production instance is back on SQLite.

### 3. Review results

The panel shows the current stage, percentage, detailed event history, imported tables/rows, and important library counts. Do not proceed if the rehearsal fails or automatically rolls back.

### 4. Run guarded cutover

Cutover stops the selected Arr, creates a new cold SQLite backup, resets the named PostgreSQL target databases, imports and validates the fresh snapshot, then switches the instance to PostgreSQL.

Downtime depends primarily on SQLite database size and storage speed. Do not restart DUMB or the Arr during this job.

### 5. Validate the application

After cutover, check:

- series/movies and file counts;
- root folders;
- quality profiles and custom formats;
- indexers and download clients;
- recent history; and
- a harmless write, such as saving an unchanged setting.

Keep the SQLite backup until the PostgreSQL deployment and its backup schedule have been proven.

## Application logs are optional

The main Arr database contains configuration, library state, and history. `logs.db` contains application log entries and can be very large.

Leave **Migrate the Arr log database too** disabled unless old application log entries are important. When disabled, the PostgreSQL log database starts fresh and cutover is faster.

## Rollback behavior

For a completed cutover, the panel can restore the preserved pre-cutover `config.xml`, set `postgres_enabled: false`, and restart the instance against SQLite.

!!! warning "Rollback is not reverse migration"
    Changes made after PostgreSQL cutover are not copied back into SQLite. Roll back promptly if validation fails. A later rollback can lose settings, library changes, history, or other writes made while PostgreSQL was active.

An interrupted job is marked as interrupted after the DUMB API restarts. Inspect the job and restore SQLite before retrying.

## PostgreSQL backups after migration

Sonarr and Radarr built-in backups do not include PostgreSQL data. Configure scheduled `pg_dump` backups for both the main and log databases after cutover. Keep `/postgres_data` protected by normal host/container backups as well.

## Supported scope

The guided importer initially supports:

- Sonarr `4.0.0.615` or newer
- Radarr `4.1.0.6133` or newer
- DUMB-managed PostgreSQL with a role that has `CREATEDB` and superuser privileges

Lidarr, Prowlarr, and Whisparr can use `postgres_enabled`, but the guided migration tool does not migrate their existing SQLite data yet.

Upstream references:

- [Sonarr PostgreSQL setup](https://wiki.servarr.com/en/sonarr/postgres-setup)
- [Radarr PostgreSQL setup](https://wiki.servarr.com/radarr/postgres-setup)

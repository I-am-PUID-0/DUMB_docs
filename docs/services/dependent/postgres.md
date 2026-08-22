---
title: PostgreSQL
icon: lucide/database
---

# PostgreSQL

PostgreSQL is the core database system used by DUMB to store metadata and internal configuration for services like Riven, Zilean, and pgAdmin. 

It is pre-installed and automatically initialized during container startup.

---

## Configuration Settings in `dumb_config.json`
```json
"postgres": {
  "enabled": false,
  "process_name": "PostgreSQL",
  "suppress_logging": false,
  "log_level": "INFO",
  "host": "127.0.0.1",
  "port": 5432,
  "databases": [
    { "name": "postgres", "enabled": true },
    { "name": "pgadmin", "enabled": true },
    { "name": "zilean", "enabled": true },
    { "name": "riven", "enabled": true },
    { "name": "traefik_proxy_admin", "enabled": true }
  ],
  "config_dir": "/postgres_data",
  "config_file": "/postgres_data/postgresql.conf",
  "log_file": "/log/postgres.log",
  "initdb_args": "--data-checksums",
  "user": "DUMB",
  "password": "postgres",
  "shared_buffers": "128MB",
  "max_connections": 100,
  "run_directory": "/run/postgresql",
  "command": "postgres -D {postgres_config_dir} -c config_file={postgres_config_file}",
  "env": {}
},
```

### Configuration Key Descriptions
- **`enabled`**: Whether to start the PostgreSQL service.
- **`process_name`**: The label used in logs and process tracking.
- **`suppress_logging`**: If `true`, disables log output for this service.
- **`log_level`**: Logging verbosity level (e.g., `DEBUG`, `INFO`).
- **`host`**: IP address for PostgreSQL to listen on.
- **`port`**: Port exposed for the PostgreSQL server.
- **`shared_buffers`** – Amount of memory allocated to PostgreSQL.
- **`max_connections`** – Maximum simultaneous database connections.
- **`databases`** – List of databases to initialize, with each entry containing:
    - **`name`** – Name of the database.
    - **`enabled`** – Whether this database should be created.
- **`config_dir`** – Directory where PostgreSQL configuration files are stored.
- **`config_file`** – Path to the primary PostgreSQL configuration file.
- **`log_file`** – Path to the PostgreSQL log file.
- **`initdb_args`** – Additional arguments passed to initdb during database initialization.
- **`user/password`** – Default database credentials.
- **`run_directory`** – Directory where PostgreSQL runtime files (like sockets) are stored.
- **`command`** – The command used to start PostgreSQL.
- **`env`** – Dictionary of environment variables passed to the process.


---

## Access & Credentials
- Default Port: `5432`
- Default User: `DUMB`
- Default Password: `postgres`
- Default Databases:
    - `postgres`
    - `pgadmin`
    - `zilean`
    - `riven`
    - `traefik_proxy_admin`
    - `dumb_metrics` when PostgreSQL is selected under **Metrics → Settings → History Storage**
    - `radarr-main` / `radarr-log` when a Radarr instance has `postgres_enabled: true`
    - `sonarr-main` / `sonarr-log` when a Sonarr instance has `postgres_enabled: true`
    - `lidarr-main` / `lidarr-log` when a Lidarr instance has `postgres_enabled: true`
    - `prowlarr-main` / `prowlarr-log` when a Prowlarr instance has `postgres_enabled: true`
    - `whisparr-main` / `whisparr-log` when a Whisparr instance has `postgres_enabled: true`
    - `bazarr`, `pulsarr`, and `altmount` when those services complete PostgreSQL cutover
    - a per-instance `seerr` database when a Seerr instance completes PostgreSQL cutover
    - `infinidysk` after a fresh InfiniDysk v1.2.0+ PostgreSQL install or a successful guarded schema-compatible cutover

!!! note "Arr PostgreSQL databases"
    DUMB creates the main/log databases and writes the matching Arr `config.xml` entries when `postgres_enabled` is true on a supported Arr instance. SQLite remains the default for new Arr instances, and PostgreSQL is an explicit opt-in.

    In onboarding, enabling `postgres_enabled` on Radarr, Sonarr, Lidarr, Prowlarr, or Whisparr automatically enables and starts PostgreSQL as needed. You do not need to select PostgreSQL separately as an optional service.

!!! info "InfiniDysk: upstream fresh-only, guarded DUMB migration available"

    InfiniDysk v1.2.0 and newer can use DUMB-managed PostgreSQL for the main
    operational database. On a fresh installation, enabling
    `infinidysk.postgres_enabled` registers the configured database (default
    `infinidysk`) and starts PostgreSQL as needed.

    Upstream itself supports PostgreSQL selection only for new installations.
    For an existing SQLite installation, do not toggle the provider directly;
    use **Database Migration** when DUMB advertises `infinidysk`. DUMB's
    separate workflow requires an official stable v1.2.0-or-newer runtime, an
    exact match to DUMB's supported SQLite and staged PostgreSQL database
    contracts, and a successful rehearsal before cutover. Any missing, extra,
    or changed schema object or migration-history entry blocks migration until
    DUMB is updated. The workflow migrates only `db.sqlite`.
    `metrics.sqlite`, `warden.db`, and `usenet-migration.db` remain local. Any
    pending InfiniDysk identity or namespace migration must complete before
    PostgreSQL is selected. See
    [InfiniDysk](../core/infinidysk.md#postgresql-in-infinidysk-v120).

!!! danger "The PostgreSQL toggle is not a migration tool"
    DUMB does not copy existing SQLite data merely because `postgres_enabled`
    is set. For services other than InfiniDysk, directly enabling it
    creates/configures a PostgreSQL database and starts the service against
    that database. InfiniDysk fails closed when an existing main SQLite store
    is present and requires the guided workflow.

    If you switch another existing SQLite-backed service directly, it may start
    against an empty PostgreSQL database and look like a fresh install.

    For Sonarr, Radarr, Lidarr, Prowlarr, Whisparr, Bazarr, Pulsarr, Seerr,
    AltMount, and InfiniDysk, use DUMB's separate
    [guided SQLite-to-PostgreSQL migration tool](../../features/arr-postgres-migration.md).
    Servarr and InfiniDysk upstream-support caveats still apply.

!!! info "AIOStreams is an advanced manual database consumer"

    The initial [AIOStreams](../optional/aiostreams.md) integration defaults to SQLite and has no `postgres_enabled` toggle or DUMB-guided migration. To use PostgreSQL, provision the database first and set the complete top-level `aiostreams.database_uri` before storing configurations. Adding a database to `postgres.databases` creates it on PostgreSQL setup, but it does not copy AIOStreams' existing SQLite records.

!!! warning "No known PostgreSQL-to-SQLite migration"
    DUMB does not reverse-copy PostgreSQL changes into SQLite. Treat PostgreSQL cutover as a long-term database choice unless you are willing to restore the preserved pre-cutover SQLite snapshot and lose later writes.

### Existing SQLite-backed services

For an existing supported service, use PostgreSQL mode only after deciding how to handle its SQLite data:

1. Keep SQLite: leave `postgres_enabled: false`.
2. Start fresh on PostgreSQL where the application supports it: back up the service data/config directory, enable `postgres_enabled`, and accept that the PostgreSQL database starts empty. This is not an existing-InfiniDysk migration path; DUMB blocks that direct switch.
3. Guided migration: open the service page, select **Database Migration**, complete a rehearsal, and review its validation before cutover.

DUMB's guided tool automates consistent SQLite backups, application-owned schema initialization, native data-only import, type conversion, dynamic sequence repair, table-count validation, progress reporting, and configuration rollback for all ten services listed above.

For an existing InfiniDysk SQLite installation, leave `postgres_enabled` off
until a successful guarded cutover enables it. Preserve an independent
configuration-directory backup, then validate the application and configure
a tested PostgreSQL logical backup before retiring the rollback snapshot.

Upstream PostgreSQL setup and migration references:

- [Radarr PostgreSQL setup](https://wiki.servarr.com/radarr/postgres-setup)
- [Sonarr PostgreSQL setup](https://wiki.servarr.com/en/sonarr/postgres-setup)
- [Lidarr PostgreSQL setup](https://wiki.servarr.com/lidarr/postgres-setup)
- [Prowlarr PostgreSQL setup](https://wiki.servarr.com/prowlarr/postgres-setup)
- [Whisparr PostgreSQL setup](https://wiki.servarr.com/whisparr/postgres-setup)
- [Bazarr PostgreSQL database](https://wiki.bazarr.media/Additional-Configuration/PostgreSQL-Database/)
- [Pulsarr PostgreSQL migration](https://jamcalli.github.io/Pulsarr/docs/installation/postgres-migration)
- [Seerr database configuration](https://docs.seerr.dev/extending-seerr/database-config/)
- [InfiniDysk PostgreSQL guide](https://github.com/infinidysk/infinidysk/blob/main/docs/operations/postgresql.md)
- [InfiniDysk native migration tracking issue #1012](https://github.com/infinidysk/infinidysk/issues/1012)

!!! note " Override any of the above using `POSTGRES_USER`, `POSTGRES_PASSWORD`, or `POSTGRES_DB` environment variables."

---

## Data & Config Paths
| Purpose              | Path                      |
|----------------------|---------------------------|
| Data Directory       | `/postgres_data`          |
| Config File          | `/postgres_data/postgresql.conf` |
| Runtime Directory    | `/run/postgresql`         |
| Log File             | `/log/postgres.log`       |

## Backups and restore testing

Persisting `/data/postgres` protects the cluster across container recreation,
but it is not a complete logical backup strategy for a running database. Create
scheduled custom-format `pg_dump` archives for each important database, retain
copies outside the DUMB data filesystem, and periodically restore an archive
into a disposable database.

Follow the [scheduled pgAdmin and pgAgent example](../../faq/pgadmin.md#example-scheduled-backups-with-pgagent)
for a ready-to-use all-database job, global-role backup, retention rotation, and
safe restore test.

---

## Useful Commands

### Run SQL Command Directly (one-liner)
```bash
docker exec -it DUMB psql -U DUMB -d riven -c 'SELECT COUNT(*) FROM media;'
```

### Enter the Container & PostgreSQL Shell
```bash
docker exec -it DUMB /bin/bash
psql -U DUMB -d riven
```

### Drop the Riven Database
!!! warning "This will permanently delete the Riven database. Be sure you’ve backed up anything important."

From the host (one-liner):
```bash
docker exec -it DUMB psql -U DUMB -c 'DROP DATABASE riven;'
```

From inside the container:
```bash
docker exec -it DUMB /bin/bash
psql -U DUMB
DROP DATABASE riven;
```

---

## Tips
- Always restart the container after modifying config files in `/postgres_data`.
- In the maintained Compose layout, `/postgres_data` is mapped by DUMB into `/data/postgres`, so persisting `/data` persists PostgreSQL. A direct `/postgres_data` bind mount is only needed for an intentional legacy/advanced layout.
- [pgAdmin](../optional/pgadmin.md) is the easiest way to visually explore and manage PostgreSQL.

### Pre-existing shared memory block

If an older DUMB process leaves PostgreSQL running inside the same container, the old server may continue owning `/postgres_data` and its original port. Starting another postmaster against that directory produces `pre-existing shared memory block ... is still in use` and a hint to terminate old server processes.

Current DUMB startup reads `postmaster.pid`, verifies that the referenced live process is PostgreSQL for the exact configured data directory, and requests a fast clean `pg_ctl` shutdown before reserving ports. If an older DUMB release already removed the PID file, startup scans PostgreSQL parent command lines and acts only when exactly one process has `-D` pointing to that same canonical data directory. It refuses ambiguous matches. DUMB never blindly removes a live PID file or deletes a shared-memory segment. If the safety check refuses a PID, inspect the complete error and process ownership rather than using `ipcrm`; the refusal means DUMB could not prove that the process was safe to stop.

---

## More Info
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

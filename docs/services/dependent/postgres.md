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
    - `radarr-main` / `radarr-log` when a Radarr instance has `postgres_enabled: true`
    - `sonarr-main` / `sonarr-log` when a Sonarr instance has `postgres_enabled: true`
    - `lidarr-main` / `lidarr-log` when a Lidarr instance has `postgres_enabled: true`
    - `prowlarr-main` / `prowlarr-log` when a Prowlarr instance has `postgres_enabled: true`
    - `whisparr-main` / `whisparr-log` when a Whisparr instance has `postgres_enabled: true`

!!! note "Arr PostgreSQL databases"
    DUMB creates the main/log databases and writes the matching Arr `config.xml` entries when `postgres_enabled` is true on a supported Arr instance. SQLite remains the default for new Arr instances, and PostgreSQL is an explicit opt-in.

    In onboarding, enabling `postgres_enabled` on Radarr, Sonarr, Lidarr, Prowlarr, or Whisparr automatically enables and starts PostgreSQL as needed. You do not need to select PostgreSQL separately as an optional service.

!!! danger "Arr PostgreSQL mode is not a migration tool"
    DUMB does not copy an existing Arr SQLite database into PostgreSQL. Setting `postgres_enabled: true` creates/configures PostgreSQL databases and starts the Arr against them; it does not migrate `radarr.db`, `sonarr.db`, `lidarr.db`, `prowlarr.db`, or `whisparr.db`.

    If you switch an existing SQLite-backed Arr instance without a manual migration, the app may start against empty PostgreSQL databases and look like a fresh install.

    Upstream Servarr migration notes are community/unsupported for the apps that document them. Treat them as advanced manual recovery/migration guidance, not as a DUMB-supported workflow.

!!! warning "No known PostgreSQL-to-SQLite migration"
    There is no known supported migration path from PostgreSQL back to SQLite for supported Arr services. Treat Arr PostgreSQL mode as a long-term database choice unless you are willing to recreate the affected Arr instance from scratch.

### Existing Arr SQLite instances

For existing Arr instances, use PostgreSQL mode only after deciding how you want to handle the existing SQLite data:

1. Keep SQLite: leave `postgres_enabled: false`.
2. Start fresh on PostgreSQL: back up the Arr config directory, enable `postgres_enabled`, and accept that the PostgreSQL databases start empty.
3. Attempt manual migration: back up the Arr config directory and `/postgres_data`, stop the Arr, enable PostgreSQL mode, let the Arr initialize the PostgreSQL schema once, stop the Arr again, then follow that Arr's upstream PostgreSQL migration guide.

DUMB only automates option wiring, database creation, dependency startup, and `config.xml` PostgreSQL entries. It does not run `pgloader`, clean seed tables, reset sequences, validate migrated data, or provide rollback from PostgreSQL to SQLite.

Upstream PostgreSQL setup and migration references:

- [Radarr PostgreSQL setup](https://wiki.servarr.com/radarr/postgres-setup)
- [Sonarr PostgreSQL setup](https://wiki.servarr.com/en/sonarr/postgres-setup)
- [Lidarr PostgreSQL setup](https://wiki.servarr.com/lidarr/postgres-setup)
- [Prowlarr PostgreSQL setup](https://wiki.servarr.com/prowlarr/postgres-setup)
- [Whisparr PostgreSQL setup](https://wiki.servarr.com/whisparr/postgres-setup)

!!! note " Override any of the above using `POSTGRES_USER`, `POSTGRES_PASSWORD`, or `POSTGRES_DB` environment variables."

---

## Data & Config Paths
| Purpose              | Path                      |
|----------------------|---------------------------|
| Data Directory       | `/postgres_data`          |
| Config File          | `/postgres_data/postgresql.conf` |
| Runtime Directory    | `/run/postgresql`         |
| Log File             | `/log/postgres.log`       |

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
- Ensure you mount `/postgres_data` if you want persistent databases.
- [pgAdmin](../optional/pgadmin.md) is the easiest way to visually explore and manage PostgreSQL.

---

## More Info
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

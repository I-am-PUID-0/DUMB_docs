---
title: PostgreSQL FAQ
icon: lucide/database
---

# PostgreSQL FAQ

Below are common questions and explanations related to **PostgreSQL**, which is the primary database engine used by DUMB.

---

## How PostgreSQL is used in DUMB

PostgreSQL stores persistent data for services that require it and for optional SQLite-to-PostgreSQL cutovers. Current integrations include:

- **Riven Backend**, **Zilean**, **Traefik Proxy Admin**, and **MediaStorm**
- Optional PostgreSQL modes for **Sonarr, Radarr, Lidarr, Prowlarr, Whisparr, Bazarr, Pulsarr, Seerr, and AltMount** after a guarded migration
- Optional DUMB Metrics history storage
- **pgAdmin**'s own database when pgAdmin is enabled

Each service has its **own database**, created automatically when DUMB starts:

| Service        | Database Name |
|----------------|----------------|
| Riven          | `riven`        |
| Zilean         | `zilean`       |
| pgAdmin (optional) | `pgadmin`   |
| Traefik Proxy Admin | `traefik_proxy_admin` |
| MediaStorm | `mediastorm` |
| Metrics history (optional default) | `dumb_metrics` |

Additional databases are registered from service configuration. PostgreSQL's internal data directory defaults to `/postgres_data`; the maintained Compose layout persists it at `/data/postgres` through DUMB's managed data mapping.

---

## What happens if I delete the database?

If `/data/postgres` (or a directly mounted legacy `/postgres_data`) is deleted, **every database in that cluster is lost**.

This includes:

- Application data and settings for PostgreSQL-backed services
- Migrated Arr-family databases
- PostgreSQL Metrics history
- pgAdmin state stored in its database

Services may create empty schemas on their next launch, but this does not reconstruct the deleted application data.

!!! warning "A directory copy is not a complete running-database backup strategy"
    Schedule logical `pg_dump` backups for every important database and test restores. Also protect the mounted `/data` tree while the stack is stopped or with a PostgreSQL-aware physical-backup process.

    Follow the [scheduled pg_dump backups with pgAdmin and pgAgent](pgadmin.md#example-scheduled-backups-with-pgagent) example, including its retention and restore-test steps.

---

## Can I reset the database intentionally?

Yes, but deleting the whole cluster resets every PostgreSQL-backed service. For a disposable installation, stop DUMB and remove `/data/postgres` (or your explicitly mounted `/postgres_data`) only after confirming the exact path and preserving any required backups.

Alternatively, use **pgAdmin 4** (if enabled) to drop individual databases manually.

> See the [PostgreSQL Useful Commands](../services/dependent/postgres.md#useful-commands) section.

> Alternatively, see the [pgAdmin FAQ](pgadmin.md#drop-a-database-or-create-a-manual-backup-in-pgadmin) section.

---

## What are the default credentials?

- **Username**: `DUMB`
- **Password**: `postgres`
- **Port**: `5432`
- These values can be customized in the `postgres` section of `dumb_config.json`.

---

## Can I connect to PostgreSQL externally?

Yes — by default, PostgreSQL binds to `127.0.0.1`. If you want to connect from an external app (like DBeaver or pgAdmin on your host machine), you'll need to:

1. Change `host` in the `postgres` section of `dumb_config.json` to `0.0.0.0`
2. Add a port binding (e.g., `5432:5432`) to your container
3. Optionally secure with a firewall or password change

---

## Is it safe to run queries against the databases?

Yes — but with caution. Direct queries using tools like pgAdmin or psql can be useful for debugging or data inspection, but changes may break app logic unless you know what you're doing.

When in doubt, make a backup first!

---

## Related Pages

- [pgAdmin Service Guide](../services/optional/pgadmin.md)
- [Riven Backend](../services/core/riven-backend.md)
- [Zilean](../services/optional/zilean.md)
- [DUMB Configuration](../features/configuration.md)

---
title: PostgreSQL FAQ
---

# PostgreSQL FAQ

Below are common questions and explanations related to **PostgreSQL**, which is the primary database engine used by DMB.

---

## 🗃️ How PostgreSQL is used in DMB

PostgreSQL is used to **store persistent data** for the following services:

- **Riven Backend** – stores indexed content, metadata, scraped results, job states, and user settings.
- **Zilean** – stores hash lookups, metadata cache, and processing history.

Each service has its **own database**, created automatically when DMB starts:

| Service        | Database Name |
|----------------|----------------|
| Riven          | `riven`        |
| Zilean         | `zilean`       |
| pgAdmin (optional) | `pgadmin`   |

The database storage path is configured using the `postgres_data` path in `dmb_config.json`, defaulting to `/postgres_data`.

---

## ❗ What happens if I delete the database?

If the PostgreSQL volume or `/postgres_data` directory is deleted, **all data for Riven and Zilean will be lost**.

This includes:

- Indexed or scraped content in Riven
- Cached metadata and hashes in Zilean
- Any custom settings stored in the database

Both services will start fresh and **reinitialize their databases** upon next launch.

!!! warning "Accidental deletion of `postgres_data` is not recoverable"
    Make sure to regularly back up your `postgres_data` directory if long-term retention is important.

    See the [pgAdmin service](pgadmin.md#-example-scheduled-backups-with-pgagent) for details on scheduling backups of the PostgreSQL databases. 

---

## 🔁 Can I reset the database intentionally?

Yes — stopping the stack, deleting the `postgres_data` directory, and starting again will reset everything.

Alternatively, use **pgAdmin 4** (if enabled) to drop individual databases manually.

> See the [PostgreSQL Useful Commands](../services/postgres.md/#-useful-commands) section.

> Alternatively, See the [pgAdmin FAQ](pgadmin.md/#-drop-a-database-or-create-a-manual-backup-in-pgadmin) section.

---

## 🔐 What are the default credentials?

- **Username**: `DMB`
- **Password**: `postgres`
- **Port**: `5432`
- These values can be customized in the `postgres` section of `dmb_config.json`.

---

## 💻 Can I connect to PostgreSQL externally?

Yes — by default, PostgreSQL binds to `127.0.0.1`. If you want to connect from an external app (like DBeaver or pgAdmin on your host machine), you'll need to:

1. Change `host` in the `postgres` section of `dmb_config.json` to `0.0.0.0`
2. Add a port binding (e.g., `5432:5432`) to your container
3. Optionally secure with a firewall or password change

---

## 🧪 Is it safe to run queries against the databases?

Yes — but with caution. Direct queries using tools like pgAdmin or psql can be useful for debugging or data inspection, but changes may break app logic unless you know what you're doing.

When in doubt, make a backup first!

---

## 📎 Related Pages

- [pgAdmin Service Guide](../services/pgadmin.md)
- [Riven Backend](../services/riven-backend.md)
- [Zilean](../services/zilean.md)
- [DMB Configuration](../features/configuration.md)

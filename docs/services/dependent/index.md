---
 title: Dependent Services Overview
---

# Dependent Services

Dependent services are essential building blocks required by one or more core services to operate correctly. These services do not perform media automation on their own but provide critical functionality like mounting, database storage, or metadata enrichment.

---

## ⚙️ What Are Dependent Services?

A service is considered **dependent** if:

* It must be running before a core service can start successfully
* It provides a shared capability such as metadata, storage, or content mounting

---

## 🧱 Dependent Service Index

| Service                                    | Description                                         | Required By                               |
| ------------------------------------------ | --------------------------------------------------- | ----------------------------------------- |
| [CLI Battery](../dependent/cli-battery.md) | Metadata and Trakt integration layer for CLI Debrid | CLI Debrid                                |
| [Phalanx DB](../dependent/phalanx-db.md)   | Distributed metadata store for CLI Debrid           | CLI Debrid (optional but often used)      |
| [PostgreSQL](../dependent/postgres.md)     | Central database used by Riven, Zilean, pgAdmin     | Riven, Zilean, pgAdmin                    |
| [rclone](../dependent/rclone.md)           | Mounts Debrid cloud storage via WebDAV              | CLI Debrid, Riven, Decypharr, Plex Debrid |
| [Zurg](../dependent/zurg.md)               | Debrid-backed WebDAV provider for use with rclone   | CLI Debrid, Riven, Plex Debrid            |

---

## 🔗 How They Work

Dependent services act as building blocks — either providing runtime resources or exposing interfaces used by core services.

For example:

* **[CLI Battery](../dependent/cli-battery.md)** must start before CLI Debrid or scraping will fail.
* **[PostgreSQL](../dependent/postgres.md)** must start before Riven, Zilean, or pgAdmin 
* **[rclone](../dependent/rclone.md)** must be active to expose the debrid content as a mounted file system to facilitate symlink creation or raw file use.
* **[Zurg](../dependent/zurg.md)** must run if rclone is configured to use its WebDAV endpoint.

---

## 🧠 Tips

* These services are typically auto-launched when their associated core service starts
* Avoid disabling them manually unless you're sure the core service won't need them
* Check logs for startup dependency errors if a core service fails to launch

---

## 📚 Related Pages

* [Core Services](../core/index.md)
* [Optional Services](../optional/index.md)
* [How Services Work Together](../index.md#-how-the-services-work-together)

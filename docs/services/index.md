---

## title: Services Overview

# Services Overview

DMB is composed of multiple services that work together to provide a complete automated media management system. Each service can be configured, updated, and monitored independently, and serves a specific function within the DMB ecosystem.

Below is a summary of the available services:

---

## 🧩 How the Services Work Together

DMB is built as a collection of microservices, each fulfilling a specific role in the pipeline:

1. **User Interaction**

    - 🖥️ **DMB Frontend** provides a graphical interface for managing all services.

2. **API & Coordination**

    * 🔌 **DMB API** acts as a centralized endpoint for frontend communication and coordinating actions between services.

3. **Metadata Management & Discovery**

    * 🧠 **Riven Backend** searches and indexes content, initiates downloads, and maintains integration with media platforms (Trakt, Overseerr, Plex).
    * 🧲 **CLI Debrid** automates discovery, upgrading, content management, and maintains integration with media platforms (Trakt, Overseerr, Plex).
    * 🎨 **Riven Frontend** interfaces directly with the backend to manage searches, downloads, and settings.

    !!! note "See the [Riven Wiki](https://rivenmedia.github.io/wiki/) and [CLI Debrid GitHub](https://github.com/godver3/cli_debrid) for more details"

4. **Metadata Caching**

    * 🔋 **CLI Battery** provides local metadata storage and Trakt integration, caching frequently accessed metadata.
    * 🌐 **Phalanx DB** offers an optional decentralized metadata store powered by Hyperswarm.
    * 🧠 **Zilean** caches metadata (e.g., hashes, content names) and serves repeated requests to reduce lookup time for indexed content.

    !!! note "See the [Zilean Wiki](https://ipromknight.github.io/zilean/getting-started.html) and [CLI Debrid GitHub](https://github.com/godver3/cli_debrid) for more details "

5. **Content Acquisition**

    * ⚡ **Zurg** interfaces with Real-Debrid to manage content on the debrid service.

6. **Cloud Storage Mounting**

    * ☁️ **rclone** mounts debrid storage (via WebDAV or similar) inside the container, making downloaded content available to other services.

7. **Persistent Storage and Management**

    * 🗃️ **PostgreSQL** provides the primary database layer for Zilean, Riven, and pgAdmin.
    * 📊 **pgAdmin 4** gives users a web-based interface for inspecting and managing PostgreSQL.

## 🧱 Core Service Summaries

### 🔌 DMB API

Coordinates service startup and exposes FastAPI endpoints.

- Default Port: `8000`
- Logs: `/log`

---

### 🖥️ DMB Frontend

User interface for managing service state, logs, and updates.

- Default Port: `3005`

---

### 📊 pgAdmin 4

Database admin UI connected to DMB's PostgreSQL backend.

- Port: `5050`
- Data Dir: `/pgadmin/data`

---

### 🗃️ PostgreSQL

Primary database for Riven, Zilean, and pgAdmin.

* Port: `5432`
* Databases: `postgres`, `pgadmin`, `zilean`, `riven`

---

### ☁️ rclone

Mounts Real-Debrid or cloud storage via WebDAV.

* Mount Dir: `/data`
* Config Dir: `/config`

---

### 🧠 Riven Backend

Handles scraping, symlinking, and service integrations.

* Port: `8080`
* Config: `/riven/backend/data/settings.json`

---

### 🎨 Riven Frontend

UI for monitoring and controlling the Riven backend.

* Port: `3000`

---

### 🧠 Zilean

Caches hashes and metadata to improve scraper efficiency.

* Port: `8182`
* Config: `/zilean/app/data/settings.json`

---

### ⚡ Zurg

Fetches and repairs Real-Debrid links. Supports multi-instance mode.

* Port: `9090`
* Config: `/zurg/RD/config.yml`

---

### 🧲 CLI Debrid

Searches, downloads, and upgrades media from Debrid services.

* Port: `5000`
* Config: `/cli_debrid/data/config/config.json`

---

### 🔋 CLI Battery

Metadata caching and Trakt integration backend for CLI Debrid.

* Port: `5001`
* Config: `/cli_debrid/data/config/settings.json`

---

### 🌐 Phalanx DB

Optional distributed metadata backend using Hyperswarm.

* Port: `8888`
* Config Dir: `/phalanx_db`

---

## 📎 Next Steps

Click on any of the service names in the sidebar or below to explore how to configure and use them:

* [DMB API](api.md)
* [DMB Frontend](dmb-frontend.md)
* [pgAdmin 4](pgadmin.md)
* [PostgreSQL](postgres.md)
* [rclone](rclone.md)
* [Riven Backend](riven-backend.md)
* [Riven Frontend](riven-frontend.md)
* [Zilean](zilean.md)
* [Zurg](zurg.md)
* [CLI Debrid](cli-debrid.md)
* [CLI Battery](cli-battery.md)
* [Phalanx DB](phalanx-db.md)

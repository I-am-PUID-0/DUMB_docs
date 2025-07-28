---
title: Services Overview
---

# Services Overview

DUMB is composed of multiple services that work together to provide a complete automated media management system. Services are categorized into:

* [DUMB Services](../services/dumb/index.md): Required for system orchestration and user interaction
* [Core Services](../services/core/index.md): Manage Debrid content orchestration or media playback
* [Dependent Services](../services/dependent/index.md): Required by one or more core services to function
* [Optional Services](../services/optional/index.md): Enhance or simplify workflows but are not required

---

## 🧹 How the Services Work Together

DUMB is built as a collection of microservices that communicate over internal APIs and shared paths. Below is an example flow:

1. **Platform Infrastructure**

    * 🔐 **DUMB API** coordinates and manages all service interactions
    * 🗃️ **DUMB Frontend** provides the web interface for managing and viewing services

2. **Debrid Orchestration & Content Management**

    * 🧠 **Riven Backend**, 🧲 **CLI Debrid**, 🚁 **Plex Debrid**, and 🌐 **Decypharr** each serve as a Debrid orchestrator: requesting, managing, and monitoring content acquisition workflows
    * These core services integrate with providers like Trakt, Overseerr, and Debrid APIs to manage what content gets fetched

3. **Media Playback**

    * 🎥 **Plex** is the core service that hosts and serves collected content to users
        * It relies on symlinked or mounted content made available through rclone/Zurg from the other core services

4. **Storage & Retrieval**

    * 📁 **rclone** mounts remote Debrid storage for local access
    * ⚡ **Zurg** provides WebDAV access to debrid downloads

5. **Metadata & Caching**

    * 🛢 **CLI Battery** and 🌐 **Phalanx DB** serve as local or distributed metadata stores
    * 🛢 **Zilean** caches metadata and exposes a Torznab-compatible indexer for scraping optimization

6. **Database Layer**

    * 📂 **PostgreSQL** stores metadata for Riven, Zilean, and pgAdmin
    * 📊 **pgAdmin** is a GUI for exploring PostgreSQL databases

---

## 🧱 Quick Reference

| Service                                                  | Type      | Key Role                                                  |
| -------------------------------------------------------- | --------- | --------------------------------------------------------- |
| [DUMB API](../services/dumb/index.md)                    | DUMB      | Centralized orchestration                                 |
| [DUMB Frontend](../services/dumb/index.md)               | DUMB      | Web-based control panel                                   |
| [Riven Backend](../services/core/riven-backend.md)       | Core      | Debrid orchestrator (searching, scraping, automation)     |
| [CLI Debrid](../services/core/cli-debrid.md)             | Core      | Debrid orchestrator (list scanning, upgrades, Plex watch) |
| [Plex Debrid](../services/core/plex-debrid.md)           | Core      | Debrid orchestrator (direct scraping and playback prep)   |
| [Decypharr](../services/core/decypharr.md)               | Core      | Debrid orchestrator for Arrs via torrent API integration  |
| [Plex](../services/core/plex-media-server.md)            | Core      | Media server for hosting and playing content              |
| [rclone](../services/dependent/rclone.md)                | Dependent | Mount Debrid storage                                      |
| [Zurg](../services/dependent/zurg.md)                    | Dependent | Serve Debrid content via WebDAV                           |
| [PostgreSQL](../services/dependent/postgres.md)          | Dependent | Persistent metadata database                              |
| [CLI Battery](../services/dependent/cli-battery.md)      | Dependent | Metadata service for CLI Debrid                           |
| [Phalanx DB](../services/dependent/phalanx-db.md)        | Dependent | Distributed metadata storage                              |
| [Zilean](../services/optional/zilean.md)                 | Optional  | Metadata cache and scraping backend                       |
| [pgAdmin](../services/optional/pgadmin.md)               | Optional  | PostgreSQL GUI                                            |
| [Riven Frontend](../services/optional/riven-frontend.md) | Optional  | UI for Riven Backend                                      |

---

## 🧠 Tips

* Use the onboarding UI to enable only the services you need
* Services will auto-start in dependency order
* Logs and errors can be viewed in the DUMB Frontend

---

## 📚 Service Categories

* [DUMB Services](../services/dumb/index.md)
* [Core Services](../services/core/index.md)
* [Dependent Services](../services/dependent/index.md)
* [Optional Services](../services/optional/index.md)

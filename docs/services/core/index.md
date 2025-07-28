---
title: Core Services Overview
---

# Core Services

Core services in DUMB are essential building blocks that handle media automation, storage, metadata processing, and orchestration. These services often rely on **dependent services** to operate fully and may optionally integrate with additional utilities for enhanced functionality.

---

## 📦 What Are Core Services?

Core services are the services that:

* Drive a major part of the media pipeline (e.g., indexing, downloading, symlinking, organization, hosting, playback, etc. )
* May require one or more **dependent services** to function

!!!note "You can use as many core services simultaneously as you like"
---

## 🧱 Core Service Index

| Service                             | Description                                          | Depends On                        | Optional Integrations        |
| ----------------------------------- | ---------------------------------------------------- | --------------------------------- | ---------------------------- |
| [CLI Debrid](cli-debrid.md)         | Debrid media scraper, automation engine, and upgrade engine              | CLI Battery, Phalanx DB, rclone, Zurg  | Zilean                  |
| [Decypharr](decypharr.md)           | Debrid-native torrent client for use with the arrs (Sonarr/Radarr) to create symlinks to debrid content | rclone                            | Zilean, Sonarr, Radarr        |
| [Plex](plex-media-server.md)        | Hosts media collected by core services               |                                   |                              |
| [Plex Debrid](plex-debrid.md)       | Debrid media scraper and automation engine           | rclone, Zurg                      | Zilean                       |
| [Riven Backend](riven-backend.md)   | Debrid media scraper and automation engine           | PostgreSQL, rclone, Zurg          | Zilean, Riven Frontend       |

---

## 🔗 Dependency Guidelines

If you enable a core service, be sure to also:

* Review optional integrations to maximize capabilities
* Use the onboarding flow in the DUMB Frontend for auto-detection and guided setup 

---

## 🚀 Example Workflows

### [CLI Debrid](cli-debrid.md) 

* **Requires:** [CLI Battery](../dependent/cli-battery.md), [Phalanx DB](../dependent/phalanx-db.md), [rclone](../dependent/rclone.md), and [Zurg](../dependent/zurg.md)
* **Optionally Uses:** [Zilean](../optional/zilean.md) (as a scraper)
* **Outputs:** Clean symlinks for Plex/Emby/Jellyfin and/or monitors Plex library for collected media

### [Decypharr](decypharr.md)

* **Requires:** [rclone](../dependent/rclone.md)
* **Optionally Uses:** [Zilean](../optional/zilean.md) (as a scraper via the arrs)
* **Outputs:** Symlinks automatically managed and organized by the arrs (Sonarr/Radarr)

### [Plex](plex-media-server.md)

* **Requires:** Content to already exist in `/mnt/debrid`
* **Does Not Scrape** or collect — serves media fetched by others

### [Plex Debrid](plex-debrid.md)

* **Requires:** [rclone](../dependent/rclone.md), and [Zurg](../dependent/zurg.md)
* **Optionally Uses:** [Zilean](../optional/zilean.md) (as a scraper)
* **Outputs:** Raw files from debrid for Plex/Emby/Jellyfin

### [Riven Backend](riven-backend.md)

* **Requires:** [PostgreSQL](../dependent/postgres.md), [rclone](../dependent/rclone.md), and [Zurg](../dependent/zurg.md)
* **Optionally Uses:** [Zilean](../optional/zilean.md) (as a scraper)
* **Outputs:** Clean symlinks for Plex/Emby/Jellyfin

---

## 🧠 Tips

* Use `process_name` in `dumb_config.json` to identify each service clearly in logs and the UI
* Onboarding will automatically add required dependencies for the Core services selected
* Dependent services will start automatically when their core service is launched

---

## 📚 Related Pages

* [Dependent Services](../dependent/index.md)
* [Optional Services](../optional/index.md)
* [How Services Work Together](../index.md#-how-the-services-work-together)

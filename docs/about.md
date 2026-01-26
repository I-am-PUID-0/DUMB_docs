---

title: About
icon: lucide/info
hide:
  - navigation

---

## About DUMB (Debrid Unlimited Media Bridge)

**Debrid Unlimited Media Bridge (DUMB)** is an all-in-one, containerized platform for managing and automating media workflows using premium debrid services (like Real-Debrid) and Usenet. Whether you're looking to automate downloads, organize libraries, mount remote content, or just reduce manual steps, DUMB aims to unify it all into a seamless experience.

---

## Mission

DUMB was created with a single goal:

**Bridge the gap between debrid or Usenet services and traditional media server ecosystems like Plex, Jellyfin, and Emby — with maximum automation and minimal configuration.**

By directly integrating the **media server itself** (e.g. Plex) within the DUMB container, the platform overcomes long-standing issues like broken bind mount propagation, sync delays, and external scan conflicts common in multi-container setups.

---

## What Makes DUMB Unique?

Unlike other solutions that focus on one piece of the puzzle, **DUMB integrates every step** of the media pipeline:

*  *Embedded media servers* — Plex, Jellyfin, and Emby run inside the same container, ensuring seamless access to mounted content and full internal control
*  *Service coordination* — via the internal DUMB API and real-time config management
*  *Automated acquisition* — with core services for discovery and orchestrators like Riven, CLI Debrid, Decypharr, and NzbDAV
*  *Cloud storage mounting* — through rclone mounts direct to debrid (e.g., Real-Debrid WebDAV) or utilizing Zurg's WebDAV
*  *Arr automation* — Sonarr, Radarr, Lidarr, and Whisparr handle queues, renaming, and library organization
*  *Library management* — using symlinks, metadata enrichment, and optional server updates
*  *Metadata caching* — with Zilean to reduce latency and boost scraping efficiency
*  *Visual control* — via the DUMB Frontend for onboarding, live logs, settings, and monitoring

All services are configured through a centralized file (`dumb_config.json`) and can be dynamically updated at runtime via the DUMB Frontend.

!!! info "Combined workflows"

    You can attach a single Arr instance to multiple workflows by setting
    `core_service` to a list (for example `["decypharr", "nzbdav"]`). When combined,
    DUMB switches Arr root folders to `/mnt/debrid/combined_symlinks/<slug>`.

---

## Architecture at a Glance

DUMB is built using a **modular, microservices** architecture, with the following components:

| Service                  | Description                                                                                  |
| ------------------------ | -------------------------------------------------------------------------------------------- |
| **DUMB API**             | Core controller and coordination hub                                                         |
| **DUMB Frontend**        | Graphical interface for managing services, configs, and logs                                 |
| **Plex Media Server**    | First-class embedded media server for direct playback of collected content                   |
| **Riven**                | Debrid content orchestration (Plex, Trakt, Seerr, lists)                                     |
| **CLI Debrid**           | Debrid content orchestration (lists, watchlists, upgrades)                                   |
| **Decypharr**            | Debrid workflow for Arr download clients and symlink libraries                               |
| **NzbDAV**               | Usenet WebDAV gateway and Arr download-client integration                                    |
| **Prowlarr**             | Indexer management and sync to Arr services                                                  |
| **Sonarr/Radarr/Lidarr/Whisparr** | Arr automation for movies, TV, music, and adult content                             |
| **Huntarr**              | Backlog search automation and quality upgrades                                               |
| **Zurg**                 | Handles Real-Debrid content interaction, file repair, and directory structuring              |
| **rclone**               | Mounts cloud storage into the local container for access by your media server                |
| **Zilean**               | Caches metadata and file hash lookups for performance                                        |
| **PostgreSQL / pgAdmin** | Internal databases and optional management UI                                                |

You can explore how these services connect in the [Services Overview](services/index.md) page.

---

## Community-Driven Development

DUMB is fully open-source and **community-powered**. While development is led by a single maintainer, contributions of all kinds are welcome — not just code!

You can help by:

* ⭐ Starring the [GitHub repo](https://github.com/I-am-PUID-0/DUMB)
*  Boosting or participating in the [Discord community](https://discord.gg/8dqKUBtbp5)
*  Submitting feedback, bug reports, or pull requests
*  Helping others with questions or documentation improvements
*  Sponsoring the Dev through [GitHub Sponsors](https://github.com/sponsors/I-am-PUID-0)

See the [Contributing Guide](contributing.md) for more details.

---

## Learn More

*  [Getting Started](getting-started/index.md)
*  [Deployment Options](deployment/index.md)
*  [Service Configuration](services/index.md)
*  [Features](features/index.md)

---

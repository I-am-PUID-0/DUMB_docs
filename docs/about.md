---
title: About
hide:
  - navigation
---

## 📦 About DUMB (Debrid Unlimited Media Bridge)

**Debrid Unlimited Media Bridge (DUMB)** is an all-in-one, containerized platform for managing and automating media workflows using premium debrid services like Real-Debrid. Whether you're looking to automate downloads, organize libraries, mount remote content, or just reduce manual steps — DUMB aims to unify it all into a seamless experience.

---

## 🎯 Mission

DUMB was created with a single goal:

**Bridge the gap between cloud-based debrid services and traditional media server ecosystems like Plex, Jellyfin, and Emby — with maximum automation and minimal configuration.**

---

## 🧩 What Makes DUMB Unique?

Unlike other solutions that focus on one piece of the puzzle, **DUMB integrates every step** of the media pipeline:

- 🔌 *Service Coordination* — via the internal DUMB API and real-time config management  
- 📥 *Automated Acquisition* — with Riven for discovery and Zurg for debrid content fetching  
- ☁️ *Cloud Storage Mounting* — through rclone mounts (e.g., Real-Debrid WebDAV)  
- 🔁 *Library Management* — using symlinks, metadata enrichment, and optional server updates  
- 📊 *Metadata Caching* — with Zilean to reduce latency and boost scraping efficiency  
- 🧠 *Visual Control* — via the DUMB Frontend for live logs, settings, and monitoring

All services are configured through a centralized file (`dumb_config.json`) and can be dynamically updated at runtime via the DUMB Frontend.

---

## 🛠️ Architecture at a Glance

DUMB is built using a **modular, microservices** architecture, with the following components:

| Service          | Description |
|------------------|-------------|
| **DUMB API**       | Core controller and coordination hub |
| **DUMB Frontend**  | Graphical interface for managing services, configs, and logs |
| **Riven**         | Content search, acquisition, and integration with platforms like Plex, Trakt, Overseerr, etc |
| **CLI Debrid**    | Content search, acquisition, and integration with platforms like Plex, Trakt, Overseerr, etc |
| **Decypharr**     | Content search, acquisition, and integration with platforms like Plex, Trakt, Overseerr, etc |
| **Zurg**          | Handles Real-Debrid content interaction, file repair, and directory structuring |
| **rclone**        | Mounts cloud storage into the local container for access by your media server |
| **Zilean**        | Caches metadata and file hash lookups for performance |
| **PostgreSQL / pgAdmin** | Internal databases and optional management UI |

You can explore how these services connect in the [Services Overview](services/index.md) page.

---

## 👥 Community-Driven Development

DUMB is fully open-source and **community-powered**. While development is led by a single maintainer, contributions of all kinds are welcome — not just code!

You can help by:

- ⭐ Starring the [GitHub repo](https://github.com/I-am-PUID-0/DUMB)
- 💬 Boosting or participating in the [Discord community](https://discord.gg/8dqKUBtbp5)
- 🛠️ Submitting feedback, bug reports, or pull requests
- 🧠 Helping others with questions or documentation improvements
- 💵 Sponsoring the Dev through [GitHub Sponsors](https://github.com/sponsors/I-am-PUID-0)



See the [Contributing Guide](contributing.md) for more details.

---

## 📚 Learn More

- 🔧 [Getting Started](getting-started/index.md)
- 🚀 [Deployment Options](deployment/index.md)
- 🧩 [Service Configuration](services/index.md)
- 🤖 [Features](features/index.md)

---

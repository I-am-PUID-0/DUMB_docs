---
title: About
hide:
  - navigation
---

## 📦 About DMB (Debrid Media Bridge)

**Debrid Media Bridge (DMB)** is an all-in-one, containerized platform for managing and automating media workflows using premium debrid services like Real-Debrid. Whether you're looking to automate downloads, organize libraries, mount remote content, or just reduce manual steps — DMB aims to unify it all into a seamless experience.

---

## 🎯 Mission

DMB was created with a single goal:

**Bridge the gap between cloud-based debrid services and traditional media server ecosystems like Plex, Jellyfin, and Emby — with maximum automation and minimal configuration.**

---

## 🧩 What Makes DMB Unique?

Unlike other solutions that focus on one piece of the puzzle, **DMB integrates every step** of the media pipeline:

- 🔌 *Service Coordination* — via the internal DMB API and real-time config management  
- 📥 *Automated Acquisition* — with Riven for discovery and Zurg for debrid content fetching  
- ☁️ *Cloud Storage Mounting* — through rclone mounts (e.g., Real-Debrid WebDAV)  
- 🔁 *Library Management* — using symlinks, metadata enrichment, and optional server updates  
- 📊 *Metadata Caching* — with Zilean to reduce latency and boost scraping efficiency  
- 🧠 *Visual Control* — via the DMB Frontend for live logs, settings, and monitoring

All services are configured through a centralized file (`dmb_config.json`) and can be dynamically updated at runtime via the DMB Frontend.

---

## 🛠️ Architecture at a Glance

DMB is built using a **modular, microservices** architecture, with the following components:

| Service          | Description |
|------------------|-------------|
| **DMB API**       | Core controller and coordination hub |
| **DMB Frontend**  | Graphical interface for managing services, configs, and logs |
| **Riven**         | Content search, acquisition, and integration with platforms like Plex, Trakt, and Overseerr |
| **Zurg**          | Handles Real-Debrid content interaction, file repair, and directory structuring |
| **rclone**        | Mounts cloud storage into the local container for access by your media server |
| **Zilean**        | Caches metadata and file hash lookups for performance |
| **PostgreSQL / pgAdmin** | Internal databases and optional management UI |

You can explore how these services connect in the [Services Overview](services/index.md) page.

---

## 👥 Community-Driven Development

DMB is fully open-source and **community-powered**. While development is led by a single maintainer, contributions of all kinds are welcome — not just code!

You can help by:

- ⭐ Starring the [GitHub repo](https://github.com/I-am-PUID-0/DMB)
- 💬 Boosting or participating in the [Discord community](https://discord.gg/8dqKUBtbp5)
- 🛠️ Submitting feedback, bug reports, or pull requests
- 🧠 Helping others with questions or documentation improvements

!!! note "DMB does **not** accept donations — but your support and involvement are deeply appreciated!"

See the [Contributing Guide](contributing.md) for more details.

---

## 📚 Learn More

- 🔧 [Getting Started](getting-started/index.md)
- 🚀 [Deployment Options](deployment/index.md)
- 🧩 [Service Configuration](services/index.md)
- 🤖 [Features](features/index.md)

---

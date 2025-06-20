---
title: Introduction
---

# 🚀 Getting Started with DMB

Welcome to **DMB – Debrid Media Bridge**: a unified media management and automation tool designed for users who want to streamline their content discovery, acquisition, and playback using services like **Plex**, **Real-Debrid**, **Trakt**, **Overseerr**, and more.

---

## 🔍 What Is DMB?

DMB combines multiple backend services into a single containerized system to provide:

- 🔎 **Search and discovery** using Trakt, Plex Watchlists, Overseerr, etc.
- ⚡ **Real-Debrid integration** for content fetching via Zurg
- ☁️ **Remote mounting** of Debrid storage using rclone
- 🧠 **Metadata caching** with Zilean
- 📦 **Automated download orchestration** with Riven
- 📊 **Web-based dashboards** for control and monitoring

---

## 🧩 Is This for You?

DMB is ideal if you:

- Have a Plex, Jellyfin, or Emby or server and want to auto-fill your library from your Overseerr/Jellyseerr, Trakt, Plex Watchlists, Mdblist, or Listrr
- Want a plug-and-play solution that works with Debrid services
- Prefer a containerized, modular deployment
- Want real-time log viewing, auto-updates, and one-click service control
- Don't want or know how to manually configure and deploy all the incorporated [Services](../services/index.md)

---

## 🖼️ Architecture at a Glance

![DMB Flow Diagram](../assets/images/under_construction.png)

!!! note  "For details on each service, visit the [Services Overview](../services/index.md)."

---

## 🛠️ System Requirements

- 🐳 Docker or a compatible runtime
- ⚙️ Linux (recommended) or Windows (WSL)
- 🔒 Real-Debrid
- 🎞️ A running Plex, Jellyfin, or Emby Server (if used for integration)

---

## ⏭️ What Next?

1. Head to [Installation](installation.md) to get ready.
2. Choose your platform in [Deployment](../deployment/index.md)
3. Learn about [Features](../features/index.md), [Services](../services/index.md), and [Configuration](../features/configuration.md)
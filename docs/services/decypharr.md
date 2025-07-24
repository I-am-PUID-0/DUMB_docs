# Decypharr Setup Guide

Decypharr is a self-hosted, open-source torrent client with integrated support for multiple Debrid services. It provides a familiar interface for torrent management that mimics Qbittorrent, while offering native compatibility with Sonarr, Radarr, and other \*Arr applications. Written in Go, it includes powerful tools for automation, organization, and repair.

---

## 💡 What is Decypharr?

Decypharr combines the power of Qbittorrent with the flexibility of Debrid services to streamline your media automation workflow. It provides a mock Qbittorrent API that can be consumed by Sonarr, Radarr, Lidarr, and similar apps, making it a drop-in replacement for torrent clients.

### Key Features

* ✅ Mock Qbittorrent API for Sonarr, Radarr, Lidarr, etc.
* 🖥 Full-featured UI for managing torrents
* 🌐 Proxy filtering for un-cached Debrid torrents
* 🔁 Multiple Debrid service support (Real Debrid, Torbox, Debrid Link, All Debrid)
* 📂 WebDAV server per Debrid provider for mounting remote files
* 🔧 Repair Worker for missing files or symlinks

---

## 📦 Integration with DUMB

To successfully run Decypharr with DUMB, the following configuration and mounting steps must be completed:

### 1. Bind Mount Setup

In both your `DUMB` and `arrs` docker-compose files, include the following bind mounts (replace `...` with the full host path to your DUMB bind mount):

**DUMB Compose**:

```yaml
tmpfs:
  - .../DUMB/mnt/debrid:/mnt/debrid:rshared
```

**Arrs Compose (Sonarr/Radarr)**:

```yaml
volumes:
  - .../DUMB/mnt/debrid:/mnt/debrid:rslave
```

> These mounts are required to ensure Decypharr-created symlinks are visible to the Arr containers.

### 2. Configure Root Folders in Arrs

Inside the Sonarr and Radarr web UI:

* Navigate to **Settings > Media Management > Root Folders**
* Add the following paths:

  * **Radarr**: `/mnt/debrid/decypharr_symlinks/movies`
  * **Sonarr**: `/mnt/debrid/decypharr_symlinks/shows`

> These directories are managed by Decypharr and must be used for proper operation.

### 3. Connect Decypharr to Arrs

Follow the [official usage guide](https://sirrobot01.github.io/decypharr/usage/#connecting-to-sonarrradarr) for step-by-step instructions on connecting your Radarr and Sonarr instances to Decypharr.

> This includes setting the correct API keys and ensuring URL paths match the container environments.

### 4. Plex Library Setup

In Plex, add the Decypharr symlink folders as library sources:

* **Movies Library**: `/mnt/debrid/decypharr_symlinks/movies`
* **TV Shows Library**: `/mnt/debrid/decypharr_symlinks/shows`

> This ensures Plex indexes files processed and renamed by Decypharr, enabling clean and consistent playback.

---

## 🧠 How It Works

Decypharr acts as both a torrent manager and a renaming/organizing engine:

* Handles torrent links via Debrid services
* Mimics Qbittorrent API for seamless \*Arr integration
* Renames and organizes files into structured symlink folders
* Provides a Web UI and WebDAV endpoints for remote management
* Ensures all changes propagate cleanly between containers using `rshared`/`rslave`

---

## 🛠️ Troubleshooting Tips

* Ensure the bind mounts are correct and both containers see the same `/mnt/debrid` structure
* Make sure Decypharr has permission to write to and create symlinks in the target directory
* If media doesn't appear in Plex, check that the symlink folders are scanned and indexed
* Use `docker inspect` to verify correct mount propagation between DUMB and Arrs

---

## 🌐 Supported Debrid Providers

* [Real Debrid](https://real-debrid.com)
* [Torbox](https://www.torbox.net)
* [Debrid Link](https://debrid-link.fr)
* [All Debrid](https://alldebrid.com)

---

## 🔗 Resources

* [Decypharr GitHub](https://github.com/sirrobot01/decypharr)
* [Decypharr Docs](https://sirrobot01.github.io/decypharr/)

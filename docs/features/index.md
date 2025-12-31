---
title: Features Overview
---

# Features Overview

## What is DUMB?

DUMB (Debrid Unlimited Media Bridge) is an all-in-one media management solution designed to streamline the process of **finding, downloading, organizing, and streaming media content**. It integrates multiple services into a **single Docker image**, providing automation and efficiency for managing media libraries.

### Key Features

* **Unified Deployment** – Combines multiple tools into a single, easy-to-deploy system with onboarding-driven setup.
* **Built-In Media Server Integration** – Includes **Plex Media Server, Jellyfin, and Emby**, fully embedded in the container to eliminate mount propagation issues.
* **Automated Content Management** – Uses **Debrid** and **Usenet** services alongside **Plex Discover Watchlists**, **Trakt lists**, and **Seerr** to automate media retrieval.
* **Arr + WebDAV Workflows** – Supports **Sonarr, Radarr, Lidarr, Whisparr**, plus WebDAV-driven clients like **Decypharr** (Debrid) and **NzbDAV** (Usenet).
* **Integrated Web UI** – Control and manage services through a simple **web-based interface**.
* **Modular Design** – Each service (Riven, Zurg, Zilean, etc.) is independently configurable and upgradable.
* **Advanced Logging & Monitoring** – View and filter service logs directly from the [DUMB Frontend](../services/dumb/dumb-frontend.md).

## Core Components

DUMB integrates the following projects to create a seamless media experience:

### **Riven**

[Riven](https://github.com/rivenmedia/riven) is one of multiple options responsible for content management, handling **search queries, downloading, and organizing media** for streaming.

### **CLI Debrid**

[CLI Debrid](https://github.com/godver3/cli_debrid) is one of multiple options responsible for content management, handling **search queries, downloading, and organizing media** for streaming.

### **Decypharr**

[Decypharr](https://github.com/sirrobot01/decypharr) is a Debrid-focused option responsible for content management, handling **search queries, downloading, and organizing media** for streaming.

### **NzbDAV**

[NzbDAV](https://github.com/nzbdav-dev/nzbdav) provides an **NZB WebDAV gateway** and Arr download-client integration for **Usenet** workflows.

### **Prowlarr**

[Prowlarr](https://prowlarr.com/) centralizes **indexer management** and syncs indexers across the Arr stack.

### **Arrs (Sonarr/Radarr/Lidarr/Whisparr)**

The Arrs handle **TV, movies, music, and adult content** automation and organization. During onboarding, selecting Decypharr or NzbDAV can wire Arr instances automatically.

### **Zurg**

[Zurg](https://github.com/debridmediamanager/zurg-testing) acts as the automation engine that interacts with **Real-Debrid** to fetch media files.

### **Zilean**

[Zilean](https://github.com/iPromKnight/zilean) enhances content discovery and caching, optimizing the efficiency of media lookups.

### **rclone**

[rclone](https://github.com/rclone/rclone) manages cloud storage connections and allows **mounting remote debrid storage** as if it were a local drive.

### **Plex Media Server**

[Plex](https://www.plex.tv/) is bundled directly inside DUMB, providing internal access to rclone-mounted content without needing to expose paths via external bind mounts.

### **Jellyfin** & **Emby**

[Jellyfin](https://jellyfin.org/) and [Emby](https://emby.media/) are alternative media servers supported inside the same container.

### **PostgreSQL** & **pgAdmin 4**

* **PostgreSQL** serves as the **primary database** for storing metadata, configurations, and user preferences.
* **pgAdmin 4** provides a **web-based database management interface**, making it easy to manage PostgreSQL.

## How Does It Work?

DUMB simplifies the media management workflow by:

1. **Run Onboarding** to select core services and auto-enable required dependencies.
2. **Scan Lists & Requests** from Plex, Trakt, and Seerr.
3. **Fetch From Debrid or Usenet** providers (Real-Debrid, AllDebrid, etc.).
4. **Route Through Orchestrators** (Riven/CLI Debrid) or **Arr clients** (Decypharr/NzbDAV).
5. **Mount & Organize Content** via Zurg + rclone and Arr-managed libraries.
6. **Stream via Plex/Jellyfin/Emby** using internal paths and embedded media servers.

## Next Steps

Explore the [Configuration](../features/configuration.md) section to understand how to set up and customize DUMB according to your needs.

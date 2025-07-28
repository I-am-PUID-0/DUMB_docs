---
title: Features Overview
---

# Features Overview

## 🚀 What is DUMB?

DUMB (Debrid Unlimited Media Bridge) is an all-in-one media management solution designed to streamline the process of **finding, downloading, organizing, and streaming media content**. It integrates multiple services into a **single Docker image**, providing automation and efficiency for managing media libraries.

### 🔑 Key Features

* **Unified Deployment** – Combines multiple tools into a single, easy-to-deploy system.
* **Built-In Media Server Integration** – Includes **Plex Media Server** (with future support for Jellyfin/Emby), fully embedded in the container to eliminate mount propagation issues.
* **Automated Content Management** – Uses **Debrid Services**, **Plex Discover Watchlists**, **Trakt lists**, and **Overseerr** to automate media retrieval.
* **Integrated Web UI** – Control and manage services through a simple **web-based interface**.
* **Modular Design** – Each service (Riven, Zurg, Zilean, etc.) is independently configurable and upgradable.
* **Advanced Logging & Monitoring** – View and filter service logs directly from the [DUMB Frontend](../services/dumb/dumb-frontend.md).

## 🛠️ Core Components

DUMB integrates the following projects to create a seamless media experience:

### 🎞️ **Riven**

[Riven](https://github.com/rivenmedia/riven) is one of multiple options responsible for content management, handling **search queries, downloading, and organizing media** for streaming.

### 🎞️ **CLI Debrid**

[CLI Debrid](https://github.com/godver3/cli_debrid) is one of multiple options responsible for content management, handling **search queries, downloading, and organizing media** for streaming.

### 🎞️ **Decypharr**

[Decypharr](https://github.com/sirrobot01/decypharr) is one of multiple options responsible for content management, handling **search queries, downloading, and organizing media** for streaming.

### 🤖 **Zurg**

[Zurg](https://github.com/debridmediamanager/zurg-testing) acts as the automation engine that interacts with **Real-Debrid** to fetch media files.

### 🗂️ **Zilean**

[Zilean](https://github.com/iPromKnight/zilean) enhances content discovery and caching, optimizing the efficiency of media lookups.

### ☁️ **rclone**

[rclone](https://github.com/rclone/rclone) manages cloud storage connections and allows **mounting remote debrid storage** as if it were a local drive.

### 🖥️ **Plex Media Server**

[Plex](https://www.plex.tv/) is bundled directly inside DUMB, providing internal access to rclone-mounted content without needing to expose paths via external bind mounts.

### 🗃️ **PostgreSQL** & **pgAdmin 4**

* **PostgreSQL** serves as the **primary database** for storing metadata, configurations, and user preferences.
* **pgAdmin 4** provides a **web-based database management interface**, making it easy to manage PostgreSQL.

## 🔍 How Does It Work?

DUMB simplifies the media management workflow by:

1. **Scanning User Watchlists** (Plex, Trakt, Overseerr, etc.).
2. **Fetching Media from Debrid Services** (Real-Debrid, AllDebrid, etc.).
3. **Downloading & Organizing Content** using Zurg & Riven.
4. **Providing a Web Interface** for monitoring & controlling downloads.
5. **Allowing Streaming via Plex** using internal access to rclone-mounted media.

## 📌 Next Steps

Explore the [Configuration](../features/configuration.md) section to understand how to set up and customize DUMB according to your needs.

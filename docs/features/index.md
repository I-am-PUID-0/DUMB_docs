---
title: Features Overview
icon: lucide/list
---

# Features Overview

## What is DUMB?

DUMB (Debrid Unlimited Media Bridge) is an all-in-one media management solution designed to streamline the process of **finding, downloading, organizing, and streaming media content**. It integrates multiple services into a **single Docker image**, providing automation and efficiency for managing media libraries.

### Key Features

* **Unified Deployment** – Combines multiple tools into a single, easy-to-deploy system with onboarding-driven setup.
* **Built-In Media Server Integration** – Includes **Plex Media Server, Jellyfin, and Emby**, fully embedded in the container to eliminate mount propagation issues.
* **Automated Content Management** – Uses **Debrid** and **Usenet** services alongside **Plex Discover Watchlists**, **Trakt lists**, and **Seerr** to automate media retrieval.
* **Arr + WebDAV Workflows** – Supports **Sonarr, Radarr, Lidarr, Whisparr**, plus WebDAV-driven clients like **Decypharr** (Debrid and Usenet), **NzbDAV**, and **AltMount**.
* **NeutArr automation** – Core backlog-search automation to fill missing content and upgrade quality.
* **Pulsarr watchlist automation** – Optional Plex watchlist request flow that can route requests into Sonarr and Radarr.
* **[Seerr Sync](seerr-sync.md)** – One-way request replication from a primary Seerr to subordinate instances for multi-household or multi-stack setups.
* **Integrated Web UI** – Control and manage services through a simple **web-based interface** with embedded service UIs.
* **Traefik access layer** – DUMB-managed embedded UI routes, optional Traefik Proxy Admin user routes, and optional Cloudflared tunnel ingress all share the bundled Traefik entrypoint while keeping ownership boundaries clear.
* **[Authentication](authentication.md)** – Optional JWT-based security with user management and session handling.
* **[Auto-update](auto-update.md)** – Keep services current with automatic updates from GitHub releases, nightly builds, or specific branches.
* **[Symlink Operations](symlinks.md)** – End-to-end guide for repair, migration, backup/restore, scheduled snapshots, and path-transition playbooks.
* **Modular Design** – Each service (Riven, Zurg, Zilean, etc.) is independently configurable and upgradable.
* **Advanced Logging & Monitoring** – View and filter service logs directly from the [DUMB Frontend](../services/dumb/dumb-frontend.md).
* **[FFprobe monitor](ffprobe-monitor.md)** – Background worker that detects and unsticks ffprobe scans in Sonarr/Radarr.
* **Real-Time Metrics** – Monitor CPU, memory, disk, and network usage with WebSocket-powered live updates.
* **[AI Assistant](ai-assistant.md)** – Optional local or cloud model diagnostics using redacted logs, service config, and dependency context.

## Component Groups

DUMB integrates the following projects and service families to create a complete media experience:

### **DUMB platform**

- **DUMB API** coordinates configuration, service lifecycle, logs, metrics, health checks, updates, onboarding, and backend automation.
- **DUMB Frontend (dmbdb)** provides the dashboard, onboarding wizard, service pages, embedded UI tabs, logs, metrics, and configuration editors.

### **Workflow engines**

- **Riven Backend** and **CLI Debrid** provide Debrid-oriented orchestration for searching, collecting, and organizing media.
- **Decypharr** supports Debrid, native Usenet, and hybrid Arr workflows with torrent/Sabnzbd-compatible endpoints and symlink libraries.
- **NzbDAV** provides an NZB WebDAV gateway and Arr download-client integration for Usenet workflows.
- **AltMount** provides an alternate Usenet workflow with WebDAV access, SABnzbd-compatible behavior, metadata storage, and optional rclone mount management.

### **Arr automation**

- **Sonarr**, **Radarr**, **Lidarr**, and **Whisparr** manage media queues, imports, renaming, and library organization.
- **Prowlarr** centralizes indexer management and syncs indexers to Arr instances.
- **NeutArr** handles missing-content and quality-upgrade searches across selected Arr instances.
- **Profilarr** syncs profiles, custom formats, regex patterns, and media-management settings for Sonarr/Radarr.

During onboarding, selecting Decypharr, NzbDAV, AltMount, or combinations of them can wire Arr instances automatically. DUMB uses `core_service` to keep those integrations scoped to the intended workflow.

### **Requests and watchlists**

- **Seerr** provides a request and discovery portal that can feed Sonarr/Radarr.
- **Pulsarr** monitors Plex watchlists and routes requests to Sonarr and Radarr when Plex is the request front door.
- Plex Discover watchlists, Trakt, MDBList, and similar list sources can feed supported workflow engines.

### **Media servers**

- **Plex Media Server** is bundled directly inside DUMB, giving it internal access to mounted and symlinked media without extra host bind-mount gymnastics.
- **Jellyfin** and **Emby** are alternative embedded media servers for the same internal-library model.

### **Storage, metadata, and databases**

- **rclone** mounts remote Debrid or WebDAV-backed storage into the container.
- **Zurg** provides WebDAV access to Debrid content for workflows that use it.
- **Zilean** caches metadata and hash lookups to improve scraping performance.
- **PostgreSQL**, **pgAdmin 4**, **Phalanx DB**, and **CLI Battery** support database, metadata, and administration workflows.

### **Access and proxying**

- **Traefik** serves DUMB-owned embedded service UI routes under `/service/ui/<service>`.
- **Traefik Proxy Admin** manages user-created LAN or public host routes through Traefik without overwriting DUMB's embedded UI routes.
- **Cloudflared** forwards Cloudflare Tunnel traffic to DUMB Traefik without direct router port forwarding.

## How Does It Work?

DUMB simplifies the media management workflow by:

1. **Run Onboarding** to select core services and auto-enable required dependencies.
2. **Scan Lists & Requests** from Plex, Trakt, and Seerr.
3. **Fetch From Debrid or Usenet** providers (Real-Debrid, AllDebrid, etc.).
4. **Route Through Orchestrators** (Riven/CLI Debrid) or **Arr clients** (Decypharr/NzbDAV/AltMount).
5. **Mount & Organize Content** via Zurg + rclone and Arr-managed libraries.
6. **Stream via Plex/Jellyfin/Emby** using internal paths and embedded media servers.
7. **Access Safely** through DUMB embedded UI routes, TPA-managed hostnames, or Cloudflare Tunnel routes that all terminate at DUMB Traefik.

## Next Steps

Explore the [Configuration](../features/configuration.md) section to understand how to set up and customize DUMB according to your needs.

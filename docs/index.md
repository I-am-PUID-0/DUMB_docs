---
title: Debrid Unlimited Media Bridge
icon: lucide/home
hide:
  - navigation
  - toc
---

<div class="md-hero hero-card" markdown>

<div class="hero-container" markdown>
<a href="https://github.com/I-am-PUID-0/DUMB">
  <picture>
    <img
      class="hero"
      alt="DUMB"
      src="assets/images/DUMB.png"
    >
  </picture>
</a>

<div class="hero-text" markdown>
<h1>DUMB - A Unified Media Solution</h1>

**DUMB** is an all-in-one media management and streaming solution that integrates multiple services into a single Docker image for streamlined deployment. Automate discovery, downloads, and library organization using Debrid and Usenet services, Plex Discover Watchlists, Trakt lists, Seerr, and more.

<div class="hero-actions" markdown>
[:octicons-arrow-right-24: Deployment Guide](deployment/index.md){ .md-button .md-button--primary }
[:material-sitemap: Architecture](architecture/index.md){ .md-button }
</div>
</div>
</div>
</div>

<div class="badges-container" style="display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin: 2em 0;">
  <a href="https://github.com/I-am-PUID-0/DUMB/stargazers">
    <img
      alt="GitHub Repo stars"
      src="https://img.shields.io/github/stars/I-am-PUID-0/DUMB?style=for-the-badge"
    />
  </a>
  <a href="https://github.com/I-am-PUID-0/DUMB/issues">
    <img
      alt="Issues"
      src="https://img.shields.io/github/issues/I-am-PUID-0/DUMB?style=for-the-badge"
    />
  </a>
  <a href="https://github.com/I-am-PUID-0/DUMB/blob/master/LICENSE">
    <img
      alt="License"
      src="https://img.shields.io/github/license/I-am-PUID-0/DUMB?style=for-the-badge"
    />
  </a>
  <a href="https://github.com/I-am-PUID-0/DUMB/graphs/contributors">
    <img
      alt="Contributors"
      src="https://img.shields.io/github/contributors/I-am-PUID-0/DUMB?style=for-the-badge"
    />
  </a>
  <a href="https://hub.docker.com/r/iampuid0/dumb">
    <img
      alt="Docker Pulls"
      src="https://img.shields.io/docker/pulls/iampuid0/dumb?style=for-the-badge&logo=docker&logoColor=white"
    />
  </a>
  <a href="https://discord.gg/8dqKUBtbp5">
    <img
      alt="Join Discord"
      src="https://img.shields.io/badge/Join%20us%20on%20Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white"
    />
  </a>
</div>

<div class="grid cards" markdown>

- ## :material-rocket-launch:{ .lg .middle } Quick Start
  Get DUMB up and running in minutes with Docker, Portainer, Unraid, or other platforms.

- ## :material-puzzle:{ .lg .middle } Unified Platform
  All your favorite media services in one container. Plex, Jellyfin, Emby, Sonarr, Radarr, and more—pre-configured and ready to use.

- ## :material-cog:{ .lg .middle } Automated Workflows
  Connect Debrid and Usenet services, Trakt lists, and Plex Discover watchlists. DUMB auto-wires the stack from onboarding to streaming.

- ## :material-auto-fix:{ .lg .middle } Guided Onboarding
  Step-by-step setup for core services, optional tools, credentials, and embedded UIs. Start with sane defaults, then refine later.

- ## :material-monitor-share:{ .lg .middle } Embedded UIs
  Use Traefik to unify service UIs under one endpoint and manage everything from the DUMB dashboard.

- ## :material-chart-line:{ .lg .middle } Live Metrics
  Track CPU, memory, disk, and network usage in real time with WebSocket-powered updates.

- ## :material-shield-lock:{ .lg .middle } Authentication
  Optional JWT auth with user management to secure the UI and API.

- ## :material-update:{ .lg .middle } Auto-Update
  Keep services current with scheduled updates or pinned versions.

- ## :material-refresh:{ .lg .middle } Auto-Restart
  Health checks and backoff restarts keep services resilient.

</div>

## What's Included

DUMB integrates a comprehensive ecosystem of media management tools:

**Media Servers**: Plex Media Server, Jellyfin, Emby  
**Orchestrators**: Riven, CLI Debrid, Plex Debrid, Decypharr, NzbDAV  
**Automation**: Sonarr, Radarr, Lidarr, Prowlarr, Whisparr, Huntarr  
**Storage & Caching**: Zurg, rclone  
**Monitoring & Tools**: Tautulli, Zilean, Seerr  
**Database**: PostgreSQL, pgAdmin 4, Phalanx DB

All services work together seamlessly with Plex Discover Watchlists, Trakt lists, Seerr, and more to streamline media discovery and access.

---

Ready to get started? Check out the [Deployment Guide](deployment/index.md) or explore the [Features](features/index.md), [Services](services/index.md), and [Reference](reference/index.md) documentation.

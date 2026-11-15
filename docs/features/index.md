---
title: Features Overview
description: Explore DUMB features for Debrid and Usenet automation, Arr apps, media servers, guided onboarding, monitoring, notifications, and embedded UIs.
icon: lucide/list
---

# Features

Choose a task to find its controls, configuration, and recovery steps. For a list of applications, use the [service catalog](../services/index.md).

## Set up and connect services

| Task | Guide |
| --- | --- |
| Change ports, paths, credentials, or service settings | [Configuration](configuration.md) |
| Run and inspect individual services | [Everyday use](usage.md) |
| Open an application's own interface | [Embedded service UIs](embedded-ui.md) |
| Require login or connect an identity provider | [Authentication](authentication.md) |
| Mirror requests to another media stack | [Seerr Sync](seerr-sync.md) |

## Keep the stack running

| Task | Guide |
| --- | --- |
| Understand startup order and readiness | [Startup lifecycle](startup-lifecycle.md) |
| Restart a failed application automatically | [Auto-restart](auto-restart.md) |
| Review, schedule, or pin service updates | [Auto-update](auto-update.md) |
| Reuse verified downloads and recover a failed update | [Install cache and safe updates](install-cache.md) |
| Guard media libraries during storage outages | [Media Library Protection](media-library-protection.md) |
| Deliver health and operation alerts | [Notifications](notifications.md) |

## Protect and move data

| Task | Guide |
| --- | --- |
| Repair paths, move symlink libraries, or restore a snapshot | [Symlink operations](symlinks.md) |
| Rehearse a supported SQLite-to-PostgreSQL conversion | [Database migration](arr-postgres-migration.md) |
| Reset one service or remove its managed files | [Service reset and removal](service-reset.md) |

## Investigate performance and failures

| Task | Guide |
| --- | --- |
| Inspect CPU, memory, storage, networks, and database pressure | [Metrics](metrics.md) |
| Compare bounded rclone streaming profiles | [Rclone Streaming Optimizer](rclone-optimizer.md) |
| Investigate a stuck Sonarr/Radarr ffprobe | [FFprobe monitor](ffprobe-monitor.md) |
| Ask a model to help interpret selected, redacted evidence | [AI Assistant](ai-assistant.md) |

<!-- dev:start -->
## Development additions

- [Setup checklist and automation](setup-checklist.md) retains missing inputs, verified connections, and manual work.
- [Backup storage](backup-storage.md) registers mounted archive destinations.
- [Installation backup and restore](installation-backups.md) protects managed installation state.
- [InfiniDysk 2 installation and upgrade](infinidysk-v2-migration.md) handles the native generation separately from 1.x.
<!-- dev:end -->

Features appear in the dashboard only when the connected DUMB API supports them. A newer frontend cannot add a missing backend capability. Each guide calls out additional prerequisites and actions that still need your decision.

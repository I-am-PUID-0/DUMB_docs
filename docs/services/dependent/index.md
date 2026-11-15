---
title: Dependent Services Overview
description: Find the databases, WebDAV mounts, and metadata services required by selected DUMB workflows, including layout-dependent CLI Battery startup.
icon: lucide/box
---

# Dependent services

These services provide databases, mounted files, or metadata to another application. The dependencies you need depend on that application's configuration and installed layout.

## Dependent Service Index

| Service                                    | Description                                         | Required By                               |
| ------------------------------------------ | --------------------------------------------------- | ----------------------------------------- |
| [CLI Battery](../dependent/cli-battery.md) | Standalone metadata and Trakt layer for stable/older CLI Debrid releases | CLI Debrid layouts that still use the standalone service |
| [Phalanx DB](../dependent/phalanx-db.md)   | Distributed metadata store for CLI Debrid           | CLI Debrid (optional but often used)      |
| [PostgreSQL](../dependent/postgres.md)     | Shared database engine for required and optional service backends | Riven, Zilean, pgAdmin, TPA, mediastorm, migrated services, optional Metrics history |
| [rclone](../dependent/rclone.md)           | Mounts Debrid/Usenet WebDAV storage                  | CLI Debrid, stable Riven, InfiniDysk, Decypharr external-rclone mode |
| [Zurg](../dependent/zurg.md)               | Debrid-backed WebDAV provider for use with rclone   | CLI Debrid, Riven            |

---

## How they work

| Dependency | Startup requirement |
|---|---|
<!-- dev:start -->
| [CLI Battery](cli-battery.md) | Runs before CLI Debrid only when its installed layout needs the standalone API. DUMB skips the managed Battery process for a recognized embedded layout. |
<!-- dev:end -->
<!-- release:start -->
| [CLI Battery](cli-battery.md) | Runs before a CLI Debrid installation that uses its standalone API. If testing an upstream embedded layout, review the [release-specific guidance](../../faq/cli-debrid.md). |
<!-- release:end -->

| [PostgreSQL](postgres.md) | Starts before applications configured to use its managed databases. |
| [rclone](rclone.md) | Makes a configured WebDAV source available as local files. The source service must be ready first. |
| [Zurg](zurg.md) | Exposes Debrid content to an rclone instance configured to use Zurg. |

A disabled dependency can prevent its consumer from becoming ready even if the consumer's own process starts. Check both logs when diagnosing startup failures.

## Related pages

- [Core services](../core/index.md)
- [Optional services](../optional/index.md)
- [Startup lifecycle](../../features/startup-lifecycle.md)

---
title: Riven FAQ
description: Understand Riven backend and frontend dependencies, branch-mode mounts, PostgreSQL persistence, connection failures, and safe symlink moves.
icon: lucide/database
---

# Riven FAQ

## Do I need both Riven Backend and Riven Frontend?

For browser-based setup, select both. **Riven Backend** performs acquisition and library work; **Riven Frontend → Embedded UI → Settings** lets you configure it. Starting the frontend alone does not provide a working Riven stack. The backend can also be managed without this frontend using its API, which is an advanced alternative.

## What changes in branch mode?

<details class="geek-details" markdown="1">
<summary>Geek details: branch-mode runtime and mount differences</summary>

The current branch layout uses Python 3.13 and Riven's native filesystem/debrid-link settings. DUMB removes the legacy Zurg/rclone runtime dependencies for a branch-enabled backend and points both the filesystem mount and updater library path at `/mnt/debrid/riven`. Stable/release-mode Riven retains the legacy Zurg/rclone dependency model.

</details>

## Is PostgreSQL required?

Yes. DUMB enables PostgreSQL for Riven, creates the required database, and starts it before the backend. In the maintained volume layout, PostgreSQL's internal `/postgres_data` path is persisted through `/data/postgres`.

## Where is Riven state stored?

- Backend settings/data: `/riven/backend/data` (persisted below `/data/riven`)
- Symlink library: `/mnt/debrid/riven_symlinks`
- Backend log collected by DUMB: `/log/riven_backend.log`

Back up both `/data` and any irreplaceable symlink-library state before a migration or rollback.

## Why can the frontend not reach the backend?

Confirm both services are running, PostgreSQL is healthy, and the frontend's configured backend/origin URL matches the backend's assigned port. Riven and InfiniDysk share desired defaults (`3000` and `8080`), so use the ports saved in the runtime DUMB configuration after conflict resolution.

## How should I move an existing Riven symlink tree?

Use DUMB's Symlinks panel to create a snapshot, preview the rewrite/root migration, and then apply it. A manual rollback restores link entries but cannot merge application/database changes made after a migration.

## Related pages

- [Riven Backend](../services/core/riven-backend.md)
- [Riven Frontend](../services/optional/riven-frontend.md)
- [PostgreSQL](../services/dependent/postgres.md)
- [Symlink Operations](../features/symlinks.md)

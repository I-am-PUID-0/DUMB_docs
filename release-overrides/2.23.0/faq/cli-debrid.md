---
title: CLI Debrid FAQ
description: Resolve CLI Debrid dependency, Battery layout, HTTP 423, update, and symlink questions, with separate guidance for released and development DUMB.
icon: lucide/terminal
---

# CLI Debrid FAQ

**Visual guide:** [Follow CLI Debrid's setup and library workflow](../services/core/cli-debrid.md).

## What does DUMB start with CLI Debrid?

The stable/older CLI Debrid workflow includes standalone CLI Battery and Phalanx
DB, plus the selected Zurg/rclone provider path. DUMB creates and orders those
dependencies during onboarding. The v0.7.29+ pre-release exception is described
below.

## Does CLI Debrid v0.7.29 still need a separate CLI Battery process?

Not in that upstream pre-release architecture. The
[v0.7.29 pre-release](https://github.com/godver3/cli_debrid/releases/tag/v0.7.29)
includes a
[CLI Battery rewrite](https://github.com/godver3/cli_debrid/commit/ef4deb5bbed60826ef2aaa48be0ecb17250ea87e)
that imports Battery as an in-process Python module instead of running its Flask
service on port `5001`.

<!-- dev:start -->
DUMB inspects the installed CLI Debrid files. For a recognized embedded layout it removes the managed standalone Battery dependency and skips that separate process, even if its saved toggle remains enabled. Older layouts that still provide `cli_battery/main.py` need the standalone service. A missing entrypoint alone does not prove the embedded layout; an unrecognized installation needs repair.
<!-- dev:end -->
<!-- release:start -->
DUMB 2.23.0 still uses the standalone Battery dependency. If you deliberately install an upstream layout with the in-process rewrite, disable the standalone Battery service and review whether onboarding or **Start Core Service** re-enables it. The release backend does not provide the newer installed-layout detection.
<!-- release:end -->

## Why is CLI Battery on a separate port?

A standalone Battery service is separate from the CLI Debrid interface. DUMB configures the connection automatically, so you should not need to edit its port just to use CLI Debrid.

<details class="geek-details" markdown="1">
<summary>Geek details: standalone Battery ports and embedded layouts</summary>

In the standalone/stable integration, CLI Debrid's UI defaults to `5000` and CLI
Battery defaults to `5001`. During setup DUMB writes
`cli_debrid.env.CLI_DEBRID_BATTERY_PORT` from the actual `cli_battery.port`,
including any dynamically reassigned port. The upstream v0.7.29 pre-release
removes this separate network hop.

</details>

## Why do I see HTTP 423 responses?

CLI Battery uses `423 Locked` while a resource is deliberately unavailable or still being prepared. For a standalone layout, confirm CLI Battery and Phalanx are running. Open their service cards and select **Service Logs**, where available; inspect CLI Debrid's logs too. Review the layout note above if Battery is integrated. Do not change ports or delete data merely because a request returns 423.

## Where are its persistent files and symlinks?

- Application data inside the container: `/cli_debrid/data` (persisted below `/data/cli_debrid` in the maintained layout)
- Curated library root: `/mnt/debrid/clid_symlinks`
- DUMB log: `/cli_debrid/data/logs/debug.log`

The raw provider mount path and the curated symlink root serve different purposes; point Arr/media-library imports at the curated root expected by your workflow.

## How should I change symlink layouts?

Use the service page's **Symlinks** tools for a dry run, snapshot, retarget, copy, or root migration. Do not bulk-edit link targets first. See [Symlink Operations](../features/symlinks.md).

## How do I troubleshoot a failed update?

Check the CLI Debrid update status and service logs, then verify the selected release/branch still exists. DUMB preserves `/cli_debrid/data` while replacing application code. Use **Override + install** only when you intentionally want DUMB to reinstall the configured target.

## Related pages

- [CLI Debrid service guide](../services/core/cli-debrid.md)
- [CLI Battery](../services/dependent/cli-battery.md)
- [Phalanx DB](../services/dependent/phalanx-db.md)
- [Auto-update](../features/auto-update.md)

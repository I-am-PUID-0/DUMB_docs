---
title: CLI Debrid FAQ
icon: lucide/terminal
---

# CLI Debrid FAQ

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

DUMB's current configuration still declares CLI Battery as a static dependency.
For stable/older CLI Debrid releases, keep it enabled. If you intentionally use
v0.7.29 or a newer pre-release containing the in-process rewrite, manually
disable the standalone CLI Battery service; its old `cli_battery/main.py` command
is no longer the required runtime.

Normal container startup respects the disabled toggle. The current guided
**Start Core Service** and onboarding flows may re-enable CLI Battery because
their dependency model is not yet version-aware, so verify the toggle afterward.

## Why is CLI Battery on a separate port?

In the standalone/stable integration, CLI Debrid's UI defaults to `5000` and CLI
Battery defaults to `5001`. During setup DUMB writes
`cli_debrid.env.CLI_DEBRID_BATTERY_PORT` from the actual `cli_battery.port`,
including any dynamically reassigned port. The upstream v0.7.29 pre-release
removes this separate network hop.

## Why do I see HTTP 423 responses?

CLI Battery uses `423 Locked` while a resource is deliberately unavailable or still being prepared. Confirm CLI Battery and Phalanx are healthy, then inspect both service logs before changing ports or deleting state.

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

---
title: Service pages
icon: lucide/sliders
---

# Service pages

This page covers the service-level controls exposed in the DUMB Frontend, including
auto-restart policies, auto-update scheduling, and configuration editors.

---

## Overview

Each service page includes:

- Current status, health, and restart counters
- Start, stop, and restart actions (except for the API service)
- Configuration editors with validation
- Log viewers (service logs, plus special logs when available)
- Embedded UI tab when supported and enabled
- Dependency graph view for core/dependency startup relationships
- Per-service auto-restart overrides
- On-demand update checks and auto-update scheduling
- Seerr Sync controls when viewing a Seerr instance
- Symlink Job Center (for symlink-capable services) with active jobs, recent history, retry, and failure clearing
- Sidebar operator QoL controls (quick filters, saved views, compact mode, and command palette)

---

## Status and controls

The header shows the service name, status dot, and health badge. When auto-restart is
enabled for a service, you also see restart counters and the last restart reason.
With [Geek Mode](settings.md#geek-mode) enabled, the header also displays the internal
config key and process name in monospace.

Action buttons:

- **Start**, **Stop**, **Restart** for the current service
- **Auto-restart** opens per-service overrides (if supported)

!!! note "API service controls"

    The DUMB API service does not show Start/Stop/Restart controls in the UI.

---

## Dependency graph view

On the **DUMB Config** tab, use the **Dependencies** action to open a pop-out dependency graph panel that:

- Shows dependency startup order for the current service context
- Highlights missing/stopped dependencies
- Provides remediation suggestions
- Offers one-click **Fix now** actions to start available dependency processes
- Links to this documentation section from the panel header

Notes:

- For multi-instance dependency services (for example `rclone`, `zurg`), the graph scopes dependencies to instances linked to the current core service via `core_service`/`core_services`. Instance-scoped conditional dependencies are filtered so that only the specific instance associated with the current service is shown -- for example, "Rclone w/ CLID" only shows its specific Zurg instance, not Zurg instances belonging to other rclone configurations.
- If no linked dependency instance exists, the panel reports that mapping gap instead of treating an unrelated instance as valid.
- The panel also infers links from service config relationships (`core_service`, `core_services`, `wait_for_url`, `wait_for_dir`) so non-core services (for example Seerr, Tautulli, Arr instances tied to Decypharr/NzbDAV) can show real dependency edges.
- Dependency resolution runs on the backend (`GET /api/process/dependency-graph`) so startup ordering and dependency edges are aligned with backend process/config semantics.
- The dependency graph surfaces **conditional startup dependencies** from the backend startup ordering logic. These are dependencies that only apply when specific services are enabled -- for example, Prowlarr depends on Sonarr/Radarr only when those are enabled; Tautulli depends on Plex only when Plex is enabled; Huntarr depends on arr services only when `use_huntarr` is enabled on those instances. These appear with the `conditional_startup_map` signal and are styled the same as other hard runtime dependencies.
- Each dependency edge displays its signal type as a colored badge tag with a tooltip explaining the signal. Signal types include:
    - **Hard runtime** (orange): `core map`, `conditional startup`, `wait for url/dir/mounts`, `rclone provider`, `non-core dep`
    - **Hard configured** (cyan): `core service fields`
    - **Soft linkage** (gray): `optional integration`, `documented integration`
- The dependency pop-out supports scope selection:
    - `Runtime`: hard runtime/configured dependencies
    - `All`: includes soft linkage edges (for example optional integrations and documented service integrations like Seerr request routing to Sonarr/Radarr)
- The `Flow` view renders a Mermaid dependency graph (with edge strength styling) and shows directed edge details.
- The `Flow` view also lists backend `parallel_groups` to make concurrent prerequisite stages explicit (for example Riven startup prerequisites in parallel before backend start).
- With [Geek Mode](settings.md#geek-mode) enabled:
    - A **Copy JSON** button copies the full dependency graph API response to the clipboard
    - A **latency badge** shows the fetch time in milliseconds next to the panel title
    - The `Flow` view also shows the raw Mermaid graph source text for troubleshooting

For dependency services (for example `zurg`/`rclone`), the panel also shows which core services currently depend on them.

---

## Process Metrics panel

With [Geek Mode](settings.md#geek-mode) enabled, the **DUMB Config** tab displays a
**Process Metrics** panel showing live data from the `/api/metrics` endpoint:

| Section | Details |
|---------|---------|
| **Process** | PID, thread count, uptime since last start |
| **Resources** | CPU% and memory RSS with color-coded badges (green < 50%, amber < 80%, red >= 80%), disk I/O read/write totals |
| **Network** | Listening ports, active connection count |
| **Disk** | Per-path existence check (green/red dot), usage with percent bar |
| **Container** | CPU core count, total/used RAM with percent |
| **Restarts** | Total restart count, last exit reason, last restart timestamp |

Click **Refresh** to re-fetch metrics on demand. Metrics are fetched once when entering a
service page with Geek Mode active.

---

## Auto-restart policy

Configure the global auto-restart behavior:

| Setting | Description |
|---------|-------------|
| **Enabled** | Auto-restart failed services |
| **Max Restarts** | Maximum restart attempts |
| **Cooldown** | Time between restart attempts |
| **Grace Period** | Wait time before health checks |

The auto-restart modal includes a contextual **Why this matters** callout linking to this section.

![Auto-restart controls](../assets/images/frontend/auto_restart.png){ .shadow }

### Service overrides

Service pages can also override auto-restart settings per service:

- Enable/disable auto-restart for the current service
- Override defaults (intervals, thresholds, backoff)
- Apply in memory or save to file

---

## Auto-update settings

The updates panel lets you check for updates on demand and configure automatic update checks:

The panel includes a contextual **Why this matters** callout linking to this section.

Manual update actions:

- **Check for updates** runs a one-time update check even if auto-update is disabled.
- **Install update** applies the latest available update when allowed.
- **Override + install** appears when a service is pinned to a release/branch and you explicitly choose to bypass the block.

Automatic update settings:

| Setting | Description |
|---------|-------------|
| **Enabled** | Check for updates automatically |
| **Start time** | Daily schedule anchor in `HH:MM` (24-hour) |
| **Interval** | Hours between update checks |

Notes:

- Saving auto-update settings reschedules the updater immediately (no service restart required).
- **Next check** is shown in the panel once auto-update is enabled and scheduled.

---

## Seerr Sync panel

On Seerr service pages, the **Seerr Sync** panel lets you:

- Configure the top-level `seerr_sync` settings (enable, polling, external primary/subordinates)
- Toggle sync behavior options (pending/approved/declined/deletes/4K)
- Select the per-instance `sync_role` (disabled/primary/subordinate)
- Test external primary/subordinate connections before saving
- View sync status and failed requests
- Review a contextual **Why this matters** callout linking to this section

API keys are hidden by default and can be revealed when needed.

Failed request lists are shown in a scrollable panel so large queues don’t expand the page.

---

## Configuration editors

The frontend includes editors for the main DUMB config and service-specific configs.

### Edit DUMB Config

View or edit `dumb_config.json`. Changes can be saved in memory or written to disk.

Notes:

- The editor runs schema validation when available.
- Invalid JSON or validation errors block saves until corrected.
- Validation errors include inline "Why invalid" guidance (for example missing required fields, wrong types, unknown keys).
- A live config diff preview shows added/changed/removed paths before apply/save.
- Risk-tagged config changes (for example command/env/path/network/restart/update/credential fields) require an explicit acknowledgement checkbox before apply/save.

### Edit Service Config

![Edit Service Config](../assets/images/frontend/edit_service_config.png){ .shadow }

For services with separate config files, you can open and modify those settings here.
Service configs should be saved to file.

---

## Logs

Service pages include log viewers when a log file is configured or when the service
is allowlisted for logs:

![View service logs](../assets/images/frontend/view_service_logs.png){ .shadow }

- Filter by text and level
- Limit displayed lines
- Follow tail and refresh on an interval (including custom intervals)
- Manual refresh
- Download logs

### Special log tabs

- **Traefik Access Logs** appear on the Traefik service page.
- **DBRepair Logs** appear on the Plex service page when DBRepair is enabled.

---

## Embedded UI

When embedded UIs are enabled and the service exposes a UI, a dedicated **Embedded UI**
tab appears.

Features:

- **Open in new tab** (only shown for local/private access)
- **Full window** toggle
- UI path selector for services with multiple entry points (for example Zilean)

NzbDAV uses a trailing slash in its embedded UI path to match its frontend routing.

---

## Default tab selection

You can choose a default tab for each service page (for example, always open logs).
The selection is stored in the UI preferences.

---

## Sidebar operator QoL

The services sidebar includes faster navigation controls for large stacks:

- **Quick filters** for `All`, `Running`, `Stopped`, and `Unhealthy` services
- **Search filter** for process name/config key matching
- **Saved views** to store and re-apply filter/search/toggle combinations
- **Compact mode** to reduce service-row density in the sidebar
- **Command palette** (`Ctrl/Cmd + K`) to jump directly to service pages
- **Assignable service shortcuts** configured from command-palette results by entering shortcut-capture mode and pressing the combo
- **Collapsible Sidebar tools** section to keep controls hidden when not needed

These controls are persisted in `dumb_config.json` under `dumb.ui.sidebar` (with local state used as a fallback during initial load) and are intended for power-user workflows across many services.

---

## Related pages

- [Settings](settings.md) - Preferences and onboarding controls
- [Dashboard](dashboard.md) - Service controls and logs

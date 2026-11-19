---
title: Usage
description: Operate DUMB through its dashboard and API, manage individual services, inspect status and logs, and understand normal startup behavior.
icon: lucide/play-circle
---

# Everyday use

Open the dashboard at `http://localhost:3005` on the Docker host, or replace `localhost` with the host's address. DUMB starts enabled services in dependency order when the container starts.

On a fresh installation, managed applications are disabled until you choose them in [onboarding](../frontend/onboarding.md). The API and frontend provide the setup interface.

## Start, stop, or inspect a service

1. Select the service on the [dashboard](../frontend/dashboard.md).
2. Check its status and health reason before taking action.
3. Use **Start**, **Stop**, or **Restart**. If a downstream media server uses the affected storage, review the playback and library-protection prompt.
4. Open **Service Logs** if startup fails, or **Tools → Dependencies** to inspect missing prerequisites.

Saving a service's configuration and starting it are separate actions. **Save to File** persists the change; **Apply in Memory**, where offered, changes only the controller's current configuration. An application may still need a restart or an explicit setup action to use new settings.

Use the [service-controls screenshot](../frontend/service-pages.md#status-and-controls) to find these controls and the [log-filter walkthrough](../frontend/service-pages.md#logs) to inspect a failure.

## Review updates

Use **Updates** on the dashboard to check enabled services and install selected available updates. For a saved release, branch, commit, or version pin, open that service's Updates panel and review its configured target.

| Action | Effect |
| --- | --- |
| Check for updates | Refresh version information without restarting the service |
| Install update | Install the available target and restart the affected service |
| Install configured release/branch/commit | Apply the source selection saved for that service |
| Override + latest | Explicitly bypass the saved selection for one install |

For scheduled checks, open that service's **Tools → Updates**, enable **Scheduled update checks**, and choose **Show on dashboard** under **When available**. Set **Start time** and **Interval (hours)**, then select **Save auto-update**. Check **Next check** to confirm a schedule exists. Fixed source selections can disable scheduling; see [Auto-update](auto-update.md).

<details class="geek-details" markdown="1">
<summary>Technical alternative: configure scheduled checks with JSON</summary>

For scheduled checks, configure each service separately:

```json
{
  "auto_update": true,
  "auto_update_mode": "check_only",
  "auto_update_start_time": "04:00",
  "auto_update_interval": 24
}
```

This fragment checks daily and reports available updates without installing them. The interval is in hours and the start time uses `HH:MM`. Settings belong inside the selected service or instance; source pins can disable scheduling. See [Auto-update](auto-update.md) for supported strategies and automatic installation.


</details>

The DUMB container itself is updated through your Docker deployment. An available API update notice does not replace the container automatically.

## Stop the container

Use your deployment tool's normal stop action. DUMB stops managed processes and unmounts rclone during shutdown.

<details class="geek-details" markdown="1">
<summary>Technical alternative: set the Compose shutdown grace period</summary>

The maintained Compose example allows 30 seconds:

```yaml
services:
  DUMB:
    stop_grace_period: 30s
```

</details>

Allow active backups, migrations, and restore jobs to finish before stopping DUMB. Closing their browser panels does not stop the backend work.

## Find the next step

- [Configuration](configuration.md) explains saved settings and environment overrides.
- [Service pages](../frontend/service-pages.md) maps the dashboard controls.
- [Startup lifecycle](startup-lifecycle.md) explains a stack that remains starting or degraded.
- [API](../api/index.md) documents scripted controls.

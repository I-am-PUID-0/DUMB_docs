---
title: Use DUMB
description: Explore actual DUMB frontend screens and follow clear guides for setup, service controls, settings, logs, updates, metrics and application access.
icon: lucide/layout-dashboard
---

# Use DUMB { #dashboard-guide }

The dashboard is where you set up and manage DUMB. Open `http://<host>:3005` in your browser, replacing `<host>` with the machine running DUMB. Sign in if authentication is enabled.

You can follow the tasks below without editing files or running API commands.

[Browse the actual interface](#ui-examples) or choose a task below.


## Choose a task

| I want to… | Open this guide |
| --- | --- |
| Set up services for the first time | [Onboarding](onboarding.md) |
| Start, stop, or check an app | [Dashboard](dashboard.md) and [service controls](service-pages.md#status-and-controls) |
| Change a DUMB setting or an app's own setting | [Configuration](../features/configuration.md) |
| Check for updates or install an update | [Auto-update](../features/auto-update.md) |
| Restart an app automatically after a failure | [Auto-restart](../features/auto-restart.md) |
| Sign in or manage DUMB accounts | [Authentication](../features/authentication.md) |
| Read an error or download a log | [Service logs](service-pages.md#logs) |
| Open Plex, Jellyfin, InfiniDysk, or another app | [Embedded UI](service-pages.md#embedded-ui) |
| Back up or repair library links | [Symlink operations](../features/symlinks.md) |
<!-- dev:start -->
| Back up or restore the whole installation | [Installation backups](../features/installation-backups.md) |
<!-- dev:end -->
| Investigate resource use | [Metrics](metrics.md) |
| Change appearance or dashboard preferences | [Settings](settings.md) |

Each task guide explains the controls to use, what to save, and how to check the result. Service-specific account and library setup is covered in the [service guides](../services/index.md).

## Watch a task

The guides below include short recordings with time to read the menus and controls. Choose Play when you are ready; these task videos do not start automatically. Each caption identifies the reviewed frontend version and example data. Your installed version and enabled services can change which tools appear.

| See how to… | Open the illustrated guide |
| --- | --- |
| Review the right configuration editor | [Configuration](../features/configuration.md) |
| Filter logs and pause their refresh | [Service logs](service-pages.md#logs) |
| Open Tools, check an update and review its version | [Check one service for updates](../features/auto-update.md#check-and-install-one-update) |
| Inspect a service's dependencies | [Dependency graph](service-pages.md#dependency-graph-view) |
| Review an automatic restart policy | [Auto-restart](../features/auto-restart.md) |
| Choose a dashboard appearance | [Settings](settings.md) |
| Find CPU, memory and disk information | [Metrics](metrics.md) |

<!-- docs:visual-gallery -->

## DUMB and application accounts are separate

A DUMB account gives operator access to its dashboard, including service and user management. Opening an app inside DUMB does not sign you into that app: Plex, Jellyfin, pgAdmin, and other services may ask for their own account.

See [Authentication](../features/authentication.md) before sharing DUMB access with someone else.

## If the instructions do not match your screen

Check the DUMB and frontend versions in **Settings → About**, then choose **Latest release** or **Development** documentation in this site's header. An older installation may not show a newer tool.

Use a current browser. If the dependency graph's Flow view cannot display, its **Details** view provides the connections as text.

## What Geek mode adds

The normal guides use frontend tools. Geek sections explain the underlying processes and connections, or show alternatives such as API calls, command-line tools, environment variables, and manual configuration.

Geek mode changes these docs; it does not change DUMB's settings. [How the documentation modes work](../reference/doc-versions.md#use-geek-mode-when-you-want-more-detail).

<details class="geek-details" markdown="1">
<summary>Geek reference: how the dashboard connects and alternative deployment settings</summary>

## Ports and live connections

The maintained Compose example publishes the frontend on `3005`. Bundled Traefik uses `18080` for service UI routes; it does not replace the frontend listener.

The frontend proxies backend requests under `/api` and streams status, metrics, and logs over WebSockets. A reverse proxy in front of the dashboard must allow those WebSocket connections. If the connection indicator is disconnected, check proxy and network settings before relying on the displayed sample as current.


## Frontend configuration

Managed installations receive these values from DUMB. A separately deployed frontend must use addresses reachable from its own container:

| Variable | Default | Purpose |
| --- | --- | --- |
| `DUMB_API_URL` | `http://127.0.0.1:8000` | Backend API |
| `DUMB_TRAEFIK_URL` | API host on port `18080` | Embedded HTTP and WebSocket proxy target |
| `NUXT_TELEMETRY_DISABLED` | `1` | Disable Nuxt telemetry |

DUMB injects the current Traefik listener into its managed frontend, including when port reservation moves Traefik away from `18080`.

## Browser support

Use a current Chrome/Chromium, Firefox, Safari, or Edge release. The dependency panel's [Flow view](service-pages.md#dependency-graph-view) uses Mermaid 12 and requires Safari 17.4+ or another ES2024-capable browser. If that view cannot render, use **Details** to inspect dependencies. See the [Mermaid 12 release notes](https://github.com/mermaid-js/mermaid/releases/tag/mermaid@12.0.0) for its browser requirements.

</details>

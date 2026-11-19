---
title: Configuration
description: Change and save DUMB service settings through the dashboard, add integration tokens, and resolve settings that do not take effect.
icon: lucide/settings
---

# Configuration

Use the dashboard to change DUMB settings and the settings of individual applications. Each service has its own page; you do not need to edit files on the server for ordinary changes.

## Change a setting

1. Open the [dashboard](../frontend/dashboard.md) and select the service you want to change.
2. Choose **DUMB Config** for how DUMB manages that service, such as its port, enabled state, or update policy. Choose **Service Config** for the application's own settings when that tab is available.
3. Find the existing setting in the editor and change only the intended value. The editor may show JSON; preserve the surrounding structure and any fields you are not changing.
4. Review validation messages and the list of changed settings. Correct errors and acknowledge any highlighted sensitive change before saving.
5. In **DUMB Config**, select **Save to File**. In **Service Config**, select **Save Service Config**.
6. Reopen the same tab to check the saved value. Follow the application's guide if it needs a restart or another setup action, then check its status and logs.

**Apply in Memory** is a temporary DUMB configuration option. Use **Save to File** when you want a setting to survive a container restart. Saving a setting does not prove that the application has applied it.

!!! warning "Paths, ownership, and credentials"

    Changing user/group IDs, data paths, or ports can prevent an existing service from starting. Follow the service's guide and keep a backup before changing these values. Configuration and backups may contain live credentials; keep them private and redact values before sharing them.

<figure class="docs-visual docs-frontend-figure">
<video class="docs-frontend-video" controls playsinline preload="none" poster="../../assets/images/guides/frontend/v1.91.0/tour-2/configuration.webp" aria-label="Choose the correct configuration editor" aria-describedby="configuration-demo-caption">
  <source src="../assets/images/guides/frontend/v1.91.0/tour-2/configuration.webm" type="video/webm">
  <p><a href="../assets/images/guides/frontend/v1.91.0/tour-2/configuration.webm">Download the demonstration</a>, or follow the written steps above.</p>
</video>
<figcaption id="configuration-demo-caption" class="docs-visual-caption">Watch: compare DUMB Config with Service Config and locate Save to File. This tour reviews the controls without saving a change. DUMB Frontend 1.91.0 · example data. Other versions may look different. <a href="../assets/images/guides/frontend/v1.91.0/tour-2/configuration.webp">Open the full-size screenshot</a>.</figcaption>
</figure>

## Add an integration token

1. Open **Settings → Tokens**.
2. Enter the **Plex Token** or **GitHub Token** you need. Public GitHub release checks normally work without a token; use only the read access required by your release source.
3. Select **Save** and wait for **Saved**.
4. Retry the affected connection or update check. Check its error message if it still fails.

## A setting changes back or does not take effect

First check that you saved in the correct tab and for the correct instance. A deployment-level override can take priority over a saved value. If one is present, update it in the tool used to deploy DUMB, or ask the person who manages that deployment to change it. The precedence reference below lists the available sources.

<details class="geek-details" markdown="1">
<summary>Technical details: runtime files, environment overrides, and configuration structure</summary>

DUMB stores its runtime configuration at `/config/dumb_config.json`. The copy at `utils/dumb_config.json` is the default template. Changing the template does not change an existing installation's saved configuration. For direct file edits, retain a working copy and use valid JSON; unsupported keys can be pruned. See the [config schema reference](../reference/config-schema.md).

## Configuration precedence

When a field has more than one value, DUMB uses this order:

| Priority | Source |
| --- | --- |
| 1 — highest | Docker secret at `/run/secrets/<ENV_VAR>` |
| 2 | Container or process environment |
| 3 | `/config/.env` |
| 4 | `/config/dumb_config.json` |
| 5 — fallback | Default template |

Environment names follow nested config paths, such as `DUMB_GITHUB_TOKEN` for `dumb.github_token`. Use the backend's [`.env.example`](https://github.com/I-am-PUID-0/DUMB/blob/master/.env.example) or the [environment variable reference](../reference/environment-variables.md) for exact names. A saved JSON value cannot override a higher-priority source.

<span id="configuration-file-structure"></span>

## General settings

These fields live at the top level:

```json
{
  "puid": 1000,
  "pgid": 1000,
  "tz": "America/New_York",
  "data_root": "/data"
}
```

| Field | Purpose |
| --- | --- |
| `puid`, `pgid` | User and group IDs for managed services; use IDs that can access the mounted data |
| `tz` | Timezone for schedules and application configuration |
| `data_root` | Base container path for service data directories |

`puid` and `pgid` must be nonzero. Changing an ID or data root on an existing installation can affect ownership and application paths; verify the mounted directories before restarting.

## Logging settings

Logging settings live under `dumb`:

```json
{
  "log_level": "INFO",
  "log_name": "DUMB",
  "log_dir": "/log",
  "log_count": 2,
  "log_size": "10M",
  "color_log": true
}
```

| Field | Purpose |
| --- | --- |
| `log_level` | Verbosity, such as `DEBUG`, `INFO`, `WARNING`, or `ERROR` |
| `log_dir` | Container directory for logs |
| `log_count` | Number of rotated logs to retain |
| `log_size` | Size that triggers rotation |
| `color_log` | Colored console output |

On supported backends, the DUMB API service page also offers a temporary DEBUG override. It takes effect immediately, does not persist, and does not change managed applications' log levels.

## Integration tokens & credentials

| Field under `dumb` | Use |
| --- | --- |
| `plex_token` | Plex API integrations, including Riven watchlists and library scans |
| `plex_address` | Plex URL reachable from inside DUMB, such as `http://127.0.0.1:32400` for bundled Plex |
| `github_token` | Higher GitHub API limits and authorized access to private or sponsored release sources |
| `github_username` | Reserved; not needed for normal setup |

Create a GitHub token from [Developer settings](https://github.com/settings/tokens) only when needed. Grant the repository read access required by the release source; DUMB does not need package-write permissions. Public release checks can work without a token. Store it as `DUMB_GITHUB_TOKEN` in `/config/.env`, the container environment, or a Docker secret, or set `dumb.github_token` in the runtime JSON.

Configuration files and backups can contain live credentials. Keep them private and redact values before sharing troubleshooting output.

## Service and instance settings

Each managed application has its own section. Some, including Arr apps, hold settings under `instances`:

```json
{
  "sonarr": {
    "instances": {
      "Default": {
        "enabled": true,
        "core_service": "decypharr"
      }
    }
  }
}
```

This is a partial example. Use the existing instance's complete configuration or the current default template when creating a new one. Ports, paths, process names, source selectors, and credentials vary by application; the [service catalog](../services/index.md) links to each guide.

## `core_service` (Arr integration)

`core_service` tells DUMB which workflow an Arr instance should use. It accepts one value, a comma-separated string, or a list:

| Value | Integration |
| --- | --- |
| `""` | No core workflow integration |
| `"decypharr"` | Decypharr |
| `"infinidysk"` | InfiniDysk |
| `"altmount"` | AltMount |
| `["decypharr", "infinidysk", "altmount"]` | Combined workflows |

For example, set `"core_service": "infinidysk"` on an InfiniDysk-backed Radarr instance. Connections still require the chosen workflow's prerequisites and setup steps. See [Core service routing](../reference/core-service.md) for matching rules and migration considerations.

</details>

## Related guides

<!-- dev:start -->
- [Setup checklist](setup-checklist.md) for connections and retained manual tasks.
<!-- dev:end -->
- [Everyday use](usage.md) for saving, starting, and updating services.
- [Multi-instance setup](../reference/instances.md) for additional application instances.

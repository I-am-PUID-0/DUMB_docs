---
title: Configuration
description: Configure DUMB services, ports, paths, credentials, logging, authentication, automation, and runtime settings in dumb_config.json.
icon: lucide/settings
---

# Configuration

DUMB stores its runtime configuration at `/config/dumb_config.json`. The copy at `utils/dumb_config.json` is the default template. Edit the runtime file or use the dashboard; changing the template does not change an existing installation's saved configuration.

## Change a setting

1. Open a service page and choose **DUMB Config** for DUMB-managed settings, or **Service Config** for the application's own configuration when available.
2. Change the intended fields and select **Save to File**.
3. Review any setup or restart action required by that application.
4. If a saved value changes back, check for an environment or secret override before editing again.

For file edits, keep a copy of the working runtime configuration and use valid JSON. DUMB validates and merges known settings with its defaults; unsupported keys can be pruned. The [config schema reference](../reference/config-schema.md) explains the structure.

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

## Related guides

- [Setup checklist](setup-checklist.md) for connections and retained manual tasks.
- [Everyday use](usage.md) for saving, starting, and updating services.
- [Multi-instance setup](../reference/instances.md) for additional application instances.

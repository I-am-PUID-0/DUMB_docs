---
title: Environment variables
icon: lucide/terminal
---

# Environment variables

Every scalar/list setting in DUMB's configuration can be overridden at startup with an environment variable or Docker secret. Service subprocess variables are separately defined under each service's `env` block.

---

## Container variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | `1000` | Container user ID |
| `PGID` | `1000` | Container group ID |
| `TZ` | unset | Time zone (for example `America/New_York`) |
| `DUMB_PNPM_STORE_ROOT` | `/config/.pnpm-store` | Persistent pnpm package store root used during service setup/builds. Override only if `/config` is not suitable. |
| `DUMB_BUN_CACHE_ROOT` | `/config/.bun-cache` | Persistent Bun package cache root used during Bun-based service setup/builds, such as Pulsarr. Override only if `/config` is not suitable. |

!!! tip "Complete generated reference"

    The repository's [`.env.example`](https://github.com/I-am-PUID-0/DUMB/blob/dev/.env.example) is generated from the current config template and contains the complete default set. The table above calls out bootstrap/cache variables operators commonly set directly.

## Config override naming

DUMB joins a configuration path with underscores and uppercases it:

| Config path | Override name |
|---|---|
| `puid` | `PUID` |
| `dumb.github_token` | `DUMB_GITHUB_TOKEN` |
| `dumb.api_service.host` | `DUMB_API_SERVICE_HOST` |
| `altmount.port` | `ALTMOUNT_PORT` |
| `sonarr.instances.Default.port` | `SONARR_INSTANCES_DEFAULT_PORT` |

Lists and objects must be valid JSON, such as `DUMB_METRICS_FILESYSTEM_PATHS=["/","/mnt/debrid"]`.

## Sources and precedence

For a config override named `DUMB_API_SERVICE_HOST`, DUMB checks:

1. `/run/secrets/DUMB_API_SERVICE_HOST`
2. The process/container environment
3. `/config/.env`
4. The value in `/config/dumb_config.json`

Blank environment values do not replace configured values. Docker secrets are read as trimmed text and have the highest priority.

---

## Service environment variables

Each service can define variables passed to that subprocess under its `env` block in `/config/dumb_config.json`. These are service runtime variables, not names for overriding DUMB's own config tree.

Example:

```json
"nzbdav": {
  "env": {
    "WEBDAV_USER": "admin",
    "WEBDAV_PASSWORD": "change-me"
  }
}
```

!!! warning "Secrets in config files"

    Treat tokens and passwords in `dumb_config.json` as secrets. Avoid committing them to source control.

---

## Related pages

- [Configuration guide](../features/configuration.md)
- [Config schema](config-schema.md)

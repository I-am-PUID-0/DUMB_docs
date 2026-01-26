---
title: Environment variables
icon: lucide/terminal
---

# Environment variables

This reference lists container-level environment variables that DUMB reads at startup. Service-specific environment variables are set in `dumb_config.json` under each service’s `env` block.

---

## Container variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | `1000` | Container user ID |
| `PGID` | `1000` | Container group ID |
| `TZ` | unset | Time zone (for example `America/New_York`) |

!!! tip "Persist your config"

    These values are typically set in your `docker-compose.yml` or `.env` file so they survive container restarts.

---

## Service environment variables

Each service can define environment variables under its `env` block in `dumb_config.json`. DUMB merges these with defaults when it performs service setup.

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

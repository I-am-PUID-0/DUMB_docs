---
title: Configuration schema
icon: lucide/file-code
---

# Configuration schema

DUMB uses a JSON schema to validate `/config/dumb_config.json` and keep service definitions consistent.

---

## Schema location

The default template and schema live in the backend repository/image:

```
utils/dumb_config.json
utils/dumb_config_schema.json
```

`utils/dumb_config.json` is a template; `/config/dumb_config.json` is the persistent runtime file. On startup DUMB copies the template when needed, adds missing defaults to existing configs, prunes keys removed from the supported template, and validates the result against the schema before creating the effective environment-overridden configuration.

The API exposes the current schema at native `GET /config/schema` (frontend proxy: `GET /api/config/schema`) and a process-specific subtree at `POST /config/process-config/schema`.

---

## Top-level structure

| Key | Description |
|-----|-------------|
| `puid` / `pgid` | Container user/group IDs |
| `tz` | Time zone string |
| `data_root` | Base path for persisted data |
| `dumb` | DUMB core settings (API, frontend, logging, tokens) |
| `traefik` | Reverse-proxy configuration |
| `traefik_proxy_admin` / `cloudflared` | Optional reverse-proxy management and tunnel connector |
| `seerr_sync` | Cross-instance Seerr synchronization |
| `postgres` / `pgadmin` | Database settings |
| `rclone` | rclone instances and mounts |
| Service keys | Core/dependent/optional services (for example `decypharr`, `nzbdav`, `cli_debrid`) |

!!! note "Service blocks are explicit"

    Each service has its own schema definition (for example `decypharr`, `nzbdav`, `cli_debrid`). This ensures consistent required fields and defaults.

---

## Validation tips

- Validate JSON changes before restart to avoid startup failures.
- Back up `/config/dumb_config.json` before large manual edits; use the frontend editor for normal service changes.
- Keep `config_dir`, `log_file`, and `port` unique for each service instance.
- Use `release_version_enabled` or `branch_enabled` when pinning versions.
- Do not edit `utils/dumb_config.json` expecting a persistent runtime change.

---

## Related pages

- [Environment variables](environment-variables.md)
- [Multi-instance configuration](instances.md)

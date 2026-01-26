---
title: Configuration schema
icon: lucide/file-code
---

# Configuration schema

DUMB uses a JSON schema to validate `dumb_config.json` and keep service definitions consistent.

---

## Schema location

The schema lives in the backend repository:

```
utils/dumb_config_schema.json
```

Use this schema to validate custom edits or generate tooling support (autocomplete, validation, templates).

---

## Top-level structure

| Key | Description |
|-----|-------------|
| `puid` / `pgid` | Container user/group IDs |
| `tz` | Time zone string |
| `data_root` | Base path for persisted data |
| `dumb` | DUMB core settings (API, frontend, logging, tokens) |
| `traefik` | Reverse-proxy configuration |
| `postgres` / `pgadmin` | Database settings |
| `rclone` | rclone instances and mounts |
| Service keys | Core/dependent/optional services (for example `decypharr`, `nzbdav`, `cli_debrid`) |

!!! note "Service blocks are explicit"

    Each service has its own schema definition (for example `decypharr`, `nzbdav`, `cli_debrid`). This ensures consistent required fields and defaults.

---

## Validation tips

- Validate JSON changes before restart to avoid startup failures.
- Keep `config_dir`, `log_file`, and `port` unique for each service instance.
- Use `release_version_enabled` or `branch_enabled` when pinning versions.

---

## Related pages

- [Environment variables](environment-variables.md)
- [Multi-instance configuration](instances.md)

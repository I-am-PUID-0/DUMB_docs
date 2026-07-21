---
title: AltMount
---

# AltMount

AltMount is a core Usenet-focused service that can provide a WebDAV interface, SABnzbd-compatible download-client behavior, metadata storage, and optional rclone mount management. In DUMB it is treated as a core Usenet workflow service so guided onboarding can wire Arr instances to it alongside or instead of NzbDAV.

## What It Provides

AltMount provides:

- A web UI and API on the configured service port
- A WebDAV-style content endpoint for Usenet-backed media workflows
- SABnzbd-compatible behavior for Arr download-client style integrations
- Local metadata storage under the configured metadata directory
- Optional rclone mount management from AltMount's own config

## Default Ports

| Service | Port |
|---------|------|
| AltMount | 8088 |

DUMB checks `http://127.0.0.1:8088/live` by default to confirm the service is ready.

## DUMB Configuration

The default DUMB config block looks like this:

```json
{
  "altmount": {
    "enabled": false,
    "postgres_enabled": false,
    "postgres_database": "",
    "process_name": "AltMount",
    "repo_owner": "javi11",
    "repo_name": "altmount",
    "pinned_version": "latest",
    "port": 8088,
    "mount_type": "rclone",
    "config_dir": "/altmount",
    "config_file": "/altmount/config.yaml",
    "metadata_dir": "/altmount/metadata",
    "mount_path": "/mnt/debrid/altmount",
    "log_file": "/altmount/logs/altmount.log",
    "wait_for_url": "http://127.0.0.1:8088/live"
  }
}
```

DUMB downloads the matching Linux release binary into `/altmount/altmount`, writes `/altmount/version.txt`, creates the metadata/log/rclone directories, and creates `/altmount/config.yaml` only when it does not already exist. Existing AltMount config files are left in place so UI or manual edits are preserved.

Choose the mount behavior with `mount_type`:

| Value | Behavior |
|-------|----------|
| `dfs` | FUSE Mount. DUMB uses the same operator-facing value as Decypharr and writes AltMount's upstream `mount_type: fuse`. |
| `rclone` | Default. Embedded/Internal Rclone. DUMB writes AltMount's upstream `mount_type: rclone`. |
| `external_rclone` | External Rclone. DUMB writes AltMount's upstream `mount_type: rclone_external`. |
| `none` | No AltMount-managed mount. |

DUMB stores the same mount-mode values used by Decypharr (`dfs`, `rclone`, `external_rclone`, `none`) and writes the matching upstream AltMount value into `/altmount/config.yaml`. AltMount's own UI names these choices Disabled, Internal RClone, AltMount Native, and External RClone.

## PostgreSQL migration

AltMount supports both SQLite and PostgreSQL through its `database` configuration. For an existing SQLite-backed service, open **Database Migration**, run a rehearsal, validate the import against AltMount's current application-created PostgreSQL schema, and only then cut over. DUMB writes the PostgreSQL DSN into `/altmount/config.yaml`, registers the target database (`altmount` by default), and retains the SQLite file for rollback.

Do not set `postgres_enabled: true` directly when existing AltMount state must be retained. DUMB has not found an upstream application-specific data migration tool, so rehearsal and post-cutover application checks are especially important. See [SQLite to PostgreSQL Migration](../../features/arr-postgres-migration.md).

AltMount `v0.3.2` contains a PostgreSQL syntax error in its bundled migration 10 expression index. During guarded schema initialization, DUMB applies the intended corrected index only when the isolated database is at Goose version 9 and contains the expected `import_queue.metadata` column, records version 10, and lets AltMount run all remaining migrations itself. If those exact safeguards do not match, DUMB refuses the repair and restores SQLite instead of skipping unknown schema work.

## First Start

1. Select `AltMount` as the Usenet workflow service in guided onboarding, or enable `altmount` in runtime config.
2. Start the service from DUMB.
3. Open the embedded UI from the AltMount service page or browse to `http://<host>:8088`.
4. Configure providers, SABnzbd behavior, Arr integration, and any advanced rclone settings in AltMount.

DUMB enables AltMount SABnzbd compatibility, adds linked Arr instances to AltMount config, and registers AltMount as a SABnzbd download client in Arr instances whose `core_service` includes `altmount`. The generated first-run config intentionally leaves `providers` empty. Add provider details in AltMount before expecting download or WebDAV workflows to return content.

## Files and Persistence

| Path | Purpose |
|------|---------|
| `/altmount/altmount` | Release binary downloaded by DUMB |
| `/altmount/config.yaml` | AltMount runtime config |
| `/altmount/metadata` | AltMount metadata root |
| `/altmount/logs/altmount.log` | AltMount service log |
| `/altmount/version.txt` | DUMB-managed installed version marker |

## Embedded UI

AltMount is available through the DUMB embedded UI proxy at `/service/ui/altmount` when enabled. Its root `/api/*` calls are routed to the AltMount service context so they do not collide with DUMB backend API routes.

## Troubleshooting

- If the service does not start, check `/altmount/logs/altmount.log` and the DUMB service logs.
- If the UI loads but providers do nothing, verify `providers` are configured in `/altmount/config.yaml` or through the AltMount UI.
- If the embedded UI sends API calls to DUMB instead of AltMount, refresh the service page so the embedded UI context cookie is reset.
- If you pin `pinned_version`, include the release tag format used by upstream, such as `v0.2.0`.

## Related Links

- [AltMount repository](https://github.com/javi11/altmount)
- [AltMount docs](https://altmount.kipsilabs.top/)
- [NzbDAV](nzbdav.md)

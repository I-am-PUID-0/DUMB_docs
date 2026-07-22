---
title: Decypharr FAQ
icon: lucide/shield
---

# Decypharr FAQ

## Which mount mode should I choose?

| Mode | Mount owner | DUMB behavior |
|---|---|---|
| `dfs` | Decypharr DFS | Decypharr owns the consolidated mount at `mount_path`; DUMB supplies the required cache directory when missing. |
| `rclone` | Decypharr embedded rclone | Decypharr owns the consolidated mount and rclone settings in its own config/UI. |
| `external_rclone` | DUMB-managed rclone | Decypharr starts first to expose WebDAV, then DUMB starts one consolidated rclone mount against `/webdav`. |
| `none` | No local mount | Use Decypharr APIs/WebDAV without asking DUMB to create a mount. |

DFS and native Usenet are current stable features; a beta branch toggle is not required to use them.

## Why does external rclone start after Decypharr?

The rclone instance consumes Decypharr's WebDAV endpoint, so starting rclone first creates a dependency cycle. DUMB starts Decypharr, waits for its WebDAV readiness, then starts the `decypharr_enabled` rclone instance.

## Where do provider API keys belong?

DUMB persists onboarding keys under `decypharr.api_keys` for every mount mode. Setup reconciles those keys into Decypharr and uses them when an external-rclone instance must be created. Avoid putting secrets into screenshots or support logs.

## How is Usenet connected to an Arr app?

When Decypharr has Usenet providers configured, DUMB adds a Sabnzbd-compatible download client named `decypharr-usenet` to linked Arr instances. Debrid downloads use Decypharr's qBittorrent-compatible client.

## Why is DUMB waiting for the wrong old provider mount?

Legacy configs may contain per-provider folders while current configs use one top-level `mount.mount_path`. Restart after saving the desired `mount_type` in DUMB so setup can reconcile `config.json`. If existing links still target the old layout, preview the Decypharr migration playbook in **Symlinks** before applying it.

## Related pages

- [Decypharr service guide](../services/core/decypharr.md)
- [Symlink Operations](../features/symlinks.md)
- [rclone](../services/dependent/rclone.md)
- [Arr core-service routing](../reference/core-service.md)

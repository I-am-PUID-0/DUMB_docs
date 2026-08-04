---
title: Media Library Protection API
description: API endpoints for media dependency preflight, protection policy, recovery status, and Plex library preferences.
icon: lucide/shield-check
---

# Media Library Protection API

All endpoints use the normal DUMB authentication policy and are capability-gated by `media_library_protection`. Plex preference controls additionally require `plex_library_settings`.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/process/media-protection/status` | Active/recent incidents and global recovery timing. Optional `process_name`. |
| `POST` | `/api/process/media-protection/preflight` | Resolve affected media servers and current activity before `stop`, `restart`, `update`, or `scheduled_update`. |
| `GET` | `/api/process/media-protection/policy?process_name=...` | Read a redacted per-server policy. |
| `PUT` | `/api/process/media-protection/policy` | Save per-server enablement, dedicated API key, idle-stop behavior, or protected mounts. |
| `PUT` | `/api/process/media-protection/settings` | Save global enablement and recovery timing. |
| `GET` | `/api/process/media-protection/plex-library-settings` | Read the supported live Plex library preferences. |
| `PUT` | `/api/process/media-protection/plex-library-settings` | Update only the allowlisted Plex library preferences. |

Lifecycle payloads for `/stop-service`, `/restart-service`, and `/update-install` accept `protection_override` with `safe`, `keep_running`, or `stop_now`. Omitting it uses `safe`. A blocked safe operation returns `status: protection_required` with the latest preflight rather than changing service state.

Dedicated Jellyfin/Emby keys are write-only. Policy responses contain an empty `api_key` and `api_key_configured`; a blank update preserves the stored key unless `clear_api_key: true` is supplied.

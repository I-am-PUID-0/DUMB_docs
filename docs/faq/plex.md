---
title: Plex FAQ
description: Reduce unnecessary reads on remote Plex libraries and diagnose buffering without treating VFS caching or HTTP 423 errors as a single-cause problem.
icon: lucide/tv
---

# Plex FAQ

## Recommended library settings

Background analysis can read substantial amounts of remote content. For a Debrid/Usenet mount, review these Plex settings before the first scan:

| Location | Setting to review | Why |
|---|---|---|
| Per-library advanced settings | Video preview thumbnails, credits detection, voice detection | Analysis can fetch media beyond what you play |
| Settings → Library | Scan automatically; partial scans on detected changes | Frequent changes can cause repeated scans |
| Settings → Library | Empty trash automatically after every scan | A temporarily missing mount should not remove your library entries |

Start with unnecessary analysis and automatic trash removal disabled. Add scheduled or workflow-triggered scans deliberately, then observe provider traffic and scan duration. These choices reduce background activity; they do not guarantee that a provider will never throttle requests.

## Plex buffers when playing through rclone

Check the bottleneck before changing cache settings: provider errors, network throughput, disk pressure, transcoding load, and mount latency can all interrupt playback.

VFS `full` mode caches file ranges as they are read and can help with seeking. It does **not** download the entire file before playback begins. Example settings for a mount with suitable local cache space:

```env
RCLONE_VFS_CACHE_MODE=full
RCLONE_VFS_CACHE_MAX_SIZE=100G
RCLONE_VFS_CACHE_MAX_AGE=6h
```

The size and age values are examples, not limits suited to every host. Open files can keep cache usage above the requested limit; leave free disk space and observe real usage.

See [rclone VFS file caching](https://rclone.org/commands/rclone_mount/#vfs-file-caching) and [flags in DUMB](../services/dependent/rclone.md#rclone-flags-via-environment-variables). Global environment variables affect all rclone instances, while explicit command arguments can take precedence. Use per-instance settings when mounts need different policies.

## Related pages

- [Plex service guide](../services/core/plex-media-server.md)
- [rclone FAQ](rclone.md)
- [Zurg FAQ](zurg.md)

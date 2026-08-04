---
title: Media Library Protection
description: Protect Plex, Jellyfin, and Emby libraries from destructive scans when rclone, NzbDAV, Decypharr, Zurg, AltMount, or CLI Debrid is stopped, updated, or unavailable.
icon: lucide/shield-check
---

# Media Library Protection

Media Library Protection reduces the chance that Plex, Jellyfin, or Emby interprets a temporary storage outage as deleted media. It is **enabled by default** and can be disabled globally or per media server.

The feature covers DUMB-managed storage dependencies such as rclone, NzbDAV, Decypharr, Zurg, AltMount, and CLI Debrid. DUMB maps each operation to affected media servers through configured mount paths; when it cannot safely narrow the relationship, it protects every enabled media server.

!!! important "Protection is not a backup"

    This feature reduces outage risk but cannot reverse an application database change that already occurred. Keep media-server database/config backups, and avoid exposing the media server directly to mount paths that can disappear without warning.

## Planned stop, restart, or update

Before DUMB changes a storage dependency it:

1. checks active playback and library-scan activity;
2. temporarily disables automatic scan triggers and cancels a running scan where the API supports it;
3. stops an idle media server for the safest maintenance path;
4. performs the storage operation;
5. waits for the dependency and mounts to remain healthy for the configured stabilization period; and
6. restores only the scan settings and media-server processes DUMB changed.

Scheduled updates use this safe policy automatically. If playback is active or activity cannot be determined, the update is deferred.

For a manual operation, dmbdb always shows the choice before DUMB pauses or stops a downstream media server:

| Choice | Behavior |
|---|---|
| **Protect & continue** | Guard scans, stop an idle media server, perform the operation, then recover automatically. Available only when activity is known idle/stopped. |
| **Keep server running** | Guard scans but leave the media server running. Existing playback may still fail if it needs data no longer available from the mount. |
| **Stop now & continue** | Stop the media server immediately and continue. This explicitly interrupts active streams. |
| **Defer operation** | Make no lifecycle change. Recommended while playback is active or activity is unknown. |

## Unexpected crash or outage

When a managed storage dependency exits unexpectedly, DUMB guards downstream scans as quickly as possible. Active streams are preserved. If **Stop after users become idle during an outage** is enabled, DUMB stops that media server only after its sessions naturally finish.

After the dependency restarts and remains healthy, the recovery journal restores scan settings and restarts only media servers that DUMB stopped. The journal is stored at `/config/media-protection/state.json` with mode `0600`, so a DUMB restart does not discard an active recovery state.

## Media-server setup

Open the Plex, Jellyfin, or Emby service page and select **Library Protection**.

### Plex

DUMB uses the Plex token it already manages for Plex integration. No second key is required.

The panel also exposes live Plex library preferences:

| Plex setting | Recommended | Why |
|---|---:|---|
| **Empty trash automatically after every scan** | Off | Highest-risk option: an outage-triggered scan can turn unavailable items into permanent removals. |
| **Scan my library automatically** | Off for remote/virtual mounts | Reconnect and filesystem events can be misleading. |
| **Run a partial scan when changes are detected** | On if automatic detection remains enabled | Limits the scan scope. |
| **Update libraries periodically** | Off unless supervised | A scheduled scan can overlap an unattended outage. |
| **Scan interval** | Deployment-specific | Used only when periodic updates remain enabled. |

These controls write directly to Plex. The outage guard snapshots the current values and restores them after recovery; it does not permanently replace the choices saved in the panel.

### Jellyfin and Emby

DUMB installs and starts Jellyfin/Emby, but it does not create an administrator account or application API key during first-run setup. Create a dedicated API key in the media server's own dashboard, then paste it into **Library Protection**.

The key is needed to inspect current sessions, identify and stop a running library scan, temporarily remove scheduled scan triggers, and disable/restore real-time monitoring for each virtual library.

The key is stored in `dumb.media_protection.services`, redacted from DUMB config/API responses and logs, and never sent to the browser after saving. Without a key, DUMB reports **Setup required**, treats activity as unknown, and defers safe unattended maintenance. An operator can still choose an explicit manual override.

## Configuration

```json
{
  "dumb": {
    "media_protection": {
      "enabled": true,
      "recovery_stabilization_seconds": 30,
      "recovery_timeout_seconds": 180,
      "monitor_interval_seconds": 5,
      "services": [
        {
          "process_name": "Jellyfin Media Server",
          "enabled": true,
          "api_key": "REDACTED",
          "stop_when_idle_on_outage": true,
          "protected_mounts": ["/mnt/debrid"]
        }
      ]
    }
  }
}
```

`protected_mounts` is optional. Leave it empty to use DUMB's dependency and `wait_for_mounts` mapping. Use explicit roots when one media server consumes only a subset of several independent mounts.

## Recovery and troubleshooting

- **Operation keeps deferring:** activity is busy or unknown. End the stream, configure the Jellyfin/Emby key, or use an explicit manual override.
- **Protection remains active:** verify the storage process, application health probe, mount state, and directory access. Recovery begins only after all checks remain healthy for the stabilization period.
- **Media server was not restarted:** DUMB restarts only a server it stopped. A server that was already stopped remains stopped.
- **Settings were not restored:** review the active incident and DUMB logs. API authentication or a changed/deleted library can prevent restoration and produces a critical recovery notification.
- **A stream failed under Keep server running:** scan protection does not cache media bytes. Playback still depends on the mount/provider being able to serve uncached ranges.

Because an unexpected process crash and mount disappearance can be nearly simultaneous, outage guarding is best-effort. Planned maintenance provides the strongest guarantee because DUMB applies the guard before stopping the dependency.

---
title: Jellyfin
description: Run Jellyfin inside DUMB as an open-source media server with shared library paths, embedded access, hardware devices, and automated workflows.
icon: lucide/play
---

# Jellyfin (Core Service)

**Jellyfin** is an open-source media server for organizing and streaming your media library. It can be used as an alternative to Plex or Emby.

---

## Setup checklist and remaining work

The checklist guides supported fresh-administrator setup and explicit library creation/reuse. Existing initialized servers are not reinitialized. Supported new-library forms offer an optional initial scan, off by default; review the paths before enabling it. Existing libraries are not rescanned by this creation choice. Choose sharing, remote access, hardware acceleration and playback policy, then test real library access/playback.

Requires the backend setup-arrangement capability. See [Setup checklist and automation](../../features/setup-checklist.md) for retained tasks, coverage and safe retries.


## Service Relationships

| Classification | Role                               |
| -------------- | ---------------------------------- |
| Core Service   | Media server                       |
| Depends On     | Content in `/mnt/debrid`           |
| Optional       | None                               |
| Exposes UI     | Yes (Web UI)                       |

---

## Configuration in `dumb_config.json`

```json
"jellyfin": {
  "enabled": false,
  "process_name": "Jellyfin Media Server",
  "suppress_logging": false,
  "auto_update": false,
  "auto_update_interval": 24,
  "auto_update_start_time": "04:00",
  "pinned_version": "",
  "port": 8096,
  "config_dir": "/jellyfin",
  "config_file": "/jellyfin/config/system.xml",
  "log_file": "/jellyfin/log/jellyfin.log",
  "command": [],
  "env": {}
}
```

### Key Configuration Fields

* `pinned_version`: Optional version pin for Jellyfin updates.
* `port`: Web UI port (default `8096`).
* `config_dir`, `config_file`, `log_file`: Paths for config and logs.
* `command`: DUMB rebuilds the data/config/cache/log arguments during setup. An explicit `--ffmpeg` selection is preserved; otherwise DUMB selects `/usr/lib/jellyfin-ffmpeg/ffmpeg` when installed.

---

## Accessing the UI

* Navigate to: `http://<host>:8096` (default Jellyfin port)
* With service UIs enabled in DUMB, open **Embedded UI** on the Jellyfin service page and sign in to Jellyfin there.

If existing libraries appear at the direct address but not in the iframe, see
[Jellyfin and Emby embedded libraries](../../frontend/service-pages.md#jellyfin-and-emby-libraries).

Fresh Jellyfin installs add the official Jellyfin APT source directly. They do
not require the `add-apt-repository` utility, which is intentionally absent from
the minimized DUMB runtime image.

## Hardware acceleration

DUMB launches Jellyfin as its configured `puid`/`pgid`. With `/dev/dri` present,
DUMB adds its service account to existing `render` and `video` groups at startup.
Managed processes receive those supplementary groups, including after a restart;
Docker `group_add` grants are retained as well. The device's numeric group must
still be accessible inside the container or LXC.

Jellyfin uses its packaged FFmpeg when available. Keep `/usr/bin/ffmpeg` owned by
the distribution package; replacing it with a symlink affects other services.
To use a custom build, supply `--ffmpeg`, followed by its absolute path, in
`jellyfin.command`.

For an Intel-only render-device setup with an installed iHD driver, DUMB defaults
`LIBVA_DRIVER_NAME` to `iHD`. An explicit value in `jellyfin.env` or the controller
environment takes precedence. AMD and mixed-vendor systems retain driver
autodetection. Select the acceleration method and supported codecs in Jellyfin's
**Dashboard → Playback → Transcoding** settings; device passthrough alone does
not enable transcoding.

See [native Proxmox GPU setup](../../deployment/proxmox.md#gpu-passthrough-and-jellyfin)
and [Jellyfin's Intel GPU guide](https://jellyfin.org/docs/general/post-install/transcoding/hardware-acceleration/intel/).

## Media Library Protection

Jellyfin requires an authorized API key before DUMB can inspect sessions and temporarily control scan tasks/library real-time monitoring. Compatible guided first-administrator setup can create a dedicated application key; the checklist offers a separate explicit choice to save that key for Library Protection. You can also create a key in Jellyfin's dashboard and save it under **Library Protection** on the Jellyfin service page. New setup-created protection policies remain disabled until you review their mount scope and enable them. Without usable credentials, unattended storage maintenance is deferred because activity is unknown.

See [Media Library Protection](../../features/media-library-protection.md).

---

## Resources

* [Jellyfin Website](https://jellyfin.org/)
* [Jellyfin GitHub](https://github.com/jellyfin/jellyfin)

---
Title: Plex Media Server
---

# Plex Media Server (Core Service)

**Plex Media Server** serves as the centralized media host for the DUMB ecosystem. It enables playback of collected media through a wide range of client devices and integrates seamlessly with DUMB core orchestrators like Riven, CLI Debrid, Plex Debrid, and Decypharr.

---

## 🔗 Service Relationships

| Classification | Role                             |
| -------------- | -------------------------------- |
| Core Service   | Media Server / Playback Host     |
| Depends On     |                                  |
| Optional       | None                             |
| Exposes UI     | Yes (Web UI on port 32400)       |

---

## 📦 Configuration in `dumb_config.json`

```json
"plex": {
  "enabled": false,
  "process_name": "Plex Media Server",
  "suppress_logging": false,
  "log_level": "INFO",
  "port": 32400,
  "auto_update": false,
  "auto_update_interval": 24,
  "config_dir": "/plex",
  "config_file": "/plex/Plex Media Server/Preferences.xml",
  "log_file": "/plex/Plex Media Server/Logs/Plex Media Server.log",
  "plex_claim": "",
  "friendly_name": "DUMB",
  "command": [],
  "env": {}
}
```

### 🔍 Key Configuration Fields

* `enabled`: Toggle Plex Media Server on or off.
* `plex_claim`: Plex claim token for initial server registration.
* `friendly_name`: The name that appears in the Plex Web App and on local clients.
* `config_dir`: Directory containing Plex server data (including preferences).
* `port`: Default access port (32400).

---

## ⚙️ Setup & Behavior

### 🧰 Requirements

* Plex must have access to:

  * Media directories (local or rclone-mounted).
  * Transcoding cache (if transcoding is enabled).
  * Valid claim token for first-time setup (if not already configured).

### Hardware Transcoding

Hardware-accelerated streaming enables Plex to use the GPU or specialized hardware encoders to offload and speed up transcoding operations, significantly improving performance and lowering CPU usage.

!!! warning "Plex Pass Required"
Hardware-accelerated transcoding is a **premium feature** and requires an active Plex Pass subscription. [Learn more](https://support.plex.tv/articles/115002178853-using-hardware-accelerated-streaming/)

#### 🧪 Docker Setup for Hardware Transcoding

To enable hardware transcoding in a Docker container:

```yaml
devices:
  - /dev/dri:/dev/dri
```

This grants the container access to the host system's Direct Rendering Infrastructure (DRI), which is required for GPU access (e.g., Intel Quick Sync, NVIDIA NVENC).

##### Intel Quick Sync Users

Additional permissions may be needed:

```yaml
group_add:
  - "992"  # Typically 'render' group
  - "993"  # Some systems require both 'render' and 'video'
```

You can confirm the group IDs for your system by running:

```bash
getent group video
getent group render
```

Make sure the Plex container runs with appropriate `PUID` and `PGID` values that also have access to `/dev/dri`.

#### ⚙️ Enabling in Plex Settings

Once the container is running and hardware access is configured:

1. Go to the Plex Web UI: `http://<host>:32400/web`
2. Navigate to: **Settings** > **Transcoder**
3. Enable the checkbox: **Use hardware acceleration when available**
4. (Optional) Enable **Use hardware-accelerated video encoding** for encoding tasks.

#### ✅ Confirming Hardware Transcoding is Active

When a video is playing:

1. Click the **three dots** next to the playback and choose **Stats for Nerds**
2. Look for entries like `hw` or `h264_qsv` or `nvenc` which indicate hardware acceleration.
3. Alternatively, open the **Server Dashboard** during playback and check the stream status for an `(hw)` label next to the transcoding type.

---

!!! tip "Troubleshooting"
If hardware transcoding does not activate:

```
* Ensure your hardware supports it (Intel iGPU, NVIDIA GPU with driver support, etc.)
* Check if `/dev/dri` exists and is mounted into the container
* Review container logs and Plex logs for errors related to transcoding
* Confirm Plex Pass is active and the account used in Plex is signed in and authorized
```

---


### 🛠️ How to Start

#### Utilize the onboarding process

!!! note "The onboarding process can be re-launched from the DUMB Frontend settings menu"

  1. Onboarding will prompt for the Plex Claim Token.
  2. Onboarding will optionally prompt for your Plex Token. If provided, this enables:

    * Enhanced functionality for Plex Pass members (e.g., downloads)
    * Preconfigured integration with other core services like Riven and CLI Debrid


#### Manually
  1. Ensure the `plex` block is properly configured in `dumb_config.json`.
  2. Provide a `plex_claim` token if starting fresh.
  3. Start the container with DUMB orchestration, or manually start the Plex service.
  4. Access via: `http://<host>:32400/web`

---

## 🧩 Integration with Other Services

Plex is designed to serve content collected and maintained by core DUMB services including **Riven**, **CLI Debrid**, **Plex Debrid**, and **Decypharr**. These services fetch, organize, and optionally symlink media content into the mounted directory used by Plex.

!!! note "By default, media content is made available inside the container at `/mnt/debrid` through rclone mounts."

* **Core services** populate `/mnt/debrid` with downloaded or upgraded content.
* Plex scans this location to index and serve the media.

!!! info "If you want to serve media from the host system, bind mount your local media directory into the container and add it as a library path in Plex."

---


## 🌐 Access

* URL: `http://<host>:32400/web`
* Credentials: Managed through Plex.tv account

---

## 📁 Mount and Path Planning

Ensure your media storage is accessible to Plex via the correct container path.

* **Default internal mount**: `/mnt/debrid`
* **Add bind mounts**: for local media stored on the host machine not managed by DUMB.

---

## 🧪 Tips and Troubleshooting

* If the container fails to start due to permissions, ensure Plex has proper access to its `config_dir` and media directories.
* Use `PUID` and `PGID` to match host user permissions.
* Logs can be viewed directly from the **DUMB Frontend**.
* You can also start, stop, restart Plex, and modify the `dumb_config.json` or Plex `Preferences.xml` from the **DUMB Frontend** interface.

---

## 🔗 Resources

* [Plex Official Site](https://www.plex.tv/)
* [Plex Claim Token Page](https://www.plex.tv/claim)
* [Plex Support](https://support.plex.tv/)

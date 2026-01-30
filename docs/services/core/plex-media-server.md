---
title: Plex Media Server
icon: lucide/tv
---

# Plex Media Server (Core Service)

**Plex Media Server** serves as the centralized media host for the DUMB ecosystem. It enables playback of collected media through a wide range of client devices and integrates seamlessly with DUMB core orchestrators like Riven, CLI Debrid, Plex Debrid, and Decypharr.

---

## Service Relationships

| Classification | Role                             |
| -------------- | -------------------------------- |
| Core Service   | Media Server / Playback Host     |
| Depends On     |                                  |
| Optional       | None                             |
| Exposes UI     | Yes (Web UI on port 32400)       |

---

## Configuration in `dumb_config.json`

```json
"plex": {
  "enabled": false,
  "process_name": "Plex Media Server",
  "suppress_logging": false,
  "log_level": "INFO",
  "port": 32400,
  "auto_update": false,
  "auto_update_interval": 24,
  "pinned_version": "",
  "config_dir": "/plex",
  "config_file": "/plex/Plex Media Server/Preferences.xml",
  "log_file": "/plex/Plex Media Server/Logs/Plex Media Server.log",
  "plex_claim": "",
  "friendly_name": "DUMB",
  "dbrepair": {
    "enabled": false,
    "run_before_start": false,
    "interval_minutes": 10080,
    "idle_check_minutes": 5,
    "backoff_multiplier": 2.0,
    "max_backoff_minutes": 60,
    "max_wait_minutes": 0,
    "install_dir": "/data/dbrepair",
    "executable": "DBRepair.sh",
    "sqlite_path": "/usr/lib/plexmediaserver/Plex SQLite",
    "databases_path": "/plex/Plex Media Server/Plug-in Support/Databases",
    "required_args": [],
    "script_args": [
      "auto"
    ],
    "log_file": "/log/plex_dbrepair.log",
    "db_path": "/plex/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db",
    "work_dir": "",
    "command": [],
    "env": {}
  },
  "command": [],
  "env": {}
}
```

### Key Configuration Fields

* `enabled`: Toggle Plex Media Server on or off.
* `plex_claim`: Plex claim token for initial server registration.
* `friendly_name`: The name that appears in the Plex Web App and on local clients.
* `config_dir`: Directory containing Plex server data (including preferences).
* `port`: Default access port (32400).
* `pinned_version`: Pin Plex to a specific version when using manual builds.
* `dbrepair`: Optional DBRepair configuration for scheduled Plex database maintenance.

!!! important  "DUMB does not yet support `port` assignment for Plex Media Server"

---

## Setup & Behavior

### Requirements

Plex must have access to:

  * Media directories (local or rclone-mounted).
  * Transcoding cache (if transcoding is enabled).
  * Valid claim token for first-time setup (if not already configured).

---

## Migrating an Existing Plex Server into DUMB

If you're migrating an existing Plex Media Server into the DUMB container, the process involves preserving your current Plex data directory and ensuring it is placed correctly within the DUMB ecosystem.

---

### Step 1: Locate your existing Plex data directory

Plex keeps its state in a folder named **`Plex Media Server`**. That folder contains:

- `Preferences.xml`
- `Plug-in Support/Databases/` (library DB)
- `Metadata/`, `Media/`, `Cache/`, `Logs/`, and more

Common locations:

| Environment | Typical Plex data path |
|-------------|------------------------|
| Linux (native) | `/var/lib/plexmediaserver/Library/Application Support/Plex Media Server` |
| Linux (snap) | `~/snap/plexmediaserver/common/Library/Application Support/Plex Media Server` |
| Docker | Your mapped volume (example: `/path/to/plex` → `/config`) |

!!! tip "What you need to copy"

    Copy the entire **`Plex Media Server`** folder, not just `Preferences.xml`.

---

### Step 2: Copy the Plex data into DUMB

Whether your current Plex server is running as a Docker container or directly on the host machine, locate its configuration directory. This directory typically contains:

* `Plex Media Server/Preferences.xml`
* `Plex Media Server/Plug-in Support/Databases/...`
* `Plex Media Server/Logs/...`

!!! warning "Stop Plex before copying"

    Stop the existing Plex server before copying data to avoid a partial or corrupted database copy.

Copy this entire Plex configuration directory to the DUMB host's Plex directory:

```bash
# Replace /path/to/existing/plex with the path from your host or old container
rsync -a "/path/to/existing/plex/Plex Media Server" "/path/to/DUMB/plex/"
```

The result should be:

```
DUMB/plex/Plex Media Server/Preferences.xml
DUMB/plex/Plex Media Server/Plug-in Support/Databases/...
```

!!! important "The internal path **must** remain `/plex/Plex Media Server/Preferences.xml` inside the container, unless you follow Step 3 below."

---

### Step 3: Point DUMB to the copied config

!!! note "This is only required if changing the default location (shown below) for Plex configs inside the container"

Update the `dumb_config.json` to ensure the `config_dir` is `/plex`, which is the internal path mounted inside the container.

```json
"plex": {
  "enabled": true,
  "config_dir": "/plex",
  "config_file": "/plex/Plex Media Server/Preferences.xml",
  ...
}
```

---

### Step 4: Verify permissions

Plex must be able to **read and write** the copied files. If you see permission errors, adjust ownership to match the user defined in your Docker compose.

!!! note "Match PUID/PGID ownership"

    The Plex data directory should be owned by the same UID/GID used in the container (`PUID`/`PGID`).  
    Example:

    ```bash
    # Replace 1000:1000 with your container PUID:PGID and adjust the path
    sudo chown -R 1000:1000 /path/to/DUMB/plex
    sudo chmod -R u+rwX,g+rwX /path/to/DUMB/plex
    ```

    If your container uses a different PUID/PGID (for example, `568:568` on some NAS setups), use that instead.

---

### Step 5: Add media content

If you have existing media content from your previous Plex setup:

1. Mount to a custom path (e.g., /mnt/local):

    !!! tip "Custom Path"
        Using /mnt/local or any other custom path allows you to preserve legacy media folder structures separately from DUMB's collection system..

    !!! note "You can also consolidate or symlink these into `/mnt/debrid` if needed."

    Example Docker Compose snippet:

    ```yaml
    volumes:
      - /path/to/old/media/movies:/mnt/local/movies
      - /path/to/old/media/shows:/mnt/local/shows
    ```

2. Update Plex library folders in the Plex Web UI to match the new internal container paths (e.g., `/mnt/local/movies`).

---

### Step 6: Restart and verify

Once configuration and mounts are complete:

1. Start the DUMB container.
2. Access Plex via `http://<host>:32400/web`.
3. Verify:
    * Your old libraries and settings are intact
    * Media paths resolve correctly
    * Server is claimed and signed in to Plex.tv

---

### Optional: reclaim or reconfigure

If you're reusing an old server and want to reset it:

* Delete `Preferences.xml` to force a new setup
* Provide a new `plex_claim` token in `dumb_config.json`

This allows you to re-register the server cleanly if needed.

---

### Summary Table

| Migration Source      | Steps                                                          |
| --------------------- | -------------------------------------------------------------- |
| Plex Docker Container | Copy container's volume contents to `DUMB/plex`                |
| Plex on Host          | Copy `/var/lib/plexmediaserver` or equivalent to `DUMB/plex`   |
| Plex Media            | Bind mount original media directories to `/mnt/debrid` in DUMB |

Once complete, your DUMB-based Plex server should fully replicate your prior setup while gaining the integration benefits of the DUMB ecosystem.

--- 

## How to Start

### Utilize the onboarding process

!!! tip "The onboarding process can be re-launched from the DUMB Frontend settings menu"

  1. Onboarding will prompt for the Plex Claim Token.
  2. Onboarding will optionally prompt for your Plex Token. If provided, this enables:

    * Enhanced functionality for Plex Pass members (e.g., downloads)
    * Preconfigured integration with other core services like Riven and CLI Debrid


### Manually
  1. Ensure the `plex` block is properly configured in `dumb_config.json`.
  2. Provide a `plex_claim` token if starting fresh.
  3. Start the container with DUMB orchestration, or manually start the Plex service.
  4. Access via: `http://<host>:32400/web`

---

## Hardware Transcoding

Hardware-accelerated streaming enables Plex to use the GPU or specialized hardware encoders to offload and speed up transcoding operations, significantly improving performance and lowering CPU usage.

!!! warning "Plex Pass Required"
    Hardware-accelerated transcoding is a **premium feature** and requires an active Plex Pass subscription. [Learn more](https://support.plex.tv/articles/115002178853-using-hardware-accelerated-streaming/)

### Docker Setup for Hardware Transcoding

To enable hardware transcoding in a Docker container:

```yaml
devices:
  - /dev/dri:/dev/dri
```

This grants the container access to the host system's Direct Rendering Infrastructure (DRI), which is required for GPU access (e.g., Intel Quick Sync, NVIDIA NVENC).

### Intel Quick Sync Users

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

### Enabling in Plex Settings

Once the container is running and hardware access is configured:

1. Go to the Plex Web UI: `http://<host>:32400/web`
2. Navigate to: **Settings** > **Transcoder**
3. Enable the checkbox: **Use hardware acceleration when available**
4. (Optional) Enable **Use hardware-accelerated video encoding** for encoding tasks.

### Confirming Hardware Transcoding is Active

When a video is playing:

1. Click the **three dots** next to the playback and choose **Stats for Nerds**
2. Look for entries like `hw` or `h264_qsv` or `nvenc` which indicate hardware acceleration.
3. Alternatively, open the **Server Dashboard** during playback and check the stream status for an `(hw)` label next to the transcoding type.

---

### Monitoring GPU Usage from Inside the Container

You can supplement Plex's built-in tools (like "Stats for Nerds") with real-time GPU monitoring inside the DUMB container.

---

#### Intel iGPU Monitoring

Intel GPUs (e.g., Quick Sync) can be monitored using `intel-gpu-tools`:

```bash
# Enter the container
docker exec -it DUMB bash

# Install the tools (Debian/Ubuntu based images)
apt update && apt install -y intel-gpu-tools

# Launch real-time GPU monitor
intel_gpu_top
```

This provides a live view of the GPU's video encode/decode engines. Look for activity under:

* `Video` or `Video/0` for decoding
* `VideoEnhance` or `Blitter` for scaling and filtering

!!! tip "Use `q` to exit `intel_gpu_top`"

---

#### NVIDIA GPU Monitoring

For NVIDIA GPUs with NVENC/NVDEC support, use the `nvidia-smi` tool:

```bash
# Enter the container
docker exec -it DUMB bash

# If not already installed, install NVIDIA tools
apt update && apt install -y nvidia-smi

# Monitor GPU usage
nvidia-smi
```

Look for the Plex process listed under the `Processes` section. When active transcoding is occurring, you should see:

* Increased `GPU-Util` percentage
* Encoder usage
* Memory allocation from Plex or `Plex Transcoder`

!!! note "If `nvidia-smi` is not recognized, ensure the container is running with the `--gpus all` flag and NVIDIA Docker runtime is enabled on the host."

---

### Troubleshooting GPU Access & Hardware Transcoding

* Confirm the container has access to `/dev/dri` or sometimes `/dev/nvidia*`
* Confirm Plex Pass is active and the account used in Plex is signed in and authorized
* Validate Plex transcoder settings are enabled for hardware use
* Check that Plex is actually transcoding (not Direct Playing)
* Ensure your hardware supports it (Intel iGPU, NVIDIA GPU with driver support, etc.)
* Review container logs and Plex logs for errors related to transcoding

---

## Integration with Other Services

Plex is designed to serve content collected and maintained by core DUMB services including **Riven**, **CLI Debrid**, **Plex Debrid**, and **Decypharr**. These services fetch, organize, and optionally symlink media content into the mounted directory used by Plex.

!!! note "By default, media content is made available inside the container at `/mnt/debrid` through rclone mounts."

* **Core services** populate `/mnt/debrid` with downloaded or upgraded content.
* Plex scans this location to index and serve the media.

!!! info "If you want to serve media from the host system, bind mount your local media directory into the container and add it as a library path in Plex."

---


## Access

* URL: `http://<host>:32400/web`
* Credentials: Managed through Plex.tv account

---

## Mount and Path Planning

Ensure your media storage is accessible to Plex via the correct container path.

* **Default internal mount**: `/mnt/debrid`
* **Add bind mounts**: for local media stored on the host machine not managed by DUMB.

---

## Tips and Troubleshooting

* If the container fails to start due to permissions, ensure Plex has proper access to its `config_dir` and media directories.
* Use `PUID` and `PGID` to match host user permissions.
* Logs can be viewed directly from the **DUMB Frontend**.
* You can also start, stop, restart Plex, and modify the `dumb_config.json` or Plex `Preferences.xml` from the **DUMB Frontend** interface.

---

## Resources

* [Plex Official Site](https://www.plex.tv/)
* [Plex Claim Token Page](https://www.plex.tv/claim)
* [Plex Support](https://support.plex.tv/)

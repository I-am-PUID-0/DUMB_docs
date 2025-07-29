---
title: rclone
---

rclone is a command-line tool used in DUMB to mount cloud storage—specifically Debrid services like Real-Debrid—into the container as a local file system. It works in tandem with Zurg and is configured automatically during container startup.

---

## ⚙️ Configuration Settings in `dumb_config.json`
Each `rclone` instance is defined under the `rclone.instances` section in `dumb_config.json`. Example:
```json
"rclone": {
    "instances": {
        "RealDebrid": {
            "enabled": false,
            "core_service": "",
            "process_name": "rclone w/ RealDebrid",
            "suppress_logging": false,
            "log_level": "INFO",
            "key_type": "RealDebrid",
            "zurg_enabled": true,
            "decypharr_enabled": false,
            "mount_dir": "/mnt/debrid",
            "mount_name": "rclone_RD",
            "cache_dir": "/cache",
            "config_dir": "/config",
            "config_file": "/config/rclone.config",
            "log_file": "/log/rclone_w_realdebrid.log",
            "zurg_config_file": "/zurg/RD/config.yml",
            "command": [],
            "api_key": ""
        }
    }
},
```

### 🔍 Configuration Key Descriptions
- **`enabled`**: Whether this rclone instance should be started.
- **`core_service`**: Flag to indicate the associated core service during onboarding.
- **`process_name`**: The label used in logs and process tracking.
- **`suppress_logging`**: If `true`, disables log output for this service.
- **`log_level`**: Logging verbosity level (e.g., `DEBUG`, `INFO`).
- **`key_type`**: The debrid service to use (`RealDebrid`, `AllDebrid`, etc.).
- **`zurg_enabled`**: Whether Zurg is linked to this rclone mount.
- **`decypharr_enabled`**: Whether Decypharr is linked to this rclone mount.
- **`mount_dir`**: The container path where the remote drive is to be mounted.
- **`mount_name`**: The rclone remote name.
- **`cache_dir`**: Directory used by rclone for VFS caching, when enabled.
- **`config_dir`**: Directory where the rclone config file is stored.
- **`config_file`**: Full path to the rclone configuration file.
- **`zurg_config_file`**: Full path to the Zurg config file for this instance.
- **`command`**: Custom CLI arguments to be appended to rclone at runtime.
- **`api_key`**: (Optional) Debrid API key, used if Zurg is not linked.

### 🔁 API Key Behavior
- If `zurg_enabled` & `zurg_config_file` are **set**: DUMB will configure rclone to use **Zurg's WebDAV** endpoint. The API key should be defined in the **Zurg instance**, not the rclone one.
- If `decypharr_enabled` is **set**: DUMB will configure rclone to use **Decypharr's WebDAV** endpoint. The API key should be defined in the **Decypharr** config.
- If `decypharr_enabled`, `zurg_enabled` & `zurg_config_file` are **unset or blank**: DUMB will configure rclone to **directly connect to the debrid service**, and the API key must be set in the rclone instance.

### ➕ Adding More Instances
Users can define additional rclone instances by duplicating the structure and ensuring:

- Each `instance name` is **unique**
- Each `process_name` is **unique**
- The `key_type` must match the type of Debrid service used (e.g., `RealDebrid`, `AllDebrid`, `TorBox`, `Premiumize`)

!!! Note "The below example creates a zurg attached rclone mount and a direct debrid connection rclone mount"

Example:
```json
"rclone": {
  "instances": {
    "RealDebrid": {
      "enabled": true,
      "core_service": "",      
      "process_name": "rclone w/ RealDebrid",
      "suppress_logging": false,
      "log_level": "INFO",
      "key_type": "RealDebrid",
      "zurg_enabled": true,
      "decypharr_enabled": false,      
      "mount_dir": "/mnt/debrid",
      "mount_name": "rclone_RD",
      "cache_dir": "/cache",
      "config_dir": "/config",
      "config_file": "/config/rclone.config",
      "zurg_config_file": "/zurg/RD/config.yml",
      "command": [],
      "api_key": ""
    },    
    "AllDebrid": {
      "enabled": false,
      "core_service": "",      
      "process_name": "rclone w/ AllDebrid",
      "suppress_logging": false,
      "log_level": "INFO",
      "key_type": "AllDebrid",
      "zurg_enabled": false,
      "decypharr_enabled": false,      
      "mount_dir": "/mnt/debrid",
      "mount_name": "rclone_AD",
      "cache_dir": "/cache",
      "config_dir": "/config",
      "config_file": "/config/rclone.config",
      "zurg_config_file": "",
      "command": [],
      "api_key": "YOUR DEBRID API KEY"
    }
  }
}
```

---

## 🧠 Features Enabled by DUMB

### 🔄 Auto-Generated `rclone.config`
DUMB generates the required `rclone.config` file at runtime. This includes:
```ini
[rclone_RD]
type = webdav
url = http://localhost:9999/dav
vendor = other
pacer_min_sleep = 0
```
This eliminates the need for any manual setup.

### 🔒 Debrid API Integration
DUMB supports multiple Debrid configurations using a combination of `rclone` and `zurg` instances.

### 🧲 Works With Zurg
Zurg exposes a WebDAV server which rclone mounts using the configuration above.

### 🔧 rclone Flags via Environment Variables
All `--flag=value` options in rclone can be passed as environment variables. Format:
```bash
RCLONE_<OPTION_NAME_UPPERCASE>=<value>
```
Example:
```bash
RCLONE_VFS_CACHE_MODE=full
RCLONE_BUFFER_SIZE=64M
RCLONE_ATTR_TIMEOUT=30s
```
This enables advanced control without modifying CLI or config files.

For more info, see [rclone docs](https://rclone.org/docs/#environment-variables).

---

## 📚 Optimizing rclone for Media Server Usage

To improve streaming performance and reduce excessive bandwidth usage when using rclone with media servers (e.g., Plex, Jellyfin, Emby), consider tuning the mount behavior using additional flags.

!!! warning "VFS cache will use hard drive space, so ensure you set an appropriate max size for your system"


You can apply these flags in three ways:

1. **As environment variables** in Docker Compose or `.env` (Recommended):

    !!! note
        Applying the below will make these settings applicable to all rclone instances.

        If you prefer to apply settings per-instance, then see option 2 or 3.

    ```env
    RCLONE_VFS_CACHE_MODE=full
    RCLONE_VFS_READ_CHUNK_SIZE=1M
    RCLONE_VFS_READ_CHUNK_SIZE_LIMIT=32M
    RCLONE_BUFFER_SIZE=64M
    RCLONE_DIR_CACHE_TIME=10s
    RCLONE_VFS_CACHE_MAX_AGE=6h
    RCLONE_VFS_CACHE_MAX_SIZE=100G
    RCLONE_ATTR_TIMEOUT=1s
    RCLONE_TPSLIMIT=10
    RCLONE_TPSLIMIT_BURST=10
    ```

2. **By modifying the `command` list** in the `dumb_config.json` rclone instance:

    !!! note 
        The `command` field is empty by default (`"command": []`) because DUMB generates the rclone command dynamically during setup and applies it in memory.

        If you add custom arguments to the `command` list, it will override the auto-generated defaults. 

        You will be responsible for maintaining all required options, such as `--mount-name` and `--mount-dir`. 

        To revert to default behavior, simply clear the field again by setting `"command": []`.

      Example default command DUMB generates:
      ```json
      "command": [
        "rclone",
        "mount",
        "rclone_RD:",
        "/mnt/debrid/rclone_RD",
        "--config", "/config/rclone.config",
        "--uid=1000",
        "--gid=1000",
        "--allow-other",
        "--poll-interval=0",
        "--dir-cache-time=10s",
        "--allow-non-empty"
      ]
      ```

      To apply performance optimizations:
      ```json
      "command": [
        "rclone",
        "mount",
        "rclone_RD:",
        "/mnt/debrid/rclone_RD",
        "--config", "/config/rclone.config",
        "--uid=1000",
        "--gid=1000",
        "--allow-other",
        "--poll-interval=0",
        "--dir-cache-time=10s",
        "--allow-non-empty",
        "--vfs-cache-mode=full",
        "--vfs-read-chunk-size=1M",
        "--vfs-read-chunk-size-limit=32M",
        "--buffer-size=64M",
        "--vfs-cache-max-age=6h",
        "--vfs-cache-max-size=100G",
        "--attr-timeout=1s",
        "--tpslimit=10",
        "--tpslimit-burst=10"
      ]
      ```

3. **Using the DUMB Frontend** to edit the instance config and add these options under `command`.

    - Use the **"Apply in Memory"** button to test changes without saving. This temporarily updates the in-memory config.
    - Use the **"Save to File"** button to persist changes to `dumb_config.json`.
    - After either action, press the **"Restart"** button for the changes to take effect.

### 🌐 Settings Description

| Setting                           | Value     | Description                                                                     |
|-----------------------------------|-----------|---------------------------------------------------------------------------------|
| `--config`                        | `/config/rclone.config`   | Path to the rclone config file generated by DUMB.                |
| `--uid`                           | `1000`                    | UID to mount as (Linked to `PUID`).                             |
| `--gid`                           | `1000`                    | GID to mount as (Linked to `PGID`).                             |
| `--allow-other`                   | *(enabled)*               | Allows other processes (like Plex) to access the mount.         |
| `--poll-interval`                 | `0`                       | Disables polling for changes (not supported by debrid remotes). |
| `--dir-cache-time`                | `10s`                     | Cache directory structure for 10 seconds.                       |
| `--allow-non-empty`               | *(enabled)*               | Allows mounting to non-empty directories.                       |
| `--vfs-cache-mode`                | `full`       | Allows writing & deletion, necessary for media server interaction.         |
| `--vfs-read-chunk-size`           | `1M`           | Minimizes initial bandwidth usage per file during scans.                   |
| `--vfs-read-chunk-size-limit`     | `32M`          | Allows efficient chunking during actual playback.                          |
| `--buffer-size`                   | `64M`          | Buffers streaming into RAM per open file (adjust to your available RAM).   |
| `--vfs-cache-max-age`             | `6h`           | Removes old cache files to preserve space.                                 |
| `--vfs-cache-max-size`            | `100G`         | Limits total disk cache size.                                              |
| `--attr-timeout`                  | `1s`           | Prevents stale attribute caching.                                          |
| `--tpslimit` / `--tpslimit-burst` | `10`           | Prevents overwhelming debrid APIs with too many requests.                  |


### ⚡ Buffer Size Tips
Adjust `--buffer-size` based on the system RAM:

| System RAM     | Recommended `--buffer-size` |
|----------------|-----------------------------|
| < 4 GB         | `16M`                       |
| 4–8 GB         | `32M–64M`                   |
| 8–16 GB        | `128M–256M`                 |
| > 16 GB        | `256M–512M+`                |

--- 

## 📂 Default Mount Structure

DUMB uses a predictable internal mount layout within the container to organize mounted debrid services and their symlinks when configured by the onboarding process.

!!! note "The below convention is automatically followed when using the onboarding system to configure core services."

### 📁 Root Mount Directory

* `/mnt/debrid` is the root mount location inside the container.

### 🛆 rclone Mount Targets

* Each rclone mount uses the core service name as its subdirectory.

  * For example:

    * Core service `riven` → `/mnt/debrid/riven`
    * Core service `decypharr` → `/mnt/debrid/decypharr`

### 🔗 Symlink Directories

* Core services that generate symlinks (e.g., Riven, Decypharr) will place them in subdirectories named with the pattern: `<core_service>_symlinks`

  * For example:

    * `/mnt/debrid/riven_symlinks`
    * `/mnt/debrid/decypharr_symlinks`

This naming convention makes it easy to identify and separate raw debrid mounts from symbolic links created for media server compatibility.

---

## ⚙️ Mount Propagation

!!! note "/mnt/debrid:rshared"    
    The `:rshared` must be included in order to support [mount propagation](https://docs.docker.com/storage/bind-mounts/#configure-bind-propagation) for rclone to the host when exposing the raw debrid files/links to an external container; e.g., the arrs or a media server.

    `:rshared` is not required when using the default configuration leveraging the internal media server or when not utilizing [Decypharr](../core/decypharr.md)

Mount propagation controls how mount events (like new mounts created inside the container) are shared between the host and the container.

In the context of DUMB, mount propagation is critical for ensuring that media servers (e.g., Plex, Jellyfin) running **OUTSIDE** the container can see and access the dynamically-mounted cloud content that rclone brings in **inside** the container.

### 🔗 Required Propagation Flags

When mounting a path like `/mnt/debrid` from the host into the DUMB container, the bind mount must include **[mount propagation](https://docs.docker.com/storage/bind-mounts/#configure-bind-propagation)** flags to allow sub-mounts (e.g., `/mnt/debrid/riven`, `/mnt/debrid/decypharr`, etc.) to be visible **OUTSIDE** the container.

#### ✅ Recommended Flag: `:rshared`

Example:

```yaml
docker-compose.yml:
  volumes:
    - /home/username/docker/DUMB/mnt/debrid:/mnt/debrid:rshared
```

Explanation:

* `:rshared` ensures two-way mount propagation.
* Any mount created inside `/mnt/debrid` in the **container** will also appear in the **host**, and vice versa.

#### Alternative: `:rslave`

* This is a safer but one-way variant.
* Host will see container mounts, but not the other way around.

Use `:rslave` **only if** you do not need to propagate mounts **from the host into the container**.

---

### ⚠️ Common Issues Without Propagation

* You may not see rclone mounts or Zurg's WebDAV mount in `/mnt/debrid` on the host.
* Media servers running on the host or in other containers may report missing files or empty directories.
* Decypharr and similar tools relying on externally (from the container) mounted paths may fail to operate correctly.

---

### 🔧 Host System Requirements
!!! note "mount --make-rshared /"

    Most Linux distributions support mount propagation. However, the base path must be a shared or slave mount, or mount propagation will not function correctly.

    See the [rclone FAQ](../../faq/rclone.md#error-response-from-daemon-path-yourhostpathmnt-is-mounted-on--but-it-is-not-a-shared-mount) for related troubleshooting.

To use mount propagation:

* The host filesystem **must support it** (most Linux distributions do).
* The base mount point (e.g., `/mnt/debrid`) must itself be a **shared** or **slave** mount.

### ✅ How to Check

You can verify the current propagation mode using the `mount` or `findmnt` command:

```bash
findmnt -o TARGET,PROPAGATION /mnt/debrid
```

or:

```bash
mount | grep /mnt/debrid
```

Look for one of these at the end of the line:

* `shared:` → shared mount
* `slave:` → slave mount
* `private:` → not propagating (default)

### 🛠️ How to Enable

To ensure the base directory allows propagation:

```bash
mount --make-shared /mnt/debrid
```

Or to make **all** mounts shared (advanced users only):

```bash
mount --make-rshared /
```

!!! warning
    These commands modify mount flags at runtime and will not persist across reboots. To persist them, you may need to update your systemd unit files or `/etc/fstab` with the appropriate `shared` propagation settings.

    See the [rclone FAQ](../../faq/rclone.md#error-response-from-daemon-path-yourhostpathmnt-is-mounted-on--but-it-is-not-a-shared-mount) for additional details


### 📅 Best Practices

* Always prefer `:rshared` for `/mnt/debrid` in **DUMB** container mounts when external access to the mounts is needed.
* Use `:rslave` in **consumer containers** (e.g., Plex, Sonarr, Radarr) for safer downstream propagation.
* Avoid `:rw` without a propagation flag—it won't propagate sub-mounts at all.
* Verify mounts with `findmnt` or `mount` on host and inside containers.

---

### 📊 Summary Table for Mount Propagation Use Cases

| Propagation Mode    | Container → Host | Host → Container | Used For                                       | Notes                                                                     |
| ------------------- | ---------------- | ---------------- | ---------------------------------------------- | ------------------------------------------------------------------------- |
| `rshared`           | Yes              | Yes              | `/mnt/debrid` in DUMB (for external consumers) | Required when external services (e.g., arrs, external Plex) access mounts |
| `rslave`            | Yes              | No               | Containers like Plex, Sonarr, Radarr           | Safer for downstream-only visibility of mounts                            |
| `private` (default) | No               | No               | Internal-only setups using DUMB's media server | Suitable when no external container needs access to rclone mounts         |

The `rshared` flag should be reserved for DUMB's own mount directory so other services can inherit its mounts, while `rslave` is appropriate for media servers that only need read access to what DUMB exposes. `private` can be used safely if no external mount visibility is needed (e.g., with built-in media server only).

---

## 💻 Accessing rclone Inside the Container
To run rclone commands manually:
```bash
docker exec -it DUMB /bin/bash
rclone listremotes
rclone mount rclone_RD: /mnt/test
```

---

## 🧠 Tips
- Mounts are bind-mounted into the container by default.
- If you mount `/mnt/debrid/` to the host with the `:rshared` flag you will see all Zurg-fetched content.
- Use the `RCLONE_LOG_LEVEL` env var to control verbosity.

---

## 📚 Resources
- [rclone Documentation](https://rclone.org/)
- [WebDAV Docs](https://rclone.org/webdav/)
- [rclone Environment Variables](https://rclone.org/docs/#environment-variables)

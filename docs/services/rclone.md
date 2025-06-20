# rclone

rclone is a command-line tool used in DMB to mount cloud storage—specifically Debrid services like Real-Debrid—into the container as a local file system. It works in tandem with Zurg and is configured automatically during container startup.

---

## ⚙️ Configuration Settings in `dmb_config.json`
Each `rclone` instance is defined under the `rclone.instances` section in `dmb_config.json`. Example:
```json
"rclone": {
  "instances": {
    "RealDebrid": {
      "enabled": true,
      "process_name": "rclone w/ RealDebrid",
      "suppress_logging": false,
      "log_level": "INFO",
      "key_type": "RealDebrid",
      "zurg_enabled": true,
      "mount_dir": "/data",
      "mount_name": "rclone_RD",
      "cache_dir": "/cache",
      "config_dir": "/config",
      "config_file": "/config/rclone.config",
      "zurg_config_file": "/zurg/RD/config.yml",
      "command": [],
      "api_key": ""
    }
  }
},
```

### 🔍 Configuration Key Descriptions
- **`enabled`**: Whether this rclone instance should be started.
- **`process_name`**: The label used in logs and process tracking.
- **`suppress_logging`**: If `true`, disables log output for this service.
- **`log_level`**: Logging verbosity level (e.g., `DEBUG`, `INFO`).
- **`key_type`**: The debrid service to use (`RealDebrid`, `AllDebrid`, etc.).
- **`zurg_enabled`**: Whether Zurg is linked to this rclone mount.
- **`mount_dir`**: The container path where the remote drive is to be mounted.
- **`mount_name`**: The rclone remote name.
- **`cache_dir`**: Directory used by rclone for VFS caching, when enabled.
- **`config_dir`**: Directory where the rclone config file is stored.
- **`config_file`**: Full path to the rclone configuration file.
- **`zurg_config_file`**: Full path to the Zurg config file for this instance.
- **`command`**: Custom CLI arguments to be appended to rclone at runtime.
- **`api_key`**: (Optional) Debrid API key, used if Zurg is not linked.

### 🔁 API Key Behavior
- If `zurg_enabled` & `zurg_config_file` are **set**: DMB will configure rclone to use **Zurg's WebDAV** endpoint. The API key should be defined in the **Zurg instance**, not the rclone one.
- If `zurg_enabled` & `zurg_config_file` are **unset or blank**: **(Future release)** DMB will configure rclone to **directly connect to the debrid service**, and the API key must be set in the rclone instance.

### ➕ Adding More Instances
Users can define additional rclone instances by duplicating the structure and ensuring:

- Each `instance name` is **unique**
- Each `process_name` is **unique**
- The `key_type` must match the type of Debrid service used (e.g., `RealDebrid`, `AllDebrid`, `TorBox`, `Premiumize`)

Example:
```json
"rclone": {
  "instances": {
    "RealDebrid": {
      "enabled": true,
      "process_name": "rclone w/ RealDebrid",
      "suppress_logging": false,
      "log_level": "INFO",
      "key_type": "RealDebrid",
      "zurg_enabled": true,
      "mount_dir": "/data",
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
      "process_name": "rclone w/ AllDebrid",
      "suppress_logging": false,
      "log_level": "INFO",
      "key_type": "AllDebrid",
      "zurg_enabled": false,
      "mount_dir": "/data",
      "mount_name": "rclone_AD",
      "cache_dir": "/cache",
      "config_dir": "/config",
      "config_file": "/config/rclone.config",
      "zurg_config_file": "",
      "command": [],
      "api_key": ""
    }
  }
}
```

---

## 🧠 Features Enabled by DMB

### 🔄 Auto-Generated `rclone.config`
DMB generates the required `rclone.config` file at runtime. This includes:
```ini
[rclone_RD]
type = webdav
url = http://localhost:9999/dav
vendor = other
pacer_min_sleep = 0
```
This eliminates the need for any manual setup.

### 🔒 Debrid API Integration
DMB supports multiple Debrid configurations **(Future release)** using a combination of `rclone` and `zurg` instances.

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

2. **By modifying the `command` list** in the `dmb_config.json` rclone instance:

    !!! note 
        The `command` field is empty by default (`"command": []`) because DMB generates the rclone command dynamically during setup and applies it in memory.

        If you add custom arguments to the `command` list, it will override the auto-generated defaults. 

        You will be responsible for maintaining all required options, such as `--mount-name` and `--mount-dir`. 

        To revert to default behavior, simply clear the field again by setting `"command": []`.

      Example default command DMB generates:
      ```json
      "command": [
        "rclone",
        "mount",
        "rclone_RD:",
        "/data/rclone_RD",
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
        "/data/rclone_RD",
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

3. **Using the DMB Frontend** to edit the instance config and add these options under `command`.

    - Use the **"Apply in Memory"** button to test changes without saving. This temporarily updates the in-memory config.
    - Use the **"Save to File"** button to persist changes to `dmb_config.json`.
    - After either action, press the **"Restart"** button for the changes to take effect.

### 🌐 Settings Description

| Setting                           | Value     | Description                                                                     |
|-----------------------------------|-----------|---------------------------------------------------------------------------------|
| `--config`                        | `/config/rclone.config`   | Path to the rclone config file generated by DMB.                |
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

## 💻 Accessing rclone Inside the Container
To run rclone commands manually:
```bash
docker exec -it DMB /bin/bash
rclone listremotes
rclone mount rclone_RD: /mnt/test
```

---

## 🧠 Tips
- Mounts are bind-mounted into the container by default.
- If you mount `/data` to the host, you will see all Zurg-fetched content.
- Use the `RCLONE_LOG_LEVEL` env var to control verbosity.

---

## 📚 Resources
- [rclone Documentation](https://rclone.org/)
- [WebDAV Docs](https://rclone.org/webdav/)
- [rclone Environment Variables](https://rclone.org/docs/#environment-variables)

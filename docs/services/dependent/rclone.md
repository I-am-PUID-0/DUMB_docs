---
title: rclone
description: Set up DUMB-managed rclone mounts, choose cache settings, share media with external containers, and understand provider credentials and paths.
icon: lucide/hard-drive
---

# rclone

rclone exposes a remote source as files inside DUMB. Depending on the selected workflow, that source can be Zurg, a direct Debrid endpoint, InfiniDysk, or Decypharr WebDAV. DUMB prepares the managed mount; the source service must be ready before it can serve files.

---

## First start

Choose your mount through the parent workflow in onboarding; DUMB creates the corresponding rclone instance where that workflow needs one. You do not need to assemble a command to use the standard setup.

1. Check that the source service, such as Zurg or InfiniDysk, is ready.
2. Open the rclone service page and review its mount and cache locations.
3. Confirm your media server can read the same absolute paths, including symlink targets.
4. Test playback and seeking before changing cache or concurrency settings.

For a media server outside DUMB, also review [mount propagation](#mount-propagation).

<details class="geek-details" markdown="1">
<summary>Technical details: configuration reference</summary>

## Configuration Settings in `dumb_config.json`
Each `rclone` instance is defined under the `rclone.instances` section in `dumb_config.json`. Example:
```json
{
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
            "api_key": "",
            "username": "",
            "password": "",
            "customer_id": ""
        }
    }
}
}
```

### Configuration Key Descriptions
- **`enabled`**: Whether this rclone instance should be started.
- **`core_service`**: Flag to indicate the associated core service(s) during onboarding.
- **`process_name`**: The label used in logs and process tracking.
- **`suppress_logging`**: Suppresses service messages in the main DUMB output.
- **`log_level`**: Logging verbosity level (e.g., `DEBUG`, `INFO`).
- **`key_type`**: The debrid or WebDAV service to use (`RealDebrid`, `AllDebrid`, `InfiniDysk`, etc.).
- **`zurg_enabled`**: Whether Zurg is linked to this rclone mount.
- **`decypharr_enabled`**: Whether Decypharr is linked to this rclone mount.
- **`mount_dir`**: The container path where the remote drive is to be mounted.
- **`mount_name`**: The rclone remote name.
- **`cache_dir`**: Directory used by rclone for VFS caching, when enabled.
- **`config_dir`**: Directory where the rclone config file is stored.
- **`config_file`**: Full path to the rclone configuration file.
- **`zurg_config_file`**: Full path to the Zurg config file for this instance.
- **`command`**: Saved command and tunable arguments. DUMB reconciles required mount, identity, cache-path, and provider flags during setup.
- **`api_key`**: (Optional) Debrid API key, used if Zurg is not linked.
- **`username`** / **`password`**: Optional direct WebDAV/FTP login credentials for providers that require account login instead of only an API key, such as direct `TorBox`, `TorBox-FTP`, and direct `RealDebrid` mounts.
- **`customer_id`**: Optional Premiumize customer ID for direct Premiumize WebDAV mounts.

### API Key Behavior

!!! tip "API Key Configuration"
    The API key location depends on your rclone configuration:

    - **Zurg enabled**: API key should be defined in the **Zurg instance**, not the rclone one.
    - **Decypharr enabled**: API key should be defined in the **Decypharr** config.
    - **InfiniDysk**: Credentials read from `WEBDAV_USER`/`WEBDAV_PASSWORD` or InfiniDysk database. The rclone `api_key` field is ignored.
    - **Direct AllDebrid connection**: `api_key` must be set in the rclone instance when both `decypharr_enabled` and `zurg_enabled` are unset or blank.
    - **Direct TorBox / TorBox-FTP connection**: Set `username` to your TorBox email and `password` to your TorBox account password.
    - **Direct Premiumize connection**: Set `customer_id` and `api_key`.

### Adding More Instances
Users can define additional rclone instances by duplicating the structure in the runtime `/config/dumb_config.json` file and restarting DUMB. The DUMB UI can edit rclone instances after they already exist, including instances created by onboarding or service automation.

- Each `instance name` is **unique**
- Each `process_name` is **unique**
- The `key_type` must match the type of Debrid or WebDAV service used (e.g., `RealDebrid`, `AllDebrid`, `TorBox`, `Premiumize`, `InfiniDysk`)
- Direct WebDAV/FTP credential fields such as `username`, `password`, and `customer_id` are valid rclone instance keys and should persist across restarts.

!!! example "Multiple Instances"
    The below example creates a zurg attached rclone mount and a direct debrid connection rclone mount.

Example:
```json
{
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
      "log_file": "/log/rclone_w_realdebrid.log",
      "zurg_config_file": "/zurg/RD/config.yml",
      "command": [],
      "api_key": "",
      "username": "",
      "password": "",
      "customer_id": ""
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
      "log_file": "/log/rclone_w_alldebrid.log",
      "zurg_config_file": "",
      "command": [],
      "api_key": "YOUR DEBRID API KEY",
      "username": "",
      "password": "",
      "customer_id": ""
    },
    "TorBox": {
      "enabled": false,
      "core_service": "",
      "process_name": "rclone w/ TorBox",
      "suppress_logging": false,
      "log_level": "INFO",
      "key_type": "TorBox",
      "zurg_enabled": false,
      "decypharr_enabled": false,
      "mount_dir": "/mnt/debrid",
      "mount_name": "rclone_TB",
      "cache_dir": "/cache",
      "config_dir": "/config",
      "config_file": "/config/rclone.config",
      "log_file": "/log/rclone_w_torbox.log",
      "zurg_config_file": "",
      "command": [],
      "api_key": "",
      "username": "YOUR TORBOX EMAIL",
      "password": "YOUR TORBOX PASSWORD",
      "customer_id": ""
    }
  }
}
}
```

---

</details>

## Features Enabled by DUMB

### Auto-Generated `rclone.config`
DUMB generates the required `rclone.config` file at runtime. This includes:
```ini
[rclone_RD]
type = webdav
url = http://localhost:9999/dav
vendor = other
pacer_min_sleep = 0
```
This eliminates the need for any manual setup.

### Debrid API Integration
DUMB supports multiple Debrid configurations using a combination of `rclone` and `zurg` instances.

### Works With Zurg
Zurg exposes a WebDAV server which rclone mounts using the configuration above.

### rclone Flags via Environment Variables
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

## Optimizing rclone for Media Server Usage

For an InfiniDysk-backed rclone instance, DUMB can benchmark bounded profiles against
the live WebDAV/provider path and produce a deployment-specific report. Open the
**Rclone Optimizer** tab on that rclone service page. The job uses an isolated
read-only shadow mount/cache, measures first byte and startup-buffer time, and
never applies its recommendation automatically. The report shows the complete
optimizer-relevant effective settings for every candidate, distinguishing
actually varied streaming values from fixed constraints, InfiniDysk recommendations,
bundled assumptions, and preserved flags; it also verifies that shadow mounts and test artifacts are
removed before a job completes. Content discovery scans the
InfiniDysk `content/<category>` paths DUMB derives from enabled Arr instances, but
measured reads use safely resolved mount-relative paths on isolated shadow mounts
instead of the production mount. Stop the media server and wait until InfiniDysk has
no imports, library ingestion, or unrelated active reads before starting a test;
concurrent activity skews results and increases provider load. See the
[Rclone Streaming Optimizer](../../features/rclone-optimizer.md) guide for content
selection, provider-risk limits, reports, apply, and rollback behavior. The
provider-evidence report always exposes its aggregate Providers, Retries, Bytes,
Provider wait, and Connection wait fields, including an explicit unavailable
state when InfiniDysk did not retain a candidate-matched trace. Applying or rolling
back settings verifies removal of the previous production FUSE mount before
rclone is restarted and requires the replacement mount to remain accessible.
For InfiniDysk, fresh DUMB-generated commands default both `--dir-cache-time` and
`--vfs-cache-max-age` to `1w`. The optimizer recommends at least that value and
preserves longer existing values. The long directory cache relies on InfiniDysk's
RC notifications to invalidate changed paths; the report warns when that RC
connection is disabled, mismatched, or unreachable. The long VFS cache age keeps
recently streamed data warm, while `--vfs-cache-max-size` continues to bound disk
use. These are InfiniDysk operational recommendations, not benchmark-scored values.

To improve streaming performance and reduce excessive bandwidth usage when using rclone with media servers (e.g., Plex, Jellyfin, Emby), consider tuning the mount behavior using additional flags.

!!! note "The examples below are generic"

    The `10s` directory-cache and `6h` VFS-cache-age values below are generic
    examples for older or non-InfiniDysk mounts. Do not copy those shorter values
    over DUMB's InfiniDysk defaults. For an InfiniDysk-backed mount, use the optimizer's
    `1w` minimum guidance (or retain a longer existing value) and keep InfiniDysk's
    rclone RC notification connection healthy.

!!! warning "VFS cache will use hard drive space, so ensure you set an appropriate max size for your system"


You can apply these flags in three ways:

=== "Environment Variables (Recommended)"

    Apply settings as environment variables in Docker Compose or `.env`:

    !!! note
        Applying the below will make these settings applicable to all rclone instances.

        If you prefer to apply settings per-instance, then see the other tabs.

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

=== "Command Array in Config"

    Modify the `command` list in the `dumb_config.json` rclone instance:

    !!! note 
        The `command` field is empty by default (`"command": []`) because DUMB generates the rclone command dynamically during setup and applies it in memory.

        Saved tunable arguments in the `command` list are preserved. DUMB still
        reconciles required mount, identity, cache-path, and provider-specific
        flags during setup.

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

=== "DUMB Frontend"

    Use the DUMB Frontend to edit the instance config and add these options under `command`.

    - Use the **"Apply in Memory"** button to test changes without saving. This temporarily updates the in-memory config.
    - Use the **"Save to File"** button to persist changes to `dumb_config.json`.
    - After either action, press the **"Restart"** button for the changes to take effect.

### Settings Description

| Setting                           | Value     | Description                                                                     |
|-----------------------------------|-----------|---------------------------------------------------------------------------------|
| `--config`                        | `/config/rclone.config`   | Path to the rclone config file generated by DUMB.                |
| `--uid`                           | `1000`                    | UID to mount as (Linked to `PUID`).                             |
| `--gid`                           | `1000`                    | GID to mount as (Linked to `PGID`).                             |
| `--allow-other`                   | *(enabled)*               | Allows other processes (like Plex) to access the mount.         |
| `--poll-interval`                 | `0`                       | Disables polling for changes (not supported by debrid remotes). |
| `--dir-cache-time`                | `10s`                     | Cache directory structure for 10 seconds.                       |
| `--rc` / `--rc-addr`              | first available from `5572` | Enables the local rclone control API; DUMB avoids configured and active RC ports. |
| `--allow-non-empty`               | *(enabled)*               | Allows mounting to non-empty directories.                       |
| `--vfs-cache-mode`                | `full`       | Allows writing & deletion, necessary for media server interaction.         |
| `--vfs-read-chunk-size`           | `1M`           | Minimizes initial bandwidth usage per file during scans.                   |
| `--vfs-read-chunk-size-limit`     | `32M`          | Allows efficient chunking during actual playback.                          |
| `--buffer-size`                   | `64M`          | Buffers streaming into RAM per open file (adjust to your available RAM).   |
| `--vfs-cache-max-age`             | `6h`           | Removes old cache files to preserve space.                                 |
| `--vfs-cache-max-size`            | `100G`         | Limits total disk cache size.                                              |
| `--attr-timeout`                  | `1s`           | Prevents stale attribute caching.                                          |
| `--tpslimit` / `--tpslimit-burst` | `10`           | Prevents overwhelming debrid APIs with too many requests.                  |


### Buffer Size Tips
Adjust `--buffer-size` based on the system RAM:

| System RAM     | Recommended `--buffer-size` |
|----------------|-----------------------------|
| < 4 GB         | `16M`                       |
| 4–8 GB         | `32M–64M`                   |
| 8–16 GB        | `128M–256M`                 |
| > 16 GB        | `256M–512M+`                |

--- 

## Default Mount Structure

DUMB uses a predictable internal mount layout within the container to organize mounted debrid services and their symlinks when configured by the onboarding process.

!!! note "The below convention is automatically followed when using the onboarding system to configure core services."

### Root Mount Directory

* `/mnt/debrid` is the root mount location inside the container.

### rclone Mount Targets

* Each rclone mount uses the core service name as its subdirectory.

  * For example:

    * Core service `riven` → `/mnt/debrid/riven`
    * Core service `decypharr` → `/mnt/debrid/decypharr`

### Symlink Directories

* Core services that generate symlinks (e.g., Riven, Decypharr) will place them in subdirectories named with the pattern: `<core_service>_symlinks`

  * For example:

    * `/mnt/debrid/riven_symlinks`
    * `/mnt/debrid/decypharr_symlinks`

This naming convention makes it easy to identify and separate raw debrid mounts from symbolic links created for media server compatibility.

---

## Mount Propagation

Mount propagation is needed when a mount created **inside DUMB** must become visible on the host or inside another container. Applications inside DUMB already share its mount namespace and do not need propagation for that internal access.

### Required propagation flags

Use a shared bind for DUMB, which produces the FUSE mount, and a receiving bind for external consumers:

```yaml
services:
  dumb:
    volumes:
      - /path/to/dumb/mnt/debrid:/mnt/debrid:rshared
  media-server:
    volumes:
      - /path/to/dumb/mnt/debrid:/mnt/debrid:rslave
```

This is a volume-layout excerpt, not a complete Compose file. The source path must be on a suitable shared Linux host mount. Absolute symlink targets must resolve inside the consumer too; propagation does not rewrite paths.

### Summary table for mount propagation use cases

The directions below are relative to the container receiving the bind:

| Mode | Container → host | Host → container | Typical use |
|---|---|---|---|
| `rshared` | Yes | Yes | DUMB's mount-producing media bind |
| `rslave` | No | Yes | External Plex, Jellyfin, or Arr container receiving DUMB's mounts |
| `rprivate` (Docker default) | No | No | A layout with no external mount consumers |

`rslave` receives host events. It cannot send a FUSE mount created inside DUMB back to the host, so it cannot replace `rshared` on DUMB's producer bind.

### Common issues without propagation

A raw mount can work inside DUMB while the host or another container sees an empty directory. Check both the producer and consumer binds, then compare their actual mount views. A regular read/write bind alone does not propagate later submount events.

### Host system requirements

Propagation is a Linux host feature; Docker Desktop does not support it. See the [official Docker reference](https://docs.docker.com/engine/storage/bind-mounts/#configure-bind-propagation).

### How to check

Run on the Docker host, using the actual host source path:

```bash
findmnt -T /path/to/dumb/mnt/debrid -o TARGET,SOURCE,FSTYPE,PROPAGATION
```

Also inspect the mount inside DUMB and the consumer. Checking only the Compose string does not establish that the host topology supports it.

### How to enable

If the source is on a private host mount, plan a dedicated shared bind while the affected services are stopped. Follow the [host-side repair example](../../faq/rclone.md#error-response-from-daemon-path-yourhostpathmnt-is-mounted-on-but-it-is-not-a-shared-mount). Persist that host configuration through the host's mount or service manager and verify it after reboot.

### Best practices

- Scope shared propagation to the media mount-producing directory.
- Use `rslave` for consumers that only receive mount events.
- Keep absolute symlink targets consistent between DUMB and consumers.
- Verify the actual mount views after container recreation or host reboot.

---

## Accessing rclone Inside the Container
To run rclone commands manually:
```bash
docker exec -it DUMB /bin/bash
rclone listremotes
rclone mount rclone_RD: /mnt/test
```

---

## Tips
- Mounts are bind-mounted into the container by default.
- If you mount `/mnt/debrid/` to the host with the `:rshared` flag you will see all Zurg-fetched content.
- Use the `RCLONE_LOG_LEVEL` env var to control verbosity.

---

## Resources
- [rclone Documentation](https://rclone.org/)
- [WebDAV Docs](https://rclone.org/webdav/)
- [rclone Environment Variables](https://rclone.org/docs/#environment-variables)

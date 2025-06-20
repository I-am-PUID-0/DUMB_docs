
# Riven Backend Configuration

The **Riven Backend** is the core component responsible for data handling, automation, API integrations, and scraping within the Riven ecosystem. Proper configuration ensures seamless integration with services like Overseerr, Plex, and Trakt.

## Configuration Settings in `dmb_config.json`

```json
"riven_backend": {
    "enabled": true,
    "process_name": "Riven Backend",
    "repo_owner": "rivenmedia",
    "repo_name": "riven",
    "release_version_enabled": false,
    "release_version": "v0.20.1",
    "branch_enabled": false,
    "branch": "release-please--branches--main",
    "suppress_logging": false,
    "log_level": "INFO",
    "host": "127.0.0.1",
    "port": 8080,
    "auto_update": false,
    "auto_update_interval": 24,
    "symlink_library_path": "/mnt",
    "clear_on_update": true,
    "exclude_dirs": [
        "/riven/backend/data"
    ],
    "env_copy": {
        "source": "/riven/backend/data/.env",
        "destination": "/riven/backend/src/.env"
    },
    "platforms": [
        "python"
    ],
    "command": [
        "/riven/backend/venv/bin/python",
        "src/main.py",
        "-p",
        "{port}"
    ],
    "config_dir": "/riven/backend",
    "config_file": "/riven/backend/data/settings.json",        
    "env": {},
    "wait_for_dir": "/data/rclone_RD/__all__"
},
```

### 🔍 Configuration Key Descriptions

- **`enabled`**: Whether to start the Riven Backend service.
- **`process_name`**: Used in logs and process tracking.
- **`host`**: IP address for the backend to listen on.
- **`port`**: Port exposed for the API.
- **`repo_owner`** / **`repo_name`**: GitHub repo to pull from.
- **`release_version_enabled`** / **`release_version`**: Use a tagged release if enabled.
- **`branch_enabled`** / **`branch`**: Use a specific branch if enabled.
- **`suppress_logging`**: If `true`, disables log output for this service.
- **`log_level`**: Logging verbosity level (e.g., `DEBUG`, `INFO`).
- **`host`**: IP address the backend should bind to.
- **`port`**: Port the backend API is served on.
- **`auto_update`**: Enables automatic self-updates.
- **`auto_update_interval`**: How often (in hours) to check for updates.
- **`symlink_library_path`**: Target path for media symlinks.
- **`clear_on_update`**: Clears build artifacts or cache during updates.
- **`exclude_dirs`**: Prevents specific directories from being affected by updates when using `clear_on_update`
- **`env_copy`**: Copies a `.env` file from one location to another. Such as the Riven .env discussed below
- **`platforms`**: Expected runtime environment (e.g., `python`).
- **`command`**: How the service is started.
- **`config_dir`** / **`config_file`**: Configuration directory and settings file.
- **`env`**: Dictionary of environment variables passed to the process.
- **`wait_for_dir`**: Delays startup until the specified directory exists.

---

## ⚙️ Branch / Version Targeting
You can control which version or branch of the backend is deployed by setting:

- `branch_enabled: true` and specifying a `branch`
- or `release_version_enabled: true` and specifying a `release_version`

---

## ⚙️ Initial Setup: Riven Backend

Before Riven Backend can be used, **initial configuration is required**.

After starting DMB, navigate to the **Riven Frontend** and open the `Settings` page. The following sections should be reviewed and updated:

### 🔧 Required Configuration
At a minimum, **enable at least one Content source** under the `Content` section. Without this, Riven cannot function.

### 🧩 Recommended Setup Areas
- **General** – Adjust base settings like min/max files size, etc.
- **Media Server** – Add your Plex, Jellyfin, or Emby server details for library syncing.
- **Content** – Configure sources such as Trakt, Overseerr, or the Plex Watchlist, MDB List, Listrr.
- **Scrapers** – Enable one or more scrapers (e.g., Zilean, Torrentio, Knightcrawler, Orionoid, Jackett, Mediafusion, Prowlarr, Comet).
- **Ranking** – Customize how results are scored and filtered.

!!! note "📝 Once complete, Riven will begin processing requests based on the selected sources and configurations."

---

## 🧵 Symlink Mounts & Media Server Integration

One of the most common issues when setting up DMB with your **Media Server (Plex, Jellyfin, or Emby)** is improper **path mapping** between containers. Since **Riven creates symlinks** to Zurg-mounted content, the following paths must be shared **identically across containers**.

In your Docker or Compose setup for both DMB and your Media Server container, ensure the following:

### ✅ Example: Correct Volume Mapping

```yaml
# rclone/Zurg mount from DMB container
- /home/username/docker/DMB/Zurg/mnt:/data

# Riven symlink mount from DMB container
- /home/username/docker/DMB/Riven/mnt:/mnt
```

In this case:

- `/data` is the mount point used by `rclone` and `Zurg` **inside** the DMB container.
- `/mnt` is where Riven places cleaned-up symlinks to that content.
- These **container-side paths (`:/data`, `:/mnt`) must be the same** in your media server container.

!!! note "📌 *The host path (`/home/username/docker/...`) can differ—it’s the container paths that must match.*"

---

### 🔁 Why This Matters

- Riven creates symlinks in `/mnt` that **point to files inside `/data`** (or your configured `mount_dir`).
- If the Media Server doesn’t share these exact mount paths, the symlinks will **break or point to invalid locations**.
- Avoid adding `/data` to your media library — instead, add `/mnt` to ensure only cleaned and processed content is indexed.

!!! tip "✅ **Best Practice:**" 
    Use the same mount paths across DMB and Media Server containers — even if the host paths differ.

---


### Host-Based Media Server: Mount Path Consistency

If your media server (such as Plex) runs **directly on the host** (not in Docker), it will access media files using the host's file system. In this setup, any symlinks created inside the DMB container must resolve correctly **on the host**. This means the media paths inside the container must exactly match the paths used by the host.

Symlink resolution is based on absolute paths. If those paths don't exist or don't match outside the container, the symlinks will be broken or unusable by the media server.

#### Example: Riven Media Directory

Suppose your media is mounted on the host at:

```
/docker/DMB/Riven/mnt
```

Since Plex (or another media server) and the DMB container need to both access this path and resolve symlinks, your Docker bind mount must look like:

```yaml
/docker/DMB/Riven/mnt:/docker/DMB/Riven/mnt
```

Then, inside the `dmb_config.json`, make sure you define:

```json
"riven_backend": {
  "symlink_library_path": "/docker/DMB/Riven/mnt",
}
```

This ensures that any symlinks Riven creates will remain valid on the host.

#### Example: Zurg Media Directory

For media processed by Zurg and symlinked by Riven:

```
/docker/DMB/Zurg/mnt
```

Use the following bind mount:

```yaml
/docker/DMB/Zurg/mnt:/docker/DMB/Zurg/mnt:shared
```

And configure the `dmb_config.json` as follows:

```json
"rclone": {
  "mount_dir": "/docker/DMB/Zurg/mnt",
}
```


#### Simplified Approach Using Standard Paths

To simplify configuration and reduce the need to hardcode deep paths, you can instead use standard directory mounts like `/mnt` and `/data`.

Docker Compose example:

```yaml
/mnt:/mnt
/data:/data:shared
```

And then update the configuration:

```json
"riven_backend": {
  "symlink_library_path": "/mnt",
},
"rclone": {
  "mount_dir": "/data",
}
```

Using standardized top-level paths makes your setup more portable and ensures symlinks will resolve correctly regardless of the underlying directory structure.

---


## Riven's Environment Variables in the `.env.example`

The `.env.example` file includes:

- `RIVEN_FORCE_ENV`: Forces env vars to override `settings.json`.
- `SETTINGS_FILENAME`: Specifies the settings file name.
- `SKIP_TRAKT_CACHE`: Skips cached results.
- `HARD_RESET`: Drops and recreates all database tables.
- `REPAIR_SYMLINKS`: Fixes any broken symlinks.
- `API_KEY`: Custom static API key.
- `WORKERS`: Number of indexing workers.

Each Riven env can also be set within DMB, either through the **"env"** section of the "riven_backend" within the `dmb_config.json`, or buy utilizing methods defined in the [Configuration](../features/configuration.md) section of the docs.



[View full example on GitHub](https://github.com/rivenmedia/riven/blob/main/.env.example)

---

## Additional Resources

- [Riven Wiki](https://rivenmedia.github.io/wiki/)
- [Riven GitHub Repository](https://github.com/rivenmedia/riven)

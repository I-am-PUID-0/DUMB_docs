# Zurg

Zurg is the debrid content fetcher that powers file discovery and caching for DMB. It mounts content made available by debrid services like Real-Debrid and exposes them over WebDAV for rclone to access. Zurg is designed to run quietly in the background and can be configured to run multiple instances.

!!! note "Current Debrid Support"
    As of this posting, **Zurg only supports Real-Debrid**. Additional debrid services may be supported in future updates.

---

## 🔀 Zurg Repositories

There are **two official Zurg repositories**:

- **[`zurg-testing`](https://github.com/debridmediamanager/zurg-testing)** – The **default** public repo used by DMB. It contains stable builds accessible to all users.
- **[`zurg`](https://github.com/debridmediamanager/zurg)** – The **sponsored-only** repo that includes the latest features, nightly builds, and premium support. DMB can access it by setting the `DMB_GITHUB_TOKEN` and changing the `repo_name` to `zurg`.

!!! note "See [Integration Tokens & Credentials](../features/configuration.md/#-integration-tokens--credentials) section for details on setting up the `DMB_GITHUB_TOKEN`"

---

## ⚙️ Configuration in `dmb_config.json`

Zurg is configured using the `instances` model to support multiple debrid services (e.g., RealDebrid, AllDebrid, Premiumize).

```json
"zurg": {
  "instances": {
    "RealDebrid": {
      "enabled": true,
      "process_name": "Zurg w/ RealDebrid",
      "repo_owner": "debridmediamanager",
      "repo_name": "zurg-testing",
      "release_version_enabled": false,
      "release_version": "v0.9.3-final",
      "suppress_logging": false,
      "log_level": "INFO",
      "host": "127.0.0.1",
      "port": 9090,
      "auto_update": false,
      "auto_update_interval": 1,
      "clear_on_update": false,
      "exclude_dirs": ["/zurg/RD"],
      "key_type": "RealDebrid",
      "config_dir": "/zurg/RD",
      "config_file": "/zurg/RD/config.yml",
      "command": "/zurg/RD/zurg",
      "user": "",
      "password": "",
      "api_key": ""
    }
  }
}
```

### 🔍 Configuration Key Descriptions

- **`enabled`**: Whether to start the Zurg instance.
- **`process_name`**: Label used for log files and process display.
- **`repo_owner`** / **`repo_name`**: GitHub repo to pull Zurg from.
- **`release_version_enabled`** / **`release_version`**: Use a specific release tag if enabled.
- **`suppress_logging`**: If `true`, disables log output for this service.
- **`log_level`**: Logging verbosity level (e.g., `DEBUG`, `INFO`).
- **`host`** / **`port`**: IP/Port to serve the WebDAV interface.
- **`auto_update`**: Enables automatic self-updates.
- **`auto_update_interval`**: How often (in hours) to check for updates.
- **`clear_on_update`**: Clears build artifacts or cache during updates.
- **`exclude_dirs`**: Prevents specific directories from being affected by updates when using `clear_on_update`
- **`key_type`**: Debrid service this Zurg instance connects to (`RealDebrid`, `AllDebrid`, etc).
- **`config_dir`** / **`config_file`**: Location of the Zurg YAML config.
- **`command`**: Full path to the Zurg binary.
- **`user`** / **`password`**: Optional basic auth credentials for WebDAV.
- **`api_key`**: Debrid API key (used by Zurg for account authentication).

---

## ⚙️ Version Targeting
You can control which version of Zurg is deployed by setting:

- `release_version_enabled: true` and specifying a `release_version`

---

## ➕ Adding Multiple Zurg Instances

You can define additional instances in the same `zurg.instances` block by copying the structure and:

- Each `instance name` is **unique**
- Each `process_name` is **unique**
- Each `config_dir` is **unique**
- Each `port` is **unique**
- The `key_type` must match the type of Debrid service used - Limited to `RealDebrid` until Zurg adds support for others

Example:
```json
"zurg": {
    "instances": {
        "RealDebrid": {
            "enabled": true,
            "process_name": "Zurg w/ RealDebrid",
            "repo_owner": "debridmediamanager",
            "repo_name": "zurg-testing",
            "release_version_enabled": false,
            "release_version": "v0.9.3-final",
            "suppress_logging": false,
            "log_level": "INFO",
            "host": "127.0.0.1",
            "port": 9090,
            "auto_update": false,
            "auto_update_interval": 1,
            "clear_on_update": false,
            "exclude_dirs": ["/zurg/RD"],
            "key_type": "RealDebrid",
            "config_dir": "/zurg/RD",
            "config_file": "/zurg/RD/config.yml",
            "command": "/zurg/RD/zurg",
            "user": "",
            "password": "",
            "api_key": ""
        },
        "RealDebrid_2": {
            "enabled": true,
            "process_name": "Zurg w/ RealDebrid 2",
            "repo_owner": "debridmediamanager",
            "repo_name": "zurg-testing",
            "release_version_enabled": false,
            "release_version": "v0.9.3-final",
            "suppress_logging": false,
            "log_level": "INFO",
            "host": "127.0.0.1",
            "port": 9091,
            "auto_update": false,
            "auto_update_interval": 1,
            "clear_on_update": false,
            "exclude_dirs": ["/zurg/RD2"],
            "key_type": "RealDebrid",
            "config_dir": "/zurg/RD2",
            "config_file": "/zurg/RD2/config.yml",
            "command": "/zurg/RD2/zurg",
            "user": "",
            "password": "",
            "api_key": ""
        }            
    }
}    
```

---

## 🧠 Tips
- The Zurg WebDAV endpoint will be used by rclone to mount files
- Always set the correct `api_key` to avoid auth issues
- Avoid using the same port or overlapping directories across instances

---

## 📚 Resources
- [Zurg Testing (default repo)](https://github.com/debridmediamanager/zurg-testing)
- [Zurg (premium repo)](https://github.com/debridmediamanager/zurg)
- [DMB GitHub Token Setup](https://github.com/I-am-PUID-0/DMB#environment-variables)

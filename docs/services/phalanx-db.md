# Phalanx DB Configuration

**Phalanx DB** is an optional decentralized metadata service that can enhance CLI Debrid by providing distributed data capabilities through Hyperswarm. It runs independently and is not required for CLI Debrid to function.

## Configuration Settings in `dmb_config.json`

```json
"phalanx_db": {
  "enabled": false,
  "process_name": "Phalanx DB",
  "repo_owner": "godver3",
  "repo_name": "phalanx_db_hyperswarm",
  "release_version_enabled": false,
  "release_version": "v0.50",
  "branch_enabled": false,
  "branch": "main",
  "suppress_logging": false,
  "log_level": "INFO",
  "port": 8888,
  "auto_update": false,
  "auto_update_interval": 24,
  "clear_on_update": true,
  "exclude_dirs": [
    "/phalanx_db/data"
  ],
  "platforms": ["pnpm"],
  "command": ["node", "phalanx_db_rest.js"],
  "config_dir": "/phalanx_db",
  "env": {}
},
```

### 🔍 Configuration Key Descriptions

* **`enabled`**: Enables or disables Phalanx DB.
* **`process_name`**: Label used for logging and monitoring.
* **`repo_owner`** / **`repo_name`**: Source GitHub repo for updates.
* **`release_version_enabled`** / **`release_version`**: Targets a specific version release.
* **`branch_enabled`** / **`branch`**: If true, uses a GitHub branch instead of a release.
* **`suppress_logging`**: Suppresses logs from this service.
* **`log_level`**: Verbosity level.
* **`port`**: Port Phalanx DB listens on.
* **`auto_update`** / **`auto_update_interval`**: Pull latest changes from GitHub.
* **`clear_on_update`** / **`exclude_dirs`**: Defines cleanup behavior and ignored folders.
* **`platforms`**: Required runtime (usually `pnpm` + Node).
* **`command`**: Startup command.
* **`config_dir`**: Root directory for the config and runtime files.
* **`env`**: Environment variables (if any).

---

## 🧪 When to Use

Phalanx DB is beneficial if you want to:

* Store metadata in a decentralized way
* Leverage peer-to-peer syncing of release data
* Enable extended features in CLI Debrid when Phalanx DB is active

!!! note "This service is **optional** and should only be enabled if you intend to use its distributed storage model."

---

## ⚙️ Branch / Version Targeting
You can control which version or branch is deployed by setting:

- `branch_enabled: true` and specifying a `branch`
- or `release_version_enabled: true` and specifying a `release_version`

---


## Additional Resources

* [Phalanx DB GitHub Repository](https://github.com/godver3/phalanx_db_hyperswarm)

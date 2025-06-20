# CLI Battery Configuration

The **CLI Battery** is a Flask-based companion application required by CLI Debrid. It provides metadata services and background processing, integrating with Trakt and exposing a lightweight web API for managing movies and TV shows. This service must be running for CLI Debrid to operate properly.

## Configuration Settings in `dmb_config.json`

```json
"cli_battery": {
  "enabled": false,
  "process_name": "CLI Battery",
  "suppress_logging": false,
  "log_level": "INFO",
  "port": 5001,
  "platforms": ["python"],
  "command": [
    "/cli_debrid/venv/bin/python",
    "cli_battery/main.py"
  ],
  "config_dir": "/cli_debrid",
  "config_file": "/cli_debrid/data/config/settings.json",
  "log_file": "/cli_debrid/data/logs/battery_debug.log",
  "env": {
    "USER_CONFIG": "/cli_debrid/data/config/",
    "USER_LOGS": "/cli_debrid/data/logs/",
    "USER_DB_CONTENT": "/cli_debrid/data/db_content/",
    "CLI_DEBRID_BATTERY_PORT": "{port}"
  }
},
```

### 🔍 Configuration Key Descriptions

* **`enabled`**: Enables the CLI Battery service.
* **`process_name`**: Display name in logs and process manager.
* **`suppress_logging`**: Suppresses CLI Battery logs in the main DMB output.
* **`log_level`**: Controls verbosity of logging.
* **`port`**: CLI Battery service port.
* **`command`**: How the service is started.
* **`config_dir`** / **`config_file`**: Configuration paths used by the battery.
* **`log_file`**: Path to the CLI Battery log file.
* **`env`**: Environment variables passed to the subprocess.

---

## ⚠️ Required by CLI Debrid

CLI Battery must be running **before** CLI Debrid launches, as the latter depends on it for coordination and metadata resolution.

---

## 🌐 Web Interface & API

CLI Battery is a Flask web app exposing a browser UI and REST API:

### 📊 Web Dashboard

* `/` — Home dashboard with metadata stats
* `/debug` — Debug view of all metadata items
* `/metadata` — Full metadata list
* `/providers` — Enable/disable metadata providers
* `/settings` — View and update settings

### 🔌 API Endpoints

* `/api/metadata/<imdb_id>` — Fetch metadata for a specific movie or show
* `/api/seasons/<imdb_id>` — Fetch seasons for a show
* `/authorize_trakt` — Start Trakt OAuth authorization
* `/trakt_callback` — Handle the Trakt OAuth callback

---

## 🌐 Access
- Navigate to: `http://<host>:<port>` 
    - default port `5001`

---


## Additional Resources

* [CLI Debrid GitHub Repository](https://github.com/godver3/cli_debrid)
* [CLI Battery Source Code](https://github.com/godver3/cli_debrid/tree/main/cli_battery)

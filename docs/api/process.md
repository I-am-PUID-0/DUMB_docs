---

## title: Process Management API

# ⚙️ Process Management API

The **Process Management** endpoints handle the launching, stopping, restarting, and tracking of subprocesses managed by DUMB.

---

## 🔄 Endpoints

### `GET /process/processes`

Returns a list of all configured processes, including both running and stopped services. This includes metadata like enabled status, version, and repository URL.

#### ✅ Example Response:

```json
{
  "processes": [
    {
      "name": "rclone w/ RealDebrid",
      "process_name": "rclone w/ RealDebrid",
      "enabled": true,
      "config": { "enabled": true, ... },
      "version": "1.65.1",
      "key": "rclone",
      "config_key": "rclone",
      "repo_url": "https://rclone.org"
    },
    {
      "name": "Zurg w/ RealDebrid",
      "process_name": "Zurg w/ RealDebrid",
      "enabled": false,
      "config": { "enabled": false, ... },
      "version": "0.5.2",
      "key": "zurg",
      "config_key": "zurg",
      "repo_url": "https://github.com/I-am-PUID-0/DUMB"
    }
  ]
}
```

---

### `GET /process`

Fetch details about a specific process including the config block, version, and config key.

#### ⚠️ Required Query Parameter:

* `process_name` (string)

#### ✅ Example Response:

```json
{
  "process_name": "rclone w/ RealDebrid",
  "config": { "enabled": true, ... },
  "version": "1.65.1",
  "config_key": "rclone"
}
```

---

### `POST /process/start`

Starts a specific process using its name as defined in `dumb_config.json`.

#### 🔧 Request Body:

```json
{
  "process_name": "rclone w/ RealDebrid"
}
```

#### ✅ Example Response:

```json
{
  "status": "Service started successfully",
  "process_name": "rclone w/ RealDebrid"
}
```

---

### `POST /process/stop`

Stops a running process.

#### 🔧 Request Body:

```json
{
  "process_name": "rclone w/ RealDebrid"
}
```

---

### `POST /process/restart`

Restarts a running process.

#### 🔧 Request Body:

```json
{
  "process_name": "rclone w/ RealDebrid"
}
```

---

### `GET /process/service-status`

Gets the current status of a process

#### ✅ Example Response:

```json
{
  "process_name": "rclone w/ RealDebrid",
  "status": "running"
}
```

---

### `POST /process/start-core-service`

Starts one or more **core services** and all required dependencies, optionally starting **optional services** as well.
This endpoint is primarily used during the **onboarding** process by the DUMB frontend to prepare services like Riven, Decypharr, or Plex Debrid.

#### 🔧 Request Body Examples:

**Riven Backend**

```json
{
  "core_services": {
    "name": "Riven Backend",
    "debrid_service": "RealDebrid",
    "debrid_key": "abc123",
    "service_options": {}
  },
  "optional_services": ["zilean","pgadmin", "riven_frontend"]
}
```

**Decypharr**

```json
{
  "core_services": {
    "name": "Decypharr",
    "debrid_service": "RealDebrid",
    "debrid_key": "abc123",
    "service_options": {}
  },
  "optional_services": []
}
```

**CLI Debrid**

```json
{
  "core_services": {
    "name": "CLI Debrid",
    "debrid_service": "RealDebrid",
    "debrid_key": "abc123",
    "service_options": {
      "phalanx_db": { "enabled": true }
    }
  },
  "optional_services": ["zilean"]
}
```

**Plex Debrid**

````json
{
  "core_services": {
    "name": "Plex Debrid",
    "debrid_service": "RealDebrid",
    "debrid_key": "abc123",
    "service_options": {
      "rclone": { "log_level": "DEBUG" },
      "zurg": { "port": 9194 }
    }
  },
  "optional_services": []
}
```json

````

The `core_services` field can be a single object or an array. Each core service will:

* Automatically provision any missing dependency instances (e.g. rclone/zurg).
* Apply any `service_options` overrides (e.g. log levels, ports).
* Start in the correct order, verifying success.

#### ✅ Example Response:

```json
{
  "results": [
    {"service": "Riven Backend", "status": "started"},
    {"service": "Decypharr", "status": "started"}
  ],
  "errors": []
}
```

#### ℹ️ Notes:

* Dependencies like Zurg or Rclone will be created using templates and attached to the calling core service.
* Optional services such as `pgadmin` or `zilean` are only started if included and configured.
* `debrid_key` is injected into Zurg if required.
* `service_options` can override config values such as `log_level`, `port`, or `enabled`.
* Any startup errors will appear in the `errors` list with detailed messages.

---

## 🧐 Notes

* All process names are matched against the entries defined in `dumb_config.json`.
* Most process commands are defined as arrays and are managed with subprocess handling inside Python.

---

## 📌 Related Files

* [`process.py`](https://github.com/I-am-PUID-0/DUMB/blob/master/api/routers/process.py)
* [`Configuration`](config.md)

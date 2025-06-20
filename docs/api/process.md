---
title: Process Management API
---

# ⚙️ Process Management API

The **Process Management** endpoints handle the launching, stopping, restarting, and tracking of subprocesses managed by DMB.

---

## 🔄 Endpoints

### `GET /process/processes`
Returns a list of currently running processes.

#### ✅ Example Response:
```json
[
  {
    "pid": 1234,
    "name": "rclone w/ RealDebrid",
    "status": "running"
  },
  {
    "pid": 1235,
    "name": "Zurg w/ RealDebrid",
    "status": "stopped"
  }
]
```

---

### `POST /process/start`
Starts a specific process using its name as defined in `dmb_config.json`.

#### 🔧 Request Body:
```json
{
  "process_name": "rclone w/ RealDebrid"
}
```

#### ✅ Example Response:
```json
{
  "success": true,
  "message": "Process started",
  "pid": 1234
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


### `GET process/service-status`
Gets the current status of a process

#### ✅ Example Response:
```json
[]
```


## 🧠 Notes

- All process names are matched against the entries defined in `dmb_config.json`.
- Most process commands are defined as arrays and are managed with subprocess handling inside Python.

---

## 📎 Related Files
- [`process.py`](https://github.com/I-am-PUID-0/DMB/blob/master/api/routers/process.py)
- [`Configuration`](config.md)
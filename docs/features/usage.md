---
title: Usage
---

# Usage

## 🚀 Running DUMB
DUMB automatically starts the services defined in `dumb_config.json` in the proper order. Each service can also be managed independently using the [DUMB Frontend](../services/dumb/dumb-frontend.md/) or by directly modifying the configuration.
!!! important "Onboarding"
    DUMB is preset to disable all services, other than the API and Frontend on the first startup. 

    On first launch of the [DUMB Frontend](../services/dumb/dumb-frontend.md), you will be directed to the Onboarding process.  


### 🔄 Automatic Service Start
All services with `"enabled": true` in the config will be started on container launch.

If a service fails to start, check its log file in the `/log` directory (or wherever `log_dir` is set).

---

## 🔃 Managing Updates

### 🛠️ Manual Updates
Each service can be updated by modifying the configuration file or using the [DUMB Frontend](../services/dumb/dumb-frontend.md). 

Updates include:

- Branch switching
- Version pinning
- Auto-update toggling

### ⚙️ Auto-Update
Some services support automatic updates. 

Enable by setting:
```json
"auto_update": true,
"auto_update_interval": 24
```
!!! note "`auto_update_interval` is measured in hours."

Services supporting auto-updates:

- DUMB Frontend
- Plex Media Server (Future release)
- Riven Backend and Frontend
- Decypharr
- NzbDAV
- Jellyfin
- Emby
- CLI Debrid
- Plex Debrid
- Sonarr
- Radarr
- Lidarr
- Prowlarr
- Whisparr
- Zilean
- Zurg

---

## ⚡ Shutdown Handling
DUMB handles graceful shutdown of all services. 

This includes:

- Stopping running processes
- Unmounting rclone mounts
- Syncing configuration states

To allow time for clean shutdowns, use:
```yaml
docker-compose:
  stop_grace_period: 60s
```

---

## 📌 Tips
- Always monitor `/log/*.log` files for troubleshooting or monitor the logs from the **DUMB Frontend**.
- Logs can be colored if `color_log` is enabled in the config.

---

## 📎 Related Docs
- [Configuration](configuration.md)
- [Services Overview](../services/index.md)
- [API](../api/index.md)

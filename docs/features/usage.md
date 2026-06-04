---
title: Usage
icon: lucide/play-circle
---

# Usage

## Running DUMB

DUMB automatically starts the services defined in `dumb_config.json` in dependency-aware order. Each service can also be managed independently using the [DUMB Frontend](../services/dumb/dumb-frontend.md) or by directly modifying the configuration.

!!! important "Onboarding"
    DUMB is preset to disable all services, other than the API and Frontend on the first startup. 

    On first launch of the [DUMB Frontend](../services/dumb/dumb-frontend.md), you will be directed to the Onboarding process.  


### Automatic Service Start
All services with `"enabled": true` in the config will be started on container launch.

If a service fails to start, check its log file in the `/log` directory (or wherever `log_dir` is set).

---

## Managing Updates

### Manual Updates
Each service can be updated by modifying the configuration file or using the [DUMB Frontend](../services/dumb/dumb-frontend.md). 

Updates include:

- Branch switching
- Version pinning
- Auto-update toggling

### Auto-Update

Most managed services support automatic update checks through the same scheduling fields. This includes top-level services and instance-based services such as Arrs, Seerr, NeutArr, Profilarr, rclone, and Zurg.

Enable by setting:
```json
"auto_update": true,
"auto_update_start_time": "04:00",
"auto_update_interval": 24
```
!!! note "`auto_update_interval` is measured in hours."
!!! note "`auto_update_start_time` uses 24-hour `HH:MM` format."

Services use one of these update modes depending on how upstream ships them:

- **GitHub release or branch services** use `release_version_enabled`, `release_version`, `branch_enabled`, and `branch`.
- **Pinned binary services** use `pinned_version`.
- **Instance-based services** store the same update fields inside each instance.

Use the service page's **Updates** panel to see whether an update is available, whether a pin or branch blocks automatic installation, and when the next scheduled check will run.

---

## Shutdown Handling
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

## Tips
- Always monitor `/log/*.log` files for troubleshooting or monitor the logs from the **DUMB Frontend**.
- Logs can be colored if `color_log` is enabled in the config.

---

## Related Docs
- [Configuration](configuration.md)
- [Services Overview](../services/index.md)
- [API](../api/index.md)

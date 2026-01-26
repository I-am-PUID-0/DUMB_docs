---
title: Tautulli
icon: lucide/bar-chart-3
---

# Tautulli

Tautulli is a monitoring and statistics application for Plex Media Server. It tracks what has been watched, who watched it, when and where they watched it, and how it was watched, providing detailed analytics and notifications.

---

## Overview

Tautulli provides:

- **Playback monitoring** - Real-time view of active streams
- **Watch statistics** - Historical data on viewing habits
- **User tracking** - Per-user watch history and statistics
- **Library analytics** - Insights into your media library
- **Notifications** - Alerts for playback events, new content, and more
- **Graphs and reports** - Visual representations of your Plex usage

---

## Default port

| Service | Port |
|---------|------|
| Tautulli | 8181 |

---

## Configuration settings in `dumb_config.json`

Below is a sample configuration for Tautulli within the `dumb_config.json` file:

```json
"tautulli": {
  "enabled": false,
  "process_name": "Tautulli",
  "repo_owner": "Tautulli",
  "repo_name": "Tautulli",
  "release_version_enabled": false,
  "release_version": "latest",
  "branch_enabled": false,
  "branch": "master",
  "suppress_logging": false,
  "log_level": "INFO",
  "port": 8181,
  "auto_update": false,
  "auto_update_interval": 24,
  "clear_on_update": true,
  "exclude_dirs": [
    "/tautulli/data"
  ],
  "platforms": [
    "python"
  ],
  "command": [
    "/tautulli/venv/bin/python",
    "Tautulli.py",
    "--config",
    "/tautulli/data/config.ini",
    "--datadir",
    "/tautulli/data",
    "--nolaunch",
    "--port",
    "{port}"
  ],
  "config_dir": "/tautulli",
  "config_file": "/tautulli/data/config.ini",
  "log_file": "/tautulli/data/logs/tautulli.log",
  "env": {}
}
```

### Configuration key descriptions

- **`enabled`**: Whether to start the Tautulli service.
- **`process_name`**: Display name used in logs and the frontend.
- **`repo_owner`** / **`repo_name`**: GitHub repository to pull from.
- **`release_version_enabled`** / **`release_version`**: Use a tagged release if enabled.
- **`branch_enabled`** / **`branch`**: Use a specific branch if enabled.
- **`suppress_logging`**: If `true`, disables log output for this service.
- **`log_level`**: Logging verbosity.
- **`port`**: Port the Tautulli web UI is exposed on.
- **`auto_update`**: Enables automatic self-updates from GitHub.
- **`auto_update_interval`**: How often (in hours) to check for updates.
- **`clear_on_update`**: Clears build artifacts or cache during updates.
- **`exclude_dirs`**: Prevents specific directories from being affected by updates.
- **`platforms`**: Required runtime (typically `python`).
- **`command`**: The command used to launch Tautulli.
- **`config_dir`** / **`config_file`**: Where configuration files are stored.
- **`log_file`**: Path to the Tautulli log file.
- **`env`**: Environment variables passed at runtime.

---

## Initial setup

After enabling Tautulli and starting the service:

1. Access the Tautulli UI at `http://<host>:8181`
2. Complete the setup wizard:
   - Connect to your Plex Media Server
   - Enter your Plex server URL (`http://127.0.0.1:32400` for DUMB's internal Plex)
   - Authenticate with your Plex account or use a Plex token

---

## Connecting to Plex

Since Plex runs inside the DUMB container, use the internal address:

| Setting | Value |
|---------|-------|
| **Plex IP or Hostname** | `127.0.0.1` |
| **Port** | `32400` |
| **Use SSL** | No (internal connection) |

!!! tip "Plex token"

    You can use your Plex token instead of signing in. The token is available in your `dumb_config.json` under the `plex_token` field.

---

## Key features

### Activity monitoring

View real-time playback activity:

- Currently playing streams
- Transcoding status
- Bandwidth usage
- Client information

### Watch statistics

Track viewing patterns:

- Most watched content
- Peak usage times
- User engagement
- Play duration vs content duration

### History

Complete playback history with:

- Date and time
- User who watched
- Device/client used
- Watch duration
- Transcode information

### Graphs

Visual analytics including:

- Daily/weekly/monthly play counts
- Concurrent streams over time
- Library growth
- User activity comparisons

---

## Notifications

Tautulli supports extensive notification options:

| Trigger | Example Use |
|---------|-------------|
| **Playback start** | Alert when someone starts watching |
| **Playback stop** | Log when playback ends |
| **New content** | Notify when new media is added |
| **Buffer warnings** | Alert on playback issues |
| **Plex server down** | Monitor server availability |

Notification agents include:

- Discord
- Slack
- Email
- Telegram
- Webhook
- And many more

---

## Newsletter feature

Tautulli can generate and send newsletters with:

- Recently added content
- Popular content this week
- User-specific recommendations

---

## Accessing via DUMB frontend

When the embedded service UI feature is enabled, Tautulli can be accessed through the DUMB frontend at:

```
http://<dumb-host>:18080/service/ui/tautulli
```

---

## Data retention

Tautulli stores historical data in a SQLite database. Configure retention settings in:

**Settings :material-arrow-right: General :material-arrow-right: History**

- Days to keep history
- Days to keep hosted images
- Grouping options for history entries

---

## Tips

- Enable the "Notify on concurrent streams" option to monitor account sharing.
- Use the API to integrate Tautulli data with other services or dashboards.
- Export statistics regularly for backup purposes.
- The "Recently Added" notification is useful for announcing new content to users.
- Logs can be viewed via DUMB's Frontend or at `/tautulli/data/logs/tautulli.log`.

---

## Resources

- [Tautulli GitHub Repository](https://github.com/Tautulli/Tautulli)
- [Tautulli Wiki](https://github.com/Tautulli/Tautulli/wiki)

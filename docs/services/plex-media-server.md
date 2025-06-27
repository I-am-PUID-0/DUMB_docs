---
Title: Plex Media Server
---

# Plex Media Server Configuration

**Plex Media Server** integrates seamlessly into the DUMB ecosystem to serve and manage your personal media library. It can be configured to either work independently or in tandem with other core services such as Riven, CLI Debrid, Plex Debrid, and Decypharr.

---

## 📦 Configuration in `dumb_config.json`

```json
"plex": {
  "enabled": false,
  "process_name": "Plex Media Server",
  "suppress_logging": false,
  "log_level": "INFO",
  "port": 32400,
  "auto_update": false,
  "auto_update_interval": 24,
  "config_dir": "/plex",
  "config_file": "/plex/Plex Media Server/Preferences.xml",
  "log_file": "/plex/Plex Media Server/Logs/Plex Media Server.log",
  "plex_claim": "",
  "friendly_name": "DUMB",
  "command": [],
  "env": {}
}
```

### 🔍 Key Configuration Fields

* `enabled`: Toggle Plex Media Server on or off.
* `plex_claim`: Plex claim token for initial server registration.
* `friendly_name`: The name that appears in the Plex Web App and on local clients.
* `config_dir`: Directory containing Plex server data (including preferences).
* `port`: Default access port (32400).

---

## ⚙️ Setup & Behavior

### 🧰 Requirements

* Plex must have access to:

  * Media directories (local or rclone-mounted).
  * Transcoding cache (if transcoding is enabled).
  * Valid claim token for first-time setup (if not already configured).

### 🛠️ How to Start

1. Ensure the `plex` block is properly configured in `dumb_config.json`.
2. Provide a `plex_claim` token if starting fresh.
3. Start the container with DUMB orchestration, or manually start the Plex service.
4. Access via: `http://<host>:32400/web`

---

## 🧩 Integration with Other Services

Plex is designed to serve content collected and maintained by core DUMB services including **Riven**, **CLI Debrid**, **Plex Debrid**, and **Decypharr**. These services fetch, organize, and optionally symlink media content into the mounted directory used by Plex.

!!! note "By default, media content is made available inside the container at `/mnt/debrid` through rclone mounts."

* **Core services** populate `/mnt/debrid` with downloaded or upgraded content.
* Plex scans this location to index and serve the media.

!!! info "If you want to serve media from the host system, bind mount your local media directory into the container and add it as a library path in Plex."

---

## 🌐 Access

* URL: `http://<host>:32400/web`
* Credentials: Managed through Plex.tv account

---

## 📁 Mount and Path Planning

Ensure your media storage is accessible to Plex via the correct container path.

* **Default internal mount**: `/mnt/debrid`
* **Add bind mounts**: for local media stored on the host machine not managed by DUMB.

---

## 🧪 Tips and Troubleshooting

* If the container fails to start due to permissions, ensure Plex has proper access to its `config_dir` and media directories.
* Use `PUID` and `PGID` to match host user permissions.
* Logs can be viewed directly from the **DUMB Frontend**.
* You can also start, stop, restart Plex, and modify the `dumb_config.json` or Plex `Preferences.xml` from the **DUMB Frontend** interface.

---

## 🔗 Resources

* [Plex Official Site](https://www.plex.tv/)
* [Plex Claim Token Page](https://www.plex.tv/claim)
* [Plex Support](https://support.plex.tv/)

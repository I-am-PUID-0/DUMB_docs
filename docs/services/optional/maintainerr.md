---
title: Maintainerr
icon: lucide/archive-restore
---

# Maintainerr

Maintainerr helps keep a media library lean by finding content that matches your rules, presenting it in a media-server collection, and optionally removing or unmonitoring it after a delay. It supports Plex, Jellyfin, or Emby as the media server and can use Sonarr, Radarr, Seerr, and Tautulli data when evaluating rules.

---

## Overview

Maintainerr provides:

- **Rule-based library review** - Combine media-server, Arr, Seerr, and Tautulli fields into cleanup rules.
- **Leaving-soon collections** - Show matched content in Plex, Jellyfin, or Emby before action is taken.
- **Delayed actions** - Choose how long matched media remains available before removal.
- **Arr and Seerr cleanup** - Unmonitor or delete Sonarr/Radarr media and clear related Seerr requests.
- **Manual safety controls** - Test media against a rule and exclude individual items from cleanup.

!!! warning "Review rules before enabling deletion"

    Begin with collection-only rules, test representative media, and use a non-zero action delay. File deletion is intentional and may not be recoverable from DUMB.

---

## Default port and data

| Service | Port | Persistent data |
|---------|------|-----------------|
| Maintainerr | 6246 | `/maintainerr/data` |

Maintainerr's primary SQLite database is `/maintainerr/data/maintainerr.sqlite`. DUMB preserves the entire data directory across source updates.

---

## Configuration settings in `dumb_config.json`

```json
"maintainerr": {
  "enabled": false,
  "process_name": "Maintainerr",
  "repo_owner": "Maintainerr",
  "repo_name": "Maintainerr",
  "release_version_enabled": false,
  "release_version": "latest",
  "branch_enabled": false,
  "branch": "development",
  "suppress_logging": false,
  "log_level": "INFO",
  "port": 6246,
  "auto_update": false,
  "auto_update_interval": 24,
  "auto_update_start_time": "04:00",
  "clear_on_update": true,
  "exclude_dirs": [
    "/maintainerr/data"
  ],
  "platforms": [],
  "command": [
    "node",
    "apps/server/dist/main.js"
  ],
  "config_dir": "/maintainerr",
  "log_file": "/maintainerr/data/logs/maintainerr.log",
  "env": {
    "NODE_ENV": "production",
    "UI_HOSTNAME": "0.0.0.0",
    "UI_PORT": "{port}",
    "DATA_DIR": "/maintainerr/data",
    "BASE_PATH": "",
    "VERSION_TAG": "stable",
    "UV_USE_IO_URING": "0"
  }
}
```

### Configuration key descriptions

- **`enabled`**: Whether DUMB starts Maintainerr.
- **`release_version_enabled`** / **`release_version`**: Pin a tagged upstream release. With pinning disabled, DUMB bootstraps the latest stable release on first install.
- **`branch_enabled`** / **`branch`**: Build an upstream source branch instead of a stable release. Upstream does not support moving a development data directory back to stable.
- **`port`**: Maintainerr's web UI and API port.
- **`auto_update`**: Check for and install newer releases using DUMB's update scheduler.
- **`clear_on_update`** / **`exclude_dirs`**: Replace application source and build output while retaining `/maintainerr/data`.
- **`config_dir`**: Maintainerr source and runtime directory.
- **`env.BASE_PATH`**: DUMB keeps this blank because its embedded UI proxy supplies the service context while Maintainerr continues to run at its own root path.

---

## Initial setup

1. Enable Maintainerr during DUMB onboarding or from its service configuration.
2. Start Maintainerr. The first source download and Yarn production build can take longer than a normal restart.
3. Open Maintainerr from its DUMB service page or browse directly to `http://<host>:6246` when that port is published.
4. Select one media server: Plex, Jellyfin, or Emby.
5. Add any Sonarr, Radarr, Seerr, or Tautulli integrations used by your rules. Services inside the same DUMB container can normally use `127.0.0.1` and their configured ports.
6. Create a collection-only rule, test several media items, and confirm the resulting collection before enabling an unmonitor or delete action.

Maintainerr owns its application configuration inside its SQLite database; there is no separate DUMB-managed settings file to edit.

---

## Updates, backups, and rollback

- DUMB rebuilds Maintainerr from the selected official release or branch and preserves `/maintainerr/data`.
- Back up `maintainerr.sqlite` before major upgrades or destructive rule changes. Maintainerr also provides a database backup action in its General settings.
- Database migrations may make an older release incompatible with newer data. To downgrade, restore a database backup created before the upgrade and then pin the matching Maintainerr release.
- Database Health Monitoring can observe the Maintainerr SQLite file in Standard or Enhanced read-only mode when you explicitly enable monitoring for this service.

---

## Reverse proxy safety

Maintainerr controls destructive library actions, so treat its UI as an administrative service. If you publish it beyond a trusted network, add an authentication layer with Traefik Proxy Admin or another reverse proxy and verify the protection before sharing the hostname.

---

## Related links

- [Maintainerr repository](https://github.com/Maintainerr/Maintainerr)
- [Maintainerr documentation](https://docs.maintainerr.info/)
- [Maintainerr installation and environment variables](https://docs.maintainerr.info/installation/)
- [Maintainerr configuration guide](https://docs.maintainerr.info/configuration/)

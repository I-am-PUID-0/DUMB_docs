---
title: Configuration
icon: lucide/settings
---

# Configuration

## Overview
DUMB relies on a **centralized configuration file**, `dumb_config.json`, to control its services, logging, API settings, and more. This file allows you to customize the behavior of DUMB without modifying the source code.

DUMB also supports **environment variables, .env files, and Docker secrets**. If the same setting is defined in multiple places, the **precedence is as follows:**

!!! tip "Configuration Precedence"
    1. **Environment Variables** (highest priority)
    2. **.env File**
    3. **Docker Secrets**
    4. **`dumb_config.json`** (lowest priority)

## Configuration File Structure

!!! caution "Be Careful When Modifying `dumb_config.json`"
    While DUMB is highly configurable via `dumb_config.json`,  
    some changes can cause failures during startup.  
    As such, it is **not recommended** to make modifications unless you fully understand their impact.
    
Below is the **general structure** of `dumb_config.json`:

```json
{
    "puid": 1000,
    "pgid": 1000,
    "tz": "",
    "dumb": { ... },
    "cli_debrid": { ... },
    "cli_battery": { ... },
    "decypharr": { ... },
    "nzbdav": { ... },
    "emby": { ... },
    "jellyfin": { ... },
    "sonarr": { ... },
    "radarr": { ... },
    "lidarr": { ... },
    "prowlarr": { ... },
    "whisparr": { ... },
    "phalanx_db": { ... },
    "plex": { ... },
    "plex_debrid": { ... },
    "postgres": { ... },
    "pgadmin": { ... },
    "rclone": { ... },
    "riven_backend": { ... },
    "riven_frontend": { ... },
    "zilean": { ... },
    "zurg": { ... }
}
```

Each section configures a specific service.

Below is a breakdown of some of the sections:

---

## General Settings

### **User & Timezone**
```json
"puid": 1000,
"pgid": 1000,
"tz": ""
```

- **puid** / **pgid** – Define the user and group IDs for container execution.
- **tz** – Set the timezone (e.g., `America/New_York`).

!!! warning "Root User Not Allowed"
    `puid`/`pgid` cannot be set to `0` (root). DUMB requires a non-root user for security reasons.
---

## Logging Settings
Located in `dumb`:
```json
"log_level": "INFO",
"log_name": "DUMB",
"log_dir": "/log",
"log_count": 2,
"log_size": "10M",
"color_log": true
```

- **log_level** – Set the logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`).
- **log_dir** – Directory where logs are stored.
- **log_count** – Number of rotated logs to retain.
- **log_size** – Maximum log file size before rotation.
- **color_log** – Enables colored log output.

---

## Integration Tokens & Credentials
Located in the `dumb` section of `dumb_config.json`:

```json
"plex_token": "",
"plex_address": "",
"github_token": "",
"github_username": ""
```

### Plex Integration
- **`plex_token`** – This token is used by Riven backend for interacting with your Plex account. It allows features such as using watchlists and sending library scan requests to the Plex server.
- **`plex_address`** – The internal or external URL of your Plex server (e.g., `http://127.0.0.1:32400`).

These values are used automatically by Riven when setting up the [Riven Backend](../services/core/riven-backend.md).

---

### GitHub Integration
- **`github_token`** – Used to increase GitHub API rate limits and unlock access to private/sponsored repositories such as [`zurg`](https://github.com/debridmediamanager/zurg) when associated with your GitHub account.
- **`github_username`** – (Reserved for future use) Will support additional GitHub-sourced services and contributor personalization.

To create a GitHub token:

1. Go to [GitHub Developer Settings → Tokens (Classic)](https://github.com/settings/tokens)
2. Click **Generate new token (classic)**
3. Set an expiration and enable the following scopes:
    - `repo:all`
    - `write:packages` 
    - `read:packages`

    ![GitHub Token](../assets/images/github_token_scope.png)
    
4. Click **Generate token** and **copy the token** — it will only be shown once
5. Add the token to your `.env` file or docker compose with `DMB_GITHUB_TOKEN=`, or `dumb_config.json` under `"github_token"`

---

## Service Configuration

Each DUMB-integrated service is configured within its own section of `dumb_config.json`.

See the individual service pages for in-depth configuration details:

- [DUMB API](../services/dumb/api.md)
- [DUMB Frontend](../services/dumb/dumb-frontend.md)
- [Decypharr](../services/core/decypharr.md)
- [CLI Debrid](../services/core/cli-debrid.md)
- [NzbDAV](../services/core/nzbdav.md)
- [Plex Media Server](../services/core/plex-media-server.md)
- [Jellyfin](../services/core/jellyfin.md)
- [Emby](../services/core/emby.md)
- [Sonarr](../services/core/sonarr.md)
- [Radarr](../services/core/radarr.md)
- [Lidarr](../services/core/lidarr.md)
- [Prowlarr](../services/core/prowlarr.md)
- [Whisparr](../services/core/whisparr.md)
- [pgAdmin 4](../services/optional/pgadmin.md)
- [PostgreSQL](../services/dependent/postgres.md)
- [rclone](../services/dependent/rclone.md)
- [Riven Backend](../services/core/riven-backend.md)
- [Riven Frontend](../services/optional/riven-frontend.md)
- [Zilean](../services/optional/zilean.md)
- [Zurg](../services/dependent/zurg.md)

---

## `core_service` (Arr Integration)

Some services (notably the Arrs) include a `core_service` field to tell DUMB which core workflow they should attach to.

Allowed values:

* `""` (blank): no core integration
* `decypharr`: route Arr automation through Decypharr
* `nzbdav`: route Arr automation through NzbDAV

Examples:

```json
"sonarr": {
  "instances": {
    "Default": {
      "core_service": "decypharr"
    }
  }
}
```

```json
"radarr": {
  "instances": {
    "Default": {
      "core_service": "nzbdav"
    }
  }
}
```


## Next Steps
1. Review and modify `dumb_config.json` as needed.
2. Review the [Usage](usage.md) page. 
3. For a deep dive into individual services, see the [Services](../services/index.md) section.

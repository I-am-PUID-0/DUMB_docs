---
title: Service ports
icon: lucide/network
---

# Service ports

This reference documents all ports used by DUMB services. Use this guide to configure firewall rules, reverse proxies, and understand network requirements.

---

!!! info "Service UI access"

    Most service UIs require the port to be exposed in your compose file before you
    can access them directly. The exceptions are when you route traffic through a
    reverse proxy or use DUMB’s embedded UIs via Traefik.

## Quick reference

| Port | Service | Type |
|------|---------|------|
| 3000 | Riven Frontend | Web UI |
| 3000 | NzbDAV Frontend | Web UI |
| 3003 | Pulsarr | Web UI |
| 3004 | Traefik Proxy Admin | Web UI/API |
| 3005 | DUMB Frontend and API gateway | Web UI/API |
| 5000 | CLI Debrid | Web UI |
| 5001 | CLI Battery | API |
| 5050 | pgAdmin | Web UI |
| 5055 | Seerr | Web UI |
| 5432 | PostgreSQL | Database |
| 6246 | Maintainerr | Web UI/API |
| 6767 | Bazarr | Web UI/API |
| 6969 | Whisparr | Web UI |
| 7777 | MediaStorm | Web UI/API |
| 7878 | Radarr (first/default instance) | Web UI |
| 7879 | Radarr (typical second instance) | Web UI |
| 8000 | DUMB API (container loopback by default) | API |
| 8080 | Riven Backend | API |
| 8080 | NzbDAV Backend | API |
| 8088 | AltMount | Web UI/API |
| 8096 | Jellyfin | Web UI |
| 8096 | Emby | Web UI |
| 8181 | Tautulli | Web UI |
| 8182 | Zilean | Web UI/API |
| 8282 | Decypharr | Web UI |
| 8686 | Lidarr | Web UI |
| 8888 | Phalanx DB | API |
| 8989 | Sonarr (first/default instance) | Web UI |
| 8990 | Sonarr (typical second instance) | Web UI |
| 9090 | Zurg (first/default instance) | API |
| 9091 | Zurg (typical second instance) | API |
| 9696 | Prowlarr | Web UI |
| 9705 | NeutArr | Web UI |
| 18080 | Traefik | Proxy |
| 18081 | Traefik Dashboard/API | Web UI/API |
| 32400 | Plex Media Server | Web UI |

!!! warning "Dynamic port reassignment"

    On startup, DUMB checks enabled-service ports for conflicts and availability.
    If a port is already in use, DUMB automatically shifts that service to the next free port and saves the updated value to `dumb_config.json`.
    This applies to single-port services and NzbDAV's `frontend_port`/`backend_port`.

---

## DUMB core services

### DUMB API

| Property | Value |
|----------|-------|
| **Port** | 8000 |
| **Type** | REST API |
| **Protocol** | HTTP |

The backend API that powers service management, configuration, and monitoring. It listens on `127.0.0.1` inside the container and is not host-published by the maintained Compose file.

```
http://localhost:8000/process/processes  # backend-native, from inside the container
http://localhost:3005/api/process/processes  # normal frontend proxy
```

### DUMB Frontend

| Property | Value |
|----------|-------|
| **Port** | 3005 |
| **Type** | Web UI / REST and WebSocket gateway |
| **Protocol** | HTTP |

The main dashboard for managing DUMB services.

The same listener exposes backend REST routes under `/api/*` and WebSocket
routes under `/ws/*`. REST requests have `/api` removed before they are sent to
the loopback-only backend on port `8000`.

```
http://localhost:3005
```

### Traefik proxy

| Property | Value |
|----------|-------|
| **Port** | 18080 |
| **Type** | Reverse Proxy |
| **Protocol** | HTTP |

Provides unified access to embedded service UIs when enabled.

```
http://localhost:18080/service/ui/<service_name>
```

### Traefik dashboard/API

| Property | Value |
|----------|-------|
| **Port** | 18081 |
| **Type** | Dashboard / API |
| **Protocol** | HTTP |

Traefik exposes its dashboard/API on the Traefik entrypoint plus one port. TPA uses this internally through `TRAEFIK_API_URL=http://127.0.0.1:18081`.

---

## Media servers

### Plex Media Server

| Property | Value |
|----------|-------|
| **Port** | 32400 |
| **Type** | Web UI / API |
| **Protocol** | HTTP/HTTPS |

```
http://localhost:32400/web
```

### Jellyfin

| Property | Value |
|----------|-------|
| **Port** | 8096 |
| **Type** | Web UI / API |
| **Protocol** | HTTP |

```
http://localhost:8096
```

### Emby

| Property | Value |
|----------|-------|
| **Port** | 8096 |
| **Type** | Web UI / API |
| **Protocol** | HTTP |

```
http://localhost:8096
```

---

## Content management

### Riven

| Component | Port | Type |
|-----------|------|------|
| Backend | 8080 | API |
| Frontend | 3000 | Web UI |

```
http://localhost:3000  # Frontend
http://localhost:8080  # API
```

### CLI Debrid

| Component | Port | Type |
|-----------|------|------|
| CLI Debrid | 5000 | Web UI |
| CLI Battery | 5001 | API |

```
http://localhost:5000
```

### Decypharr

| Property | Value |
|----------|-------|
| **Port** | 8282 |
| **Type** | Web UI |
| **Protocol** | HTTP |

```
http://localhost:8282
```

### NzbDAV

| Component | Port | Type |
|-----------|------|------|
| Frontend | 3000 | Web UI |
| Backend | 8080 | API |

```
http://localhost:3000  # Frontend
```

!!! note "NzbDAV and Riven desired defaults overlap"

    The default NzbDAV ports (`3000` and `8080`) overlap with Riven defaults.
    DUMB's startup port allocator normally moves a conflicting enabled service to the next free port and persists the result. Use the runtime configuration/UI—not this default table—as the authority for a running stack.

### AltMount

| Setting | Default |
|---------|---------|
| `port` | `8088` |
| `config_file` | `/altmount/config.yaml` |
| `metadata_dir` | `/altmount/metadata` |
| `mount_path` | `/mnt/debrid/altmount` |
| `log_file` | `/altmount/logs/altmount.log` |

AltMount also exposes `/live`; DUMB probes it while completing the post-start
Arr integration pass.

---

## Arr suite

The Arr applications support multiple instances for different workflows (for example Decypharr, NzbDAV, or AltMount). The first instance starts from the application's base default; additional/conflicting instances are assigned the next free port and saved to `/config/dumb_config.json`.

### Sonarr (TV shows)

| Instance | Typical port |
|----------|--------------|
| First/default | 8989 |
| Second | 8990 |

```
http://localhost:8989  # typical first instance
http://localhost:8990  # typical second instance
```

### Radarr (Movies)

| Instance | Typical port |
|----------|--------------|
| First/default | 7878 |
| Second | 7879 |

```
http://localhost:7878  # typical first instance
http://localhost:7879  # typical second instance
```

### Lidarr (Music)

| Property | Value |
|----------|-------|
| **Port** | 8686 |
| **Type** | Web UI |

```
http://localhost:8686
```

### Whisparr (Adult)

| Property | Value |
|----------|-------|
| **Port** | 6969 |
| **Type** | Web UI |

```
http://localhost:6969
```

### Prowlarr (Indexers)

| Property | Value |
|----------|-------|
| **Port** | 9696 |
| **Type** | Web UI |

```
http://localhost:9696
```

### NeutArr

| Instance | Port |
|----------|------|
| Default | 9705 |

```
http://localhost:9705  # Default instance
```

### Seerr

| Property | Value |
|----------|-------|
| **Port** | 5055 |
| **Type** | Web UI |

```
http://localhost:5055
```

---

## Optional services

### Pulsarr

| Property | Value |
|----------|-------|
| **Port** | 3003 |
| **Type** | Web UI |

```
http://localhost:3003
```

### Maintainerr

| Property | Value |
|----------|-------|
| **Port** | 6246 |
| **Type** | Web UI/API |

```
http://localhost:6246
```

### MediaStorm

| Property | Value |
|----------|-------|
| **Port** | 7777 |
| **Type** | Web UI / API |

The embedded UI opens at `/admin`.

```text
http://localhost:7777/admin
```

### Bazarr

| Property | Value |
|----------|-------|
| **Port** | 6767 |
| **Type** | Web UI / API |

```text
http://localhost:6767
```

### Tautulli

| Property | Value |
|----------|-------|
| **Port** | 8181 |
| **Type** | Web UI |

```
http://localhost:8181
```

### Zilean

| Property | Value |
|----------|-------|
| **Port** | 8182 |
| **Type** | Web UI / API |

```
http://localhost:8182
```

### Traefik Proxy Admin

| Property | Value |
|----------|-------|
| **Port** | 3004 |
| **Type** | Web UI / API |

```
http://localhost:3004
```

### Cloudflared

Cloudflared does not expose a local web UI port. It opens an outbound tunnel connection to Cloudflare and forwards public hostname traffic to DUMB Traefik.

---

## Dependent services

### Zurg

| Instance | Port | Use Case |
|----------|------|----------|
| First/default | 9090 | Any linked workflow |
| Typical second | 9091 | Any additional linked workflow |

```
http://localhost:9090  # typical first instance
http://localhost:9091  # typical second instance
```

### Phalanx DB

| Property | Value |
|----------|-------|
| **Port** | 8888 |
| **Type** | API |

```
http://localhost:8888
```

---

## Database services

### PostgreSQL

| Property | Value |
|----------|-------|
| **Port** | 5432 |
| **Type** | Database |
| **Protocol** | PostgreSQL |

```
postgresql://<user>:<password>@localhost:5432/<configured_database>
```

### pgAdmin

| Property | Value |
|----------|-------|
| **Port** | 5050 |
| **Type** | Web UI |

```
http://localhost:5050
```

---

## Port ranges by category

### Web UIs (browser access)

```
3000-3005, 5000, 5050, 5055, 6969, 7878-7879, 8088, 8096,
8181-8182, 8282, 8686, 8989-8990, 9696, 9705, 18081, 32400
```

### APIs (service communication)

```
5001, 5432, 8000, 8080, 8888, 9090-9091
```

### Proxy

```
18080
```

---

## Firewall configuration

### Minimum required ports

For basic DUMB operation, publish only:

| Port | Required For |
|------|--------------|
| 3005 | DUMB Frontend and its `/api`/`/ws` proxy |

### Full access

For complete functionality including all service UIs:

```bash
# Example UFW configuration
sudo ufw allow 3005/tcp  # DUMB Frontend
sudo ufw allow 18080/tcp # Traefik (embedded UIs)
sudo ufw allow 32400/tcp # Plex
```

The backend port `8000` is loopback-only and unpublished by default. Expose it only when a direct API consumer requires it, after changing `dumb.api_service.host` to `0.0.0.0`, enabling authentication, and restricting network access.

!!! tip "Use Traefik for consolidated access"

    Instead of exposing all service ports, enable embedded UIs and access services through Traefik on port 18080. See [Embedded UIs](../features/embedded-ui.md).

---

## Related pages

- [Embedded UIs](../features/embedded-ui.md)
- [Configuration](../features/configuration.md)
- [Services Overview](../services/index.md)

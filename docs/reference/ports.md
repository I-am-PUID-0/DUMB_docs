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
| 3005 | DUMB Frontend | Web UI |
| 5000 | CLI Debrid | Web UI |
| 5001 | CLI Battery | API |
| 5050 | pgAdmin | Web UI |
| 5055 | Seerr | Web UI |
| 5432 | PostgreSQL | Database |
| 6969 | Whisparr | Web UI |
| 7878 | Radarr (Decypharr) | Web UI |
| 7879 | Radarr (NzbDAV) | Web UI |
| 8000 | DUMB API | API |
| 8080 | Riven Backend | API |
| 8080 | NzbDAV Backend | API |
| 8096 | Jellyfin | Web UI |
| 8096 | Emby | Web UI |
| 8181 | Tautulli | Web UI |
| 8182 | Zilean | Web UI/API |
| 8282 | Decypharr | Web UI |
| 8686 | Lidarr | Web UI |
| 8888 | Phalanx DB | API |
| 8989 | Sonarr (Decypharr) | Web UI |
| 8990 | Sonarr (NzbDAV) | Web UI |
| 9090 | Zurg (Riven) | API |
| 9091 | Zurg (CLID) | API |
| 9696 | Prowlarr | Web UI |
| 9705 | Huntarr | Web UI |
| 18080 | Traefik | Proxy |
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

The backend API that powers service management, configuration, and monitoring.

```
http://localhost:8000/api/...
```

### DUMB Frontend

| Property | Value |
|----------|-------|
| **Port** | 3005 |
| **Type** | Web UI |
| **Protocol** | HTTP |

The main dashboard for managing DUMB services.

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

!!! warning "NzbDAV port overlap"

    The default NzbDAV ports (`3000` and `8080`) overlap with Riven defaults.
    If you run both services, change one set of ports to avoid conflicts.

---

## Arr suite

The Arr applications support multiple instances for different workflows (Decypharr vs NzbDAV).

### Sonarr (TV shows)

| Instance | Port |
|----------|------|
| Decypharr | 8989 |
| NzbDAV | 8990 |

```
http://localhost:8989  # Decypharr instance
http://localhost:8990  # NzbDAV instance
```

### Radarr (Movies)

| Instance | Port |
|----------|------|
| Decypharr | 7878 |
| NzbDAV | 7879 |

```
http://localhost:7878  # Decypharr instance
http://localhost:7879  # NzbDAV instance
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

---

## Optional services

### Huntarr

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

---

## Dependent services

### Zurg

| Instance | Port | Use Case |
|----------|------|----------|
| Riven | 9090 | Riven workflow |
| CLID | 9091 | CLI Debrid workflow |

```
http://localhost:9090  # Riven instance
http://localhost:9091  # CLID instance
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
postgresql://localhost:5432/dumb
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
3000-3005, 5000, 5050, 5055, 6969, 7878-7879, 8096,
8181-8182, 8282, 8686, 8989-8990, 9696, 9705, 32400
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

For basic DUMB operation, expose these ports:

| Port | Required For |
|------|--------------|
| 3005 | DUMB Frontend |
| 8000 | DUMB API |

### Full access

For complete functionality including all service UIs:

```bash
# Example UFW configuration
sudo ufw allow 3005/tcp  # DUMB Frontend
sudo ufw allow 8000/tcp  # DUMB API
sudo ufw allow 18080/tcp # Traefik (embedded UIs)
sudo ufw allow 32400/tcp # Plex
```

!!! tip "Use Traefik for consolidated access"

    Instead of exposing all service ports, enable embedded UIs and access services through Traefik on port 18080. See [Embedded UIs](../features/embedded-ui.md).

---

## Related pages

- [Embedded UIs](../features/embedded-ui.md)
- [Configuration](../features/configuration.md)
- [Services Overview](../services/index.md)

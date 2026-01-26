---
title: Traefik proxy
icon: lucide/traffic-cone
---

# Traefik proxy

Traefik provides optional reverse-proxy routing for service UIs. When enabled, it exposes a single entry point and maps services to path-based routes.

---

## What Traefik does in DUMB

- Builds dynamic routes for enabled services
- Adds path prefixes for UI services (for example `/sonarr/`, `/radarr/`)
- Supports embedded iframes in the frontend

---

## Default access

| Component | Default |
|-----------|---------|
| Traefik entrypoint | `http://<host>:18080/` |
| DUMB API (Scalar) | `http://<host>/dumb_api_service/scalar` |
| DUMB Frontend | `http://<host>/dumb_frontend/` |

!!! info "Path prefixes"

    Some services use explicit prefixes (for example Emby/Jellyfin use `/web`), which Traefik preserves.

---

## How routes are generated

The backend generates Traefik config based on enabled services and their ports. Services with UIs are registered automatically when they are enabled in `dumb_config.json`.

---

## Security considerations

!!! warning "No built-in auth"

    Most service UIs do not require authentication. If you expose Traefik outside your LAN, add authentication and TLS at the proxy layer.

---

## Related pages

- [Embedded UIs](../features/embedded-ui.md)
- [Service ports](../reference/ports.md)

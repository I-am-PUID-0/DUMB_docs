---
title: Traefik proxy
icon: lucide/traffic-cone
---

# Traefik proxy

Traefik provides optional reverse-proxy routing for service UIs and user-managed external routes. When enabled, it exposes a single entry point and maps requests to services through DUMB-generated dynamic config and, optionally, Traefik Proxy Admin.

---

## What Traefik does in DUMB

- Builds dynamic routes for enabled embedded service UIs
- Adds path prefixes for UI services under `/service/ui/<service>`
- Supports embedded iframes in the frontend
- Can poll Traefik Proxy Admin for user-managed host-based reverse proxy routes
- Can receive public traffic through the optional Cloudflared service

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

DUMB separates Traefik configuration ownership into lanes:

| Owner | Purpose | Location or endpoint |
|-------|---------|----------------------|
| DUMB | Static Traefik configuration | `/config/traefik/traefik.yml` |
| DUMB | Embedded UI dynamic routes | `/config/traefik/dynamic/services.yaml` |
| DUMB | Optional custom dynamic routes from `traefik.services`/`traefik.middlewares` | `/config/traefik/dynamic/dynamic_config.yml` |
| Traefik Proxy Admin | User-managed reverse proxy routes | `http://127.0.0.1:3004/api/traefik/config` |

Traefik watches `/config/traefik/dynamic` with the file provider. When Traefik Proxy Admin is enabled, DUMB also adds Traefik's HTTP provider pointed at TPA's generated config endpoint.

---

## Security considerations

!!! warning "No built-in auth"

    Most service UIs do not require authentication. If you expose Traefik outside your LAN, add authentication and TLS at the proxy layer.

---

## Related pages

- [Embedded UIs](../features/embedded-ui.md)
- [Traefik Proxy Admin](../services/optional/traefik-proxy-admin.md)
- [Cloudflared](../services/optional/cloudflared.md)
- [Service ports](../reference/ports.md)

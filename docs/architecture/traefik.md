---
title: Traefik proxy
icon: lucide/traffic-cone
---

# Traefik proxy

Traefik provides optional reverse-proxy routing for service UIs and user-managed external routes. When enabled, it exposes a single entry point and maps requests to services through DUMB-generated dynamic config and, optionally, Traefik Proxy Admin. Cloudflared can then carry Cloudflare Tunnel traffic to that same entrypoint.

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
| DUMB API (Scalar) | `http://<host>:18080/service/ui/dumb_api_service/scalar` |
| DUMB Frontend | `http://<host>:3005/` (published directly, not through the embedded-service route set) |

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

This split is intentional:

- DUMB can safely regenerate embedded UI routes whenever services change.
- TPA can manage host-based routes, auth, and middleware without DUMB overwriting them.
- Cloudflared can bring external traffic to Traefik without replacing either DUMB's routes or TPA's routes.

---

## Default configuration

```json
"traefik": {
  "enabled": false,
  "process_name": "Traefik",
  "pinned_version": "v3.6.6",
  "suppress_logging": false,
  "log_level": "INFO",
  "log_file": "/log/traefik.log",
  "access_log_file": "/log/traefik_access.log",
  "port": 18080,
  "entrypoints": {
    "web": {
      "address": ":18080"
    }
  },
  "command": [
    "/traefik/traefik",
    "--configFile=/config/traefik/traefik.yml"
  ],
  "config_dir": "/config/traefik",
  "config_file": "/config/traefik/traefik.yml"
}
```

`pinned_version` selects the Traefik binary DUMB installs. The config and both
log paths live under the persistent `/config` and `/log` mounts. DUMB rewrites
its generated route files when service UI definitions change; put operator-owned
host routes in Traefik Proxy Admin rather than editing `services.yaml` by hand.

---

## Security considerations

!!! warning "Embedded routes do not add auth"

    DUMB's generated embedded-service routes do not add an authentication
    middleware. Some upstream apps have their own login and some do not. If you
    expose Traefik outside your LAN, use protected TPA routes, Cloudflare Access,
    or another deliberate authentication layer and verify it before publishing.

---

## Related pages

- [Embedded UIs](../features/embedded-ui.md)
- [Traefik Proxy Admin](../services/optional/traefik-proxy-admin.md)
- [Cloudflared](../services/optional/cloudflared.md)
- [Service ports](../reference/ports.md)

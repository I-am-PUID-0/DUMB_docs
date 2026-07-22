---
title: Frontend architecture
icon: lucide/monitor
---

# Frontend architecture

The DUMB frontend is a Nuxt 4 application that renders the dashboard, service controls, and embedded UIs. It communicates with the DUMB API for configuration, logs, metrics, and service status.

---

## Key directories

| Path | Purpose |
|------|---------|
| `pages/` | Route-driven pages (dashboard, settings, onboarding) |
| `components/` | Reusable UI components |
| `composables/` | Shared logic and API hooks |
| `stores/` | Pinia stores for app state |
| `services/` | API clients and service abstractions |
| `layouts/` | Layout templates |

---

## Data flow

```mermaid
%%{ init: { "flowchart": { "curve": "basis" } } }%%
flowchart LR
    CLIENT([Browser UI or API client])
    ST[Pinia stores]
    FE[dmbdb server<br/>port 3005]
    BE[[DUMB API<br/>127.0.0.1:8000]]

    CLIENT ==>|UI state| ST
    ST ==>|REST /api/*| FE
    CLIENT ==>|external REST /api/*| FE
    FE ==>|strip /api and forward| BE
    CLIENT -.->|WebSocket /ws/*| FE
    FE -.->|forward unchanged| BE
```

The frontend server is also the public API gateway. Its `/api/*` middleware
removes the leading `/api` and forwards the request to the backend-native route
on port `8000`. For example, `:3005/api/config` becomes `:8000/config`.
WebSockets use `/ws/*` on both sides and are forwarded without that rewrite.

This same-origin design lets the browser avoid cross-origin API calls and means
the standard Compose deployment needs to publish only port `3005`. External
automation can use the gateway too; backend authentication is still applied
after the request is forwarded.

---

## Embedded service UIs

The frontend can embed service UIs in iframes when Traefik is enabled, keeping navigation and authentication within the DUMB experience.

!!! tip "Traefik paths"

    DUMB-owned embedded UIs use Traefik paths like `http://<host>:18080/service/ui/radarr` or `http://<host>:18080/service/ui/sonarr` when proxying is enabled. Inside dmbdb service pages, iframe traffic is routed through frontend `/ui/<service>` paths so root-style service apps can keep their own relative URLs.

---

## Configuration UX

Configuration editing is performed in the settings UI, which:

- Reads service config from the API
- Validates changes client-side where possible
- Submits updates to the backend for persistence

---

## Related pages

- [Frontend overview](../frontend/index.md)
- [Dashboard guide](../frontend/dashboard.md)
- [Settings guide](../frontend/settings.md)

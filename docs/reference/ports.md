---
title: Service ports
description: Look up default DUMB listener ports, identify collisions, and choose which ports to publish for dashboards, media clients, and external integrations.
icon: lucide/network
---

# Service ports

These are **fresh-configuration defaults**, not a report of your running stack. Check the port saved in the dashboard or `/config/dumb_config.json` before adding a Docker mapping or configuring another application.

The maintained Compose file publishes **3005 only**. It serves the dashboard, REST gateway (`/api/*`), and WebSockets (`/ws/*`). Embedded UIs use this address too; individual service ports are needed for direct clients and external integrations.

## DUMB listeners

| Service | Default port | Access |
|---|---:|---|
| DUMB Frontend and API gateway | 3005 | `http://<host>:3005`; normal entry point |
| DUMB API | 8000 | Container loopback `127.0.0.1`; not published by default |
| Traefik embedded UI proxy | 18080 | Internal frontend proxy target; direct access requires a mapping |
| Traefik dashboard/API | 18081 | Entry point plus one; normally consumed internally |

Use `http://<host>:3005/api/process/processes` for REST requests. WebSocket requests use `ws://<host>:3005/ws/status` without `/api`. See the [API guide](../api/index.md).

## Workflow and media services

| Service | Default port | Purpose / direct path |
|---|---:|---|
| Riven Frontend | 3000 | Web UI |
| Riven Backend | 8080 | API |
| CLI Debrid | 5000 | Web UI |
| CLI Battery | 5001 | API; separate listener only for versions using the external service |
| Decypharr | 8282 | Web UI/API |
| InfiniDysk frontend | 3000 | Web UI |
| InfiniDysk backend | 8080 | API/WebDAV |
| AltMount | 8088 | Web UI/API; `/live` readiness endpoint |
| Plex Media Server | 32400 | `/web` |
| Jellyfin | 8096 | Web UI/API |
| Emby | 8096 | Web UI/API |

<!-- dev:start -->
Native InfiniDysk 2 uses its backend listener for the native application UI as well. Read the [InfiniDysk guide](../services/core/infinidysk.md) for the selected generation rather than assuming the generation 1 split applies.
<!-- dev:end -->

## Arr applications and library tools

| Service | Default port | Purpose |
|---|---:|---|
| Sonarr | 8989 | TV |
| Radarr | 7878 | Movies |
| Lidarr | 8686 | Music |
| Whisparr | 6969 | Adult media |
| Prowlarr | 9696 | Indexers |
| NeutArr | 9705 | Search automation |
| Profilarr | 6868 | Profiles and custom formats |
| Seerr | 5055 | Requests |
| Bazarr | 6767 | Subtitles |
| Tautulli | 8181 | Plex monitoring |
| Pulsarr | 3003 | Watchlist automation |
| Maintainerr | 6246 | Library rules |
| Zilean | 8182 | Lookup API |

These defaults refer to the first configured instance. A second Sonarr or Radarr often receives `8990` or `7879`, but those values are not reserved for a particular instance. See [multi-instance configuration](instances.md).

## Optional access and streaming services

| Service | Default port | Notes |
|---|---:|---|
| AIOStreams | 3006 | `/stremio/configure`; addon clients need a stable trusted HTTPS `base_url` |
| mediastorm | 7777 | `/admin` |
<!-- dev:start -->
| Audiobookshelf | 13378 | `/audiobookshelf/`; reverse proxies must support WebSockets |
<!-- dev:end -->
| Traefik Proxy Admin | 3004 | Web UI/API |
| Authelia | 9091 | Identity portal/API |
| Cloudflared | None | Outbound tunnel connector; no local web UI listener |

Use the [AIOStreams publishing guide](../services/optional/aiostreams.md#publish-aiostreams-for-stremio) for its public addon address. The embedded `/ui/aiostreams` address is not its public `base_url`.

## Storage and database services

| Service | Default port | Protocol |
|---|---:|---|
| Zurg | 9090 | HTTP/WebDAV |
| Phalanx DB | 8888 | HTTP API |
| PostgreSQL | 5432 | PostgreSQL, not HTTP |
| pgAdmin | 5050 | Web UI |

A second Zurg instance often receives `9091`, which also overlaps Authelia's default. Use the assigned port, not an assumed sequence.

## Port collisions

DUMB checks enabled-service ports and can move a conflicting listener to the next available port, then save the result. This includes InfiniDysk frontend/backend ports. Traefik reserves its entry point and dashboard together.

Common default overlaps are:

- Riven and InfiniDysk: `3000` and `8080`.
- Jellyfin and Emby: `8096`.
- A second Zurg instance and Authelia: `9091`.

Docker mappings do not update themselves when an internal listener changes. If a service moves from `8096` to `8097`, update its mapping and any direct consumers. Embedded routing uses DUMB's generated service configuration.

## Publish only the listeners you use

For example, a stack with direct Plex access can publish:

```yaml
ports:
  - "3005:3005"   # DUMB dashboard, API gateway, embedded UIs
  - "32400:32400" # Plex clients
```

Add a service mapping when another application or device needs it. A web UI being available through the dashboard does not expose its native protocol to external clients.

The backend's default `127.0.0.1:8000` listener cannot be exposed by adding `8000:8000` alone. Direct backend access also requires changing `dumb.api_service.host`. Prefer the existing gateway and follow [networking guidance](../deployment/networking.md) when changing exposure.

DUMB authentication protects its own API and dashboard flows. Direct upstream application ports and published Traefik routes need their own access controls. Docker's published-port firewall behavior also depends on the host; see [Docker packet filtering](https://docs.docker.com/engine/network/packet-filtering-firewalls/).

## Related pages

- [Networking and ports](../deployment/networking.md)
- [Embedded UIs](../features/embedded-ui.md)
- [Service catalog](../services/index.md)

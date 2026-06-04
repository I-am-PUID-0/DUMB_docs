---
title: Optional Services Overview
icon: lucide/puzzle
---

# Optional Services

Optional services enhance the DUMB ecosystem by adding scraping capabilities, database tools, request automation, or controlled access paths. These are not required by every core service to function, but they can improve performance, visibility, automation, and how you expose selected services.

---

## What Are Optional Services?

Optional services are:

* Not essential for startup or core functionality
* Dynamically linked during runtime if available
* Frequently used to improve performance, metadata accuracy, or user experience

---

## Optional Service Index

| Service                           | Description                                                 | Used By                        |
| --------------------------------- | ----------------------------------------------------------- | ------------------------------ |
| [pgAdmin](../optional/pgadmin.md) | Web-based PostgreSQL administration UI                      | PostgreSQL                     |
| [Riven Frontend](../optional/riven-frontend.md) | Web-based UI for management of the [Riven Backend](../core/riven-backend.md) | Riven |
| [Tautulli](../optional/tautulli.md) | Plex monitoring and statistics                            | Plex Media Server              |
| [Pulsarr](../optional/pulsarr.md) | Plex watchlist request automation                         | Plex, Sonarr, Radarr           |
| [Traefik Proxy Admin](../optional/traefik-proxy-admin.md) | User-managed Traefik reverse proxy routes | Traefik, PostgreSQL |
| [Cloudflared](../optional/cloudflared.md) | Cloudflare Tunnel connector for DUMB Traefik | Traefik |
| [Zilean](../optional/zilean.md)   | Debrid scraper and metadata cache for various core services | Riven, CLI Debrid, Plex Debrid |

---

## How They Work

Optional services attach to the DUMB ecosystem dynamically:

* **[pgAdmin](../optional/pgadmin.md)** provides a GUI for exploring and managing the PostgreSQL instance used by Riven and Zilean.
* **[Riven Frontend](../optional/riven-frontend.md)** provides a GUI for exploring and managing content requests that are facilitated by the [Riven Backend](../core/riven-backend.md).
* **[Tautulli](../optional/tautulli.md)** monitors your Plex server, tracking playback history, user activity, and providing detailed statistics.
* **[Pulsarr](../optional/pulsarr.md)** monitors Plex watchlists and routes approved requests into Sonarr and Radarr.
* **[Traefik Proxy Admin](../optional/traefik-proxy-admin.md)** lets operators create Traefik reverse proxy routes for services inside or outside the DUMB container. It owns user-managed host routes while DUMB continues to own embedded UI routes.
* **[Cloudflared](../optional/cloudflared.md)** runs a Cloudflare Tunnel connector inside DUMB so public traffic can reach the built-in Traefik entrypoint without direct port forwarding. Cloudflared carries traffic to Traefik; Traefik and TPA still decide which service receives it.
* **[Zilean](../optional/zilean.md)** improves scraping efficiency by caching previous results from [Debrid Media Manager](https://debridmediamanager.com/) hash lists shared by users and reducing redundant queries. Core services like Riven and CLI Debrid can use it as a scraping backend.

These services can be disabled at any time without affecting the startup of core or dependent services.

---

## Tips

* If not using Zilean, make sure other scrapers are configured in Riven and CLI Debrid.
* pgAdmin is useful during debugging, migrations, or manual SQL work — but not required for normal operation.
* Use Traefik Proxy Admin and Cloudflared together when you want public hostnames without opening router ports. Configure protection before publishing sensitive services.
* You can start optional services manually from the DUMB Frontend or include them in onboarding.

---

## Related Pages

* [Core Services](../core/index.md)
* [Dependent Services](../dependent/index.md)
* [How Services Work Together](../index.md#-how-the-services-work-together)

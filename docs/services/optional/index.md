---
title: Optional Services Overview
icon: lucide/puzzle
---

# Optional Services

Optional services enhance the DUMB ecosystem by adding scraping capabilities, database tools, or alternate content discovery paths. These are not required by any core service to function but can improve performance, visibility, and control.

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
| [Zilean](../optional/zilean.md)   | Debrid scraper and metadata cache for various core services | Riven, CLI Debrid, Plex Debrid |

---

## How They Work

Optional services attach to the DUMB ecosystem dynamically:

* **[pgAdmin](../optional/pgadmin.md)** provides a GUI for exploring and managing the PostgreSQL instance used by Riven and Zilean.
* **[Riven Frontend](../optional/riven-frontend.md)** provides a GUI for exploring and managing content requests that are facilitated by the [Riven Backend](../core/riven-backend.md).
* **[Tautulli](../optional/tautulli.md)** monitors your Plex server, tracking playback history, user activity, and providing detailed statistics.
* **[Zilean](../optional/zilean.md)** improves scraping efficiency by caching previous results from [Debrid Media Manager](https://debridmediamanager.com/) hash lists shared by users and reducing redundant queries. Core services like Riven and CLI Debrid can use it as a scraping backend.

These services can be disabled at any time without affecting the startup of core or dependent services.

---

## Tips

* If not using Zilean, make sure other scrapers are configured in Riven and CLI Debrid.
* pgAdmin is useful during debugging, migrations, or manual SQL work — but not required for normal operation.
* You can start optional services manually from the DUMB Frontend or include them in onboarding.

---

## Related Pages

* [Core Services](../core/index.md)
* [Dependent Services](../dependent/index.md)
* [How Services Work Together](../index.md#-how-the-services-work-together)

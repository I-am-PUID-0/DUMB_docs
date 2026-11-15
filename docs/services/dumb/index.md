---
title: DUMB Services Overview
description: Understand the DUMB backend API and dashboard, their default ports, and where to look when the management interface is unavailable.
icon: lucide/link
---

# DUMB services

The backend API and dashboard provide the management interface for the stack. They start with the container when enabled; the default configuration enables both.

## DUMB service index

| Service | Default port | Purpose |
|---|---|---|
| [DUMB API](api.md) | `8000` | Configuration, service control, logs, health, and background-job APIs |
| [DUMB Frontend](dumb-frontend.md) | `3005` | Onboarding, dashboard, service pages, and settings |

The dashboard's server proxies browser requests to the API. In the maintained Docker setup, publish the frontend port; the backend can stay on loopback inside the container.

## How they work

The backend coordinates managed service processes and shared state. The dashboard reads that state and sends requested actions to the API. Disabling the dashboard removes browser access but does not turn the backend into a different service manager. Disabling the API makes dashboard controls unavailable.

## If the dashboard does not load

1. Confirm the DUMB container is running and the frontend port is published.
2. Inspect the **DUMB Frontend** and **DUMB API** startup logs.
3. If the page opens but actions fail, check API connectivity and your authentication session.
4. Use the ports saved in your running configuration if you changed the defaults.

See [networking and ports](../../deployment/networking.md), [API reference](../../api/index.md), and [dashboard guide](../../frontend/index.md).

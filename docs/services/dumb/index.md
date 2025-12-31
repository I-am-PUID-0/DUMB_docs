---
title: DUMB Services Overview
---

# DUMB Services

DUMB includes two internal services that form the backbone of the entire system:

* The **DUMB API** provides centralized coordination, configuration management, and control over all other services.
* The **DUMB Frontend** offers a web-based interface for monitoring, onboarding, logging, and runtime service interaction.

These services are always required and are started automatically when the container launches.

---

## What Are DUMB Services?

DUMB services are:

* **Core to the platform infrastructure**
* **Always-on** - though not recommended, they can be disabled if needed or desired 
* Required for orchestration, onboarding, and log visibility

---

## DUMB Service Index

| Service                                       | Description                                                                | Role                         |
| --------------------------------------------- | -------------------------------------------------------------------------- | ---------------------------- |
| [DUMB API](../dumb/api.md)             | FastAPI backend for service control, config updates, log streaming, health | Orchestration & Coordination |
| [DUMB Frontend](../dumb/dumb-frontend.md) | Web interface for onboarding, log viewing, and service control             | UI & User Interaction        |

---

## How They Work

* **[DUMB API](../dumb/api.md)** is the internal backend that exposes HTTP endpoints for service management, logs, onboarding, and health monitoring. It must be responsive for any service to be monitored or configured.
* **[DUMB Frontend](../dumb/dumb-frontend.md)** connects to the DUMB API and renders a modern web interface to help users manage their instance through onboarding steps, status dashboards, log viewers, and config editors.

These services talk to each other over localhost and coordinate all other configured components.

---

## Tips

* Both services are auto-launched and should not be disabled.
* If the UI does not load, check the logs for `dumb_frontend` and `dumb_api`.
* Configuration updates and onboarding rely on the DUMB API — make sure it is reachable and healthy.

---

## Related Pages

* [API](../../api/index.md)
* [Core Services](../core/index.md)
* [Dependent Services](../dependent/index.md)
* [Optional Services](../optional/index.md)
* [How Services Work Together](../index.md#-how-the-services-work-together)

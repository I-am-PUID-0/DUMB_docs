---
title: Frontend Overview
icon: lucide/layout-dashboard
---

# DUMB Frontend

The DUMB Frontend is a modern web application built with Nuxt 4 (Vue 3) that provides a unified interface for managing and monitoring all DUMB services. It communicates with the DUMB API to control services, view logs, and monitor system health.

---

## Overview

The frontend provides:

- **Service dashboard** - View and control all services from a single page
- **Real-time monitoring** - Live status updates and system metrics
- **Onboarding wizard** - Guided setup for first-time configuration
- **Log viewer** - Real-time and historical log access with filtering
- **Settings management** - Configure services, users, and preferences
- **Embedded service UIs** - Access service interfaces without leaving DUMB

---

## Default port

| Service | Port |
|---------|------|
| DUMB Frontend | 3005 |

When accessed through Traefik, the frontend is available at port `18080`.

---

## Key pages

| Page | Path | Purpose |
|------|------|---------|
| [Dashboard](dashboard.md) | `/` | Service overview and control |
| [Onboarding](onboarding.md) | `/onboarding` | Initial setup wizard |
| [Settings](settings.md) | `/settings` | Configuration and user management |
| [Service pages](service-pages.md) | `/settings` | Auto-restart, auto-update, config editors |
| [Metrics](metrics.md) | `/metrics` | System resource monitoring |
| Service Detail | `/services/[id]` | Individual service management |
| Login | `/login` | User authentication |
| Setup | `/setup` | First-time user creation |

---

## Features

### Real-time updates

The frontend maintains WebSocket connections to receive live updates:

- **Service status** - Running/stopped state, health checks
- **System metrics** - CPU, memory, disk usage
- **Log streaming** - New log entries as they occur

### Service control

Start, stop, and restart services directly from the dashboard or service detail pages. The frontend shows:

- Current status (running, stopped, unknown)
- Health check results
- Auto-restart count and status
- Last restart timestamp

### Embedded service UIs

When enabled, access service web interfaces directly within DUMB:

- Riven Frontend
- pgAdmin
- Seerr
- Tautulli
- Arr services (Radarr, Sonarr, etc.)
- And more

This provides a unified experience without exposing individual service ports.

### Split view mode

Compare two pages side-by-side with the resizable split view:

- Monitor logs while viewing dashboard
- Compare service configurations
- View metrics alongside service details

### Service detail pages

Each service has a dedicated detail page with:

- Live status and health
- Embedded UI tab when available
- Config and log shortcuts
- Auto-restart controls

---

## Authentication

The frontend supports optional JWT-based authentication:

- **First-time setup** - Create admin account or skip authentication
- **Login** - Secure access with username/password
- **Remember me** - Persistent sessions across browser restarts
- **User management** - Create, disable, and delete users

See the [Authentication](../features/authentication.md) guide for details.

---

## Configuration

The frontend reads its configuration from environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DUMB_API_URL` | `http://127.0.0.1:8000` | Backend API endpoint |
| `NUXT_TELEMETRY_DISABLED` | `1` | Disable Nuxt telemetry |

---

## Browser support

The frontend is tested on modern browsers:

- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

---

## Next steps

- [Dashboard](dashboard.md) - Learn about the main service view
- [Onboarding](onboarding.md) - Set up DUMB for the first time
- [Settings](settings.md) - Configure preferences and users
- [Metrics](metrics.md) - Monitor system resources

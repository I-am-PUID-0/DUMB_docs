---
title: Startup lifecycle
description: Understand DUMB startup phases, readiness checks, degraded startup, Docker health, notification baselining, and startup performance controls.
icon: lucide/activity
---

# Startup lifecycle

DUMB distinguishes a service that is still starting from one that is unhealthy
in steady state. The lifecycle is:

1. `initializing`
2. `preinstalling`
3. `starting_services`
4. `stabilizing`
5. `ready` or `degraded`
6. `shutting_down`

The DUMB API starts before enabled-service preinstall. An already-installed
frontend can also start early, so the dashboard can show startup progress while
large service installs or migrations continue.

## Readiness and stabilization

During `stabilizing`, DUMB checks every enabled process and each configured
`port`, `frontend_port`, `backend_port`, and `webdav_port`. Every enabled
service must remain ready for the stabilization window before the lifecycle
becomes `ready`.

```json
"dumb": {
  "startup": {
    "readiness_timeout_seconds": 300,
    "readiness_poll_interval_seconds": 5,
    "stabilization_seconds": 15
  }
}
```

| Setting | Default | Purpose |
|---------|---------|---------|
| `readiness_timeout_seconds` | `300` | Maximum time to wait for all enabled services |
| `readiness_poll_interval_seconds` | `5` | Delay between readiness checks |
| `stabilization_seconds` | `15` | Continuous healthy period required before `ready` |

If the deadline expires, DUMB enters `degraded` instead of shutting down the
API/frontend. The dashboard identifies services that missed readiness, and one
consolidated degraded-startup notification can be routed to operators.

## Startup-safe monitoring

Until startup reaches `ready` or `degraded`:

- Auto-restart does not health-check or restart services.
- Automatic service, resource, database, and recovery notifications are
  suppressed.
- Database Health does not probe a service that is still starting.
- Manual notification tests remain available.
- Docker health reports startup progress instead of declaring the container
  unhealthy merely because a slow service is still initializing.

When startup becomes terminal, notification monitoring records a fresh
baseline. It does not send recovery messages for failures that existed only
during startup. Persistent conditions must still satisfy their normal duration
threshold before they alert.

Auto-restart then applies its grace period. A successful process spawn is only
an attempt; DUMB records `service.auto_restart.succeeded` after the restarted
service passes health checks.

## Preinstall behavior

Every enabled instance is preinstalled. Instances of the same service key run
sequentially so shared source/runtime trees are not modified concurrently,
while different service keys can still preinstall in parallel.

A failed preinstall is retried through normal service startup. Startup is
reported as degraded only if the service still misses the final readiness
deadline.

## Ownership and network storage

Startup ownership repair no longer performs a full count pass followed by a
second walk. It caps ownership workers and treats correctly owned top-level
trees as healthy, avoiding repeated traversal of large package caches on NFS.
Service-specific setup still repairs a subtree when its top-level ownership is
wrong.

JavaScript package caches are disposable. For NFS-backed `/config`, consider
moving these existing cache roots to host-local storage with the matching
environment overrides:

- `DUMB_PNPM_STORE_ROOT`
- `DUMB_BUN_CACHE_ROOT`
- `DUMB_YARN_CACHE_ROOT`

Keep durable service configuration and databases on storage appropriate for
their recovery requirements.

## API

When capability `startup_lifecycle` is true:

```http
GET /api/process/startup-status
```

The response includes the current phase, timestamps, expected services,
per-service `pending`/`starting`/`ready` state, and terminal failures.

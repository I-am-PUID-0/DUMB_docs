---
title: DUMB API
icon: lucide/code
---

# DUMB API
The **DUMB API** is the central communication layer between the DUMB Frontend and the backend service. It handles requests for logs, service management (start/stop), configuration updates, and health checks.

## Access model

The maintained Compose file does not publish port `8000`. The API binds to `127.0.0.1:8000` inside the DUMB container and dmbdb proxies it through the normal frontend address:

| Use | URL |
|---|---|
| REST through dmbdb | `http://<host>:3005/api/<backend-path>` |
| WebSockets through dmbdb | `ws://<host>:3005/ws/<stream>` |
| Native API inside the container | `http://127.0.0.1:8000/<backend-path>` |

For example, native `/process/processes` is exposed as `/api/process/processes` through dmbdb. WebSocket routes do not gain an `/api` prefix.

The proxy is available to more than the dashboard itself. Scripts, integrations,
and other API clients can call `http://<host>:3005/api/...`; dmbdb removes the
gateway prefix and forwards the request to FastAPI. The backend performs the
same authentication and authorization checks regardless of which access path
was used.

!!! danger "Direct exposure"
    Setting `host` to `0.0.0.0` and publishing port `8000` exposes powerful lifecycle and configuration endpoints. Enable DUMB authentication and restrict the port to trusted networks before doing this.

---

## Development and release versions

DUMB's `dev` branch records the version planned for the next stable release.
The source/API version is a plain semantic version such as `2.24.0`; a
development image displays a rolling identity such as `v2.24.0-dev.34` and the
**Dev build** badge in **Settings → About**. The development suffix identifies
the image build. API compatibility checks use the source/API core version and
the backend's advertised capabilities.

The release manifest tracks the last actual stable release. For example,
while the stable release is `2.23.0`, development source can declare `2.24.0`
with a manifest baseline of `2.23.0`. Promoting that work through the normal
`master` release process produces `2.24.0`. Advancing the development source
version does not consume that release number or create a stable tag.

### Keeping the development version current

The **Sync dev version** workflow runs after a `dev` push, after publication of
a stable release, and when manually requested. It calculates the next version
from the actual stable release and subsequent commits using the pinned
release-please calculator and repository release policy. When necessary, it
commits only `pyproject.toml` and `.github/.release-please-manifest.json` back
to `dev`. It keeps the manifest at the stable baseline and updates the source
version to the candidate.

After `2.24.0` is released, the next development candidate is normally
`2.24.1`; a new feature can make it `2.25.0` under the release policy.
Repeating synchronization with unchanged release history and commits makes
no new commit. Its own version-update commit can trigger ordinary CI and
another synchronization check, which makes no further change.

For maintainers:

- Use **Actions → Sync dev version → Run workflow**, selecting **dev**. Enable
  **Calculate the dev version without committing it** for a preview-only run;
  leave it disabled to apply a needed metadata update. Check the workflow
  summary for the stable baseline, candidate API version and source SHA.
  Rerun after correcting an access or configuration failure.
- The workflow uses the existing `RELEASE_PLEASE_TOKEN`. Its authenticated
  GitHub account supplies the commit identity. That token must be able to
  write repository contents on `dev` under the repository's branch rules;
  token-created commits allow the normal CI checks to run.
- A concurrent change to the branch must not be overwritten. If the expected
  branch head changes before the update is accepted, rerun synchronization
  against the current head.
- Synchronization updates source metadata. It does not create a release PR,
  stable tag, GitHub release, or container image. Image builds retain their
  manual and release-triggered entry points.

dmbdb uses the same synchronization approach with its own `main` release
branch, package version and stable release history. Its candidate version is
independent of the DUMB API version. See
[frontend development versions](dumb-frontend.md#frontend-development-versions).

Manual `dev` image builds also calculate the API version once for the
requested immutable DUMB commit, so both architecture builds use the same
version even when synchronization has not yet landed. The build keeps that
requested source SHA; it does not silently check out a newer `dev` commit.
See [building a development image](dumb-frontend.md#build-a-development-image-with-a-chosen-frontend)
for frontend selection and image digest checks.

## Configuration Settings in `dumb_config.json`
Located in `dumb.api_service`:
```json
"enabled": true,
"process_name": "DUMB API",
"log_level": "INFO",
"host": "127.0.0.1",
"port": 8000
```

### Configuration Key Descriptions
- **`enabled`** – Whether the API service should run.
- **`process_name`** – Used in process management and logs.
- **`log_level`** – Logging verbosity for the API.
- **`host`** – Address on which the backend listens. Keep the default loopback value when using dmbdb.

    !!! note "`0.0.0.0` allows access to the API from all addresses"

- **`port`** – Internal backend listener port. It is not automatically published to the Docker host.

## What the API owns

- Optional JWT authentication and user setup
- Service lifecycle, dependency graphs, update controls, and onboarding
- DUMB and service configuration validation/persistence
- Logs, current metrics, metrics history, Database Health, and notifications
- Symlink repair/snapshots and guarded SQLite-to-PostgreSQL migration jobs
- Optional AI diagnostic bundle preview and provider calls
- Real-time log, status, and metrics WebSockets

The backend advertises optional features through `GET /process/capabilities`. Frontends and automation should gate newer actions on these capability flags instead of assuming every DUMB version supports every endpoint.

## Health and interactive schema

- Native health check: `GET /health`
- OpenAPI JSON: `/openapi.json`
- Swagger UI: `/docs`
- Scalar UI: `/scalar`

The interactive documentation endpoints live on the native backend listener. See the [API overview](../../api/index.md) for access choices and the complete reference.

## Persistence and logs

API settings are stored with the main runtime configuration at `/config/dumb_config.json`. Authentication users and the generated JWT secret are stored separately at `/config/users.json`. DUMB logs are written below the configured `/log` directory.

When the backend exposes `runtime_api_log_level`, the DUMB API service page can
temporarily enable DEBUG logging for the running DUMB and Uvicorn loggers. This
requires no restart, does not modify `dumb_config.json`, and automatically
returns to configured logging after the override is disabled or the container
restarts. It does not change managed-service verbosity.

## Related pages

- [API overview](../../api/index.md)
- [Authentication](../../features/authentication.md)
- [Configuration API](../../api/config.md)
- [Process Management API](../../api/process.md)
- [WebSocket API](../../api/websocket.md)

---

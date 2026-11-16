---
title: Process Management API
description: List DUMB services, control their lifecycle, inspect startup readiness, discover dependencies, and check backend capability flags.
icon: lucide/cpu
---

# Process Management API

Use these endpoints to list services, inspect startup state, and start, stop, or restart a managed process. Process names must match the names returned by `GET /process/processes`; do not infer them from configuration keys.

All paths are backend-native. When calling through port `3005`, prefix REST paths with `/api`. Authentication is enforced by the backend.

## Find the right workflow

| Task | Reference |
|---|---|
| Service lifecycle, status, discovery, and runtime log level | This page |
| Check or install updates; maintain the install cache | [Updates and install cache](updates.md) |
| Repair, back up, compare, or restore symlinks | [Symlink operations](symlinks.md) |
| Move a supported application from SQLite to PostgreSQL | [PostgreSQL migration](postgres-migration.md) |
| Benchmark an InfiniDysk-backed rclone mount | [Rclone optimizer](rclone-optimizer.md) |
| Rename a legacy NzbDAV installation to InfiniDysk | [Namespace migration](infinidysk-migration.md) |
<!-- dev:start -->
| Plan and complete a service arrangement | [Setup](setup.md) |
| Back up or restore a managed installation | [Installation backups](installation-backups.md) |
| Register an archive destination | [Backup storage](backup-storage.md) |
| Install or migrate to native InfiniDysk 2 | [InfiniDysk 2](infinidysk-v2.md) |
<!-- dev:end -->

## Service endpoints

### `GET /process/processes`

Returns all configured processes, including enabled status, version, repo URL,
sponsorship URL, manual-update support, and the last recorded update status. The
dashboard uses the latter two fields to build its update inventory without one
status request per service.

#### Example Response:

```json
{
  "processes": [
    {
      "name": "rclone w/ RealDebrid",
      "process_name": "rclone w/ RealDebrid",
      "enabled": true,
      "config": { "enabled": true, "...": "..." },
      "version": "1.65.1",
      "key": "rclone",
      "config_key": "rclone",
      "repo_url": "https://rclone.org",
      "sponsorship_url": "https://rclone.org/sponsor/",
      "supports_manual_update": true,
      "update_status": {
        "status": "update_available",
        "current_version": "1.65.1",
        "available_version": "1.66.0"
      }
    }
  ]
}
```

### `GET /process`

Fetch details about a specific process.

#### Required Query Parameter:

* `process_name` (string)

#### Example Response:

```json
{
  "process_name": "rclone w/ RealDebrid",
  "config": { "enabled": true, "...": "..." },
  "version": "1.65.1",
  "config_key": "rclone",
  "repo_url": "https://rclone.org",
  "sponsorship_url": "https://rclone.org/sponsor/"
}
```

### `POST /process/start-service`

Starts a specific process.

#### Request Body:

```json
{
  "process_name": "rclone w/ RealDebrid"
}
```

#### Example Response:

```json
{
  "status": "Service started successfully",
  "process_name": "rclone w/ RealDebrid"
}
```

### `POST /process/stop-service`

Stops a running process.

#### Request Body:

```json
{
  "process_name": "rclone w/ RealDebrid"
}
```

### `POST /process/restart-service`

Restarts a running process.

#### Request Body:

```json
{
  "process_name": "rclone w/ RealDebrid"
}
```

### `GET /process/service-reset/preview`

Returns the guarded reset/removal plan when capability `service_reset=true`.

Required query parameter: `process_name`. Optional `action` is `reset` (default) or `remove`. The response identifies whether DUMB will reset a required template or remove a custom instance, reports `default_instance_after_removal` when removing the final custom instance will restore the disabled default template, lists exact eligible file targets, and reports retained/shared paths and dependency-reference warnings. Preview is read-only.

### `POST /process/service-reset`

Stops one eligible service, cancels its DUMB schedules, writes a private full-config backup, then applies a freshly validated preview.

```json
{
  "process_name": "Sonarr Movies",
  "action": "remove",
  "confirmation": "Sonarr Movies"
}
```

`confirmation` must exactly match `process_name`. `reset` preserves application files. `remove` clears only the returned DUMB-owned paths. Neither action removes mounts, symlink libraries, shared caches, PostgreSQL databases, external data stores, or other service configuration. DUMB API and DUMB Frontend are excluded.

See [Service Reset and Removal](../features/service-reset.md) for template behavior, safety boundaries, and recovery.

### `GET /process/service-status`

Gets the current status of a process.

Pass `include_health=true` to include structured health and Auto-restart state.
The `health_status` value is `healthy`, `degraded`, `starting`, or `unhealthy`.
`healthy` remains for backward compatibility; use `health_status` when the
difference between an application starting, degraded, and restart-worthy
unhealthy state matters.

#### Example Response:

```json
{
  "process_name": "InfiniDysk",
  "status": "running",
  "healthy": true,
  "health_status": "starting",
  "health_reason": "InfiniDysk reports migrating",
  "health_details": {
    "probe": "InfiniDysk backend health",
    "endpoint": "/health",
    "supported": true,
    "http_status": 503,
    "reported_status": "migrating"
  },
  "restart": {}
}
```

Health details expose only bounded probe metadata and component names/statuses.
They do not include response bodies, credentials, or arbitrary remote URLs.

### `GET /process/startup-status`

Returns the readiness-aware container startup lifecycle when capability
`startup_lifecycle` is true. The response includes phase/timestamps, expected
service names, each service's `pending`, `starting`, or `ready` state, and
terminal failure summaries.

```json
{
  "phase": "stabilizing",
  "terminal": false,
  "expected_services": ["DUMB API", "DUMB Frontend", "InfiniDysk"],
  "services": {
    "DUMB API": {"state": "ready", "reason": null},
    "DUMB Frontend": {"state": "ready", "reason": null},
    "InfiniDysk": {
      "state": "starting",
      "reason": "InfiniDysk reports migrating",
      "health_status": "starting",
      "health_details": {
        "probe": "InfiniDysk backend health",
        "endpoint": "/health",
        "http_status": 503,
        "reported_status": "migrating"
      }
    }
  },
  "failures": {}
}
```

## Runtime API logging

These endpoints are available when `/process/capabilities` advertises
`runtime_api_log_level`.

### `GET /process/runtime-log-level`

Returns the configured and effective DUMB API logging levels and whether a
temporary DEBUG override is active.

```json
{
  "configured_level": "INFO",
  "configured_uvicorn_level": "INFO",
  "effective_level": "DEBUG",
  "debug_enabled": true,
  "override_active": true,
  "temporary": true,
  "resets_on_restart": true
}
```

### `POST /process/runtime-log-level`

Enables or disables a temporary DEBUG override without restarting the DUMB
container or API. Enabling changes the running shared DUMB logger and Uvicorn
loggers immediately. Disabling restores their configured levels.

```json
{
  "debug_enabled": true
}
```

The override is intentionally not written to `dumb_config.json` and is cleared
by a container restart. It does not modify managed-service logging settings.
DEBUG output can be substantially larger and may contain additional operational
details; DUMB's normal log redaction remains active.

### `POST /process/start-core-service`

Starts one or more core services and all required dependencies. This is used during onboarding.

The `core_services` field can be a single object or an array. The `name` can be the config key (e.g., `riven_backend`) or a display name (e.g., `Riven`).

#### Request Body Examples:

=== "Riven"

    ```json
    {
      "core_services": {
        "name": "riven_backend",
        "debrid_service": "RealDebrid",
        "debrid_key": "abc123",
        "service_options": {}
      },
      "optional_services": ["zilean", "pgadmin", "riven_frontend"]
    }
    ```

=== "Decypharr"

    ```json
    {
      "core_services": {
        "name": "decypharr",
        "debrid_service": "RealDebrid",
        "debrid_key": "abc123",
        "service_options": {
          "decypharr": {
            "mount_type": "dfs",
            "mount_path": "/mnt/debrid/decypharr"
          }
        }
      },
      "optional_services": []
    }
    ```

=== "CLI Debrid"

    ```json
    {
      "core_services": {
        "name": "cli_debrid",
        "debrid_service": "RealDebrid",
        "debrid_key": "abc123",
        "service_options": {
          "phalanx_db": { "enabled": true }
        }
      },
      "optional_services": ["zilean"]
    }
    ```

#### Example Response:

```json
{
  "results": [
    {"service": "riven_backend", "status": "started"},
    {"service": "decypharr", "status": "started"}
  ],
  "errors": []
}
```

!!! note "Notes"
    * Dependencies like Zurg or rclone are created using templates and attached to the calling core service.
    * Optional services such as `pgadmin`, `zilean`, `bazarr`, `pulsarr`, `maintainerr`, `mediastorm`, `traefik_proxy_admin`, or `cloudflared` are started only if included.
    * `debrid_key` is injected into Zurg or Decypharr as needed.
    * `service_options` can override config values such as `log_level`, `port`, or `enabled`.
    * Any startup errors appear in the `errors` list.

### `GET /process/core-services`

Returns the available core services, their dependencies, and default service options (used by onboarding).

### `GET /process/dependency-graph`

Returns backend-resolved dependency relationships for a specific process, including:

* static core dependencies (with instance-scoped matching for `rclone`/`zurg`)
* inferred links from `core_service`/`core_services`
* inferred links from `wait_for_url`/`wait_for_dir` entries (including localhost port matching)
* inferred links from `wait_for_mounts` by matching required mount paths to provider service mount points
* rclone provider links (`zurg_enabled`, `decypharr_enabled`, `key_type=infinidysk`) to reflect WebDAV provider dependencies directly
* non-core hard dependency map for service-specific startup requirements (for example `riven_frontend -> riven_backend`, `zilean -> postgres`, `pgadmin -> postgres`)
* conditional startup dependencies from the backend startup ordering logic -- config-aware dependencies like `tautulli -> plex` (when plex is enabled), `bazarr -> sonarr/radarr` (when those Arrs are enabled), `prowlarr -> sonarr/radarr` (when those Arrs are enabled), `neutarr -> sonarr` (when Sonarr has `use_neutarr` enabled), etc. For instance-scoped services (`rclone`, `zurg`), conditional deps are filtered per-instance so that only the specific associated instances are shown (for example, a rclone instance with `zurg_enabled` only shows its own zurg instance, not zurg instances belonging to other rclone configurations)
* documented integration links (soft linkage, `scope=all` only) -- for example `seerr -> sonarr/radarr` request routing
* per-process status state used by the frontend dependency graph panel
* `dependency_truth_table` describing the 12 dependency signal types and whether each is treated as hard dependency vs linkage
* `signals` array on each row/edge identifying which detection signals established the relationship (for example `["core_service_map"]`, `["rclone_provider_zurg", "conditional_startup_map"]`)

#### Required Query Parameter:

* `process_name` (string)

#### Optional Query Parameter:

* `scope` (string): `runtime` (default) or `all`
    * `runtime` returns runtime/configured hard dependencies
    * `all` additionally includes soft linkage edges (for example optional Zilean integrations)

The response includes `parallel_groups` metadata describing concurrent
prerequisite/dependent stages around the selected service.

#### Example Response (shape):

```json
{
  "process_name": "Seerr Main",
  "config_key": "seerr",
  "context": { "mode": "core", "key": "seerr", "core": { "key": "seerr", "name": "Seerr", "dependencies": [] } },
  "scope": "runtime",
  "startup_order": [{ "key": "seerr", "label": "Seerr", "state": "running" }],
  "dependency_rows": [],
  "dependent_rows": [],
  "linked_outgoing_rows": [{ "process_name": "Plex Media Server", "key": "plex", "label": "Plex Media Server", "state": "running" }],
  "linked_incoming_rows": [],
  "nodes": [{ "id": "Seerr Main", "process_name": "Seerr Main", "key": "seerr", "label": "Seerr Main", "state": "running" }],
  "edges": [{ "source": "Seerr Main", "target": "Plex Media Server", "signals": ["wait_for_url"], "strength": "hard_runtime" }],
  "parallel_groups": [{ "id": "pre_core", "label": "Parallel prerequisites", "type": "parallel", "members": ["PostgreSQL", "Rclone w/ Riven"] }],
  "updated_at": "2026-02-11T18:45:00Z"
}
```

### `GET /process/optional-services`

Returns optional services. You can pass `core_service` and `optional_services` query params to tailor the list.

### `GET /process/mediastorm-initial-admin-password`

Returns mediastorm's active bootstrap credential while its first-login password file exists:

```json
{
  "available": true,
  "username": "admin",
  "password": "admin",
  "credential_kind": "default"
}
```

After the administrator changes the password, mediastorm deletes the file and the endpoint returns:

```json
{
  "available": false,
  "username": "admin",
  "password": null,
  "credential_kind": null
}
```

`credential_kind` is `default` when the file contains mediastorm's current public `admin` password
and `installation_specific` for an older generated password or an explicit
`STRMR_INITIAL_ADMIN_PASSWORD` value.

On current mediastorm builds, clients using the public default must provide a replacement
`newPassword` in the same login request. A login containing only `admin` / `admin` returns HTTP
`428` with code `password_change_required`; the replacement is committed before the first session
is created.

The endpoint uses the existing DUMB authentication dependency, accepts no caller-supplied path, and
reads only the fixed mediastorm cache credential. It refuses symlinks, non-regular files, oversized
values, and multiline values. Responses include `Cache-Control: no-store, private` and
`Pragma: no-cache`; clients must not persist the password.

DUMB checks both `initial_admin_password` and `initial_admin_password.txt` through mediastorm's
configured persistent cache directory. Clients should gate this endpoint on the
`mediastorm_initial_admin_password` capability.

## Capabilities

### `GET /process/capabilities`

Read capabilities before offering an optional workflow. The response is the authority for that running backend; the docs channel or the dashboard version alone cannot establish support.

```bash
curl -H "Authorization: Bearer $DUMB_ACCESS_TOKEN" \
  http://localhost:3005/api/process/capabilities
```

Common capability groups:

| Fields | Controls |
|---|---|
| `manual_update_check`, `configured_source_install`, `commit_sha_pinning` | Manual update checks and saved source targets |
| `auto_update_start_time`, `auto_update_mode` | Schedule anchors and report-only schedules |
| `startup_lifecycle` | Readiness-aware `GET /process/startup-status` |
| `runtime_api_log_level` | Temporary DEBUG control for the running API |
| `symlink_*` | Individual repair, manifest, job, restore, and scheduling operations |
| `postgres_migration*`, `postgres_migration_service_keys` | Guarded database migration and the supported service list |
| `metrics_history_storage`, `metrics_history_hot_activation` | History providers and live PostgreSQL activation |
| `metrics_filesystem_selection`, `metrics_network_interface_selection` | Selected filesystem and interface metrics |
| `infinidysk_migration*` | Legacy identity and namespace migration |
| `rclone_optimizer_infinidysk` | InfiniDysk generation 1 rclone optimizer |
| `mediastorm_initial_admin_password` | No-store bootstrap credential readback |
<!-- dev:start -->
| `setup_arrangements` | Retained service setup plans and action runs |
| `setup_infinidysk_runtime_choices`, `setup_infinidysk_runtime_protocol` | Native runtime selection handoff; protocol `1` |
| `installation_backup`, `installation_backup_protocol` | Installation backup/restore; protocol `1` |
| `installation_backup_cancellation`, `installation_backup_phase_progress` | Job-specific cancellation and measured phase progress |
| `backup_storage_selection`, `backup_storage_protocol` | Registered archive destinations; protocol `1` |
| `backup_storage_shared_permissions` | Explicit shared-permissions consent per storage profile |
| `infinidysk_v2`, `infinidysk_v2_migration`, `infinidysk_v2_migration_protocol` | Native generation 2 workflow; protocol `1` |
| `infinidysk_v2_postgres` | Native generation 2 PostgreSQL conversion |
| `infinidysk_v2_async_preview` | Background migration preview with progress, cancellation and result retrieval |
| `infinidysk_v2_consumer_recovery`, `infinidysk_v2_consumer_recovery_protocol` | Retained target/consumer recovery; protocol `1` |
| `infinidysk_v2_cleanup`, `infinidysk_v2_cleanup_protocol` | Guarded v1 retirement; protocol `1` |
| `infinidysk_v2_low_space_migration`, `infinidysk_v2_external_blob_staging` | Explicit capacity-saving migration choices |
<!-- dev:end -->

Require the exact protocol advertised by the relevant workflow. Treat an absent flag as unsupported. Legacy `arr_postgres_migration*`, `nzbdav_install_info`, and `rclone_optimizer_nzbdav` aliases exist for older clients; new clients should use canonical names.

<!-- dev:start -->
Generation 2 also requires valid `api_version` SemVer at least `2.24.0`. Its runtime, mount backend, and database provider are separate choices. `infinidysk_v2_rclone_optimizer` is currently false, including when a generation 2 installation retains rclone.
<!-- dev:end -->

## Previously on this page

These section links remain available for existing bookmarks:

### Setup plans and retained runs
<!-- dev:start -->
See [Setup API](setup.md).
<!-- dev:end -->
<!-- release:start -->
The guided arrangement API is available in the development documentation.
<!-- release:end -->

### Install cache
See [install cache endpoints](updates.md#install-cache).

<span id="get-processupdate-status"></span>
<span id="get-processupdate-notices"></span>
<span id="post-processupdate-check"></span>
<span id="post-processupdate-install"></span>
<span id="post-processauto-updatereschedule"></span>

### Updates and scheduling
See [Updates and install cache API](updates.md).

### Installation backup and restore
<!-- dev:start -->
See [Installation backups API](installation-backups.md).
<!-- dev:end -->
<!-- release:start -->
Managed installation archives are available in the development documentation.
<!-- release:end -->

### Registered backup storage
<!-- dev:start -->
See [Backup storage API](backup-storage.md).
<!-- dev:end -->
<!-- release:start -->
Registered archive destinations are available in the development documentation.
<!-- release:end -->

<span id="post-processsymlink-repair"></span>
<span id="post-processsymlink-repair-async"></span>
<span id="post-processsymlink-manifestbackup"></span>
<span id="post-processsymlink-manifestbackup-async"></span>
<span id="get-processsymlink-job-status"></span>
<span id="get-processsymlink-job-latest"></span>
<span id="post-processsymlink-manifestrestore"></span>
<span id="get-processsymlink-manifestcompare"></span>
<span id="post-processsymlink-manifestrestore-async"></span>
<span id="get-processsymlink-backup-status"></span>
<span id="get-processsymlink-backup-manifests"></span>
<span id="get-processsymlink-manifest-files"></span>
<span id="post-processsymlink-backupreschedule"></span>

<span id="get-processpostgres-migrationpreflight"></span>
<span id="post-processpostgres-migrationstart"></span>
<span id="get-processpostgres-migrationstatus"></span>
<span id="get-processpostgres-migrationlatest"></span>
<span id="post-processpostgres-migrationrollback"></span>

### Symlink operations
See [Symlink operations API](symlinks.md).

### SQLite-to-PostgreSQL Migration
See [PostgreSQL migration API](postgres-migration.md).

### Rclone streaming optimizer
See [Rclone optimizer API](rclone-optimizer.md).

### InfiniDysk 2 workflows
<!-- dev:start -->
See [InfiniDysk 2 API](infinidysk-v2.md).
<!-- dev:end -->
<!-- release:start -->
Native InfiniDysk 2 support requires the development backend.
<!-- release:end -->

<span id="get-processinfinidysk-migrationstatus"></span>
<span id="post-processinfinidysk-migrationremind-later"></span>
<span id="post-processinfinidysk-migrationpreflight"></span>
<span id="get-processinfinidysk-migrationjob-status"></span>
<span id="get-processinfinidysk-migrationcleanup-preview"></span>
<span id="post-processinfinidysk-migrationcleanup"></span>
<span id="post-processinfinidysk-migrationstop-playback"></span>
<span id="post-processinfinidysk-migrationapply"></span>

### InfiniDysk migration
See [Namespace migration API](infinidysk-migration.md).

## Related pages

- [Configuration API](config.md)
- [Process router source](https://github.com/I-am-PUID-0/DUMB/blob/dev/api/routers/process.py)

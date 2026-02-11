---
title: Process Management API
icon: lucide/cpu
---

# Process Management API

The **Process Management** endpoints handle launching, stopping, restarting, and tracking subprocesses managed by DUMB.

---

## Lifecycle flow

```mermaid
%%{ init: { "flowchart": { "curve": "basis" } } }%%
flowchart TD
    A([Start or restart request])
    B{Endpoint}
    C[Start core service<br/>/process/start-core-service]
    D[Start or restart service<br/>/process/start-service or /process/restart-service]
    E[Validate + persist config]
    F[Run setup hooks]
    G{Port conflict?}
    H[Adjust ports + save]
    I[Launch process]
    J([Status + logs])

    A ==> B
    B -- Core service --> C
    B -- Single service --> D
    C ==> E
    E ==> F
    F ==> G
    G -- Yes --> H
    G -- No --> I
    H ==> I
    D ==> F
    I ==> J
```

---

## Endpoints

### `GET /process/processes`

Returns all configured processes, including enabled status, version, repo URL, and sponsorship URL.

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
      "sponsorship_url": "https://rclone.org/sponsor/"
    }
  ]
}
```

---

### `GET /process`

Fetch details about a specific process.

#### Required Query Parameter:

* `process_name` (string)

#### Optional Query Parameter:

* `scope` (string): `runtime` (default) or `all`
    * `runtime` returns runtime/configured hard dependencies
    * `all` additionally includes soft linkage edges (for example optional Zilean integrations)
* response includes `parallel_groups` metadata to describe concurrent prerequisite/dependent stages around the selected service

#### Example Response:

```json
{
  "process_name": "rclone w/ RealDebrid",
  "config": { "enabled": true, "...": "..." },
  "version": "1.65.1",
  "config_key": "rclone"
}
```

---

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

---

### `POST /process/stop-service`

Stops a running process.

#### Request Body:

```json
{
  "process_name": "rclone w/ RealDebrid"
}
```

---

### `POST /process/restart-service`

Restarts a running process.

#### Request Body:

```json
{
  "process_name": "rclone w/ RealDebrid"
}
```

---

### `GET /process/service-status`

Gets the current status of a process.

#### Example Response:

```json
{
  "process_name": "rclone w/ RealDebrid",
  "status": "running"
}
```

---

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
          "decypharr": { "use_embedded_rclone": true }
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

=== "Plex Debrid"

    ```json
    {
      "core_services": {
        "name": "plex_debrid",
        "debrid_service": "RealDebrid",
        "debrid_key": "abc123",
        "service_options": {
          "rclone": { "log_level": "DEBUG" },
          "zurg": { "port": 9194 }
        }
      },
      "optional_services": []
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
    * Optional services such as `pgadmin` or `zilean` are started only if included.
    * `debrid_key` is injected into Zurg or Decypharr as needed.
    * `service_options` can override config values such as `log_level`, `port`, or `enabled`.
    * Any startup errors appear in the `errors` list.

---

### `GET /process/core-services`

Returns the available core services, their dependencies, and default service options (used by onboarding).

---

### `GET /process/dependency-graph`

Returns backend-resolved dependency relationships for a specific process, including:

* static core dependencies (with instance-scoped matching for `rclone`/`zurg`)
* inferred links from `core_service`/`core_services`
* inferred links from `wait_for_url`/`wait_for_dir` entries (including localhost port matching)
* inferred links from `wait_for_mounts` by matching required mount paths to provider service mount points
* rclone provider links (`zurg_enabled`, `decypharr_enabled`, `key_type=nzbdav`) to reflect WebDAV provider dependencies directly
* non-core hard dependency map for service-specific startup requirements (for example `riven_frontend -> riven_backend`, `zilean -> postgres`)
* per-process status state used by the frontend dependency graph panel
* `dependency_truth_table` describing dependency signals and whether each is treated as hard dependency vs linkage

#### Required Query Parameter:

* `process_name` (string)

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

---

### `GET /process/optional-services`

Returns optional services. You can pass `core_service` and `optional_services` query params to tailor the list.

---

### `POST /process/symlink-repair`

Runs symlink target rewrites for service symlink trees (Decypharr, NzbDAV, CLI Debrid, Riven).

Use this endpoint when mount paths change and existing symlink targets need to be rewritten.

#### Request Body:

```json
{
  "dry_run": true,
  "include_broken": true,
  "presets": ["decypharr_beta_consolidated"],
  "roots": ["/mnt/debrid/decypharr_symlinks", "/mnt/debrid/clid_symlinks"],
  "root_migrations": [
    {
      "from_root": "/mnt/debrid/decypharr_symlinks",
      "to_root": "/mnt/debrid/combined_symlinks"
    }
  ],
  "overwrite_existing": false,
  "copy_instead_of_move": false,
  "rewrite_rules": [
    {
      "from_prefix": "/mnt/debrid/old",
      "to_prefix": "/mnt/debrid/new"
    }
  ],
  "backup_path": "/config/symlink-repair/manifest.json"
}
```

#### Behavior

* `dry_run: true` scans and reports without changing symlinks.
* `dry_run: false` rewrites matching symlinks in place.
* `process_name` is optional but recommended for async runs/job lookup.
* Provide at least one of: `presets`, `rewrite_rules`, `root_migrations`.
* `root_migrations` moves symlink entries from one symlink tree to another while
  preserving relative paths. This is intended for individual-root to combined-root migrations.
* `overwrite_existing` controls behavior when a destination symlink already exists during root migration.
* `copy_instead_of_move` (root migration mode) creates destination symlinks and keeps source symlinks in place.
* If `roots` is omitted, backend defaults are used:
  `/mnt/debrid/decypharr_symlinks`, `/mnt/debrid/nzbdav-symlinks`,
  `/mnt/debrid/combined_symlinks`, `/mnt/debrid/clid_symlinks`, and
  `riven_backend.symlink_library_path` when configured.
* `backup_path` is written only for non-dry-run operations with changes.

#### Example Response:

```json
{
  "dry_run": true,
  "scanned_symlinks": 2451,
  "changed": 312,
  "moved": 120,
  "copied": 0,
  "skipped_unchanged": 2139,
  "errors": [],
  "changes": []
}
```

### `POST /process/symlink-repair-async`

Queues symlink repair as a background job and returns immediately.

Use `GET /process/symlink-job-status` (or `/process/symlink-job-latest`) to track completion.

#### Response (example)

```json
{
  "status": "queued",
  "job_id": "76d1a3bd35f84e3fab0cc39f81246849",
  "operation": "symlink_repair"
}
```

### `POST /process/symlink-manifest/backup`

Creates a standalone snapshot manifest of symlink entries for later restore.

#### Request Body:

```json
{
  "backup_path": "/config/symlink-repair/snapshots/latest.json",
  "roots": ["/mnt/debrid/decypharr_symlinks", "/mnt/debrid/clid_symlinks"],
  "include_broken": true
}
```

#### Behavior

* Writes a manifest containing `link_path` + `target` entries.
* If `roots` is omitted, backend default symlink roots are used.
* Used by the internal DUMB scheduler when `symlink_backup_enabled` is set on supported services.
* Scheduled runs can prune older manifests when `symlink_backup_retention_count` is greater than `0`.

### `POST /process/symlink-manifest/backup-async`

Queues a standalone snapshot backup as a background job and returns immediately.

#### Response (example)

```json
{
  "status": "queued",
  "job_id": "8e9fd0fbe88d4a6fbb2f3f77b2a3f8c1",
  "operation": "symlink_manifest_backup"
}
```

### `GET /process/symlink-job-status`

Returns status/result for background symlink jobs.

#### Query Params

- `job_id` (required)

#### Response fields

- `status`: `queued`, `running`, `completed`, or `error`
- `result`: operation payload when completed
- `error`: error payload when failed
- `created_at`, `updated_at`, `started_at`, `finished_at` timestamps (when available)

### `GET /process/symlink-job-latest`

Returns the latest symlink job for a process/operation (optionally only active jobs).

#### Query Params

- `process_name` (required)
- `operation` (optional, default `symlink_manifest_backup`)
- `active_only` (optional, default `true`)

### `POST /process/symlink-manifest/restore`

Restores symlinks from a previously generated snapshot manifest.

#### Request Body:

```json
{
  "manifest_path": "/config/symlink-repair/snapshots/latest.json",
  "dry_run": true,
  "overwrite_existing": false,
  "restore_broken": true
}
```

#### Behavior

* `dry_run: true` previews restore actions without writing.
* `overwrite_existing` controls whether existing paths are replaced.
* `restore_broken` controls whether entries with currently missing targets are restored.

### `GET /process/symlink-manifest/compare`

Compares a snapshot manifest against current filesystem state and returns projected restore outcomes.

#### Query Params

- `manifest_path` (required)
- `overwrite_existing` (optional, default `false`)
- `restore_broken` (optional, default `true`)
- `sample_limit` (optional, default `50`, max `200`)

#### Behavior

* Uses the same overwrite/missing-target rules as restore.
* Returns projected counts (`projected_restored`, skipped categories, errors).
* Returns `sample_changes` with representative actions (`create`, `overwrite`, `skip_*`) for quick review before apply.

### `POST /process/symlink-manifest/restore-async`

Queues restore as a background job and returns immediately.

Use `GET /process/symlink-job-status` (or `/process/symlink-job-latest`) to track completion.

### `GET /process/symlink-backup-status`

Returns current symlink-backup scheduler state for a service.

### `GET /process/symlink-backup-manifests`

Lists backup manifests that match the current service `symlink_backup_path` template.

### `GET /process/symlink-manifest-files`

Lists files from the directory of a provided `manifest_path` (defaults to `/config/symlink-repair/snapshots/latest.json` directory).

Use this to populate manifest pickers in the Snapshot tab for quick restore/overwrite selection.

### `POST /process/symlink-backup/reschedule`

Rebuilds symlink-backup schedule state from current service config.

#### Request Body:

```json
{
  "process_name": "Decypharr"
}
```

---

### `GET /process/capabilities`

Returns backend capabilities and feature flags. Used by the frontend to determine available features.

#### Example Response:

```json
{
  "optional_only_onboarding": true,
  "optional_service_options": true,
  "manual_update_check": true,
  "seerr_sync": true,
  "auto_update_start_time": true,
  "symlink_repair": true,
  "symlink_repair_async": true,
  "symlink_manifest_backup": true,
  "symlink_manifest_backup_async": true,
  "symlink_job_status": true,
  "symlink_job_latest": true,
  "symlink_manifest_restore": true,
  "symlink_manifest_restore_async": true,
  "symlink_manifest_compare": true,
  "symlink_backup_schedule": true,
  "symlink_backup_manifest_list": true,
  "symlink_manifest_file_list": true
}
```

| Field | Description |
|-------|-------------|
| `optional_only_onboarding` | Whether onboarding can skip core service selection |
| `optional_service_options` | Whether optional service options are exposed for onboarding |
| `manual_update_check` | Whether manual update check/install routes are available |
| `seerr_sync` | Whether Seerr sync feature routes are available |
| `auto_update_start_time` | Whether anchored auto-update start time is supported |
| `symlink_repair` | Whether `/process/symlink-repair` is available |
| `symlink_repair_async` | Whether `/process/symlink-repair-async` is available |
| `symlink_manifest_backup` | Whether `/process/symlink-manifest/backup` is available |
| `symlink_manifest_backup_async` | Whether `/process/symlink-manifest/backup-async` is available |
| `symlink_job_status` | Whether `/process/symlink-job-status` is available |
| `symlink_job_latest` | Whether `/process/symlink-job-latest` is available |
| `symlink_manifest_restore` | Whether `/process/symlink-manifest/restore` is available |
| `symlink_manifest_restore_async` | Whether `/process/symlink-manifest/restore-async` is available |
| `symlink_manifest_compare` | Whether `/process/symlink-manifest/compare` is available |
| `symlink_backup_schedule` | Whether scheduled symlink backup status/reschedule routes are available |
| `symlink_backup_manifest_list` | Whether `/process/symlink-backup-manifests` is available |
| `symlink_manifest_file_list` | Whether `/process/symlink-manifest-files` is available |

---

!!! tip "Important Notes"
    * All process names are matched against the entries defined in `dumb_config.json`.
    * Most process commands are defined as arrays and are managed with subprocess handling inside Python.

---

## Related Files

* [`process.py`](https://github.com/I-am-PUID-0/DUMB/blob/master/api/routers/process.py)
* [Configuration](config.md)

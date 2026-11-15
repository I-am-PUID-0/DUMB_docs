---
title: Symlink operations API
description: Repair symlinks, capture and compare manifests, restore saved links, and poll asynchronous DUMB symlink jobs and schedules.
icon: lucide/code
---

# Symlink operations API

Endpoint paths below are backend-native. Add `/api` when using the dashboard gateway, for example `http://localhost:3005/api/process/capabilities`.

### `POST /process/symlink-repair`

Runs symlink target rewrites for service symlink trees (Decypharr, InfiniDysk, CLI Debrid, Riven).

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
  `/mnt/debrid/decypharr_symlinks`, `/mnt/debrid/infinidysk-symlinks`,
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

Lists files under `/config/symlink-repair/snapshots` by default.

<!-- dev:start -->
With an explicit registered backup destination, lists only owned symlink catalog artifacts for the selected process; a managed `manifest_path` must verify before its namespace is listed. See [Backup storage API](backup-storage.md).
<!-- dev:end -->

Use this to populate manifest pickers in the Snapshot tab for quick restore/overwrite selection.

### `POST /process/symlink-backup/reschedule`

Rebuilds symlink-backup schedule state from current service config.

#### Request Body:

```json
{
  "process_name": "Decypharr"
}
```

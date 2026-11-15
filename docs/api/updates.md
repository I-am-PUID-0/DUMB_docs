---
title: Updates and install cache API
description: Inspect DUMB service update status, install selected versions, manage update schedules, and maintain the verified installation cache.
icon: lucide/code
---

# Updates and install cache API

Endpoint paths below are backend-native. Add `/api` when using the dashboard gateway, for example `http://localhost:3005/api/process/capabilities`.

## Updates and scheduling

### `GET /process/update-status`

Returns the last recorded update state for the required `process_name` query parameter.

<!-- dev:start -->
Scheduled work can add the following fields to `update_status`:

| Field | Meaning |
| --- | --- |
| `scheduler_state` | `running`, `deferred`, `error`, `blocked`, `disabled`, or `completed` for the scheduled callback |
| `scheduler_job` | `update` or `api` |
| `scheduler_message` | Progress or outcome message for the scheduled callback |
| `scheduler_started_at` | Callback start time as Unix seconds |
| `scheduler_elapsed_seconds` | Observed running duration |
| `scheduler_long_running` | Whether the callback has been running for at least five minutes |
| `retry_after_seconds`, `next_retry_at` | Retry delay and Unix retry time when admission is deferred |
| `last_run_status` | Completed callback outcome, including `rescheduled` when its due time moved before execution |

These fields supplement the existing `status`, `message`, schedule, and install
timing fields. Polling clients should display the message and tolerate absent
fields on older backends. A long-running flag does not mean the callback has
been stopped or its locks released. Scheduled service updates remain serial;
other due services can report `deferred` while the active callback finishes.
For DUMB API and DUMB Frontend, a known available update remains in `status`
and `message` during a recheck or deferral. Read `scheduler_state` and
`scheduler_message` for live progress; a failed recheck also records
`last_check_error` without discarding that known result.
Scheduled backups publish corresponding worker fields through
[`GET /process/symlink-backup-status`](symlinks.md#get-processsymlink-backup-status),
with `scheduler_job: "symlink_backup"` and `next_backup_at`.
<!-- dev:end -->

### `GET /process/update-notices`

Returns available, informational, and recently applied update notices. `scope=project` (default) limits notices to DUMB/dmbdb; `scope=all` includes managed services.

Project terminal statuses are retained by the backend in `/config/update_notices.json`. Available DUMB API/frontend entries can include `releases_behind` when the installed release is present in the bounded GitHub release history, plus `last_check_error`/`last_check_failed_at` when a transient recheck failure leaves a known available result in place. Browser dismissals are presentation-only and do not mutate this endpoint's retained state.

The DUMB API is checked at startup and daily regardless of service auto-update opt-in. Its check is always report-only; applying a new API image remains external to this endpoint.

### `POST /process/update-check`

Runs a manual update check without installing it.

```json
{
  "process_name": "AltMount",
  "force": true
}
```

### `POST /process/update-install`

Installs an available update. `allow_override: true` temporarily ignores the
saved release, branch, commit, or pinned-version selection and installs the
latest stable release; DUMB restores the saved configuration afterward.
`target` optionally supplies a supported release selector; `target:
"configured"` applies the currently configured pinned commit/release/branch
without clearing or bypassing it.

Configured-target update-check responses include
`configured_target_kind` (`release`, `branch`, or `commit`) and
`configured_target_installed`. Clients can use these fields to offer the
matching configured-target installation action only when it is needed.

```json
{
  "process_name": "InfiniDysk",
  "allow_override": false,
  "target": "configured"
}
```

A completed install response can include backend-measured timing fields when
`update_timing_metrics` is advertised:

```json
{
  "status": "updated",
  "message": "Updated InfiniDysk to v0.10.0-rc.2.",
  "install_duration_seconds": 97.4,
  "downtime_seconds": 21.8,
  "downtime_status": "completed",
  "timing_completed_at": "2026-08-05T12:34:56+00:00"
}
```

`install_duration_seconds` covers the complete backend update operation.
`downtime_seconds` is the sum of observed intervals from stopping the managed
process until an application readiness probe succeeds. `downtime_status` is
`completed`, `ongoing`, or `not_observed`. An `ongoing` value is a lower bound
captured when the operation ended without verified readiness; `not_observed`
means no running managed process was stopped. Scheduled installs publish the
same fields through cached `update_status` data.

### `POST /process/auto-update/reschedule`

Recomputes the next automatic-update run after changing a service's enabled
state, interval, start time, or `auto_update_mode`. The supported modes are
`install` (the backward-compatible default) and `check_only` (record the result
without installing or restarting the service).

```json
{
  "process_name": "AltMount"
}
```

Clients should gate manual update actions on the `manual_update_check`
capability, configured-target installation on `configured_source_install`, and
the start-time control on `auto_update_start_time`, and the scheduled-action
selector on `auto_update_mode`. The dashboard multi-service
workflow is gated on `dashboard_bulk_updates`; it orchestrates the existing
per-service check/install endpoints sequentially and never sends bulk source
overrides. Clients should show update timing only when
`update_timing_metrics=true`.

### Install cache

These endpoints are available when `/process/capabilities` advertises
`install_cache_management=true`:

- `GET /process/install-cache/status` returns the full managed, legacy, and
  combined totals; namespace sizes; exact discovered legacy entries; configured
  limits; file counts; recent install-operation stages; and cache-root recovery
  fields (`configured_path`, active `path`, `using_fallback`, and
  `fallback_reason`).
- `POST /process/install-cache/verify` hashes cached download objects and
  quarantines invalid entries.
- `POST /process/install-cache/prune` accepts optional
  `{"max_size_gib": 25}` and removes least-recently-used cache entries until
  the limit is met.
- `POST /process/install-cache/artifacts/clear` accepts an optional
  `service_key`; omitting it clears all compiled build artifacts.

When `install_cache_limit_settings=true`, the dashboard persists a changed
limit through the normal global config update endpoint using
`{"dumb":{"install_cache":{"max_size_gib":25}}}`. The global schema accepts
1 through 1024 GiB. Pruning remains an explicit maintenance action.

When `install_cache_cleanup=true`,
`POST /process/install-cache/cleanup` accepts a non-empty `scopes` array. Valid
values are `downloads`, `dependencies`, `artifacts`, `quarantine`, and
`legacy`. Paths are not accepted. For example:

```json
{
  "scopes": ["legacy", "quarantine"]
}
```

Maintenance endpoints return HTTP 409 during nonterminal startup phases or
while DUMB's service-update lock is active.

Cache maintenance never deletes service configuration, databases, media, or
the currently active runtime. See [Install cache and safe
updates](../features/install-cache.md).

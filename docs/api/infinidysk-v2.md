---
title: InfiniDysk 2 API
description: Use guarded native InfiniDysk 2 installation, major upgrade, consumer recovery, PostgreSQL conversion, and v1 retirement workflows.
icon: lucide/code
development_only: true
---

# InfiniDysk 2 API

Endpoint paths below are backend-native. Add `/api` when using the dashboard gateway, for example `http://localhost:3005/api/process/capabilities`.

## InfiniDysk 2 workflows

These routes are independent of the existing NzbDAV namespace migration and
generation 1 PostgreSQL adapter. See the
[InfiniDysk 2 upgrade guide](../features/infinidysk-v2-migration.md) for downtime,
containment, mount/library checks and recovery limits. Paths below are relative
to the DUMB API; the dashboard accesses them through its `/api` proxy prefix.

Clients require a valid `api_version >= 2.24.0`, explicit boolean
`infinidysk_v2=true`, `infinidysk_v2_migration=true` and numeric
`infinidysk_v2_migration_protocol=1`. Native PostgreSQL conversion also requires
`infinidysk_v2_postgres=true`. Missing, malformed, older or unknown versions and
protocols disable mutations. Retained job/recovery displays remain independent
of those new-operation controls.

### Major installation and upgrade

| Method | Route | Purpose |
|--------|-------|---------|
| `GET` | `/process/infinidysk-v2/status` | Current generation, fresh/migration mode, mount choices, eligibility and latest retained job |
| `POST` | `/process/infinidysk-v2/preview` | Review a source-bound plan and receive a short-lived authorization |
| `POST` | `/process/infinidysk-v2/preview/start` | Start a background preview using the same options as `/preview` |
| `GET` | `/process/infinidysk-v2/preview/task` | Retrieve the latest preview task |
| `GET` | `/process/infinidysk-v2/preview/task/{task_id}` | Poll one preview task and retrieve its completed result |
| `POST` | `/process/infinidysk-v2/preview/task/{task_id}/cancel` | Request cancellation of that preview without stopping services |
| `POST` | `/process/infinidysk-v2/rehearse` | Run the actual contained native importer against retained source snapshots |
| `POST` | `/process/infinidysk-v2/start` | Start an eligible fresh install or guarded major cutover |
| `GET` | `/process/infinidysk-v2/jobs/{job_id}` | Retrieve one persisted job as `{"job": {...}}` |
| `GET` | `/process/infinidysk-v2/jobs/{job_id}/report` | Read the retained native import report as plain text with `Cache-Control: no-store` |
| `POST` | `/process/infinidysk-v2/cancel` | Request cooperative cancellation of the exact active major job and protected source recovery |
| `POST` | `/process/infinidysk-v2/rollback` | Restore the exact retained major-migration source when authorized |
| `POST` | `/process/infinidysk-v2/retry-consumers` | Verify/restart the owned exposed v2 target and retry only retained pending consumers |
| `POST` | `/process/infinidysk-v2/finish-consumer-recovery` | Acknowledge leaving pending consumers stopped after verified v2 delivery |
| `POST` | `/process/infinidysk-v2/cleanup/preview` | Review owned v1 removal paths and retained backups after a validated cutover |
| `POST` | `/process/infinidysk-v2/cleanup` | Retire automated rollback and remove only the approved unchanged v1 entries |

Preview body:

```json
{
  "mode": "migrate",
  "mount_backend": "rclone",
  "import_strategy": "preserve"
}
```

`mode` is `migrate` or `fresh`; fresh mode cannot overwrite an existing source.
`mount_backend` is `rclone` or explicit `fuse`. The initial major workflow accepts
only `import_strategy: "preserve"`; it does not regenerate existing outputs.
The exact consumer-visible mount path is retained. Generation 2 uses separate
runtime/data directories and the verified beta artifact.

#### Low-space migration

A supporting backend advertises
`infinidysk_v2_low_space_migration: true`. For an existing-data migration only,
the optional boolean `reclaim_source_space: true` selects guarded reuse of the
local v1 data tree after full archive verification. It requires an explicit
registered `backup_destination_id` on a different filesystem and a supported
local source/candidate layout. Omit the field or use `false` to retain the
default local-source recovery. Clients must not send this option to older
backends or treat archive selection alone as permission to reuse source data.

A low-space preview includes `source_storage` with
`mode: "archive_recovery"`, `reclaim_source_space: true` and
`rollback_requires_archive: true`. Its `required_acknowledgements` additionally
requires `archive_recovery`. Both rehearsal and rollback can release the exact
owned candidate before restoring original v1 files from the retained archive.
Recovery refuses an unavailable/replaced archive or changed owned path.
The capacity review retains actual free-space readings and includes remaining
local database, verification and safety requirements. Reuse removes a complete
candidate-copy allocation; it does not remove native output growth. New v2
metadata and retained v1 blobs can coexist, so native headroom also includes at
least a comparable full source-tree logical allocation. This remains an estimate
because the native metadata/compression formats differ. Recovery checks local
restore capacity before releasing the owned candidate and again after removal.

#### External legacy blob staging

For a backend advertising the strict boolean
`infinidysk_v2_external_blob_staging: true`, an existing-data preview can also
request `offload_legacy_blobs: true`:

```json
{
  "mode": "migrate",
  "mount_backend": "rclone",
  "import_strategy": "preserve",
  "backup_destination_id": "migration_archive",
  "reclaim_source_space": true,
  "offload_legacy_blobs": true
}
```

This option requires `mode: "migrate"`, `reclaim_source_space: true` and the
registered recovery archive on a different filesystem. Omit it for ordinary
reuse. Archive selection or the older low-space capability alone does not
authorize offload. The major status response can additionally advertise
`capabilities.external_blob_staging: true`; clients must gate the new option
using its explicit capability rather than the backend version alone.

The preview retains `source_storage.mode: "archive_recovery"` and adds
`source_storage.offload_legacy_blobs: true` for the chosen mode.
`required_acknowledgements` additionally requires `external_blob_staging`.
Use the acknowledgements returned by that preview for rehearsal and start.

DUMB verifies the cold recovery archive, copies and verifies a separate expanded
legacy blob input at the destination, then releases only the corresponding owned
local blob files. Public job stages distinguish `staging_blobs`,
`verifying_blob_staging` and `releasing_local_blobs`. The importer reads the
staged input while active SQLite, control state and PostgreSQL verification
scratch remain local. The archive remains the authoritative v1 rollback source;
a missing or damaged expanded copy does not substitute for that archive.

Capacity reporting includes `external_blob_staging` for the expanded input
on the destination and `native_import_growth` for local v2 output, in addition
to the recovery archive and other working requirements. The same destination
therefore needs room for both the archive and expanded input.

`capacity.phases` contains objects with `phase`, `status` and `filesystems`.
The phases are `before_blob_release` and `after_blob_release`; the flattened
`capacity.filesystems` rows also identify their `phase`. Each row's
`free_bytes` remains the measured filesystem value. Preview can separately
report `projected_released_bytes` and `projected_available_bytes`, with
`release_is_projected: true`; these are estimates, not increased observed free
space or a reservation. The worker checks fresh actual capacity after unlinking
the verified owned local files, without projected release credit, before import.
Source moves or symlinks created outside this workflow are not an offload
request.

After accepted import or completed v1 restoration, DUMB attempts cleanup of
only the recorded, unchanged expanded input. The verified recovery archive
remains retained. A missing, changed or otherwise unremovable staging copy can
leave `job.staging_cleanup_required: true` without invalidating an accepted
import or blocking restoration from the valid archive. Preserve the warning
and retained evidence; it does not authorize deleting a replacement directory.

#### Background preview

Use the background routes only when the strict boolean
`infinidysk_v2_async_preview: true` is advertised. The existing synchronous
`POST /preview` remains available for older clients.

Starting and polling return `{"protocol": 1, "task": {...}}`. Each task includes
`task_id`, `status`, `stage`, `message`, `created_at`, `updated_at`, the selected
`options`, `options_fingerprint`, `can_cancel` and `cancel_requested`. Major
workflow status also includes `preview_task`, so reopening the panel can reconnect
without submitting another scan. Only the latest task is retained; requesting a
different or no-longer-retained identity returns HTTP 409.

An identical request reuses the active task; changing options while it is running
is refused. An optional `request_id` (16–128 letters, digits, underscores or
hyphens) also deduplicates a retry of the latest request after a lost response.
Reusing that identity with different options is refused. Wait for the active task
to finish or cancel it before requesting a different preview.

Preview performs metadata and prerequisite checks while services remain running.
It does not stop services, copy source data or start the native importer. There is
no overall preview time limit. Cancellation is cooperative: follow the task until
it stops. A controller restart marks an unfinished preview as interrupted; it
does not automatically rerun it or enter migration recovery.

Task states are `queued`, `running`, `completed`, `cancelled`, `failed` and
`interrupted`. Only a completed task returns the normal result in `task.preview`,
with `preview_available: true`. An expired or consumed authorization returns
`preview: null`, `preview_available: false` and `preview_unavailable_reason` of
`expired` or `consumed`; generate a fresh preview before continuing. Status and
result responses use `Cache-Control: no-store, private` because a completed
preview contains its short-lived authorization token.

The authorization period starts at completion, not when scanning begins. Task
identity and progress alone never authorize rehearsal or cutover; review that
completed result and its required acknowledgements first.

#### Preview contract

The preview returns `protocol`, `ready`, `preview_token`, `expires_at`,
`plan_fingerprint`, `confirmation_text`, `current`, `target`, `checks`,
`blockers`, `warnings`, `inventory`, `required_acknowledgements` and
`rehearsal_required`. The public fingerprint binds a rehearsal to its plan;
it is not an authorization token. Recorded inventory is not proof that
unmanaged consumers or STRM URLs are absent.

#### Compatibility authentication policy

Updated status responses include `current.compatibility_auth_policy`; previews
include `target.compatibility_auth_policy`. When the legacy compatibility relay
is enabled, it reports
`{"enforced": true, "mode": "required", "reason": "legacy_compatibility_listener"}`.
This is a read-only explanation of the authentication policy DUMB enforces at
native launch, not a runtime settings probe or a mutation option. With no relay the values are `false`, `null` and `null`.
The backend rejects conflicting explicit authentication overrides before native
setup or migration. Older backends may omit the object.

#### Rehearse and start

Rehearse and start body, using values from the current preview:

```json
{
  "preview_token": "<current-preview-token>",
  "confirmation": "MIGRATE INFINIDYSK TO V2",
  "acknowledgements": {
    "backup": true,
    "downtime": true,
    "beta": true,
    "oidc_policy": true,
    "downstream": true
  },
  "rehearsal_job_id": "<validated-rehearsal-job-id>"
}
```

Omit `rehearsal_job_id` for the rehearsal request and for a fresh installation
that does not require one. Always use the backend's exact confirmation text;
fresh mode has a different phrase. A major cutover requires a successful
rehearsal with `status: "rehearsed"`, `mode: "rehearsal"`,
`result.validated: true` and the matching
`plan_fingerprint`. A successful rehearsal refreshes its reviewed preview's
expiry for 30 minutes and exposes `preview_expires_at` as Unix seconds; clients
can update that preview's countdown without treating a changed plan as approved.
Changed source facts, failed containment, unexplained native omissions, an
unsupported source adapter or failed identity/policy proof block
activation. General external networking remains denied during the contained
import. Supporting builds permit read-only NNTP article reads only through a
relay bound to the configured source providers, capped at two connections per
provider or its lower configured limit, and four overall with one request in
flight per connection. Active TLS-enabled upstream connections retain certificate and
hostname verification; insecure legacy TLS overrides are refused. Source and
affected managed consumers remain quiesced. Temporary relay configuration must
not replace the normal provider settings used after import; there is no
unrestricted network fallback.
The required `downstream` review covers current Arr/media mount paths, remote
path mappings, symlinks/STRM origins and stopped external writers/scanners.
OIDC-configured sources remain blocked until their target policy is verified;
the acknowledgement is not an authorization to bypass a blocker.

Start/rehearse responses and `status.job` expose a public job, including its
identity, mode, status, stage, message, fingerprint and result. A successful
cutover uses `status: "completed"`. The terminal `status: "failed_restored"`
confirms the source was restored and permits a fresh preview; recovery flags
remain authoritative for available actions. Rollback is available only when
`can_rollback` or `actions.rollback` is explicitly true.
Send `job_id` and the exact `rollback_confirmation_text` as `confirmation` to
the rollback route. When `rollback_requires_discard_ack: true`, also send
`acknowledge_discard_v2_writes: true` after explicitly reviewing that v2 writes
will be discarded. A held exposed target does not offer ordinary v1 rollback.
The default mode retains the original local source;
low-space recovery restores it from the retained archive. Later 2.x writes are
not merged back into v1.

For an offload-enabled job, accepted rollback promptly returns its persisted
`rolling_back` job while archive restoration continues in the worker. Poll the
job route until restoration and service recovery finish; the response does not
mean v1 is already running. Other existing migration modes retain their
synchronous rollback behavior. The exact confirmation and any required
`acknowledge_discard_v2_writes` consent are checked before either path starts.

#### Cancellation

The `infinidysk_v2_cancel: true` capability gates new cancellation requests.
For a job advertising `can_cancel: true` or `actions.cancel: true`, send
`{"job_id": "SERVER_JOB_ID", "confirmation": "SERVER_CANCEL_CONFIRMATION"}` to
`/process/infinidysk-v2/cancel`, using its exact `cancel_confirmation_text`.
The response can set `cancel_requested: true` while the owned worker reaches a
checkpoint and restores the source. Repeating that same accepted cancellation
is idempotent. Do not treat the acknowledgement as completed recovery: poll the
job until its terminal state and recovery flags confirm the outcome. If source
recovery fails, retain the evidence and use the offered rollback action.
Once `activation_exposed: true`, cancellation cannot implicitly restore v1;
follow the current exposed-target recovery actions instead.

`status.job` prioritizes a retained blocking job over newer completed attempts;
`blocking_job_count` explains when other blocked jobs also remain. Updated jobs
can expose `import_progress` with a native `stage`, `elapsed_seconds`, and
`processed`/`total` counts when the native API provides them. These describe
native conversion rather than the entire validation/cutover/recovery pipeline.
#### Job progress and evidence

The outer `stage` and `message` describe the current DUMB phase.

Bulk native import, file copy and database snapshot/restore have no fixed
overall deadline. Thirty minutes without observable native progress or provider
reads produces a warning while the worker continues; polling heartbeats alone
do not establish progress. Actual process or verification failures still block
acceptance. Startup dependency/readiness checks remain separate from bulk work;
neither a warning nor a transport timeout authorizes repeating a mutation or
bypassing retained recovery checks.

Updated jobs can expose `import_report` with `status` equal to `accepted`,
`review_required` or `blocked`, `imported_files`, `skipped_files`,
`reasons` entries `{reason, count}`, `skipped` entries `{path, reason}`,
`review_required`, `review_digest` and `blocking_reasons`.
The optional sample counts and truncation flags explain bounded public details;
the complete native report remains in private job storage.

Supporting reports also expose a bounded `import_report.history` summary with
`source_rows`, `completed`, `failed`, `unsupported_status`, `invalid_identity`
and `imported_this_attempt`. Verified history adds `verified_present` and
`attempt_count_differs`; missing required identities can add `missing_completed`
and `missing_failed` counts. These diagnostics distinguish a per-attempt report
count from actual preserved history; they do not relax identity checks.

Known source incompatibilities may complete a validated rehearsal with
`import_report.status: "review_required"`. Starting its cutover also requires
`acknowledgements.skipped_media: true` and `skip_review_digest` matching that
rehearsal's server-issued `review_digest`. The digest covers every omitted
identity, path and reason, including entries beyond a public sample. Actual
cutover omissions may be the same set or a strict subset, including none, only
with unchanged complete canonical source media/history census and identical
remaining identities, names, paths and exact reasons. Every required completed
and failed history identity must still exist in the actual native database;
a lower per-attempt report count alone is not a history-loss allowance.
The private complete census also binds referenced metadata/NZB blob contents
while excluding volatile health scheduling. Changed source facts or stale proof
require a fresh isolated rehearsal; public samples cannot reauthorize it.
Unknown/provider failures, ambiguous identities and unrecognized reports remain blockers; the
acknowledgement is not a general skip override.

A successful rehearsal can record `candidate_discarded=true` after the native
candidate/group is proven stopped and v1 plus managed consumers are restored.
Only its full job-owned candidate is removed; receipts, the source archive or
backup and minimal database proof remain. Default-mode failed rehearsal
candidates are kept. Low-space recovery can remove its candidate before archive
restoration. The later cutover still needs its mode's local capacity and fresh
source checks.

### Recover an exposed v2 target or pending consumers

These additive protocol 1 controls require
`infinidysk_v2_consumer_recovery: true` and numeric
`infinidysk_v2_consumer_recovery_protocol: 1`. Keep `status: "recovery_required"`
or an interrupted controller's retained state distinct from a request to restore v1:

- `recovery_kind: "v2_activation"` means the v2 target was exposed and may contain
  new writes, but accepted runtime/mount activation still needs verification.
- `recovery_kind: "v2_consumers"` with `activation_committed: true` means the
  healthy native target and delivery mount passed cutover acceptance before
  downstream service resumption. A later consumer failure retains that cutover.
- `consumer_recovery` contains `failed` records with `process_name`, `reason_code`
  and a sanitized `message`, plus `pending` and `resumed` process-name arrays.
  Its boolean `ready` combines the last verified native health with current
  registered-process and delivery-mount checks. Status reads do not perform a
  new native health probe; each recovery action rechecks health before changing
  state. It does not mean every consumer resumed.

For an explicitly advertised `can_retry_consumers: true`, post `job_id` and the
exact `confirmation_texts.retry_consumers` as `confirmation` to
`/process/infinidysk-v2/retry-consumers`. This action can be offered while
`ready: false`: it verifies the owned accepted target and can restart its
provider/mount before retrying only the exact retained pending consumers in
dependency order. It does not repeat native import or restore v1.

Finishing requires both `can_finish_consumer_recovery: true` and `ready: true`.
After reviewing the remaining stopped consumers, post `job_id`, the exact
`confirmation_texts.finish_consumer_recovery` as `confirmation`, and
`acknowledge_pending_consumers: true` to
`/process/infinidysk-v2/finish-consumer-recovery`. The job completes with warnings
and keeps its recovery kind, activation flags and consumer results available
after reload. Provider conversion, unrelated mutations and v1 cleanup remain
blocked while recovery is held.

If the controller booted with only the recovery control plane, a successful
retry or finish can return `result.restart_required: true` with a job message
instructing a DUMB restart. Retained applications can already be running, but
normal background workers were not initialized on that controller. Restart the
container when instructed, then refresh status and verify normal startup;
`status: "completed"` alone does not remove this requirement.

Older held activated jobs without the new private target binding require
manual review, with both v1 and v2 data retained. Possible exposure does not
itself authorize retry, cancellation, cleanup or ordinary rollback, and the
backend does not fabricate replacement acceptance evidence for those records.

Do not infer ordinary rollback or cancel permission from `recovery_required`.
After exposure, a healthy completed cutover can separately advertise a manual
rollback requiring `rollback_requires_discard_ack: true` and its explicit
`acknowledge_discard_v2_writes` request acknowledgement. Missing acknowledgements
are refused; retained v1 state does not contain later v2 writes.

### Retire a completed v1 installation

This separate workflow also requires `infinidysk_v2_cleanup=true` and numeric
`infinidysk_v2_cleanup_protocol=1`. It is available only for an eligible completed
v1-to-v2 cutover, with healthy owned v2 delivery and verified retained backups.
A fresh generation 2 installation has no old v1 installation to retire.
Low-space jobs also withhold original-tree cleanup because their source data was
reused; their archive remains required for rollback.

Preview with `{"job_id": "SERVER_JOB_ID"}`. The response supplies the exact
removal/retention lists, estimated reclaim, expiring `preview_token`, typed
`confirmation_text` and acknowledgement names. Start using those server values:

```json
{
  "job_id": "SERVER_JOB_ID",
  "preview_token": "SERVER_PREVIEW_TOKEN",
  "confirmation": "SERVER_CONFIRMATION_TEXT",
  "acknowledgements": {
    "playback": true,
    "test_import": true,
    "rollback_retirement": true
  }
}
```

Poll the existing job endpoint for cleanup progress. The backend verifies the
full retained backup and a bounded immutable deletion whitelist before durably
retiring automated rollback. It then removes only verified original entries.
Interruption keeps rollback retired; a fresh preview can resume the same
whitelist. Backups, retirement receipts and PostgreSQL databases remain retained.
See [Retire the old v1 installation](../features/infinidysk-v2-migration.md#retire-the-old-v1-installation)
for operator checks and recovery limits.

### Native generation 2 PostgreSQL

| Method | Route | Purpose |
|--------|-------|---------|
| `GET` | `/process/infinidysk-v2/postgres/status` | Reconcile native provider/job state and advertise guarded actions |
| `POST` | `/process/infinidysk-v2/postgres/preview` | Verify a dedicated empty destination and its physical identity |
| `POST` | `/process/infinidysk-v2/postgres/start` | Retain recovery state and start native copy/synchronization |
| `POST` | `/process/infinidysk-v2/postgres/cutover` | Switch only the current synchronized job to PostgreSQL |
| `POST` | `/process/infinidysk-v2/postgres/cancel` | Cancel the current native job after destination identity checks |
| `POST` | `/process/infinidysk-v2/postgres/rollback` | Restore the retained SQLite snapshot when its guards permit |

Managed destination preview:

```json
{"target": {"use_managed_postgres": true, "database": "infinidysk_v2"}}
```

An external `target` supplies `host`, `port`, `database`, `user`, `password`
and `sslmode`. Remote connections require verified TLS or explicit `require`
mode. Passwords and connection URLs remain private and are not returned in
public status. Preview returns the current/target summaries, physical
`target_identity` (`system_identifier`, `database_oid`, `schema`), checks and a
short-lived `preview_token`/`confirmation_text`.
Provision the dedicated empty database with `C` collation and its role before previewing; choosing
`use_managed_postgres` selects DUMB's connection settings, not database creation.

Start requires that token and exact confirmation, plus
`acknowledge_backup: true` and `acknowledge_destructive_target: true`.
Subsequent cutover/cancel/rollback requests use the **current `job_id`**, exact
text from `status.confirmation_texts[action]` and both acknowledgements. They
do not reuse an expired initial preview token after a long synchronization.
Only strict `status.actions[action] == true` admits an action; the backend
rechecks native state, source/target identities and recovery evidence.

Cancel can truncate the dedicated destination's migration tables. Rollback
does not merge later PostgreSQL writes into SQLite. Environment-managed
`INFINIDYSK_DATABASE_URL` configurations disable native provider moves, and
direct upstream cleanup routes must not bypass DUMB's checks.

Confirmed cancellation can return `status: "cancelled"` and
`cleanup_required: true` while SQLite remains usable and ordinary lifecycle is
unblocked. Bounded cleanup warnings stay private; they can refer to source
change-capture cleanup as well as destination tables. Keep a nonblocking review
notice visible without interpreting it as an active transfer. A warning-directed
managed restart may be appropriate; direct cleanup SQL is not authorized by
the notice.

Rollback does not require PostgreSQL connectivity. The wrapper durably records
the restored SQLite device/inode before startup. A retry after delayed delivery
checks that same live file rather than replacing newly accepted SQLite writes;
changed file identity blocks recovery.

### Conflicts and recovery

An expired/mismatched preview, wrong job, changed source/target or competing
lifecycle/migration operation returns a conflict (`409`). A backend below the
minimum code version rejects mutations (`426`). Refresh status and obtain a
fresh preview instead of automatically replaying a failed POST. HTTP timeouts
do not cancel native workers. Keep retained job identities visible when status
cannot be confirmed, and disable actions until a valid current response returns.

Neither workflow falls back to `/infinidysk-migration/*`,
`/postgres-migration/*` or the old `/arr-postgres-migration/*` routes.

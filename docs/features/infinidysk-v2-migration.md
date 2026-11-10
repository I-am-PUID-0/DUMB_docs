---
title: InfiniDysk 2 Installation and Upgrade
description: Review InfiniDysk 2 installation, guarded major upgrades, rclone or native FUSE mounts, library paths, recovery, and native PostgreSQL conversion in DUMB.
icon: lucide/arrow-up-circle
---

# InfiniDysk 2 installation and upgrade

DUMB keeps InfiniDysk 1.x as the default. InfiniDysk 2 uses a different native
runtime, configuration and data layout. Install it or move existing data through
**Service tools → InfiniDysk 2 migration** on the InfiniDysk service page.
When the backend identifies an eligible empty installation, a dashboard notice
opens the same wizard in fresh-install mode.

The wizard requires DUMB API **2.24.0 or newer**, explicit InfiniDysk 2 capabilities
and migration protocol **1**. An older, unknown or temporarily unavailable
backend cannot start a migration. Previously discovered job identities and
recovery information remain visible. The supported native artifact is currently
**`v2.0.0-beta.6`**; selecting 2.x through a 1.x release or source field is refused.

## Separate the choices

| Choice | Initial behavior |
|--------|------------------|
| Runtime generation | Keep 1.x until an explicit, validated 2.x installation or cutover |
| Mount | Preserve the existing rclone-over-WebDAV mount by default; native FUSE is an explicit alternative |
| Database | Import v1 SQLite or v1 PostgreSQL into a separate generation 2 SQLite database first; PostgreSQL conversion is optional afterward |
| Import strategy | Preserve existing outputs; changing generation or mount does not regenerate symlinks or STRM files |

SQLite-to-SQLite migration converts the generation 1 schema and data into the
generation 2 format while retaining the original source. PostgreSQL is optional;
you can keep generation 2 SQLite or convert it separately after validation.

The original 1.x runtime, configuration and data remain the rollback source.
Generation 2 program files and data use separate directories. The native runtime
uses its verified artifact; active 1.x branch/commit selectors are cleared in
the prepared 2.x configuration while the original selection stays in recovery.
Do not toggle the generation or provider fields to bypass the wizard.

## Before starting

Keep independent backups of the source database, configuration, identity and
signing keys, symlink trees and existing STRM files. DUMB's retained migration
state is useful recovery evidence, not a replacement for those backups.

An existing source must meet the 1.3-era database schema floor checked by the
backend and have an empty job queue after quiescence. The release label alone
does not establish schema compatibility. Finish or resolve any existing
namespace or database migration before starting another workflow.

Sources with OIDC configured are currently blocked until the target policy has
been verified. The login/OIDC acknowledgement does not override that blocker.

Review every affected Arr, request producer and media server. Stop new imports,
playback and scans for the approved downtime. The preview records managed
mounts, enabled managed consumers and configured link roots. Check external
consumers, remote path mappings, library roots and signed stream URLs separately;
an empty recorded STRM list does not prove that none exist.

!!! warning "Contained import can block an upgrade"

    DUMB rehearses the actual upstream importer in a private environment with
    external network access and writes to the original data denied. The host
    must support the required Linux namespaces, `nsenter` and Landlock ABI 3 or
    newer. Failed containment checks block the operation.

    Imports needing external NNTP/provider reads can skip records when network
    access is denied. Skipped, failed or incompletely proven media prevents
    activation; the original generation 1 installation is retained. There is
    no automatic online or uncontained fallback. Keep using 1.x when its data
    cannot pass these checks.

A v1 PostgreSQL source also needs a backend-supported source snapshot adapter
and successful dump/restore proof. If that path is unavailable or unverified,
the preview blocks it. The major importer does not directly reuse the v1
PostgreSQL database as a generation 2 database.

## Choose archive storage

The migration panel's **Backup destination** selects the legacy local backup
tree or [registered local/NAS archive storage](backup-storage.md) for this job.
Use **Register destinations and manage the global default** to register an
existing container-mounted directory. Registration alone does not move backups
or adopt a new default. Review the selected destination and local working-space
requirements in each new preview.

A registered destination holds a closed, verified source archive. Active v2
SQLite data, job/control state and import/database-restore scratch remain local.
Keep independent backups even when DUMB retains and verifies its own archive.

## Review and run

The preview inventories the complete source data and runtime trees and checks
copy capacity. Filesystem entry counts include application blob stores and any
build or dependency directories inside those trees; they are not counts of
titles or media files. The storage review shows source entry counts and logical
size, then each filesystem's required space, available space, shortfall and status.
Required space already includes retained backups, the candidate installation,
PostgreSQL staging and restore overhead when applicable, up to 512 MiB for the
inventory manifest, and a safety margin. Paths sharing a filesystem use one
combined budget. An unavailable estimate does not pass the capacity check.

These estimates do not reserve space. DUMB checks capacity again before copying;
keep enough space available throughout the operation.

If an inventory or capacity check blocks the preview, keep the original
installation and its files intact. Do not bypass the check, truncate the
inventory or delete blobs or build files to get past it. Review the configured
source locations and available space, and resolve the blocker before retrying.

1. Open the migration tool and review the detected source, target directories,
   database and exact mount path.
2. Keep **historical rclone over WebDAV**, or explicitly choose **native FUSE**.
   The backend must verify ownership, prerequisites and consumer visibility.
3. Generate a preview. Review its checks, blockers, warnings and recorded scope.
   Existing migrations preserve the exact mount path; they do not rename the
   virtual library namespace or change import strategy.
4. Confirm the independent backup, downtime, beta, login/OIDC policy and
   downstream-path acknowledgements, then type the displayed confirmation.
   The downstream review confirms existing Arr/media mount paths, remote path
   mappings, symlinks and STRM origins, and that external writers/scanners are
   stopped. It is an operator review, not an automatic audit of external players.
5. For existing data, run the isolated rehearsal. Cutover requires a validated
   rehearsal matching the reviewed plan. A fresh installation must instead
   prove that it will not overwrite existing data.
6. Start the installation or migration and follow the persistent job. A changed
   source or expired preview requires another review; a successful rehearsal can
   be reused only when its public plan fingerprint still matches.

After a validated rehearsal, DUMB confirms that the native candidate and its
process group have stopped and that v1 and its managed consumers were restored.
It then removes only that job's full private candidate copy, retaining the
verification receipts, source archive or backup and minimal database evidence.
Failed rehearsals retain their candidate for investigation. Cutover prepares
its local working candidate after the source checks pass again; allow enough
space for that peak even when a successful rehearsal has released its copy.

Closing the panel or visiting another page does not cancel the backend job.
The global notice reopens progress or recovery after navigation and reload.
Only job identities are saved for browser recovery; preview authorizations and
database passwords are not. A transport error does not prove that a job stopped.
Refresh status before retrying, and retain an unconfirmed job's recovery evidence.

## Mount and library continuity

Both mount choices expose InfiniDysk's virtual filesystem. Keeping
`/mnt/debrid/infinidysk` alone is insufficient: existing relative paths such as
`content/<category>/...`, completed-download paths, categories and link semantics
must still identify the same media.

| Mount | Consequences |
|-------|--------------|
| rclone over WebDAV | Native FUSE stays off. DUMB uses the generation 2 HTTP endpoint and Basic login, keeps `--links`, and uses a shorter directory-cache policy because 1.x RC refresh notifications are absent. Rclone settings remain rclone-owned. |
| Native FUSE | Requires working FUSE access, permissions and mount visibility in every consumer namespace. The old associated rclone owner must stop and detach before the native mount takes its exact path. Rclone flags and optimizer recommendations do not apply. |

A foreign, ambiguous, busy or stale mount blocks a transition. DUMB does not
mount over another owner or force-detach a mount to make the check pass. Keep
unrelated rclone instances and shared storage workflows intact.

For symlinks, compare raw targets and verify they resolve through the selected
mount. For STRM files, preserve identity/signing material and the original
reachable origin and signed path. A valid token does not repair a retired URL
route. Generic preview/view links may differ between generations. DUMB's symlink
repair tool does not rewrite STRM URLs.

Choose any later symlink/STRM strategy change separately in InfiniDysk's native
configuration. A global STRM selection still produces symlinks for music and
book jobs. Validate playback from the actual media server/player network;
STRM does not establish compatibility with every media server or remove all
filesystem requirements.

## Native PostgreSQL conversion

After generation 2 is validated, open **Service tools → InfiniDysk 2 database
conversion**. This uses the native copy, synchronization and cutover engine,
not DUMB's generation 1 SQLite-to-PostgreSQL adapter.

1. Provision and start a dedicated, empty PostgreSQL database with **`C`
   collation** and a suitable role
   first. For DUMB-managed PostgreSQL, configure its
   [database list](../services/dependent/postgres.md); otherwise use your external
   administrator workflow. The migration preview does not create a destination.
   Then select that managed database or supply its external TCP address and TLS policy.
2. Preview the destination. Review its physical cluster identity, database OID
   and schema, along with source, emptiness and recovery checks.
3. Confirm backups and the destination reset acknowledgement, type the exact
   confirmation, then start native copying and synchronization.
4. Wait for the backend to advertise **cutover**. Review and confirm that action
   separately. The native restart may retain its process ID; wait for confirmed
   provider state and service health.

External credentials are sent only to the private backend preview and cleared
from the form. They are not returned in public status or browser job storage.
The backend checks the current job and physical source/target identities before
each destructive action; a changed target or stale preview blocks it.

!!! warning "Dedicated destination required"

    Native cancellation can empty the migration destination's tables. Never
    use a database belonging to another application or reuse the source as the
    destination. Cancel and rollback are offered only when their current
    backend guards permit them; do not call upstream cleanup routes to bypass
    those checks.

The native **cancel** and retained **rollback** actions require their own exact
confirmation and acknowledgements. Rollback restores retained SQLite state; it
does not merge later PostgreSQL writes. A fresh 2.x deployment configured directly
through `INFINIDYSK_DATABASE_URL` is environment-managed and disables the native
provider conversion UI. Do not use that variable to convert an existing store.

Cancellation can complete with a nonblocking **native cleanup needs review**
notice while SQLite remains active. Retained private warnings can concern
PostgreSQL destination tables or SQLite change-capture cleanup. Review that
evidence under `/config/migrations/infinidysk-v2-postgres` before reusing the
destination or changing capture state. The private bundle also contains
connection credentials. If the native
warning calls for a restart, use a normal managed restart after reviewing it;
do not delete tables or provider files to clear the notice. A nonempty destination
still fails a later preview.

Rollback can restore the retained SQLite source while PostgreSQL is unreachable.
DUMB records the restored file identity before restarting it. If mount recovery
is delayed, retrying verifies that same SQLite file and its health without
restoring over writes accepted since the first restart. A missing or replaced
file remains blocked for investigation.

## Validate and recover

Before resuming normal work, verify queue/history/provider settings, timezone,
login and OIDC policy, virtual categories, existing symlinks, representative
file/range/seek reads, signed STRM playback and paths from each real consumer.
Run a deliberate test import only after those checks and review the resulting
Arr and media-server paths. A healthy process or a successful fixture test is
not proof of real provider/account playback.

InfiniDysk 2 uses a dedicated root URL for its UI. Use the direct local address
or configured public portal; embedded subpath login/playback remains unavailable
unless the backend explicitly advertises a validated adapter.

If the job is interrupted or needs recovery, keep the original data and private
job evidence under `/config/migrations/infinidysk-v2`. Use the offered guarded
rollback and exact job confirmation. Major rollback restores the retained v1
runtime/configuration; later generation 2 writes are not copied back. A failed
rollback or unavailable recovery action needs investigation before restarting
imports, scans or services. Do not delete retained state to clear a banner.

## Retire the old v1 installation

After a verified cutover and real-library validation, the same migration panel
can offer **Retire the old v1 installation**. Keep independent backups and
confirm successful playback and a test import before using it.

1. Select **Review old-installation cleanup** and review the exact old paths,
   estimated reclaim and retained backups.
2. Confirm playback, test-import and rollback-retirement acknowledgements, then
   type the server's exact confirmation.
3. Select **Retire rollback and remove reviewed v1 files** and follow the job.

Cleanup verifies the retained source backup and unchanged v1 files, then durably
retires automated major rollback before removing reviewed entries. Backups and
receipts remain retained; PostgreSQL databases, shared mounts and unrelated
libraries are not removed. Later v2 writes are never merged into a v1 backup.

If cleanup stops, the old tree can be partially removed and automated rollback
stays retired. Preserve the job and deletion-manifest evidence; use a fresh
review to resume the same removal plan. Changed files or mounts stop remaining
removal, and new files are retained rather than added to the deletion plan.
Do not delete backups or job state to clear a cleanup warning.

See [Process Management API](../api/process.md#infinidysk-2-workflows),
[Media Library Protection](media-library-protection.md),
[Symlink Operations](symlinks.md) and the
[generation 1 PostgreSQL migration guide](arr-postgres-migration.md) for the
separate existing workflows.

---
title: Installation Backup and Restore
description: Back up DUMB configuration, managed application state and databases, schedule verified archives, and restore an installation from mounted storage.
icon: lucide/archive-restore
---

# Installation backup and restore

Open **Settings → Backups and restore** to manage installation archives and
shared backup destinations. This requires a backend advertising installation
backup protocol `1`; older backends continue to expose their existing tools.

## What an installation backup contains

The preview inventories DUMB configuration, authentication and signing state,
managed application configuration and persistent data, managed databases, and
configured symlink state. Existing data belonging to disabled services is
included when it is discovered. Review the actual roots and exclusions rather
than assuming that a process's working directory is its complete data directory.

Plex DBRepair's native installation and database directories are included from
the nested `plex.dbrepair` settings when they exist, including when scheduled
repair is disabled. The default installation directory is `/data/dbrepair`.
Its supported `install_dir` and `databases_path` settings supplement the
existing Plex database coverage; see the
[Plex configuration guide](../services/core/plex-media-server.md). A command's
working directory alone does not add its contents to the archive.

Media content, mounted remote libraries, external services and databases,
container images, host deployment files and separate log/cache stores are outside
the installation archive. Application-owned logs, artwork, blob stores and caches
inside an included data root may still be included. Preserve your Compose/Portainer deployment, bind mounts
and external systems separately. A symlink's target text is preserved without
copying the referenced media. Recognized STRM, subtitle, metadata and artwork
sidecars in managed library-link directories are included. Actual media files
and unrecognized regular payloads in those directories remain blockers; DUMB
identifies the path instead of silently omitting it. DUMB refuses unsupported
or ambiguous state instead of silently reporting a complete backup.

The first archive format preserves regular files, directories, literal symlinks,
normal POSIX ownership/permissions and modification times. Hardlinks are stored
as independent files. Extended attributes, ACLs, special permission bits and
unresolved nested mounts are blockers. Nested controller-auth paths or an
inventory that exceeds the restorable transaction budget also require review;
the utility does not silently discard that state.

Archives contain credentials and private keys and are not encrypted.
Restrict access to the destination, partial exports and downloaded copies;
shared storage permission consent does not prove confidentiality.

## Choose storage

In **Backup destination**, expand **Register a backup destination**.
Register an existing container-visible directory, then explicitly select that
destination or **Use global default**. The separate **Global default** controls
show, set or clear the saved preference. See
[Backup storage](backup-storage.md) for registration and mount requirements.

An already-mounted NFS/SMB directory can hold closed archives when it passes the
storage checks. Enable **Allow shared archive permissions** during registration
only when you trust the destination's access controls; it starts unchecked and
restrictive POSIX checks remain the default.
DUMB does not mount shares or change their existing ownership/permissions.
Active database and private recovery working files remain local. A missing or
replaced destination mount blocks the operation;
DUMB does not write into an underlying local directory as a fallback.

## Create a backup

Use the container's direct frontend/API access before starting. Managed reverse
proxies and tunnels can be stopped with the applications, so their public or
embedded ingress path may be unavailable during the operation.

1. Select a destination and request a backup preview.
2. Review included paths, exclusions, space estimates and any blockers.
3. Stop external writers to the included data. Confirm the displayed downtime
   acknowledgement before starting.
4. Follow the job until its archive has passed complete readback verification.

DUMB records which managed services are running and quiesces them for a
consistent filesystem snapshot, including managed SQLite and PostgreSQL state.
The API and frontend remain available through their direct ports for progress.
Previously running services
are resumed after a backup when it is safe; previously stopped services are not
started just because a backup ran. An error is retained with recovery guidance.

Database consistency follows the requirements for a stopped
[PostgreSQL cluster](https://www.postgresql.org/docs/current/backup-file.html)
and a quiescent [SQLite database and its journals](https://sqlite.org/howtocorrupt.html#_backup_or_restore_while_a_transaction_is_active).

Capacity is checked for the archive destination and local working storage.
There is no fixed overall file-count or archive-payload-size ceiling.
Preview measures the inventory and its verification metadata, then checks
whether the available local space can support the verification ledgers.
Archive overhead and restore staging also count toward the estimates. A large
backup destination does not replace the need for local working space.

Large artwork, blob and application-data trees can require a lengthy metadata
scan before a preview is ready. This phase inventories entries rather than
copying the complete file contents, and it does not stop applications.
Individual path, nesting, record and supported-metadata checks still apply;
available disk space does not make an unsafe archive restorable.

Estimates are not a reservation: another process can consume space afterward.
Admission is checked again during the operation, and failed or incomplete
output is never advertised as a verified backup.

If the connection drops after a start request, the operation may already have
been accepted. Reconnect through direct frontend/API access and refresh status
before submitting another operation. Keep the recorded job identity when one
was received.

The archive list reports completed archives separately from running or failed
jobs. Record the selected archive and retain an independent copy before relying
on it for disaster recovery. A checksum verifies the recorded bytes; a successful
restore rehearsal remains the practical test of your recovery procedure.

## Unclassified data in a backup preview

A preview can stop on an unrecognized child of `data_root`, even when that
directory is empty. Current backends identify the first unclassified path and
entry type in the blocker; long or unusual paths are escaped and can be marked
as truncated. The backup job has not started and managed services have not
been stopped.

The inventory follows supported application persistence settings. There is no
generic application/media classification wizard or arbitrary include/exclude
switch for this guard. Review the reported path and its owning service's
actual configuration. Do not add unrelated settings, rename, move or delete
state just to clear the warning. If an existing DUMB-managed path is missing
from coverage, retain it and report its path and owning tool so that its
persistence can be qualified. Custom state and external media require their
own backup/deployment review; DUMB does not silently omit them or sweep them
into an installation archive.

## Schedule backups

Scheduling is off by default. Enable it deliberately, choose its destination,
interval and retention, and save the schedule. Scheduled backups use the same
coverage, quiescence, admission and verification checks as manual backups, so
schedule them during a suitable maintenance window.

Missed or blocked jobs remain visible. A schedule does not bypass startup,
another active operation, unavailable storage or insufficient space. Retention
applies only to verified scheduled installation archives owned by that schedule;
manual archives and other tools' backups are retained separately.

## Restore an existing or fresh installation

A restore replaces managed state and requires downtime. Keep a separate backup
of the current installation and keep external writers stopped throughout the
operation, including any other DUMB container using the same mounted state.
Restore only archives whose origin you trust.

1. Provision the required container image and original container-visible mounts.
   For a fresh installation, open the backup/restore entry before rerunning
   onboarding or enabling application services.
2. Select a catalogued archive, or enter the container-visible path of an
   installation archive already mounted into the container. The mounted-file
   option does not require the old installation's local catalog receipts.
   If that file has fixed/shared permissions, review its origin and access
   controls before enabling **Allow shared archive permissions**. This is an
   independent checkbox for the mounted file and starts unchecked.
   Catalogued archives use their registered destination's permission policy.
3. Request a restore preview. Review archive integrity, application data roots,
   container/database compatibility, destination identity, space requirements,
   and any existing data that would be replaced.
4. Complete the displayed acknowledgements and confirmation phrase, then start.
5. Follow the retained job. After a successful restore, restart the container
   when instructed so DUMB reloads the restored configuration and authentication.
6. Verify login, mounts, application databases, imports and playback before
   retiring the independent backup.

The restore cannot recreate host mounts or a missing external database.
Incompatible paths, architecture or database state are blockers. Restored
authentication can require the original installation's login after restart.
Keep the original registry image digest with your deployment files; archive
compatibility metadata does not recreate or pin the container image itself.

Restore preview reads and verifies the complete archive. Large NAS archives can
take several minutes; the interface reports verification in progress and does
not automatically submit another request. This read-only phase does not stop
applications. Restore staging is also verified before managed writers are stopped
and live state is replaced.

Archives are checked before extraction into private local staging. Paths,
checksums and file types are validated; archive links cannot direct extraction
outside that staging tree. The restore retains rollback evidence for replaced
state. A failure during read-only verification does not stop applications.
Before live replacement, DUMB attempts to resume any writers it stopped if the
operation fails. Once replacement has started, or if the previous running set
cannot be safely resumed, DUMB keeps applications blocked for recovery instead
of starting them against a mixture of old and restored data. Use the offered
rollback/recovery action and retain its files until recovery completes.

## Startup and private recovery state

DUMB checks its local installation-recovery records before normal applications
start. If those records require recovery or cannot be trusted, only the API and
already-installed frontend start. Service actions can return `409` while this
installation-wide hold is active; the recovery banner identifies the blocked
controller rather than an individual application's startup failure.

Some configuration mounts give new directories a group-inheritance bit
(**SGID**), even when DUMB creates them with private `0700` permissions. Current
builds recognize that inheritance on otherwise private, eligible controller
state and clear it after a complete safety check. New installation-control
folders are created with controller ownership and mode `0700`. This repair does
not make shared or writable recovery payloads trustworthy: unexpected owners,
shared/special file permissions, links and changed mounts still require review.
The diagnostic distinguishes ownership, permission and mount failures.

Preserve `/config/installation-backups`, its job records and referenced backups
when investigating a hold. Use the relevant retained recovery action, then
restart when instructed. Do not delete the directory, purge databases or apply
recursive ownership/permission changes to clear the banner. A
[major InfiniDysk migration](infinidysk-v2-migration.md#progress-cancellation-and-recovery)
has its own job, cancellation and rollback flow.

## Related tools

- [Symlink operations](symlinks.md) provides smaller link snapshots and schedules.
- [InfiniDysk 2 installation and upgrade](infinidysk-v2-migration.md) has its own
  major-upgrade archive and rollback workflow.
- Application-native backup/export tools and external systems keep their own
  recovery contracts.

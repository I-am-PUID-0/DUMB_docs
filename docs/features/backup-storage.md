---
title: Backup Storage
description: Register local or already-mounted NAS archive destinations for InfiniDysk upgrades and symlink snapshots while preserving local database and recovery state.
icon: lucide/archive
---

# Backup storage

Register a named destination for **installation backups**, **InfiniDysk 2
major-migration archives** or **standalone and scheduled symlink snapshots**.
Open **Settings → Backups and restore** for the central controls. These appear when the
backend advertises the corresponding storage capabilities. Existing backup
paths remain the default until you explicitly select a registered destination.

## Register an existing destination

The directory must already exist inside the DUMB container. A host-only path
is insufficient. Mount NFS/SMB storage on the host and expose it to the container
through your normal deployment configuration before registration. DUMB does not
mount network shares or request their credentials.

1. Open **Register destinations and manage the global default** in
   **Settings → Backups and restore**, the InfiniDysk migration panel or the
   Symlink operations panel.
2. Enter a unique identifier, display name and existing container-visible path.
3. Select **Preview destination**, review its checks, then **Register destination**.
4. Select the destination for the current operation. Use **Save global default**
   only when you want to save a shared preference; registration alone does not
   change that preference or any service's backup selection.

**Use global default** explicitly adopts that saved preference. Clearing the
global default blocks future operations using that choice until you select a
new default or an explicit destination. An existing custom backup path remains
active when the legacy/local choice is selected.
Saving a symlink schedule applies its selected destination to that schedule;
changing a draft selection does not save it. Use a new identifier when moving
an existing registered root to another directory or filesystem.

## Cold archives and local working storage

Local directories and already-mounted NFS/SMB directories can hold closed
archive files when they pass DUMB's ownership, private-permission and readback
checks. The destination must support private directories and files; a share
that cannot enforce those permissions does not qualify. Archives can contain
configuration credentials, identity/signing keys and database data. Restrict
access and keep an independent backup with a tested restore procedure.

Active SQLite databases, migration control state, the inventory manifest and
import/database-restore scratch stay on verified local storage. SQLite WAL
requires local shared-memory and locking behavior and does not support network
filesystems. See the [SQLite WAL documentation](https://www.sqlite.org/wal.html).
Selecting NAS archive storage therefore does not remove local working-space
requirements. Review each filesystem's capacity before starting.

The registered-storage consumers are the tools listed above.
Existing Arr PostgreSQL migration backups, native PostgreSQL recovery snapshots,
application-managed backups and runtime-install rollback transactions keep
their existing locations and settings.

For a managed installation archive, scheduling and fresh-container recovery,
see [Installation backup and restore](installation-backups.md). Configuration
`.bak` copies, service-reset configuration backups and migration recovery bundles
remain separate tools. Protect host deployment files, external systems and media
through their independent backup/restore plans.

## Verification and recovery

DUMB records the selected root's identity and writes only its own managed
artifacts. Exports use private temporary files, complete-byte checksum/readback
verification and atomic publication. The manifest browser lists registered
artifacts rather than browsing arbitrary NAS files. Opening or downloading a
managed artifact verifies its content again; the list's checksum records the
completed export verification.

For registered destinations, a missing or replaced mount blocks use instead of
writing into the local directory underneath an absent NAS mount. Legacy custom
paths retain their existing behavior until you select registered storage. After
an interruption, preserve the job, partial-export evidence and original source,
then restore storage availability and review the offered recovery action.
Network availability and server durability still depend on your deployment.

Managed backups use opaque references. Select them through the picker or use
the authenticated download API; the reference is not a website URL or a
filesystem path. InfiniDysk creates its local import candidate from the original
source; the archive provides retained data for manual recovery. Automated major
rollback starts the retained originals until that rollback is explicitly retired.

Scheduled symlink retention removes only that process's scheduled managed
snapshots. Manual snapshots are retained separately from automatic pruning.
A symlink snapshot records link paths and targets; protect the referenced
media and application databases through their normal backup plans.

See [InfiniDysk 2 installation and upgrade](infinidysk-v2-migration.md),
[Symlink operations](symlinks.md) and the
[Process Management API](../api/process.md#registered-backup-storage).

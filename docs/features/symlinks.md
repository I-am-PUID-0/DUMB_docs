---
title: Symlink Operations
icon: lucide/link
---

# Symlink Operations

This page is the canonical reference for how DUMB uses, repairs, migrates, snapshots, and restores symlink libraries.

It covers:

- Path model and service-specific symlink roots
- Repair modes and when to use each one
- Snapshot backup/restore and scheduled backups
- Safe migration playbooks (including Decypharr beta path changes and individual -> combined roots)
- Frontend option behavior and backend API behavior
- Troubleshooting and recovery

---

## Why symlinks matter in DUMB

In DUMB workflows, services like Decypharr, NzbDAV, CLI Debrid, and Riven create curated symlink libraries that point to mounted content (for example rclone/DFS paths under `/mnt/debrid`).

This gives you:

- Clean, curated libraries for media servers
- Separation between raw mount trees and user-facing libraries
- Faster migration paths when providers or mount layouts change

Common failure mode:

- A symlink exists, but its target path no longer exists after mount/path changes.

---

## Path model (high level)

Typical roots inside the container:

  - Raw/mount content roots:
    - `/mnt/debrid/decypharr`
    - `/mnt/debrid/clid`
    - `/mnt/debrid/nzbdav`
    - `/mnt/debrid/riven`
  - Curated symlink library roots:
    - `/mnt/debrid/decypharr_symlinks`
    - `/mnt/debrid/nzbdav-symlinks`
    - `/mnt/debrid/clid_symlinks`
    - `/mnt/debrid/combined_symlinks`
    - `/mnt/debrid/riven_symlinks`

Important:

- Symlink targets are path-sensitive. If the target path changes, links may break until repaired/migrated.

---

## Supported service workflows

### Decypharr

- Arr requests route to Decypharr.
- Decypharr resolves content in debrid-backed mount paths.
- Arr rename/import behavior produces curated symlink results for library paths.
- Common migration: provider-layout path rewrite (for example `realdebrid/__all__` -> `__all__`).

### NzbDAV

- Arr workflow uses NzbDAV download-client flow.
- Final libraries are curated symlink paths under NzbDAV roots or combined roots.

### CLI Debrid

- CLI Debrid can create symlinks from mounted content into `/mnt/debrid/clid_symlinks`.
- A frequent use case is cloning/migrating these entries into another symlink tree for downstream import workflows.

### Riven

- Uses configured `symlink_library_path`.
- Included in backend defaults when configured.

---

## DUMB symlink tools

DUMB provides three categories of symlink operations:

1. Repair/migration (`POST /api/process/symlink-repair`)
2. Standalone snapshot backup/restore (`POST /api/process/symlink-manifest/backup`, `POST /api/process/symlink-manifest/restore`)
   - Async backup/restore modes:
     - `POST /api/process/symlink-manifest/backup-async`
     - `POST /api/process/symlink-manifest/restore-async`
     - `GET /api/process/symlink-job-status`
3. Scheduled snapshot backup and restore selection (`/api/process/symlink-backup-*`)

See API details: [Process Management API](../api/process.md).

---

## Repair modes (what each one does)

### 1) Prefix rewrite mode

Use when link targets changed path prefix but links should stay in-place.

Example:

- From: `/mnt/debrid/decypharr/realdebrid/__all__/...`
- To: `/mnt/debrid/decypharr/__all__/...`

Behavior:

- Scans symlink entries in selected roots
- Rewrites target strings that match `from_prefix`
- Leaves symlink file location unchanged

### 2) Preset rewrite mode

Use for known migrations with built-in rules.

Current preset:

- `decypharr_beta_consolidated`

Behavior:

- Same as prefix rewrite, but rule set is predefined.

### 3) Root migration mode

Use when symlink files themselves must move between library trees.

Example:

- From: `/mnt/debrid/decypharr_symlinks/...`
- To: `/mnt/debrid/combined_symlinks/...`

Behavior:

- Preserves relative path under the destination root
- Supports:
    - move (default)
    - copy (`copy_instead_of_move: true`) for staged transition/import

---

## Frontend option behavior (important details)

### Roots behavior

- `Roots override` replaces defaults for that run (it does not append).
- `Add root from common paths` is a UI helper that appends selected paths into the `Roots override` textbox.
- In current Symlink Repair UI:
  - choose a **Playbook** for common migrations, or custom modes
  - root override controls are shown for prefix-rewrite playbooks
  - preset rewrite playbook uses service-scoped defaults for the current service page
  - root migration playbooks use explicit `from_root` and `to_root`

### Service-scoped defaults (repair UI)

On each service page, default repair scope is narrowed to that service root unless overridden:

- Decypharr page -> `/mnt/debrid/decypharr_symlinks`
- NzbDAV page -> `/mnt/debrid/nzbdav-symlinks`
- CLI Debrid page -> `/mnt/debrid/clid_symlinks`
- Riven page -> `symlink_library_path` (or `/mnt/debrid/riven_symlinks` fallback)

### Backup manifest on apply

Repair UI supports automatic backup manifest creation on apply runs:

- Auto-backup enabled by default
- If no explicit path is provided, a timestamped path is generated

This gives you rollback/audit artifacts without manual setup each run.

---

## Snapshot backup / restore

Snapshot tab behavior:

- `Manifest path` now includes a dropdown picker of existing snapshot files (same directory scan behavior as scheduled restore), plus a `Custom path` option.
- `Manifest path` remains fully editable when `Custom path` is selected.
- Backup root scope defaults to `Current service root` on the active service page.
- Managed default manifest path now follows snapshot root selection:
    - current/specific root => `/config/symlink-repair/snapshots/{service}.json`
    - all default roots => `/config/symlink-repair/snapshots/latest.json`
- Backup root scope supports:
    - Current service root
    - All default roots
    - A specific known root
    - Custom roots (textarea)

### Standalone backup

Create snapshot manifest:

```json
{
  "backup_path": "/config/symlink-repair/snapshots/latest.json",
  "roots": ["/mnt/debrid/decypharr_symlinks"],
  "include_broken": true
}
```

### Restore from snapshot

```json
{
  "manifest_path": "/config/symlink-repair/snapshots/latest.json",
  "dry_run": true,
  "overwrite_existing": false,
  "restore_broken": true
}
```

Recommended flow:

1. Run restore in dry-run mode
2. Review output
3. Apply with confirmation when expected

---

## ELI5: which button should I use?

Think of symlinks like shortcut files.

- If the shortcut is in the right folder, but points to the wrong place:
    - use **Repair** with **prefix rewrite** (or preset)
- If you want shortcuts to live in a different folder:
    - use **Repair** with **Move symlink entries between roots**
- If you want shortcuts copied into a new folder, but keep originals:
    - use **Move symlink entries between roots** with **copy mode**
- If you are nervous about changes:
    - take a **Snapshot backup** first
- If you want automatic safety backups:
    - use **Schedule** and set interval + retention

Simple examples:

- "My CLI Debrid links should also exist for Decypharr/Arr":
    - move/copy from `/mnt/debrid/clid_symlinks` to `/mnt/debrid/decypharr_symlinks`
- "My CLI links still live in `clid_symlinks`, but target path changed":
    - rewrite target prefix from old mount path to new mount path
- "I just want to test before touching anything":
    - click **Dry run** first

Golden rule:

- Dry run first
- Then apply
- Keep backup manifest enabled

---

## Scheduled backup behavior

Enabled with service config keys:

- `symlink_backup_enabled`
- `symlink_backup_interval`
- `symlink_backup_start_time`
- `symlink_backup_path`
- `symlink_backup_include_broken`
- `symlink_backup_roots` (optional override)
- `symlink_backup_retention_count`

### Retention

- `symlink_backup_retention_count = 1` is the default when unset
- `0` disables pruning (keep all matching manifests)
- Values `> 0` keep newest `N`, pruning older files matching the service template

### Default cadence

- Default `symlink_backup_interval` is `168` hours (weekly) unless overridden.

### Restore from scheduled backups

Use the Schedule tab dropdown to pick an available manifest discovered from the configured template.

---

## Migration playbooks

### Playbook A: Decypharr beta provider path consolidation

Use preset rewrite:

```json
{
  "dry_run": true,
  "presets": ["decypharr_beta_consolidated"]
}
```

Then apply:

```json
{
  "dry_run": false,
  "presets": ["decypharr_beta_consolidated"],
  "backup_path": "/config/symlink-repair/decypharr-rewrite.json"
}
```

### Playbook B: Individual -> combined symlink roots

```json
{
  "dry_run": false,
  "root_migrations": [
    {
      "from_root": "/mnt/debrid/decypharr_symlinks",
      "to_root": "/mnt/debrid/combined_symlinks"
    }
  ]
}
```

### Playbook C: Clone CLI Debrid symlinks into Decypharr tree

```json
{
  "dry_run": false,
  "root_migrations": [
    {
      "from_root": "/mnt/debrid/clid_symlinks",
      "to_root": "/mnt/debrid/decypharr_symlinks"
    }
  ],
  "copy_instead_of_move": true
}
```

Use this when you want to seed/import existing curated content into another service’s expected symlink root without deleting originals.

### Playbook D: Move CLI Debrid symlinks into Decypharr tree (cutover)

```json
{
  "dry_run": false,
  "root_migrations": [
    {
      "from_root": "/mnt/debrid/clid_symlinks",
      "to_root": "/mnt/debrid/decypharr_symlinks"
    }
  ],
  "copy_instead_of_move": false
}
```

Use this when you are done with the old tree and want a true move.

### Playbook E: Retarget CLI Debrid symlink targets from `clid` mount to Decypharr mount

Use custom prefix rewrite on CLI Debrid root:

```json
{
  "dry_run": false,
  "roots": ["/mnt/debrid/clid_symlinks"],
  "rewrite_rules": [
    {
      "from_prefix": "/mnt/debrid/clid/",
      "to_prefix": "/mnt/debrid/decypharr/__all__/"
    }
  ]
}
```

Notes:

- This rewrites existing link targets in-place.
- Exact `to_prefix` should match your active Decypharr mount layout.
- Dry-run first to confirm expected match count.

### Playbook F: Cross-service import seeding for Arrs

Goal: make existing non-Arr symlink libraries importable by Arr workflows.

Suggested sequence:

1. Snapshot backup source + destination roots.
2. Run root migration in copy mode (`copy_instead_of_move: true`) from source root to Arr-consumed root.
3. Validate imports in Arr.
4. Optionally run cleanup move/remove after stable import.

### Playbook G: Combined root adoption without losing existing libraries

When switching to `/mnt/debrid/combined_symlinks`:

1. Copy individual roots into combined root first.
2. Update consumers/importers to combined root.
3. Monitor and validate.
4. Move or archive old roots after confirmation.

### Playbook H: Recovery from bad apply

If an apply run produced unwanted results:

1. Use the apply-time backup manifest (or latest snapshot manifest).
2. Run restore with `dry_run: true`.
3. If output looks correct, run apply restore.
4. Re-run targeted repair only if needed.

---

## Safe operating checklist

Before apply runs:

1. Verify service and root scope (avoid broad accidental rewrites)
2. Run dry-run first
3. Confirm backup manifest path/auto-backup
4. Apply with confirmation
5. Validate sampled symlinks + Arr/media-server visibility

For large migrations:

1. Snapshot backup first
2. Prefer copy mode for staged cutovers
3. Validate import behavior
4. Switch consumers to new root
5. Cleanup old root once stable

---

## Do Arr apps need updates after symlink changes?

Short answer: sometimes.

Use this quick map:

- Prefix rewrite only (targets changed, symlink root stayed the same):
    - Arr changes usually: **No**
    - Why: Arr still sees the same symlink path; only the underlying target changed.

- Root migration/copy to a new symlink tree that Arr will now use:
    - Arr changes usually: **Yes**
    - Why: Arr import/root assumptions may still point at old paths.

- Clone CLI Debrid symlinks into Decypharr tree for import seeding:
    - Arr changes usually: **Yes (at least one-time import/discovery)**
    - Why: Arr did not create these symlinks, so they are usually unknown to Arr until Manual Import (or equivalent discovery/import action).

- Move from individual roots to `combined_symlinks` as primary workflow:
    - Arr changes usually: **Yes**
    - Why: completed import source path and/or related path mappings often need to align with combined layout.

- Snapshot backup/restore only:
    - Arr changes usually: **No**
    - Why: this restores symlink state, not Arr configuration.

### What to update in Arr when required

When you switch Arr-facing paths, review these in each Arr instance:

1. Download/import source path assumptions
    - Ensure the path Arr receives from the download workflow is still valid after migration.

2. Remote Path Mappings (when Arr sees different paths than DUMB)
    - If Arr runs in a different container/host namespace, update mappings so Arr can translate source paths.

3. Root folders (managed library destination)
    - If your managed destination path changed, update Arr Root Folders for future imports.

4. Manual Import source path (for seeding workflows)
    - For one-time seeding, point Manual Import at the copied destination tree (for example `/mnt/debrid/decypharr_symlinks`).

5. Validation
    - Run one test import after migration.
    - Confirm no path mismatch warnings in Arr logs.
    - Confirm media server paths still resolve.

### Practical examples

- Example A: `retarget_clid_mount_to_decypharr`
    - Arr update: **Yes (usually one-time Manual Import/discovery for existing items)**
    - Reason: even if symlink paths are valid, Arr often has no item records for symlinks it did not create.

- Example B: `copy_clid_to_decypharr`
    - Arr update: **Yes (one-time Manual Import/discovery)**
    - Arr update: **Yes** for ongoing workflow switches if path assumptions/mappings also change.

- Example C: `move_individual_to_combined`
    - Arr update: usually **Yes**
    - Update source-path assumptions and any remote path mappings.

---

## Troubleshooting

### Symptom: Restore/repair shows no changes

Check:

- Selected roots actually contain symlinks
- Prefix/preset matches existing target strings exactly
- You are not accidentally scoped to the wrong service root

### Symptom: CLI -> Decypharr migration succeeds but Arr import still misses items

Check:

- Arr download/import root actually points at the destination symlink tree.
- Relative directory depth expected by Arr matches copied/moved tree.
- Source links were copied (not moved) if you still depend on CLI tree.

### Symptom: Prefix rewrite changed fewer links than expected

Check:

- `from_prefix` includes trailing slash behavior exactly as stored in symlinks.
- Some links may point to mixed provider layouts; run additional rewrite passes if needed.
- Include-broken setting may be excluding currently broken links.

### Symptom: Media server sees broken links

Check:

- Target paths exist in the same namespace the media server uses
- Host/container bind mounts preserve expected absolute paths
- Symlink targets resolve from the media server runtime context

### Symptom: Scheduled backups not appearing

Check:

- `symlink_backup_enabled` is true
- Path template includes writable destination
- Schedule status endpoint reports next/last run
- Manifest list endpoint pattern matches your template

### Symptom: Snapshot restore says manifest missing even though file exists

Check:

- Snapshot `Manifest path` dropdown currently selected a real file and not `Custom path` with stale text.
- Path exists inside the container namespace (not host-only path).
- File permissions allow DUMB process user to read manifest.

---

## API references

- [Process Management API](../api/process.md)
  - `/process/symlink-repair`
  - `/process/symlink-manifest/backup`
  - `/process/symlink-manifest/backup-async`
  - `/process/symlink-job-status`
  - `/process/symlink-job-latest`
  - `/process/symlink-manifest/restore`
  - `/process/symlink-manifest/restore-async`
  - `/process/symlink-manifest-files`
  - `/process/symlink-backup-status`
  - `/process/symlink-backup-manifests`
  - `/process/symlink-backup/reschedule`

Related service pages:

- [Decypharr](../services/core/decypharr.md)
- [CLI Debrid](../services/core/cli-debrid.md)
- [NzbDAV](../services/core/nzbdav.md)
- [Riven Backend](../services/core/riven-backend.md)

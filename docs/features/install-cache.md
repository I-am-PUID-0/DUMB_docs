---
title: Install Cache and Safe Updates
description: Understand DUMB's verified dependency and build caches, transactional service updates, automatic rollback, cache maintenance, and clean rebuild recovery.
icon: lucide/package-check
---

# Install cache and safe updates

DUMB keeps reproducible downloads, package-manager data, and selected compiled
service artifacts under `/config/.cache/dumb`. The cache accelerates container
startup, updates, and exact-source reinstalls without treating a cached file as
trusted merely because it already exists.

Service configuration, databases, media, symlinks, credentials, and active
runtime directories are not cache entries.

Destructive update clears are built from guarded exclusions rather than trusting
only the saved `exclude_dirs` list. DUMB automatically preserves an in-tree
service config file, explicit config/data/database paths, conventional persistent
data/database directories, root-level SQLite files and their active sidecars,
and symlinked data directories. The guarded paths are also excluded from archive
merges, while replaceable source and runtime output can still be refreshed.

## Safety model

An external project can always fail to download or build. DUMB's goal is to
make that failure non-destructive:

1. Resolve the requested release, branch head, or exact commit.
2. Download into a content-addressed cache and verify its SHA-256 digest.
   Conditional requests reuse unchanged content, and a failed revalidation may
   use the last digest-verified object for that exact URL.
3. Validate the complete archive before applying files. Unsafe paths, links,
   malformed archives, extraction errors, and configured size limits fail the
   installation.
4. Build and verify the replacement runtime.
5. Stop the old process only when the replacement is ready where the service
   layout supports candidate activation.
6. Start the replacement and require it to remain healthy for the configured
   stabilization period.
7. Restore the previous runtime automatically if activation or health
   stabilization fails.

Traefik Proxy Admin uses full same-filesystem candidate activation. Other
source-built services retain a rollback snapshot of replaceable runtime files
while their persistent paths stay in place. Services whose package manager or
database owns the upgrade transaction keep their existing service-specific
recovery behavior.

!!! warning "Application database migrations"

    A runtime rollback cannot safely undo every application-owned database
    migration. DUMB never replaces persistent data with a cached copy. If an
    upstream migration is not backward compatible, leave the restored service
    stopped and follow that application's documented database recovery path.

## Configuration

```json
{
  "dumb": {
    "install_cache": {
      "enabled": true,
      "path": "/config/.cache/dumb",
      "max_size_gib": 25,
      "artifact_retention_count": 2,
      "clean_retry": true,
      "max_download_size_mb": 4096,
      "max_archive_entries": 250000,
      "max_unpacked_size_gib": 50,
      "activation_health_timeout_seconds": 120,
      "activation_stabilization_seconds": 15
    }
  }
}
```

Keep the cache on persistent local storage when possible. It may reside on a
different filesystem from service runtimes, but transactional candidate
directories are always created beside their target so activation uses an
atomic same-filesystem rename. DUMB refuses broad system/data roots such as
`/`, `/config`, `/data`, and `/mnt` as the cache root and falls back to the
default cache directory.

The cache is owned by the DUMB controller rather than managed service users.
If the cache root or one of its managed namespaces is recursively `chown`ed,
DUMB validates the tree and restores controller ownership before the next
cache operation. The repair removes group/other write permission while
preserving executable bits required by cached runtimes. It does not follow
symlinks or cross a nested mount inside the cache tree.

If the configured cache is a symlink, has an unsupported file type, contains
an unexpected nested mount during ownership repair, or cannot be repaired due
to filesystem permissions, DUMB leaves active runtimes untouched and uses a
new controller-only cache under `/tmp` for the current process. The dashboard
shows this fallback and its reason. Correct the configured path or ownership
and restart DUMB to resume the persistent cache; the temporary fallback is not
reused after restart.

## Package-manager behavior

- pnpm uses a shared content-addressed store grouped by pnpm major, verifies
  store integrity, and attempts a frozen lockfile install first. A lockfile
  compatibility retry is allowed only after pnpm specifically reports a
  lockfile mismatch; it remains inside the rollback-protected install phase.
- Python services receive a clean virtual environment. pip and Poetry share
  download caches by Python ABI and architecture, and DUMB runs `pip check`
  before accepting the environment.
- NuGet packages are shared by architecture. Projects with
  `packages.lock.json` restore in locked mode; publish remains `--no-restore`.
- Go module and build caches are persistent and architecture-scoped.
- Bun, Yarn, and Deno retain persistent shared caches and use immutable/frozen
  lock behavior when their project supplies a lockfile.
- mediastorm OCI data remains digest-addressed and verified.

## Dashboard maintenance

Newer backends advertise `install_cache_management`. The dashboard **Updates**
panel then shows three distinct totals:

- **Managed cache** is the current `/config/.cache/dumb` tree and is the value
  governed by `max_size_gib`.
- **Legacy release caches** are exact DUMB-owned package-manager locations
  discovered from older releases.
- **Combined install cache** is the complete managed plus legacy disk usage.

The panel also shows current namespace sizes and actions to:

- save a managed-cache limit from 1 through 1024 GiB when the backend advertises
  `install_cache_limit_settings`;
- verify downloaded objects and quarantine corrupt entries;
- prune least-recently-used entries down to the configured limit; and
- clear compiled artifacts so the next reinstall performs a clean build.

Backends that additionally advertise `install_cache_cleanup` expose a
user-directed cleanup selector. It can remove only legacy caches, quarantine,
compiled artifacts, verified downloads, dependency caches, or all rebuildable
cache. Every scope requires confirmation. DUMB accepts named scopes rather
than filesystem paths, re-discovers legacy entries immediately before
deletion, and refuses symlinked, mounted, or moved paths. Maintenance returns
HTTP 409 until startup completes and while DUMB's service-update lock is active.

Saving the limit persists `dumb.install_cache.max_size_gib`. It does not delete
anything immediately. Select **Prune to limit** when you want DUMB to reclaim
least-recently-used rebuildable cache entries down to the new target. This split
prevents an accidental number change from immediately removing a warm cache.

Legacy discovery covers the old per-project pnpm/Bun buckets, Maintainerr Yarn
cache, Profilarr Deno cache, and DUMB-created per-service pip, Poetry, and NuGet
package caches. It does not classify generic application cache directories as
install cache, and it preserves the current Traefik Proxy Admin runtime data
that still intentionally lives below `/config/.pnpm-store`.

The frontend hides the entire section for APIs without
`install_cache_management` and independently hides scoped cleanup unless
`install_cache_cleanup=true`. The editable limit is independently gated by
`install_cache_limit_settings=true`, so a newer frontend does not submit the
new nested config field to an older backend schema.

Pruning and clearing artifacts never stop services or remove active runtimes.
Cleaning downloads or dependency caches makes later installs slower until the
cache warms again. DUMB serializes these actions against managed updates, but
operators should still avoid cleanup while another install path is actively
building.
Do not manually delete transaction journals or `dumb-previous` directories
while an update is active.

## Recovery guidance

If an update reports that the previous runtime was restored:

1. Confirm that the service is running and inspect its service log.
2. Open **Updates → Install cache** and run **Verify downloads**.
3. Use **Clear build artifacts** if the failure points to missing or invalid
   compiled output.
4. Retry the update. DUMB will reuse valid dependency downloads but rebuild the
   service runtime.
5. If rollback itself failed, do not repeatedly update. Preserve the service
   directory and logs, then restore the application's data from its normal
   backup process.

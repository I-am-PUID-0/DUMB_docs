---
title: InfiniDysk installation and updates
description: Choose InfiniDysk release tags or source pins and understand verified archives, rolling release channels, source fallback, and update recovery.
icon: lucide/cloud
---

# InfiniDysk installation and updates

[Back to InfiniDysk setup](infinidysk.md).

## Tracking a moving InfiniDysk release tag

InfiniDysk tags do not need a matching GitHub Release. To track a tag such as
`dev`, enable the release selector and use the tag name:

```json
{
"infinidysk": {
    "release_version_enabled": true,
    "release_version": "dev",
    "commit_sha": "",
    "branch_enabled": false,
    "auto_update": true
}
}
```

DUMB treats any digit-free InfiniDysk tag, such as `dev`, `lts`, or `edge`, as a
moving release channel. With `auto_update: true`, DUMB checks it at the normal
configured interval and installs it when the underlying commit changes. Manual
**Check for updates** and **Install update** remain available.

With `auto_update: false`, startup validates and keeps an already installed
runtime even when the moving tag now points at another commit. DUMB does not
turn a container restart into an implicit channel update. Use the Updates panel
to install the newly resolved commit deliberately. If the installed backend or
frontend runtime is incomplete, startup still attempts the configured channel
so a broken or missing installation can recover.

The installed marker is recorded as `dev-<short-sha>`. The source archive is
downloaded by the resolved full SHA, so the installed source and recorded
marker remain consistent even if the tag moves during the update.

## Prebuilt archives and automatic source fallback

For InfiniDysk release selectors, DUMB first looks for the official
architecture-specific `linux-x64` or `linux-arm64` release archive. It requires
GitHub's published SHA-256 digest, resolves the selected tag to its full commit,
requires the release asset's target commit to still match that tag, validates
the complete backend and frontend runtime, and activates them as one
rollback-safe unit. DUMB selects the exact channel asset deterministically and
accepts only InfiniDysk or legacy NzbDAV archive roots for the selected CPU architecture.
This handles renamed rolling assets such as `rc`, whose downloaded archive can
keep the concrete RC version in its internal root directory.

If a selected tag has no GitHub Release object, has no compatible archive, or
has release assets that lag behind a moved channel tag, DUMB automatically
downloads the current resolved commit and uses its source-build path. The same
fallback applies when archive verification fails. This keeps the service
installable while making the fallback reproducible. Open the service page's
**Updates** panel to see **Installed using**, the resolved release, the selected
archive when applicable, and the prebuilt fallback reason.

The practical channel behavior is:

| Selector | DUMB behavior |
| --- | --- |
| `latest` | Resolve the current stable GitHub Release, then use its verified archive or source fallback |
| `prerelease` | For the official InfiniDysk repository, follow the `rc` channel so a newer `dev` snapshot cannot be mistaken for an RC; then use its verified archive or source fallback |
| `dev`, `rc`, `lts`, `edge` | Track the exact digit-free tag when it exists; use a matching verified release archive when published, otherwise build that tag's resolved commit |
| Versioned/dated tag | Treat it as a fixed configured release; use its verified archive when published, otherwise build its resolved commit |
| Full `commit_sha` or branch | Source build by design |

!!! note "Why DUMB does not unpack the Docker image"

    The official InfiniDysk container is Alpine/musl-based, while DUMB's
    runtime and managed packages are Ubuntu/glibc-based. Extracting application
    files from that image would also pull a runtime layout and native libraries
    built for a different libc boundary. The official Ubuntu-built release
    archives are the compatible prebuilt format for DUMB; source fallback is
    the compatibility path when no usable archive exists.

After a prebuilt install, DUMB starts the archive's framework-dependent native
apphost against DUMB's compatible .NET runtime, even if a local .NET SDK remains
from an older source build. Source installs continue to launch through the
managed local SDK and application DLL.

The same revision suffix remains visible for the rolling **prerelease** channel
and for branch, exact-commit, or other moving-tag installs. Ordinary stable
release versions are shown in the frontend as their clean release tag (for
example, `v0.10.0`); DUMB retains the resolved commit internally for download,
cache, and source-integrity checks rather than presenting it as part of the
stable version.

When the selected tag also has an architecture-specific InfiniDysk release archive,
DUMB tries that archive first. The rolling `rc` GitHub Release is therefore a
valid moving channel: DUMB resolves its current commit and asset digest before
installing it. Branch and exact-commit selections remain source builds.

DUMB accepts the current `infinidysk-<version>-linux-<arch>.tar.gz` release
artifact and the former `nzbdav-<version>-linux-<arch>.tar.gz` name. The selected
asset must include a published SHA-256 digest, and its archive root must match
the asset name. When both names are published for one release, DUMB prefers the
name matching the configured repository. A renamed official artifact therefore
uses the verified prebuilt path instead of silently falling back to a source
build.

Existing installations whose marker is only `dev` perform one update to adopt
the commit-aware marker. Tags containing any digit, such as `v0.9.5`,
`2026.08.03`, or `dev2`, remain pinned configured releases and do not enable
scheduled automatic updates. Use **Install configured release** to apply those
tags intentionally.

## Pinning an exact InfiniDysk commit

Set `commit_sha` to the complete SHA from the configured `repo_owner` and
`repo_name`:

```json
{
"infinidysk": {
    "repo_owner": "infinidysk",
    "repo_name": "infinidysk",
    "commit_sha": "0123456789abcdef0123456789abcdef01234567"
}
}
```

The commit pin overrides `release_version_enabled` and `branch_enabled`.
Automatic updates stay disabled while the pin is present. Change the SHA to
move deliberately to another revision, or clear it to return to the configured
release/branch strategy.

After saving a new SHA, open **Updates** and select **Install configured
commit**. This installs and restarts InfiniDysk on the saved commit. Do not use
**Override + latest** for this operation; that action intentionally installs the
latest moving release while leaving the saved pin in place for a later restart.

## Source-build update safety

Branch and exact-commit updates publish the .NET backend into a clean candidate
directory, validate the complete runtime, and then replace the installed backend
as one unit. This prevents assemblies removed or upgraded upstream from remaining
in `/infinidysk/app` and being loaded alongside the new build.

After upgrading from an older DUMB version, an existing branch or commit install
may rebuild once even when its Git revision has not changed. That one-time rebuild
records the current source-build format and replaces any legacy overlaid output.
Do not manually delete `/infinidysk/app` or enable `clear_on_update` for this recovery;
use **Install configured release/branch/commit** and let DUMB preserve the previous
backend until the replacement candidate passes validation.

`clear_on_update` applies only to replaceable source and runtime files. Before
any clear or archive merge, DUMB automatically carries forward configured
exclusions, an in-tree `config_file`, explicit config/data/database path fields,
conventional `data`/`db` directories, root-level SQLite databases and active
WAL/SHM/journal sidecars, and symlinked persistent data directories. This guard
also applies when an older saved configuration omitted those paths from
`exclude_dirs`.

Keep normal backups of application databases and configuration. The update guard
prevents DUMB's installer from intentionally clearing those files; it is not a
replacement for backups or application-native database recovery.

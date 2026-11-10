---
title: Audiobookshelf
description: Run Audiobookshelf in DUMB for audiobook, ebook, and podcast libraries with persistent storage, first-run accounts, media mounts, and updates.
icon: lucide/book-open
---

# Audiobookshelf

[Audiobookshelf](https://www.audiobookshelf.org/) serves audiobook and podcast libraries, tracks listening progress, and provides basic ebook reading. DUMB runs it inside the DUMB container as an optional managed service.

DUMB handles installation, updates, process control, and web access. Add existing book files through your media mounts and configure libraries in Audiobookshelf. Book acquisition and download-client integration remain separate workflows; podcast subscriptions and episode downloads are configured in Audiobookshelf.

## Setup checklist and remaining work

The checklist can guide demonstrably fresh root-account setup and explicit library creation/reuse. Initialized servers remain preserved. Choose audiobook/podcast paths and user access, then test scans and actual playback. Readiness is not a library/playback test.

Requires the backend setup-arrangement capability. See [Setup checklist and automation](../../features/setup-checklist.md) for retained tasks, coverage and safe retries.


## Runtime requirements

The managed installation supports Linux amd64 and arm64 and uses Node.js 24 and FFmpeg from the DUMB image. Update the DUMB image before enabling Audiobookshelf if an older image lacks these runtimes.

## Enable Audiobookshelf

Select **Audiobookshelf** in the **Optional Services** onboarding step. For an existing installation, open its service page, enable it in **DUMB Config**, save, and start it.

The relevant defaults are:

```json
"audiobookshelf": {
  "enabled": false,
  "process_name": "Audiobookshelf",
  "repo_owner": "advplyr",
  "repo_name": "audiobookshelf",
  "release_version_enabled": false,
  "release_version": "latest",
  "commit_sha": "",
  "branch_enabled": false,
  "branch": "master",
  "auto_update": false,
  "auto_update_interval": 24,
  "auto_update_start_time": "04:00",
  "port": 13378,
  "runtime_dir": "/opt/audiobookshelf",
  "config_dir": "/audiobookshelf/config",
  "metadata_dir": "/audiobookshelf/metadata"
}
```

| Setting | Purpose |
| ------- | ------- |
| `port` | Listener port; use the actual assigned port shown in DUMB |
| `runtime_dir` | Managed application files, separate from persistent state |
| `config_dir` | SQLite database, accounts, libraries, settings, and progress |
| `metadata_dir` | Metadata, images, cache, streams, logs, and backups |
| `release_version_enabled` / `release_version` | Select an official published release, using `latest` or an exact tag |
| `branch_enabled` / `branch` | Build the selected official source branch, defaulting to `master` |
| `commit_sha` | Pin an exact full 40-character source commit; overrides branch and release selection |
| `auto_update` | Enable scheduled release updates; branch and commit selections disable automatic updates |

Use `config_dir` and `metadata_dir` to choose the persistent data paths. Library folders are selected separately in Audiobookshelf.

## Persistent storage and media mounts

With DUMB's normal `/data` volume, `/audiobookshelf` maps to `/data/audiobookshelf`. The default database and metadata therefore persist under `/data/audiobookshelf/config` and `/data/audiobookshelf/metadata`. Keep both directories when upgrading or replacing the container. Application files in `/opt/audiobookshelf` are managed separately.

Keep the SQLite configuration directory on local storage. Audiobookshelf's [storage requirements](https://audiobookshelf.org/docs/documentation/install/docker/#docker-compose) exclude network-backed configuration databases. If your `/data` volume uses NFS or SMB, mount a local directory separately, for example at `/audiobookshelf-config`, and set `config_dir` to that path.

Add your media folders to the existing DUMB Compose service. For example:

```yaml
services:
  DUMB:
    volumes:
      - ./data:/data
      - /srv/media/audiobooks:/audiobooks:ro
      - /srv/media/ebooks:/ebooks:ro
      - /srv/media/podcasts:/podcasts
```

Adjust the host paths to your folders. Inside Audiobookshelf, select the container paths `/audiobooks`, `/ebooks`, or `/podcasts`, rather than their host paths.

The managed service uses DUMB's configured `puid` and `pgid`. It needs read access to book folders and write access to a podcast folder when downloading episodes. The read-only book examples support scanning and playback; tools that modify source files need a writable mount.

## First-time setup

1. Start Audiobookshelf and open its UI from the DUMB service page.
2. Complete **Initial Server Setup** to create its root administrator account and password. The displayed config and metadata paths should match your DUMB configuration.
3. Sign in with that Audiobookshelf account.
4. Add a book or podcast library and choose one or more mounted container folders.
5. Scan the library and review the identified items before listening or reading.

The account created here is used by Audiobookshelf's web and mobile clients. See the [upstream initialization API](https://api.audiobookshelf.org/#initialize-the-server) for the corresponding first-run setup contract.

For direct access, publish the assigned port on the DUMB container and open:

```text
http://<dumb-host>:13378/audiobookshelf/
```

DUMB uses Audiobookshelf's standard `/audiobookshelf/` application path. Reverse proxies must preserve that path and support WebSocket connections. See [service ports](../../reference/ports.md) for port publishing and [upstream reverse proxy guidance](https://audiobookshelf.org/docs/category/reverse-proxy/).

## Organize books and podcasts

For books made of multiple files, keep each book in its own folder. A simple layout is:

```text
/audiobooks/Example Author/Example Book/01.mp3
/audiobooks/Example Author/Example Book/02.mp3
/ebooks/Example Author/Example Book/Example Book.epub
```

Audiobook and ebook files can also share the same book folder. Follow the [book directory structure guide](https://audiobookshelf.org/docs/documentation/libraries/book-library/directory-structure/) to keep separate titles from being grouped together.

Ebook support is basic. Supported formats include EPUB, PDF, CBR, CBZ, AZW3, and MOBI; AZW3 and MOBI do not track reading progress. See [Audiobookshelf's ebook guide](https://audiobookshelf.org/docs/documentation/libraries/book-library/ebooks/) for primary and supplementary ebooks.

Create podcast libraries and subscriptions in Audiobookshelf. Its own podcast controls can fetch episodes into a writable library folder. See [podcast libraries](https://audiobookshelf.org/docs/category/podcast-library/).

## Updates and backups

DUMB builds Audiobookshelf from its official source repository. It stages the server and web client together, uses the selected source's npm lockfiles, and checks the candidate runtime before replacing the installed application.

### Published releases

The default follows the latest official release. To select an exact release, set `release_version_enabled: true` and enter its official tag in `release_version`. Clear `commit_sha` and turn off `branch_enabled` when returning to release builds. Set `auto_update` to enable scheduled updates while following the latest release. Exact release pins disable automatic updates; use **Install configured release** to apply that saved tag.

### Branches and source commits

To use a branch, save these source settings in Audiobookshelf's **DUMB Config**:

```json
"release_version_enabled": false,
"commit_sha": "",
"branch_enabled": true,
"branch": "master"
```

Select **Check for updates**, then **Install configured branch** to build the selected branch head. The branch is resolved to an exact commit before building; the installed version includes its branch name and shortened commit SHA. A branch can change without changing Audiobookshelf's package version, so update checks compare the source commit.

To pin an exact revision, set `commit_sha` to its full 40-character hexadecimal GitHub commit SHA, save, and select **Install configured commit**. This selection takes precedence over the branch and release fields. Clear it before following a branch or release again.

DUMB disables scheduled automatic updates while a branch or commit is selected. Use the manual update controls to advance a branch or select another commit. A normal restart can reuse the installed build for the same branch; it does not require fetching the branch head on every start.

### Backups and recovery

Stop Audiobookshelf before copying its SQLite configuration directory, or use a SQLite-consistent backup method. Back up the configuration database, metadata, DUMB configuration, and your media separately. The application runtime is disposable; replacing it does not replace the libraries you mounted or the persistent state directories. Keep library paths stable so the saved configuration continues to locate your files.

Audiobookshelf may migrate its database after an application update. Switching to an older release, branch, or commit does not reverse those migrations; restore a compatible pre-update database backup when the older application cannot use the newer data.

DUMB's [Database Health Monitoring](../../features/metrics.md#database-health-monitoring) can observe `config_dir/absdatabase.sqlite` in Standard or Enhanced read-only mode. Enable both the global collector and monitoring for Audiobookshelf; this monitoring does not back up or repair the database.

[Reset / Remove](../../features/service-reset.md) follows DUMB's normal service controls. **Reset DUMB configuration** keeps application files and data while restoring disabled defaults. **Remove service files** lists the managed configuration, metadata, runtime, and log paths it can clear. Review that preview: custom paths outside managed roots, shared directories, and unrecognized runtimes are retained, along with media libraries and unrelated siblings under the persistent data root.

### Known upstream dependency audit

An integration check of Audiobookshelf **v2.37.1** using `npm audit --omit=dev` on **2026-10-14 (UTC)** reported **40 affected package entries** in its installed production dependency graph: **4 critical, 22 high, 6 moderate, and 8 low**. The graph includes transitive dependencies and native-build tools retained after pruning development dependencies. Runtime exploitability was not established for every reported entry.

DUMB builds the selected official release, branch, or commit with its upstream lockfiles and npm's package integrity checks, retaining upstream dependency versions. Proposed fixes for `axios`, `nodemailer`, and `sqlite3` include major-version changes that require separate compatibility work. This application audit is separate from the DUMB backend's Python dependency audit.

## Troubleshooting

DUMB captures the managed process log at `/log/audiobookshelf.log`; view it from the service page's logs. The native health endpoint is `http://127.0.0.1:13378/healthcheck` inside the DUMB container; replace `13378` with the saved service port if it changed.

### The library is empty or files are missing

Confirm that the folder exists inside the DUMB container, then use that container path in the library settings. Check permissions for DUMB's configured user and follow the supported book folder layout. Start a library scan after adding your files.

### The setup screen appears again after container replacement

Check that `config_dir` still points at the original persistent database directory and that the `/data` or custom local bind is present. An empty configuration directory starts a new Audiobookshelf server.

### Playback or live updates fail through a reverse proxy

Verify the proxy preserves `/audiobookshelf/` and allows WebSocket upgrades. Compare the result with direct access to the assigned service port.

### Search does not ignore accents

The optional nuSQLite search extension is not installed. Audiobookshelf uses its [standard SQLite search fallback](https://github.com/advplyr/audiobookshelf/blob/v2.37.1/server/Database.js#L985), so searches do not automatically remove accents. Include accents in your search when needed.

## Resources

- [Audiobookshelf documentation](https://audiobookshelf.org/docs/)
- [Official source and releases](https://github.com/advplyr/audiobookshelf)
- [Library overview](https://audiobookshelf.org/docs/documentation/libraries/common-content/overview/)

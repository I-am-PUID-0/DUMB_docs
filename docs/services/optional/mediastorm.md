---
title: MediaStorm
icon: lucide/clapperboard
---

# MediaStorm

MediaStorm is a self-hosted streaming server and client ecosystem for Debrid, torrent, and Usenet sources. DUMB installs its server, browser client, subtitle helpers, Deno runtime, and Iroh companion from MediaStorm's official OCI image, then runs it as an optional PostgreSQL-backed service.

---

## What DUMB manages

- MediaStorm listens on port `7777`.
- The embedded service UI opens the administrative interface at `/admin`.
- The browser player is available at `/watch`.
- DUMB automatically enables its managed PostgreSQL service and creates the `mediastorm` database.
- Account, watch-history, and playback data live in PostgreSQL. Settings and application cache persist under `/mediastorm`, which maps to DUMB's persistent `/data/mediastorm` service directory.
- DUMB downloads the correct `linux/amd64` or `linux/arm64` MediaStorm OCI runtime on first install and stores it under `/mediastorm/runtime`.
- OCI manifests and layers are SHA-256 verified, only MediaStorm's allowlisted runtime paths are extracted, and release selections must match the image's internal version before DUMB activates them.
- MediaStorm supports DUMB's manual and scheduled update checks. Branch installs are not supported because upstream's complete runtime is published as an OCI image rather than a reproducible GitHub source release.
- MediaStorm can follow `latest` or be pinned to a published OCI release tag, commit-specific OCI tag, or immutable OCI digest.

| Service | Default port | Embedded entry | Persistent state |
|---------|--------------|----------------|------------------|
| MediaStorm | 7777 | `/admin` | PostgreSQL plus `/mediastorm` |

---

## Configuration in `dumb_config.json`

```json
"mediastorm": {
  "enabled": false,
  "process_name": "MediaStorm",
  "repo_owner": "godver3",
  "repo_name": "mediastorm",
  "release_version_enabled": false,
  "release_version": "latest",
  "suppress_logging": false,
  "log_level": "INFO",
  "port": 7777,
  "auto_update": false,
  "auto_update_interval": 24,
  "auto_update_start_time": "04:00",
  "config_dir": "/mediastorm",
  "log_file": "/log/mediastorm.log",
  "wait_for_tcp": [
    {
      "name": "PostgreSQL",
      "host": "127.0.0.1",
      "port": 5432,
      "timeout": 2
    }
  ],
  "command": [
    "/mediastorm/runtime/mediastorm",
    "--port",
    "7777"
  ],
  "env": {
    "STRMR_CONFIG": "/mediastorm/settings.json",
    "STRMR_WEB_APP_DIR": "/mediastorm/runtime/web",
    "MEDIASTORM_IROH_DIRECT_DIR": "/mediastorm/runtime/iroh",
    "DATABASE_URL": ""
  }
}
```

DUMB fills `DATABASE_URL` from the managed PostgreSQL credentials during setup. Do not copy the generated credential-bearing value into documentation, screenshots, or support logs. The installer always uses the fixed official `godver3/mediastorm` repository and does not accept an arbitrary registry URL from service configuration.

### Version selection

Leave `release_version_enabled` set to `false` to follow `godver3/mediastorm:latest`. To install and retain a specific build, set it to `true` and choose one of these `release_version` forms:

| Selection | Example | Behavior |
|-----------|---------|----------|
| OCI release tag | `1.5.0` | Installs the published MediaStorm release tag and accepts its dated internal version. |
| GitHub release | `v1.5.0-20260711` | Resolves the matching dated or semantic OCI release tag and requires the exact internal version. |
| Full commit tag | `2e4fdf5f08146795d455604ec16233050b43465a` | Installs the OCI tag published for that full upstream commit. Use a digest when registry-level immutability is required. |
| OCI digest | `sha256:<64 lowercase hex characters>` | Installs the exact immutable image manifest. |

DUMB writes the selected value to `/mediastorm/runtime/install-selector.txt`, the resolved upstream tag to `oci-reference.txt`, and the verified manifest digest to `image-digest.txt`. On restart, it compares the selected value with the installed marker and reinstalls only when the selection changes.

Pinned releases, commits, and digests disable automatic updates through DUMB's standard pin behavior. Disable the pin to return to `latest`, or change `release_version` to perform an intentional upgrade or rollback. Branch names and arbitrary image tags are rejected.

---

## Initial setup

!!! warning "First login credentials"

    - **Username:** `admin`
    - **Password:** `admin`

    These are public upstream defaults. Change the password immediately after the first login and before exposing MediaStorm outside your trusted network.

1. Select **MediaStorm** under Optional Services during onboarding, or enable it from its DUMB service configuration.
2. Start MediaStorm. On first install, DUMB downloads and verifies the architecture-specific OCI layers, builds the local Python subtitle-helper environment, starts PostgreSQL, and waits for it before launching the service. The initial download is several hundred MiB.
3. Open the MediaStorm embedded UI. It starts at `/admin`.
4. Sign in with the first-login credentials shown above, then change the password under **Admin UI → Accounts → Change Password**.
5. Add TMDB and TVDB API keys in MediaStorm's admin settings. Media discovery will be incomplete until both are configured.
6. Configure the Debrid, torrent, or Usenet providers you intend to use.
7. Open `/watch` for the browser client, or point a supported MediaStorm mobile/TV client at the reachable DUMB host and MediaStorm port.

!!! warning "Secure the administrative interface"

    The initial credentials are public defaults, and `/admin` controls providers and users. Change the password before exposing MediaStorm beyond a trusted network. Prefer a VPN or a carefully tested authenticated reverse-proxy route; never publish the raw port with its default credentials.

---

## Backups and updates

Back up both parts of MediaStorm state:

- the DUMB-managed PostgreSQL `mediastorm` database; and
- the persistent `/mediastorm` directory, especially `settings.json` and cached application state. `/mediastorm/runtime` can be excluded when your backup process supports exclusions because DUMB can reinstall it.

When following `latest`, use **Check for updates** and **Install update** on the MediaStorm service page for one-time updates, or enable `auto_update` for scheduled checks. DUMB compares `/mediastorm/runtime/version.txt` with the latest GitHub release, downloads the official OCI runtime into a staging directory, verifies it, and atomically replaces the old runtime only after validation succeeds. A pin blocks normal update installation until you change/disable the pin or explicitly approve the frontend's override action. Before a major upgrade or rollback, preserve a matching database and settings/cache backup because application migrations can make rollback depend on restoring both together.

Database Health Monitoring can observe the MediaStorm PostgreSQL database in Standard or Enhanced read-only mode when monitoring is explicitly enabled for the service.

---

## Embedded UI and direct access

MediaStorm uses root-relative routes for `/admin`, `/watch`, accounts, sharing, and `/api/*`. The DUMB Frontend keeps those requests attached to the active MediaStorm iframe so they do not collide with DUMB's own routes.

For troubleshooting, direct access is `http://<host>:7777` when you publish that port. DUMB's embedded UI does not require the port to be published separately.

---

## Troubleshooting

- **Service waits or exits at startup:** Check PostgreSQL status first, then inspect the MediaStorm service log. DUMB creates the database and connection URL during setup.
- **Install fails during an OCI layer download:** Confirm the DUMB container can reach Docker Hub and has enough free space for the compressed image plus the staged runtime. Retrying the start repeats the verified install.
- **OCI version mismatch:** Upstream's `latest` image does not yet match its latest GitHub release. DUMB preserves the existing runtime and refuses to activate the mismatched image; retry after upstream finishes publishing.
- **Pinned version cannot be resolved:** Confirm the value is a published MediaStorm release tag, full 40-character commit tag, or complete `sha256:` digest. Short commit hashes and branch names are intentionally rejected.
- **Discovery is empty or metadata is missing:** Verify both TMDB and TVDB keys in `/admin`.
- **An embedded link opens the DUMB page instead:** Refresh the MediaStorm service page to renew iframe context, then retry. Report the exact MediaStorm path that escaped the iframe.
- **A client cannot connect:** Use an address reachable from that device, confirm port `7777` is exposed or reverse proxied, and do not use `127.0.0.1` from another device.
- **Remote invitation fails:** Check the MediaStorm log for Iroh errors and confirm outbound networking is available from the DUMB container.

---

## Related links

- [MediaStorm repository](https://github.com/godver3/mediastorm)
- [MediaStorm releases](https://github.com/godver3/mediastorm/releases)
- [PostgreSQL](../dependent/postgres.md)
- [Embedded service UIs](../../features/embedded-ui.md)

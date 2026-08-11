---
title: mediastorm
description: Configure mediastorm in DUMB for PostgreSQL-backed Debrid, torrent, and Usenet streaming with verified OCI updates and embedded client access.
icon: lucide/clapperboard
---

# mediastorm

mediastorm is a self-hosted streaming server and client ecosystem for Debrid, torrent, and Usenet sources. DUMB installs its server, browser client, subtitle helpers, Deno runtime, and Iroh companion from mediastorm's official OCI image, then runs it as an optional PostgreSQL-backed service.

---

## What DUMB manages

- mediastorm listens on port `7777`.
- The embedded service UI opens the administrative interface at `/admin`.
- The browser player is available at `/watch`.
- DUMB automatically enables its managed PostgreSQL service and creates the `mediastorm` database.
- Account, watch-history, and playback data live in PostgreSQL. Settings and application cache persist under `/mediastorm`, which maps to DUMB's persistent `/data/mediastorm` service directory.
- DUMB downloads the correct `linux/amd64` or `linux/arm64` mediastorm OCI runtime on first install and stores it under `/mediastorm/runtime`.
- OCI manifests and layers are SHA-256 verified, only mediastorm's allowlisted runtime paths are extracted, and the image must contain a valid internal version before DUMB activates it. Explicit dated release pins must also match that internal version exactly.
- mediastorm supports DUMB's manual and scheduled update checks. Branch installs are not supported because upstream's complete runtime is published as an OCI image rather than a reproducible GitHub source release.
- mediastorm can follow `latest` or be pinned to a published OCI release tag, commit-specific OCI tag, or immutable OCI digest.

| Service | Default port | Embedded entry | Persistent state |
|---------|--------------|----------------|------------------|
| mediastorm | 7777 | `/admin` | PostgreSQL plus `/mediastorm` |

---

## Configuration in `dumb_config.json`

```json
"mediastorm": {
  "enabled": false,
  "process_name": "mediastorm",
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
    "DATABASE_URL": "",
    "PATH": "/mediastorm/runtime/python-venv/bin:/mediastorm/runtime/bin:/usr/local/go/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    "LIBGL_ALWAYS_SOFTWARE": "1",
    "VK_ICD_FILENAMES": "/usr/share/vulkan/icd.d/lavapipe_icd.json"
  }
}
```

DUMB fills `DATABASE_URL` from the managed PostgreSQL credentials during setup. Do not copy the generated credential-bearing value into documentation, screenshots, or support logs. The installer always uses the fixed official `godver3/mediastorm` repository and does not accept an arbitrary registry URL from service configuration.

### Version selection

Leave `release_version_enabled` set to `false` to follow `godver3/mediastorm:latest`. To install and retain a specific build, set it to `true` and choose one of these `release_version` forms:

| Selection | Example | Behavior |
|-----------|---------|----------|
| OCI release tag | `1.5.0` | Installs the published mediastorm release tag and accepts its dated internal version. |
| GitHub release | `v1.5.0-20260711` | Resolves the GitHub tag to its immutable full-commit OCI tag when upstream did not publish a matching dated OCI tag, then requires the exact internal version. |
| Full commit tag | `2e4fdf5f08146795d455604ec16233050b43465a` | Installs the OCI tag published for that full upstream commit. Use a digest when registry-level immutability is required. |
| OCI digest | `sha256:<64 lowercase hex characters>` | Installs the exact immutable image manifest. |

DUMB writes the selected value to `/mediastorm/runtime/install-selector.txt`, the resolved upstream tag to `oci-reference.txt`, and the verified manifest digest to `image-digest.txt`. Update checks resolve the selected OCI manifest and compare its digest with the installed digest. This detects a moved `latest` or pinned OCI tag even when its name and mediastorm's GitHub release metadata have not changed.

Pinned releases, commits, and digests disable automatic updates through DUMB's standard pin behavior. Disable the pin to return to `latest`, or change `release_version` to perform an intentional upgrade or rollback. Branch names and arbitrary image tags are rejected.

---

## Initial setup

!!! warning "First login credentials"

    - **Username:** `admin`
    - **Password:** `admin` on current mediastorm builds

    This is a public bootstrap credential. Current mediastorm builds require the first-login form
    to include a new password and confirmation; the default is replaced atomically before the
    first admin session is created. This flow works through Docker and reverse proxies.

    mediastorm writes the active first-login password to its protected bootstrap credential file.
    DUMB displays that value on the mediastorm service page while the file exists, which keeps
    pinned builds and installations using `STRMR_INITIAL_ADMIN_PASSWORD` compatible. mediastorm
    deletes the file after the password changes, and the DUMB warning then disappears automatically.
    DUMB recognizes both `initial_admin_password.txt` and the current extensionless
    `initial_admin_password` filename.

1. Select **mediastorm** under Optional Services during onboarding, or enable it from its DUMB service configuration.
2. Start mediastorm. On first install, DUMB downloads and verifies the architecture-specific OCI layers, builds the local Python subtitle-helper environment, starts PostgreSQL, and waits for it before launching the service. The initial download is several hundred MiB.
3. Open the mediastorm embedded UI. It starts at `/admin`.
4. Sign in as `admin` with the password shown on the DUMB service page. For current builds this is `admin`; enter and confirm a replacement password in the additional first-login fields. Pinned builds without those fields should be changed immediately under **Admin UI → Accounts → Change Password**.
5. Add TMDB and TVDB API keys in mediastorm's admin settings. Media discovery will be incomplete until both are configured.
6. Configure the Debrid, torrent, or Usenet providers you intend to use.
7. Open `/watch` for the browser client, or point a supported mediastorm mobile/TV client at the reachable DUMB host and mediastorm port.

!!! warning "Secure the administrative interface"

    The `admin` / `admin` bootstrap is publicly known, and `/admin` controls providers and users.
    Change it before exposing mediastorm beyond a trusted network. Do not copy a customized
    first-login password into logs, screenshots, or support bundles. Prefer a VPN or a carefully
    tested authenticated reverse-proxy route; never publish the raw port before completing
    first-login setup.

---

## Backups and updates

Back up both parts of mediastorm state:

- the DUMB-managed PostgreSQL `mediastorm` database; and
- the persistent `/mediastorm` directory, especially `settings.json` and cached application state. `/mediastorm/runtime` can be excluded when your backup process supports exclusions because DUMB can reinstall it.

Before first-login setup is complete, backups of the cache may contain
`initial_admin_password.txt` or `initial_admin_password`. Treat that backup as credential-bearing
data, especially when an installation-specific password is configured. The live bootstrap file is
removed by mediastorm after the admin password changes.

When following `latest`, use **Check for updates** and **Install update** on the mediastorm service page for one-time updates, or enable `auto_update` for scheduled checks. DUMB compares the installed manifest digest with `godver3/mediastorm:latest`, downloads the official OCI runtime into a staging directory, verifies its layers and internal version marker, and atomically replaces the old runtime only after validation succeeds. After restart, DUMB requires mediastorm's local `/health` endpoint to remain ready for the configured stabilization period before the update is recorded as successful and downtime is closed. GitHub release publication can lag behind the moving OCI image and does not block a valid `latest` update. A pin blocks normal update installation until you change/disable the pin or explicitly approve the frontend's override action. Before a major upgrade or rollback, preserve a matching database and settings/cache backup because application migrations can make rollback depend on restoring both together.

Database Health Monitoring can observe the mediastorm PostgreSQL database in Standard or Enhanced read-only mode when monitoring is explicitly enabled for the service.

---

## Embedded UI and direct access

mediastorm uses root-relative routes for `/admin`, `/watch`, accounts, sharing, and `/api/*`. The DUMB Frontend keeps those requests attached to the active mediastorm iframe so they do not collide with DUMB's own routes.

For troubleshooting, direct access is `http://<host>:7777` when you publish that port. DUMB's embedded UI does not require the port to be published separately.

---

## Troubleshooting

- **Service waits or exits at startup:** Check PostgreSQL status first, then inspect the mediastorm service log. DUMB creates the database and connection URL during setup.
- **First-login password is not shown:** Current builds use `admin` / `admin`. If the password was already replaced, the bootstrap file and DUMB warning are expected to be gone. Otherwise confirm mediastorm completed its first start and verify that `/data/mediastorm/cache/initial_admin_password` (or the `.txt` compatibility filename) is readable by the DUMB container.
- **`admin` / `admin` is rejected:** On current builds, entering only the public default is intentionally incomplete. Fill the **New admin password** and **Confirm new password** fields on the same login form. API clients receive HTTP `428` with code `password_change_required` and must resubmit the login with `newPassword`.
- **Onboarding asks for another password change:** Update mediastorm. Current onboarding recognizes that the password was already secured during first sign-in and leaves the second password change optional.
- **Install fails during an OCI layer download:** Confirm the DUMB container can reach Docker Hub and has enough free space for the compressed image plus the staged runtime. Retrying the start repeats the verified install.
- **OCI version mismatch for a pin:** The selected dated release expects an exact internal version. DUMB first tries a matching dated OCI tag, then the immutable full-commit OCI tag resolved from the official GitHub release, and uses the semantic OCI tag only as a compatibility fallback. If every available image contains another build, DUMB preserves the existing runtime. Confirm that the release and its commit-specific image still exist upstream, or return to the unpinned `latest` channel.
- **Pinned version cannot be resolved:** Confirm the value is a published mediastorm release tag, full 40-character commit tag, or complete `sha256:` digest. Short commit hashes and branch names are intentionally rejected.
- **Discovery is empty or metadata is missing:** Verify both TMDB and TVDB keys in `/admin`.
- **An embedded link opens the DUMB page instead:** Refresh the mediastorm service page to renew iframe context, then retry. Report the exact mediastorm path that escaped the iframe.
- **A client cannot connect:** Use an address reachable from that device, confirm port `7777` is exposed or reverse proxied, and do not use `127.0.0.1` from another device.
- **Remote invitation fails:** Check the mediastorm log for Iroh errors and confirm outbound networking is available from the DUMB container.

---

## Related links

- [mediastorm repository](https://github.com/godver3/mediastorm)
- [mediastorm releases](https://github.com/godver3/mediastorm/releases)
- [PostgreSQL](../dependent/postgres.md)
- [Embedded service UIs](../../features/embedded-ui.md)

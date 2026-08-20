---
title: AIOStreams
description: Deploy AIOStreams in DUMB, publish its Stremio endpoint over HTTPS, and connect Prowlarr, Zilean, InfiniDysk, or AltMount.
icon: lucide/clapperboard
---

# AIOStreams

AIOStreams combines Stremio addons, search sources, Debrid services, and Usenet playback services into one configurable Stremio addon. DUMB manages the AIOStreams runtime and lifecycle; you choose the addons, indexers, and playback services from the AIOStreams dashboard.

---

## What DUMB manages

| Property | DUMB default |
| --- | --- |
| Service key | `aiostreams` |
| Process name | `AIOStreams` |
| Port | `3006` |
| Configuration root | `/aiostreams` |
| Persistent data | `/aiostreams/data` |
| Extracted runtime | `/aiostreams/runtime` |
| Log | `/log/aiostreams.log` |
| Health endpoint | `/api/v1/health` |
| Database | SQLite at `./data/db.sqlite` |

DUMB downloads `ghcr.io/viren070/aiostreams` for the host architecture, verifies the selected OCI manifest and layers, and extracts the required runtime. Both `amd64` and `arm64` are supported. A separate Docker container, Docker socket, Node installation, and local source build are not required; DUMB supplies its managed Node 24 runtime.

DUMB can follow the latest stable image or install an exact stable tag. AIOStreams does not expose DUMB branch or commit-SHA source selection.

!!! note "Persistent paths"

    DUMB replaces `/aiostreams/runtime` during a successful update but preserves `/aiostreams/data`. The SQLite database, runtime settings, configuration records, and disk-backed caches therefore survive normal service updates.

---

## Before you enable it

Prepare the pieces that match your intended workflow:

- A stable public DNS name and trusted HTTPS route for remote Stremio clients, such as `https://aiostreams.example.com`.
- Enough persistent space for `/aiostreams/data`. AIOStreams can cache Usenet segments, grabbed NZBs, and torrent metadata there.
- API keys or login details for the search and playback services you intend to use.
- Outbound access from DUMB to GHCR for the first install and later updates.

You do **not** need every related DUMB service. For example, a Debrid-only setup can use AIOStreams without InfiniDysk or AltMount, while a Usenet setup can use either AIOStreams' native engine or one of those external playback services.

---

## Bootstrap settings versus dashboard settings

AIOStreams separates its configuration into two groups:

1. **Bootstrap settings** must exist before AIOStreams can open its database. DUMB supplies the port, database URI, base URL, dashboard administrator credentials, data paths, and encryption secret.
2. **Runtime settings** are stored in the AIOStreams database and should normally be edited from the AIOStreams dashboard.

DUMB intentionally avoids setting ordinary runtime options through environment variables. Upstream treats an environment-provided runtime value as operator-locked, which makes the corresponding dashboard field read-only.

The default DUMB service block is:

```json
"aiostreams": {
  "enabled": false,
  "process_name": "AIOStreams",
  "release_version_enabled": false,
  "release_version": "latest",
  "base_url": "http://localhost:3006",
  "auth_username": "admin",
  "auth_password": "",
  "secret_key": "",
  "database_uri": "sqlite://./data/db.sqlite",
  "suppress_logging": false,
  "log_level": "INFO",
  "port": 3006,
  "auto_update": false,
  "auto_update_mode": "install",
  "auto_update_interval": 24,
  "auto_update_start_time": "04:00",
  "command": [
    "node",
    "/aiostreams/runtime/packages/server/dist/server.js"
  ],
  "config_dir": "/aiostreams",
  "log_file": "/log/aiostreams.log",
  "env": {
    "NODE_ENV": "production",
    "LD_PRELOAD": "/aiostreams/runtime/lib/libmimalloc.so.2",
    "HOME": "/aiostreams/data",
    "XDG_CACHE_HOME": "/aiostreams/data/cache",
    "DISK_CACHE_DIR": "/aiostreams/data/cache",
    "SYSTEM_LIFECYCLE_ENABLED": "false"
  }
}
```

DUMB fills and persists `secret_key` when it is blank. The template `http://localhost:3006` base URL is local-only bootstrap behavior; setup keeps its port synchronized while the value remains default-like. Onboarding exposes `base_url`, `auth_username`, and `auth_password`; use the service configuration editor for the advanced `database_uri` override.

`release_version_enabled: false` follows the official stable `latest` OCI tag. When enabled, `release_version` accepts `latest` or an exact stable semantic tag such as `v2.33.2`; moving branches, arbitrary tags, and commit SHAs are rejected. DUMB injects `PORT`, `BASE_URL`, `INTERNAL_URL`, `SECRET_KEY`, `DATABASE_URI`, `AIOSTREAMS_AUTH`, and `AIOSTREAMS_AUTH_PERMISSIONS` from the top-level settings at setup time. Keep ordinary AIOStreams runtime preferences in its dashboard instead of duplicating them under `env`.

### `BASE_URL`

DUMB's `aiostreams.base_url` is the public base URL AIOStreams uses when it generates manifest, genre, and stream URLs.

- Local-only evaluation can use the generated local value.
- Remote Stremio use requires a stable, browser-reachable HTTPS base URL. A dedicated root hostname such as `https://aiostreams.example.com` is the normal and recommended deployment.
- Upstream-supported path-prefix deployments may use the configured public prefix when the reverse proxy routes it consistently.
- Do not use DUMB's embedded `/ui/aiostreams` address as `BASE_URL`.
- Do not append `/stremio/configure`, a query string, or a fragment to the base URL.

After changing `base_url`, restart AIOStreams and save/install the Stremio configuration again so its generated URLs use the new base URL.

### Dashboard administrator credentials

Set `auth_username` and `auth_password` during onboarding. The password must contain 12–256 characters and cannot contain commas or leading/trailing whitespace. DUMB maps this pair to AIOStreams' bootstrap authentication and grants the account the explicit `admin` permission, which includes Dashboard, configuration creation, Proxy, Service, and SABnzbd access.

The AIOStreams landing and Configure pages can remain public while the Dashboard requires this login. Enable AIOStreams' **Auth Required** runtime setting from the Dashboard if configuration creation should require authentication too.

Changing either top-level credential requires an AIOStreams restart. Advanced operators can leave `auth_password` blank and manage a multi-user `AIOSTREAMS_AUTH` plus `AIOSTREAMS_AUTH_PERMISSIONS` configuration directly under `aiostreams.env`; DUMB preserves that explicit environment configuration.

### `SECRET_KEY`

DUMB generates and persists a cryptographically random 64-character hexadecimal `SECRET_KEY`. AIOStreams uses it to encrypt stored configurations.

!!! danger "Never rotate or delete the generated secret"

    Changing `SECRET_KEY` after first use makes existing encrypted AIOStreams configurations unreadable. Include DUMB's runtime configuration in every AIOStreams backup, keep it private, and restore the same value during disaster recovery.

### Database selection

SQLite is the default and is appropriate for a normal single-instance DUMB deployment. Its effective database file is retained under `/aiostreams/data`.

PostgreSQL is an advanced first-deployment choice in the initial DUMB integration:

- DUMB does not expose an `aiostreams.postgres_enabled` toggle.
- DUMB does not create, migrate, rehearse, or roll back an AIOStreams PostgreSQL database.
- Provision the database and credentials first, then set a complete `aiostreams.database_uri`, for example `postgres://user:password@127.0.0.1:5432/aiostreams`.
- If credentials contain reserved URL characters, percent-encode them in the URI.

Choose the database before storing configurations. Pointing an existing SQLite installation at a blank PostgreSQL database starts with an empty AIOStreams store; it does not copy the SQLite data. AIOStreams applies its own schema migrations to whichever database it opens, but that is not a SQLite-to-PostgreSQL data migration.

See [PostgreSQL](../dependent/postgres.md) for database backup and restore guidance.

---

## First start

1. Enable AIOStreams during onboarding or from its service configuration.
2. Set the dashboard administrator username and a strong password.
3. Set `base_url` to the final public HTTPS base URL when remote Stremio clients will use the addon.
4. Start AIOStreams. The first install extracts and validates the official OCI runtime before launch.
5. Open the embedded service tab, select **Dashboard**, and sign in with the administrator credentials from step 2.
6. Configure the search addons and playback services you need.
7. Use **Save & Install** in AIOStreams and install the generated addon in Stremio.

Always use the port saved in DUMB's current service configuration. DUMB may move `3006` to another free port if an enabled service or host listener already uses it.

---

## Publish AIOStreams for Stremio

The embedded service tab is an operator convenience. A remote Stremio client must be able to reach the manifest and stream URLs generated from `BASE_URL` directly.

For a DUMB-managed reverse-proxy path:

1. Create a dedicated hostname in [Traefik Proxy Admin](traefik-proxy-admin.md), such as `aiostreams.example.com`.
2. Point it to `127.0.0.1` and AIOStreams' **saved** DUMB port, normally `3006`.
3. Provide trusted public HTTPS, either through Traefik's own certificate flow or [Cloudflared](cloudflared.md).
4. Set `aiostreams.base_url` to the exact public base URL and restart AIOStreams.
5. Open `https://aiostreams.example.com/stremio/configure`, save the configuration, and install it in Stremio.

When Cloudflare Tunnel terminates public TLS, leave TPA's **Certificate Resolver** blank for this route. Configure the tunnel origin as `https://localhost:18080` with **No TLS Verify** enabled, as described in the Cloudflared guide.

!!! warning "Do not put an interactive login in front of the whole addon host"

    Stremio fetches manifests, catalogs, and streams without completing a browser SSO or ForwardAuth redirect. A whole-host Authelia, TPA SSO, or Cloudflare Access challenge can therefore break the addon even when the configure page works in a browser.

    Use AIOStreams' own operator/configuration controls and treat an installed manifest URL as a bearer secret. Only use an external access layer when you have deliberately exempted every Stremio-facing route required by your configuration.

---

## Connect DUMB services

Use direct loopback URLs for services in the same DUMB container. Do not enter a DUMB embedded `/ui/<service>` URL. Because DUMB can resolve port conflicts dynamically, verify each service's saved port before copying the example.

### Prowlarr

Prowlarr can supply both torrent and Usenet search results to AIOStreams.

1. In Prowlarr, copy the API key from **Settings → General**.
2. In the AIOStreams dashboard, open the built-in Prowlarr settings.
3. Set the URL to `http://127.0.0.1:9696`, replacing `9696` with the saved Prowlarr instance port.
4. Enter the API key and select the indexers AIOStreams may query.
5. On `/stremio/configure`, add the built-in **Prowlarr** addon to the configuration and select compatible playback services.

Prowlarr redirects NZB grabs instead of proxying them. Review each indexer's rules if search and grab traffic can leave through different public IP addresses. Co-hosting Prowlarr, AIOStreams, and the Usenet playback service inside DUMB normally gives them the same outbound address, but network-level proxies can change that.

### Zilean

1. Enable and start DUMB's Zilean service.
2. In AIOStreams' built-in Zilean settings, use `http://127.0.0.1:8182`, replacing `8182` with the saved Zilean port.
3. Add the built-in **Zilean** addon on `/stremio/configure`.
4. Select a compatible Debrid playback service for the results.

Zilean supplies cached Debrid Media Manager hash-list results. It does not turn those results into InfiniDysk or AltMount Usenet playback.

### InfiniDysk

AIOStreams currently labels this service **NzbDAV**. Select **NzbDAV** in AIOStreams when connecting DUMB's canonical **InfiniDysk** service.

1. Complete InfiniDysk's provider setup.
2. Copy the SABnzbd API key and configure dedicated WebDAV credentials in InfiniDysk.
3. On AIOStreams' **Services** page, add **NzbDAV**.
4. Set **URL** to InfiniDysk's direct local frontend/API address, normally `http://127.0.0.1:3000`. Use its saved port when DUMB reassigned it.
5. Enter the SABnzbd API key, WebDAV username, and WebDAV password.
6. Choose one player-facing route:
    - **AIOStreams proxy, recommended:** Leave **Public URL** blank and provide an AIOStreams auth credential (`username:password`) whose user has **Proxy** permission.
    - **Direct:** Set **Public URL** to a separately published, trusted HTTPS InfiniDysk origin.

The local URL is for AIOStreams-to-InfiniDysk API traffic. The public URL, when set, is sent to the player. Never put a loopback or DUMB embedded UI address in **Public URL**.

### AltMount

1. Complete AltMount's administrator, NNTP provider, WebDAV, and SABnzbd-compatible API setup.
2. In AltMount, confirm the SAB API is enabled and copy the API key plus WebDAV credentials.
3. On AIOStreams' **Services** page, add **AltMount**.
4. Set **URL** to `http://127.0.0.1:8088`, replacing `8088` with AltMount's saved DUMB port.
5. Enter the API key and WebDAV credentials.
6. Leave **Public URL** blank and provide an AIOStreams auth credential (`username:password`) whose user has **Proxy** permission, or intentionally publish AltMount at its own trusted HTTPS origin and enter that direct URL.

AIOStreams uses AltMount's SABnzbd-compatible API and WebDAV stream surface. This integration is independent of whether AltMount uses FUSE, embedded rclone, external rclone, or no mount for its Arr workflow.

### AIOStreams native Usenet engine

InfiniDysk and AltMount are optional for AIOStreams. To stream directly through AIOStreams instead:

1. Configure NNTP providers in the AIOStreams dashboard's Usenet settings.
2. Add indexers through Prowlarr, Newznab, or another supported built-in addon.
3. Add **AIOStreams** as the playback service on `/stremio/configure`.
4. Supply an AIOStreams auth credential (`username:password`) whose user has **Service** permission.

The native engine uses the AIOStreams host for both search-related proxying and NNTP streaming, and stores bounded disk cache data beneath `/aiostreams/data` by default. Respect provider connection limits when other DUMB services use the same NNTP account.

---

## Authentication and secrets

AIOStreams' configure page is public by default, but its Dashboard requires operator authentication. For a shared or internet-reachable deployment:

- Use strong onboarding-managed administrator credentials; DUMB translates them into `AIOSTREAMS_AUTH` and an explicit `admin` permission entry.
- Enable AIOStreams' **Auth Required** runtime setting when configuration creation should require a login.
- Keep the generated configuration access key stable. Rotating it invalidates existing configurations until they are saved again.
- For advanced multi-user configurations, give each additional AIOStreams auth credential (`username:password`) only the permission its user needs, such as **Proxy** for proxied InfiniDysk/AltMount streams or **Service** for the native Usenet engine.
- Keep sensitive logging disabled and do not post manifest URLs, AIOStreams auth credentials, provider credentials, or exported configs containing credentials in support logs.

The installed Stremio manifest URL grants access to that saved configuration. Treat it like an API token even when the dashboard itself requires login.

An AIOStreams auth credential is the `username:password` pair defined in `AIOSTREAMS_AUTH`; it is not the saved Stremio manifest URL or configuration password. The onboarding-managed administrator has all permissions. Advanced operators can define narrower additional users directly in the environment. Follow the upstream environment-variable guide for the current authentication and permission syntax.

---

## Backups and recovery

Back up AIOStreams before upgrades, database changes, or secret/configuration edits.

### SQLite deployment

1. Stop AIOStreams, or use a SQLite-consistent online backup method.
2. Back up all of `/aiostreams/data`, not only `db.sqlite`.
3. Back up `/config/dumb_config.json` and its DUMB-managed backup so the generated `SECRET_KEY`, `base_url`, selected version, and advanced bootstrap values are recoverable.
4. Store a copy outside the DUMB container and outside the host filesystem that holds the live service.
5. Test restoring the data and the **same** secret into a disposable environment.

### PostgreSQL deployment

Back up `/config/dumb_config.json` and `/aiostreams/data`, then create and test a logical PostgreSQL dump of the AIOStreams database. The data-directory copy does not contain PostgreSQL records.

AIOStreams also offers a per-configuration export under **Save & Install → Backups**. Use **Exclude Credentials** before sharing an export. That JSON is useful for rebuilding one user's addon configuration, but it does not replace the instance database, DUMB bootstrap configuration, or `SECRET_KEY` backup.

---

## Troubleshooting

| Symptom | Check |
| --- | --- |
| AIOStreams does not start | Confirm the log does not report a missing/invalid 64-hex secret, database connection failure, unsupported image architecture, or failed OCI verification. |
| Configure opens but Dashboard rejects login | Use the `aiostreams.auth_username` and `aiostreams.auth_password` values saved during onboarding, then restart AIOStreams after changing either value. The Configure page is public unless **Auth Required** is enabled. |
| Configure page works locally but Stremio cannot install | `base_url` must be the exact trusted public HTTPS base URL (including any configured prefix), not a loopback, raw container port, `/ui/aiostreams` URL, configure route, query, or fragment. |
| Addon installed before `base_url` changed still fails | Restart AIOStreams, reopen `/stremio/configure`, and save/install the configuration again. |
| Prowlarr or Zilean test fails | Use `127.0.0.1` with the service's saved DUMB port and confirm its API key when required. |
| InfiniDysk or AltMount returns an unreachable stream URL | Leave **Public URL** blank and configure an AIOStreams auth credential (`username:password`) whose user has **Proxy** permission, or set it to a separate trusted HTTPS origin reachable by the player. |
| Existing configs fail after restore | Restore the original `SECRET_KEY`; a newly generated value cannot decrypt them. |
| Switching `aiostreams.database_uri` shows an empty installation | Selecting another database does not migrate data. Restore the former URI/database or perform an operator-managed migration from a verified backup. |
| Public browser route works but playback redirects to login | Remove the interactive whole-host auth middleware or design explicit Stremio-route exemptions. |

Check `/api/v1/health` on the direct service listener when distinguishing AIOStreams health from DNS, TLS, or reverse-proxy problems.

---

## Related links

- [AIOStreams repository](https://github.com/Viren070/AIOStreams)
- [AIOStreams documentation](https://docs.aiostreams.viren070.me/)
- [AIOStreams environment variables](https://docs.aiostreams.viren070.me/configuration/environment-variables)
- [AIOStreams Usenet guide](https://docs.aiostreams.viren070.me/guides/usenet)
- [Prowlarr](../core/prowlarr.md)
- [Zilean](zilean.md)
- [InfiniDysk](../core/infinidysk.md)
- [AltMount](../core/altmount.md)
- [Traefik Proxy Admin](traefik-proxy-admin.md)
- [Cloudflared](cloudflared.md)

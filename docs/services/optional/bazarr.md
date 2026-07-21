---
title: Bazarr
icon: lucide/captions
---

# Bazarr

[Bazarr](https://www.bazarr.media/) is an optional subtitle manager for movies and TV shows. It reads library information from Sonarr and Radarr, searches configured subtitle providers, and writes downloaded subtitles beside the media files.

## How DUMB runs Bazarr

DUMB installs the official Bazarr release inside the DUMB container and runs it as a managed service:

- Web UI/API port: `6767`
- Application files: `/opt/bazarr`
- Persistent configuration and database: `/bazarr/data`, backed by `/data/bazarr`
- Media access: the same `/mnt/debrid` tree used by Sonarr and Radarr
- Updates: managed by DUMB; Bazarr's self-updater is disabled with `NO_UPDATE=true`

Because Bazarr, the Arr services, and the debrid mounts run in the same DUMB container, Bazarr sees the same container paths directly. A separate Bazarr container and host mount-propagation setup are not required.

## Enable Bazarr

### Guided onboarding

Select **Bazarr** in the **Optional Services** step. DUMB starts it in the post-core phase so an enabled Sonarr or Radarr service is available first.

### Existing installation

Open the Bazarr service page in the DUMB frontend, enable the service in **DUMB Config**, save, and start it. The default configuration is:

```json
"bazarr": {
  "enabled": false,
  "postgres_enabled": false,
  "postgres_database": "",
  "process_name": "Bazarr",
  "repo_owner": "morpheus65535",
  "repo_name": "bazarr",
  "release_version_enabled": false,
  "release_version": "latest",
  "suppress_logging": false,
  "log_level": "INFO",
  "port": 6767,
  "auto_update": true,
  "auto_update_interval": 24,
  "auto_update_start_time": "04:00",
  "clear_on_update": true,
  "exclude_dirs": [
    "/opt/bazarr/venv"
  ],
  "platforms": [
    "python"
  ],
  "command": [
    "/opt/bazarr/venv/bin/python",
    "/opt/bazarr/bazarr.py",
    "--config",
    "/bazarr/data",
    "--port",
    "{port}"
  ],
  "config_dir": "/opt/bazarr",
  "config_file": "/bazarr/data/config/config.yaml",
  "log_file": "/bazarr/data/log/bazarr.log",
  "env": {
    "NO_UPDATE": "true"
  }
}
```

## First-time Bazarr setup

Open Bazarr from its service page or browse to:

```text
http://<dumb-host>:18080/service/ui/bazarr
```

Then complete these steps in Bazarr:

1. Under **Settings -> Sonarr**, enable Sonarr if you manage TV shows.
2. Use `localhost` as the address, the assigned Sonarr port (default `8989`), and the API key from Sonarr's **Settings -> General** page.
3. Under **Settings -> Radarr**, enable Radarr if you manage movies.
4. Use `localhost` as the address, the assigned Radarr port (default `7878`), and the API key from Radarr's **Settings -> General** page.
5. Test each connection, select subtitle languages and profiles, then configure at least one subtitle provider.

If your Arr instances use non-default ports, use the actual ports shown on their DUMB service pages.

DUMB treats `bazarr.port` as authoritative. If DUMB assigns a different port to avoid a conflict, Bazarr's persisted **Settings -> General -> Port** value is synchronized to the same port during setup. Restart Bazarr after manually changing `bazarr.port` so both the managed launch command and Bazarr's saved setting are updated.

## Media paths

Bazarr relies on the paths reported by Sonarr and Radarr. Inside DUMB, all three services see the same filesystem, so the reported Arr path should already be valid in Bazarr. Keep the Arr root folders and Bazarr access on the same `/mnt/debrid/...` paths.

Do not add remote path mappings merely because DUMB itself is running in Docker. A mapping is only needed if an Arr instance reports a path that genuinely differs from the path Bazarr can access.

## Updates and persistence

DUMB checks the official Bazarr GitHub release and installs updates according to `auto_update_interval` and `auto_update_start_time`. The Python virtual environment is retained during an application update and its requirements are refreshed from the release.

Bazarr uses `/bazarr/data/db/bazarr.db` by default. The database and settings remain under `/data/bazarr` across container replacement or application updates. Do not place Bazarr's SQLite configuration directory on NFS.

## PostgreSQL migration

Bazarr supports PostgreSQL, and DUMB exposes the guarded **Database Migration** tool on the Bazarr service page. Run a rehearsal first, review all table counts, then perform cutover. DUMB configures Bazarr's official `POSTGRES_*` environment values and creates the `bazarr` database by default.

Do not set `postgres_enabled: true` directly on an existing installation; that changes the backend without copying `bazarr.db`. Bazarr's upstream guide requires the SQLite database to have been used with Bazarr 1.1.5 or newer before migration. DUMB converts the SQLite timestamp values to the types in Bazarr's current PostgreSQL schema, preserves the SQLite source, and restores SQLite configuration automatically when cutover fails. See [SQLite to PostgreSQL Migration](../../features/arr-postgres-migration.md).

## Troubleshooting

### Bazarr cannot connect to Sonarr or Radarr

- Confirm the Arr service is running.
- Use `localhost`, not the DUMB host's LAN address.
- Verify the assigned port on the Arr service page.
- Copy the API key again from the Arr application's **Settings -> General** page.

### Bazarr reports that a media path does not exist

- Compare the exact path shown in Bazarr with the path recorded in Sonarr or Radarr.
- Confirm the file is visible at that same path inside DUMB's `/mnt/debrid` tree.
- If the underlying debrid mount is unhealthy, recover or restart the mount-providing service, then restart Bazarr so it refreshes the library path.

### Bazarr does not appear in the embedded UI

- Confirm Bazarr is enabled and running on its assigned port.
- Restart Traefik after enabling Bazarr if its service route has not appeared.
- Use the Bazarr service page or `/service/ui/bazarr`; do not open the dmbdb internal `/ui/bazarr` proxy path directly.

## Related links

- [Bazarr setup guide](https://wiki.bazarr.media/Getting-Started/Setup-Guide/)
- [Bazarr PostgreSQL database](https://wiki.bazarr.media/Additional-Configuration/PostgreSQL-Database/)
- [Sonarr](../core/sonarr.md)
- [Radarr](../core/radarr.md)
- [Embedded service UIs](../../features/embedded-ui.md)
- [Auto-update](../../features/auto-update.md)

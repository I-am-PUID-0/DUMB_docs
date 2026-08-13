---
title: Profilarr
description: Run Profilarr v1 or v2 in DUMB and connect it to managed Sonarr and Radarr instances.
icon: lucide/sliders
---

# Profilarr

Profilarr is a profile and custom format manager for **Sonarr** and **Radarr**. DUMB supports both the legacy v1 application and the redesigned v2 application, and can auto-link either generation to matching Arr instances.

---

## Overview

Profilarr provides:

- **Repository‑backed profiles** - version‑control your profiles and formats
- **Cross‑stack consistency** - keep Sonarr/Radarr aligned across debrid and usenet stacks
- **Media management sync** - naming rules, quality definitions, and misc settings
- **Version-aware installation** - run a v1 release, a v2 release, a branch, or an exact commit
- **Safe v2 ownership** - DUMB changes only v2 Arr connections tagged `dumb:auto`

---

## Default port

| Service | Port |
|---------|------|
| Profilarr | 6868 |

---

## Configuration in `dumb_config.json`

### Profilarr instance configuration

```json
"profilarr": {
  "instances": {
    "Default": {
      "enabled": false,
      "core_service": "",
      "process_name": "Profilarr",
      "repo_owner": "Dictionarry-Hub",
      "repo_name": "profilarr",
      "release_version_enabled": false,
      "release_version": "latest",
      "commit_sha": "",
      "branch_enabled": false,
      "branch": "main",
      "suppress_logging": false,
      "log_level": "INFO",
      "port": 6868,
      "auto_update": false,
      "auto_update_interval": 24,
      "auto_update_start_time": "04:00",
      "clear_on_update": true,
      "exclude_dirs": ["/profilarr/default/config"],
      "config_dir": "/profilarr/default",
      "log_file": "/profilarr/default/config/log/profilarr.log"
    }
  }
}
```

#### Profilarr instance keys

- **`enabled`**: Whether to start this Profilarr instance.
- **`core_service`**: Filters which Arr instances are auto‑linked (see below).
- **`repo_owner` / `repo_name`**: GitHub repository for Profilarr itself.
- **`release_version_enabled` / `release_version`**: Profilarr is unpinned by default and follows the latest stable release. Enable release pinning and enter an explicit tag such as `v1.1.4`, `v1.1.5`, or `v2.0.9` to stay on that release.
- **`commit_sha`**: Build this Profilarr instance from an exact full 40-character GitHub SHA. It overrides release/branch selection and disables automatic updates for that instance until cleared.
- **`branch_enabled` / `branch`**: Use a specific branch if enabled.
- **`port`**: Port the Profilarr UI is exposed on.
- **`auto_update` / `auto_update_interval` / `auto_update_start_time`**: Automatic update settings.
- **`config_dir` / `log_file`**: Profilarr installation/config root and log path.

`command`, build platforms, and generation-specific environment variables are runtime-managed. DUMB detects the downloaded source layout and writes the correct v1 Gunicorn or v2 standalone command automatically.

## Choosing v1 or v2

New configurations default to `release_version_enabled: false` with `release_version: latest`, so they follow the current stable Profilarr release without being pinned. Existing DUMB configurations pinned to `v1.1.4` remain pinned and continue using the v1 Python/React build.

| Selector | DUMB behavior |
|----------|---------------|
| Default unpinned selection (`release_version_enabled: false`) | Follows the latest stable release, currently a v2 Deno/SvelteKit build. |
| An explicit `v2.x` tag | Pins and runs the selected v2 Deno/SvelteKit application. |
| A `v1.x` tag | Builds and runs the legacy Python/React application. |
| `branch_enabled: true` | Downloads the selected branch and detects its layout. |
| `commit_sha` | Downloads the exact commit and detects its layout; automatic updates are disabled. |

After choosing an explicit release, branch, or commit, use **Install configured release/branch/commit** or restart the service. For the default unpinned configuration, use the normal update action or restart the service so DUMB resolves and installs the current stable release.

!!! warning "v2 is a fresh application state"

    Profilarr v2 does not provide an in-place migration from v1 app data. DUMB preserves the shared config root during upgrades, but keeps the primary databases separate: v1 uses `config/profilarr.db`, while v2 uses `config/data/profilarr.db`. Configure v2 through its first-run setup instead of expecting v1 users, repositories, or profile selections to be imported.

---

## Arr instance options

Profilarr auto‑linking is controlled per Arr instance:

```json
"sonarr": {
  "instances": {
    "Default": {
      "enabled": true,
      "use_profilarr": true
    }
  }
}
```

Key:

- **`use_profilarr`**: Opt this Arr instance into Profilarr auto‑linking.

---

## Auto-linking behavior

DUMB automatically links Profilarr to Sonarr/Radarr instances that:

- are enabled
- have `use_profilarr: true`
- match the Profilarr instance `core_service` filter

On v1, DUMB retains its original repository seeding and one-time initial-sync behavior. On v2, DUMB creates and updates only Arr connection rows tagged `dumb:auto`. It deliberately leaves v2 databases, profiles, quality profiles, custom formats, and sync choices under Profilarr's control. A user-created v2 Arr connection with the same name is left unchanged.

### `core_service` filtering

- **Blank (`""`)**: Manual mode. DUMB does **not** auto‑link any Arr instances.
- **Single core service** (e.g., `decypharr`): Links only Arrs in that stack.
- **Combined** (e.g., `decypharr, infinidysk, altmount`): Links Arrs across matching Debrid and Usenet stacks.

---

## v1 default repository seeding

This section applies only to Profilarr v1. If no repository is connected, DUMB seeds a default repo on first run:

- `https://github.com/johman10/profilarr-trash-guides`

This provides ready‑to‑sync profiles, custom formats, regex patterns, and media management defaults.

---

## v1 initial sync behavior

This section applies only to Profilarr v1. When DUMB creates a new Profilarr app entry, it triggers a one-time initial sync:

- **Profiles**
- **Custom formats**
- **Regex patterns** (used during profile/format compilation)
- **Media management**:
  - naming rules
  - misc settings
  - quality definitions

!!! note "Regex patterns"

    Regex patterns are not Arr settings. They are used by Profilarr to compile profiles and formats, so they won’t appear in Arr UI.

### Forcing the initial sync again

Delete the Arr entry in Profilarr and restart Profilarr from the DUMB frontend. DUMB will recreate the entry and run the initial sync again.

## Profilarr v2 notes

- Complete Profilarr's account setup when you first open v2.
- Profilarr v2 initializes its own application database and default Dictionarry v2 database.
- DUMB retries Arr auto-linking after Profilarr starts so the v2 migrations can finish first.
- The optional upstream parser service used for custom-format and quality-profile expression testing is not managed by DUMB. Core v2 profile management and Arr synchronization do not require it.
- v2 supports Linux AMD64 and ARM64 builds in DUMB.

---

## v1 tagging rules for repo items

DUMB uses filename tags to avoid cross‑syncing:

- **Profiles / custom formats** require `sonarr` or `radarr` in the filename.
- **Regex patterns / media management** apply to both if no app‑specific tag is found.

---

## Troubleshooting

### Missing API keys

If auto‑link runs before Arrs finish writing `config.xml`, you may see:

```
Profilarr auto-link: missing API key for sonarr ...
```

DUMB retries automatically after Arr start, but you can also restart Profilarr once the Arrs are fully up.

---

## Resources

- [Profilarr Repository](https://github.com/Dictionarry-Hub/profilarr)
- [Profilarr Docs](https://dictionarry.dev/)

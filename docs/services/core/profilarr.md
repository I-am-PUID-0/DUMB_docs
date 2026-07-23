---
title: Profilarr
icon: lucide/sliders
---

# Profilarr

Profilarr is a profile and custom format manager for **Sonarr** and **Radarr**. In DUMB it can be auto‑linked to your Arr instances so quality profiles, custom formats, regex patterns, and media management settings stay aligned across stacks.

---

## Overview

Profilarr provides:

- **Repository‑backed profiles** - version‑control your profiles and formats
- **Cross‑stack consistency** - keep Sonarr/Radarr aligned across debrid and usenet stacks
- **Media management sync** - naming rules, quality definitions, and misc settings
- **Initial sync automation** - DUMB can seed and apply settings on first link

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
      "release_version_enabled": true,
      "release_version": "v1.1.4",
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
      "exclude_dirs": [
        "/profilarr/default/config"
      ],
      "platforms": [
        "python",
        "pnpm"
      ],
      "command": [
        "/profilarr/default/backend/venv/bin/gunicorn",
        "--chdir",
        "/profilarr/default/backend",
        "--bind",
        "0.0.0.0:{port}",
        "--timeout",
        "600",
        "app.main:create_app()"
      ],
      "config_dir": "/profilarr/default",
      "log_file": "/profilarr/default/config/log/profilarr.log",
      "env": {
        "PROFILARR_CONFIG_DIR": "/profilarr/default/config",
        "FLASK_ENV": "production",
        "PYTHONPATH": "/profilarr/default/backend"
      }
    }
  }
}
```

#### Profilarr instance keys

- **`enabled`**: Whether to start this Profilarr instance.
- **`core_service`**: Filters which Arr instances are auto‑linked (see below).
- **`repo_owner` / `repo_name`**: GitHub repository for Profilarr itself.
- **`release_version_enabled` / `release_version`**: Use GitHub releases when enabled.
- **`commit_sha`**: Build this Profilarr instance from an exact full 40-character GitHub SHA. It overrides release/branch selection and disables automatic updates for that instance until cleared.
- **`branch_enabled` / `branch`**: Use a specific branch if enabled.
- **`port`**: Port the Profilarr UI is exposed on.
- **`auto_update` / `auto_update_interval` / `auto_update_start_time`**: Automatic update settings.
- **`config_dir` / `log_file`**: Profilarr installation/config root and log path.

!!! note "Pinned compatibility default"
    DUMB currently enables the tested `v1.1.4` release selector by default. Do not replace it with an arbitrary current upstream release unless you intend to compatibility-test DUMB's install, launch, and auto-link behavior against that version.

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

## Auto‑linking behavior

DUMB automatically links Profilarr to Sonarr/Radarr instances that:

- are enabled
- have `use_profilarr: true`
- match the Profilarr instance `core_service` filter

### `core_service` filtering

- **Blank (`""`)**: Manual mode. DUMB does **not** auto‑link any Arr instances.
- **Single core service** (e.g., `decypharr`): Links only Arrs in that stack.
- **Combined** (e.g., `decypharr, nzbdav, altmount`): Links Arrs across matching Debrid and Usenet stacks.

---

## Default repository seeding

If no repository is connected inside Profilarr, DUMB seeds a default repo on first run:

- `https://github.com/johman10/profilarr-trash-guides`

This provides ready‑to‑sync profiles, custom formats, regex patterns, and media management defaults.

---

## Initial sync behavior

When DUMB creates a new Profilarr app entry, it triggers a one‑time initial sync:

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

---

## Tagging rules for repo items

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

---
title: Before you install
description: Prepare persistent storage, provider accounts, user IDs, and a network plan before deploying DUMB on Docker or native Proxmox LXC.
icon: lucide/download
---

# Before you install

Have a host, persistent storage, and credentials for the services you plan to use. DUMB creates its initial configuration at startup; you do not need to write a complete `dumb_config.json` first.

## Host requirements

| Requirement | Guidance |
|---|---|
| Runtime | Docker Engine on Linux, including WSL2; or the [native Proxmox LXC helper](../deployment/proxmox.md) |
| CPU and memory | Start around 2 vCPU and 2 GB RAM for a small stack. This is a planning estimate; source builds, databases, transcoding, and larger service selections need more. |
| Storage | Persistent storage for configuration, databases, logs, and library paths; SSD storage is preferable for databases and source builds. |
| User and group | Non-root `PUID` and `PGID` with access to the host directories. Check them with `id -u` and `id -g`. |
| Networking | Access to image/package registries and your providers. Publish dashboard port `3005` unless you deliberately change it. |

!!! warning "Docker Desktop and external mounts"

    Docker Desktop does not support the bind mount propagation needed to share DUMB-created FUSE/rclone submounts with containers outside DUMB. For Windows, use [Docker Engine inside WSL2](../deployment/wsl.md). See [Docker's propagation documentation](https://docs.docker.com/engine/storage/bind-mounts/#configure-bind-propagation).

## Accounts and credentials

| Selected integration | Have this ready |
|---|---|
| Debrid | API key for each selected provider |
| Usenet | NNTP host, port, username/password, connection limit, and TLS setting |
| Plex | Claim/token and server address when the selected integration requires them |
| Private or sponsored GitHub repository | A read-capable GitHub token with the access that repository requires |
| Cloudflared | A Cloudflare Tunnel token |

You only need credentials for the integrations you enable. See [integration tokens](../features/configuration.md#integration-tokens-credentials).

## Persistent directories

The maintained Compose layout mounts four host directories. Native LXC uses the same absolute paths directly in the guest.

| Path inside DUMB | Contents |
|---|---|
| `/config` | DUMB configuration, authentication data, migration jobs, snapshots, and feature state |
| `/log` | DUMB and collected service logs |
| `/data` | Persistent application data. DUMB maps internal paths such as `/plex`, `/postgres_data`, and `/decypharr` into subdirectories here. |
| `/mnt/debrid` | Mounts, generated links, and library paths |

Keep these paths when recreating or upgrading the container. Store a separate backup of important configuration and application data; a bind mount alone is not a backup.

!!! note "Existing installations"

    Separate direct mounts such as `/postgres_data` or `/plex` are legacy or advanced layouts. They can prevent DUMB from creating managed data symlinks. Preserve an existing layout until you have reviewed its migration; do not add those mounts to a new deployment by default.

## Decide who reads the library

- **Everything inside DUMB:** use a normal `/mnt/debrid` bind mount.
- **External Arr or media-server containers:** use matching library and target paths. If they need DUMB-created FUSE/rclone submounts, prepare a shared host mount and use `:rshared` on DUMB's bind, with the appropriate consumer propagation.
- **Remote machines:** plan an explicit sharing method. A path that exists inside DUMB does not automatically become available elsewhere.

The need for propagation comes from the deployment topology, not the workflow's name. Adding `:rshared` to Compose does not prepare the host mount.

## Ready to deploy

Choose your [deployment guide](../deployment/index.md), start DUMB, and open `http://<host>:3005`. Then follow [onboarding](../frontend/onboarding.md).

<!-- dev:start -->
Review the retained [setup checklist](../features/setup-checklist.md) for automatic and manual integration tasks.
<!-- dev:end -->

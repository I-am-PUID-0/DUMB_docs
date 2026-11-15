---
title: Deployment
description: Choose a Docker, NAS, Windows WSL2, or native Proxmox deployment guide for DUMB, then verify storage and first-run access.
icon: lucide/server
---

# Deploy DUMB

Choose the host or management tool where you want to install DUMB. Each link below opens the complete installation guide for that platform.

After installation, you will use the [DUMB dashboard](../frontend/index.md) for everyday setup, service controls, updates and logs. The deployment guide covers the host setup needed to reach that dashboard.

| Your environment | Guide | What it manages |
|---|---|---|
| Linux terminal | [Docker Compose](docker.md) | Compose file, storage, and container lifecycle |
| Existing Portainer installation | [Portainer](portainer.md) | DUMB as a Portainer stack |
| Existing Dockge installation | [Dockge](dockge.md) | DUMB as a Compose stack |
| Unraid | [Unraid](unraid.md) | Community Applications template and host paths |
| Windows | [WSL2](wsl.md) | Docker Engine in a Linux distribution |
| Proxmox | [Native LXC](proxmox.md) | DUMB and managed services directly in a Debian guest |
| Synology | [Container Manager](synology.md) | A Compose project with NAS storage |
| QNAP | [Container Station](qnap.md) | A Compose application with shared folders |
| TrueNAS SCALE | [Custom App](truenas.md) | A Compose-based app with datasets |

The native Proxmox helper has its own validation status and runtime requirements; read its guide before treating it as equivalent to the Docker image.

## Before starting

Read [Before you install](../getting-started/installation.md) for credentials, sizing, permissions, and persistence. Every normal deployment preserves these paths:

| Path | Purpose |
|---|---|
| `/config` | DUMB configuration and feature state |
| `/log` | DUMB and service logs |
| `/data` | Application data mapped through DUMB-managed internal paths |
| `/mnt/debrid` | Mounts and library paths |

DUMB creates `dumb_config.json` when needed. Keep the host directories when replacing the container.

## Choose the network and mount layout

The default Compose file publishes **port 3005** for the dashboard, REST gateway, and WebSockets. Embedded service UIs can use that same address. Publish individual service ports only when clients need direct access. See [Networking and ports](networking.md).

Use a normal `/mnt/debrid` bind if all consumers run inside DUMB. External consumers of FUSE/rclone submounts need a prepared shared Linux host mount and suitable propagation. See [Before you install](../getting-started/installation.md#decide-who-reads-the-library).

!!! warning "Windows hosts"

    Docker Desktop cannot provide the bind propagation required for external FUSE consumers. Use the [WSL2 guide](wsl.md) for Docker Engine on Windows.

## After starting

1. Open `http://<host>:3005`.
2. Configure access and select services in [Onboarding](../frontend/onboarding.md).
3. Check service logs and finish application-specific setup.
4. Test an import and playback through the applications you selected.

Keep a backup before changing persistent storage or moving hosts.

<!-- dev:start -->
The development backend provides [installation backup and restore](../features/installation-backups.md).
<!-- dev:end -->

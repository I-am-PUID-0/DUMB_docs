---
title: Deploy with Synology
icon: simple/synology
---

# Deploy with Synology Container Manager

DSM 7.2 Container Manager supports Docker Compose through **Projects**. A project
can upload a Compose file or use the built-in YAML editor.

## Prerequisites

- A Synology model/architecture supported by the DUMB image (`amd64` or `arm64`)
- DSM Container Manager installed
- A shared folder for persistent DUMB storage
- A numeric UID/GID with read/write access to that folder
- `/dev/fuse` and the required container capabilities if the selected workflow
  creates FUSE mounts

Synology documents the project workflow in
[Container Manager: Project](https://kb.synology.com/en-us/DSM/help/ContainerManager/docker_project).

## Prepare persistent storage

Create this structure in File Station or over SSH:

```text
/volume1/docker/DUMB/
├── config/
├── data/
├── log/
└── mnt/debrid/
```

Replace `volume1` if the share is on another volume. Apply permissions for the
same UID/GID you will enter as `PUID` and `PGID`.

## Create the project

1. Open **Container Manager** → **Project** → **Create**.
2. Enter a project name such as `dumb` and choose a project working directory.
3. Upload or paste the current
   [DUMB Compose file](https://github.com/I-am-PUID-0/DUMB/blob/master/docker-compose.yml).
4. Replace `/home/username/docker/DUMB` with `/volume1/docker/DUMB`.
5. Set `TZ`, `PUID`, and `PGID`.
6. Review the summary, create the project, and start it.

The persistent mounts should resolve to:

```yaml
volumes:
  - /volume1/docker/DUMB/config:/config
  - /volume1/docker/DUMB/log:/log
  - /volume1/docker/DUMB/data:/data
  - /volume1/docker/DUMB/mnt/debrid:/mnt/debrid
```

Open `http://<synology-address>:3005`. DUMB API requests use the frontend proxy
at `/api`; the native backend on `8000` is intentionally not published.

## FUSE and mount propagation

Keep `/dev/fuse`, `SYS_ADMIN`, and the security options from the maintained
Compose file when your workflow needs rclone/FUSE. Support can vary by DSM,
model, and kernel. A successful container start alone does not prove that an
external media-server container can see nested mounts.

For external consumers, set the DUMB bind to:

```yaml
- /volume1/docker/DUMB/mnt/debrid:/mnt/debrid:rshared
```

Mount that host directory into the consumer at `/mnt/debrid` using `rslave` or
an equivalent propagation mode. If DSM does not preserve propagation, keep the
producer and consumers inside DUMB or select a workflow that exposes ordinary
files/symlinks.

## Updating

In **Project**, edit the YAML if the upstream Compose file changed, pull the
current image, and rebuild/recreate the project. Do not use **Clean** or delete
the persistent shared folders unless you intend to remove DUMB data.

Continue with [Getting Started](../getting-started/index.md).

---
title: Deploy with Docker
description: Install DUMB with Docker Compose on Linux, prepare persistent directories, set user IDs, and verify the dashboard and first-run setup.
icon: fontawesome/brands/docker
---

# Deploy with Docker

Use Docker Compose to run DUMB on a Linux host. If you already manage containers with [Portainer](portainer.md) or [Dockge](dockge.md), use that guide instead. Windows users should prepare [WSL2](wsl.md) first.

## 1. Check Docker Engine and Compose

You need Docker Engine, the Compose plugin, a supported 64-bit host (`amd64` or `arm64`), and a non-root account with permission to use Docker. Commands below use `sudo` for Docker operations.

Install Docker using its official package instructions for [Ubuntu](https://docs.docker.com/engine/install/ubuntu/), [Debian](https://docs.docker.com/engine/install/debian/), or your distribution. Use a currently supported OS release. Docker's convenience script is intended for testing and development, so use the package repository for an ongoing installation.

```bash
docker --version
docker compose version
sudo docker run --rm hello-world
```

Avoid the Snap build for DUMB; its confinement can interfere with the mount and device access used by FUSE workflows. If you prefer Docker without `sudo`, follow [Docker's Linux post-installation guide](https://docs.docker.com/engine/install/linux-postinstall/). Membership in the `docker` group grants control equivalent to host root.

## 2. Prepare persistent storage

Create a directory as the non-root account that will own DUMB's application data:

```bash
mkdir -p "$HOME/docker/DUMB"/{config,log,data,mnt/debrid}
cd "$HOME/docker/DUMB"
id -u
id -g
```

Keep the numeric UID and GID for the next step. `PUID` and `PGID` must be greater than zero.

| Host subdirectory | Path inside DUMB | Contents |
|---|---|---|
| `config` | `/config` | DUMB settings, authentication, and feature state |
| `log` | `/log` | DUMB and collected application logs |
| `data` | `/data` | Persistent application data |
| `mnt/debrid` | `/mnt/debrid` | Mounts, generated links, and library paths |

DUMB maps internal application paths such as `/plex` and `/postgres_data` into `/data`. Do not add a separate bind mount for every service on a new installation.

## 3. Download and edit the Compose file

```bash
curl --fail --show-error --location \
  https://raw.githubusercontent.com/I-am-PUID-0/DUMB/master/docker-compose.yml \
  --output docker-compose.yml
```

Open `docker-compose.yml` and review:

| Setting | What to enter |
|---|---|
| Host volume paths | Replace `/home/username/docker/DUMB` with the absolute directory created above |
| `PUID`, `PGID` | The nonzero values returned by `id -u` and `id -g` |
| `TZ` | A time zone such as `Etc/UTC` |
| Image | `iampuid0/dumb:latest` for the stable channel; see [documentation versions](../reference/doc-versions.md) for development |
| Ports | Keep `3005:3005` for normal dashboard/API access |
| `/dev/dri` | Keep for supported GPU acceleration; remove this device mapping if the host has no such device |
| `/dev/fuse`, `SYS_ADMIN`, AppArmor option | Required by workflows that create FUSE/rclone mounts |

For example, the environment section can use:

```yaml
environment:
  - TZ=Etc/UTC
  - PUID=1000
  - PGID=1000
```

Use your actual user IDs. Do not leave the template's ID fields blank.

!!! note "External consumers of FUSE mounts"

    A private `/mnt/debrid` bind is sufficient if all consumers run inside DUMB. If an external Arr or media-server container needs DUMB-created submounts, prepare a shared Linux host mount before adding `:rshared`. See [Before you install](../getting-started/installation.md#decide-who-reads-the-library). Docker Desktop does not support this propagation.

## 4. Start DUMB

From the directory containing the Compose file:

```bash
sudo docker compose config --quiet
sudo docker compose up -d
sudo docker compose logs --follow --tail=100
```

The first start may take longer while services are installed. Leave the process running and inspect the logs for the actual failure if startup stalls. Press `Ctrl+C` to leave the log viewer; this does not stop the detached container.

## 5. Open the dashboard

Open `http://<host>:3005`, then complete [onboarding](../frontend/onboarding.md). The same listener forwards REST requests under `/api` and WebSockets under `/ws`.

The backend-native API binds to `127.0.0.1:8000` inside DUMB and is not published by the maintained Compose file.

If the page is unavailable, check:

```bash
sudo docker compose ps
sudo docker compose logs --tail=200
```

Confirm the published port, host firewall, and address. A service that starts successfully still needs its accounts, providers, root folders, and media libraries configured before an import/playback test.

## Direct service access

Embedded UIs can use the dashboard address. When another client needs a native service port, add it alongside `3005`, using the assigned runtime port:

```yaml
ports:
  - "3005:3005"
  - "7878:7878"   # Radarr, if its configured port is 7878
  - "32400:32400" # Plex
```

Apply changes with `sudo docker compose up -d`. Compare bridge and host networking in [Networking and ports](networking.md).

Do not publish `8000` for normal use. A mapping alone cannot expose its loopback listener; direct backend access also requires an intentional bind-address change and appropriate access controls.

<!-- dev:start -->
## Optional Audiobookshelf storage

The normal `/data` mount preserves `/data/audiobookshelf/config` and `/data/audiobookshelf/metadata`. Add separate media mounts for books and podcasts. The SQLite configuration directory must be on local storage; if `/data` is network-backed, use a separate local bind and set `audiobookshelf.config_dir` to that container path. See [Audiobookshelf](../services/optional/audiobookshelf.md).
<!-- dev:end -->

## Update or stop

To adopt a new DUMB image while preserving bind-mounted data:

```bash
sudo docker compose pull
sudo docker compose up -d
```

DUMB's application auto-updates are separate from replacing the container image. Review [Auto-update](../features/auto-update.md).

To stop without removing the container, use `sudo docker compose stop`. `sudo docker compose down` removes the container and Compose network while leaving the bind-mounted directories in place. Keep a backup before upgrades or storage changes.

For a shell when diagnosing a problem:

```bash
sudo docker compose exec DUMB bash
```

Use `exit` to leave the shell. If you attach to the container's main process instead, Docker's default detach sequence is `Ctrl+P`, then `Ctrl+Q`.

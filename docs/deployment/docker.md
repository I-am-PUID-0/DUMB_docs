---
title: Deploy with Docker
icon: fontawesome/brands/docker
---

# Deploy with Docker

This guide assumes you have never used Docker before. It walks through what Docker
is, how Docker Compose works, how to install Docker on Ubuntu, and how to deploy
DUMB cleanly with persistent storage.

!!! tip "Prefer a UI?"

    [Portainer](portainer.md) is a great option if you want a web UI for managing
    containers, logs, and volumes. If you want to deploy DUMB with Portainer
    Stacks, follow the [Portainer deployment guide](portainer.md) instead.

---

## Prerequisites

Before you begin, confirm you have:

- A system running **Ubuntu 20.04 or later**
- A **non-root user** with `sudo` privileges
- An active internet connection
- Access to a terminal

!!! warning "Avoid the Snap package"

    Do not install Docker via Snap. The Snap build often breaks networking,
    volume mounts, and socket permissions required by DUMB. Use the official
    Docker install method in this guide instead.

!!! tip "Windows users"

    If you're on Windows, use the [Windows Setup Guide (Docker/WSL)](wsl.md).

---

## What Docker and Docker Compose do

Docker runs applications inside **containers**, which are isolated environments
that package the app and its dependencies. Docker Compose is a helper tool that
starts one or more containers using a `docker-compose.yml` file.

For DUMB, Compose:

- Pulls the DUMB image from a registry
- Creates a container with your settings
- Mounts your local folders so configs and logs persist
- Exposes ports so you can reach the UI and API

---

## Install Docker (official method)

1. Download the official installer:

    ```bash
    curl -fsSL https://get.docker.com -o get-docker.sh
    ```

2. Run it and follow any prompts:

    ```bash
    sh get-docker.sh
    ```

!!! note "WSL detected"

    If the installer reports WSL, follow the [Windows Setup Guide (Docker/WSL)](wsl.md).

---

## Install Docker on other Linux distributions

If you are not on Ubuntu, use the official Docker Engine instructions for your OS:

- **Debian**: https://docs.docker.com/engine/install/debian/
- **Fedora**: https://docs.docker.com/engine/install/fedora/
- **RHEL/CentOS**: https://docs.docker.com/engine/install/centos/
- **Arch**: https://docs.docker.com/engine/install/archlinux/

Use the Docker Engine package (not Snap). Once installed, return to this guide
and continue from **Confirm Docker and Compose are installed**.

---

## Confirm Docker and Compose are installed

1. Check the Docker version:

    ```bash
    docker --version
    ```

2. Check Docker Compose version:

    ```bash
    docker compose version
    ```

Example output:

```bash
Docker version 26.1.4, build 5650f9b
Docker Compose version v2.24.2
```

---

## Optional: allow non-root Docker usage

By default, Docker commands require `sudo`. If you want to run Docker without
`sudo`, add your user to the `docker` group.

```bash
sudo usermod -aG docker $USER
```

Log out and back in (or reboot) so group membership refreshes.

If you skip this step, keep using `sudo` for Docker commands.

---

## Define the directory structure

These folders store configs, logs, and data **outside** the container, so they
survive upgrades and restarts.

1. Create a workspace:

    ```bash
    cd ~
    mkdir -p docker
    cd docker
    ```

2. Create DUMB directories:

    ```bash
    mkdir -p DUMB/config DUMB/log DUMB/data DUMB/mnt/debrid
    ```

---

!!! info "Stopping here for Portainer"

    If you plan to deploy DUMB via Portainer **Stacks**, stop after creating the
    directory structure. You will paste the `docker-compose.yml` into Portainer
    and deploy it from there instead of running `docker compose` on the host.

## Download and edit `docker-compose.yml`

1. Download the latest Compose file:

    ```bash
    curl -O https://raw.githubusercontent.com/I-am-PUID-0/DUMB/master/docker-compose.yml
    ```

2. Replace the default path with your home directory:

    ```bash
    sed -i "s|/home/username/docker/DUMB|$HOME/docker/DUMB|g" docker-compose.yml
    ```

3. Fill in `TZ`, `PUID`, and `PGID`:

    ```bash
    read -p "Enter your timezone [UTC]: " TZ && TZ=${TZ:-UTC} && \
    sed -i \
      -e "s|TZ=|TZ=$TZ|" \
      -e "s|PUID=|PUID=$(id -u)|" \
      -e "s|PGID=|PGID=$(id -g)|" \
      docker-compose.yml
    ```

!!! tip "Timezone format"

    Use a region format like `America/New_York` or `Europe/London`.

---

## Start DUMB with Docker Compose

Run the container in detached mode:

```bash
sudo docker compose up -d
```

Example output:

```bash
[+] Running 2/2
 Container DUMB  Started
 Network docker_default  Created
```

The container now runs in the background.

---

## Access the UI

By default:

- **DUMB Frontend**: `http://<host>:3005`
- **DUMB API**: `http://<host>:8000`

If you do not see the UI:

- Confirm the container is running: `sudo docker ps`
- Check logs: `sudo docker logs -f DUMB`
- Ensure ports are exposed in your `docker-compose.yml`
- See [Service ports](../reference/ports.md)

---

## Expose ports for direct UI access

Docker only exposes ports you explicitly map in your `docker-compose.yml`.
If a UI is not reachable, it usually means the port is not mapped.

Example: expose the DUMB frontend and API.

```yaml
services:
  DUMB:
    ports:
      - "3005:3005"
      - "8000:8000"
```

Example: expose an Arr service UI (Radarr).

```yaml
services:
  DUMB:
    ports:
      - "7878:7878"
```

!!! info "Reverse proxy or embedded UIs"

    If you use a reverse proxy (Traefik, Nginx, Caddy) or DUMB’s embedded UIs,
    you can avoid exposing every service port directly.

After updating ports, restart the stack:

```bash
sudo docker compose down
sudo docker compose up -d
```

---

## Common Docker commands

### Attach to the running container

```bash
sudo docker attach DUMB
```

### Detach without stopping

Press `Ctrl + P` then `Ctrl + Q` to detach and leave it running.

!!! important "Avoid Ctrl+C"

    `Ctrl+C` stops the container if it is attached to your terminal.

### View logs

```bash
sudo docker logs -f DUMB
```

### Stop and remove the container

```bash
sudo docker compose down
```

---

## Next steps

- Continue setup in the [DUMB Frontend](../services/dumb/dumb-frontend.md)
- Review [Configuration](../features/configuration.md)
- Use [Service ports](../reference/ports.md) to expose UIs as needed

---
title: Deploy with Portainer
icon: simple/portainer
---

## Deploying DUMB with Portainer

Portainer provides a user-friendly web interface for managing Docker containers
and stacks. This guide walks you through deploying **Debrid Unlimited Media
Bridge (DUMB)** using Portainer's stack deployment feature.

---

## Prerequisites

Before you begin:

- Docker must be installed and running
- Portainer must be installed and running
- Internet access (to pull the DUMB image)
- Host directories prepared for persistent data storage

!!! warning "Avoid the Snap package"

    Do not install Docker via Snap. The Snap build often breaks networking,
    volume mounts, and socket permissions required by DUMB. Use the official
    Docker install method instead.

---

## Install Docker (if needed)

If Docker is not installed yet, follow the [Docker deployment guide](docker.md)
up through **Confirm Docker and Compose are installed**.

---

## Install Portainer (quick start)

Use this if Portainer is not installed yet. It runs Portainer as a container.

```bash
docker volume create portainer_data
docker run -d \
  --name portainer \
  -p 9443:9443 \
  -p 9000:9000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  --restart=always \
  portainer/portainer-ce:latest
```

Then open `https://<host>:9443` and complete the setup wizard.

---

## Prepare the directory structure

Create folders for persistent config, logs, data, and mounts:

```bash
mkdir -p /home/$USER/docker/DUMB/config /home/$USER/docker/DUMB/log /home/$USER/docker/DUMB/data /home/$USER/docker/DUMB/mnt/debrid
```

!!! warning "Avoid `~` in Portainer stacks"

    Portainer does not reliably expand `~` in stack files. Use full paths such
    as `/home/<user>/docker/DUMB`.

---

## Where to get the Compose file

Pull the latest Compose file from GitHub:

```bash
curl -O https://raw.githubusercontent.com/I-am-PUID-0/DUMB/master/docker-compose.yml
```

---

## Edit paths and environment variables

Update the Compose file before pasting it into Portainer:

- Replace `/home/username/docker/DUMB` with your actual path (for example `/home/<user>/docker/DUMB`).
- Set `TZ` to your timezone (for example `America/New_York`).
- Set `PUID` and `PGID` to your user and group IDs.

Use this helper to patch the compose file:

```bash
read -p "Enter your DUMB base path [/home/$USER/docker/DUMB]: " DUMB_PATH
DUMB_PATH=${DUMB_PATH:-/home/$USER/docker/DUMB}
read -p "Enter your timezone [UTC]: " TZ
TZ=${TZ:-UTC}
PUID=$(id -u)
PGID=$(id -g)

sed -i \
  -e "s|/home/username/docker/DUMB|$DUMB_PATH|g" \
  -e "s|TZ=|TZ=$TZ|" \
  -e "s|PUID=|PUID=$PUID|" \
  -e "s|PGID=|PGID=$PGID|" \
  docker-compose.yml
```

---

## Copy the Compose content for Portainer

Print the file and copy it into Portainer’s **Web editor**:

```bash
cat docker-compose.yml
```

---

## Step-by-step deployment

### 1. Log into Portainer

Navigate to your Portainer instance (e.g., `http://localhost:9000`, or `https://localhost:9443`) and log in.

---

### 2. Navigate to Stacks

Click on **Stacks** in the left sidebar.

![Stacks Sidebar](../assets/images/portainer/stacks.PNG)

---

### 3. Click "Add Stack"

Click the **+ Add stack** button at the top-right.

![Add Stack](../assets/images/portainer/add_stack.PNG)

---

### 4. Configure the stack

Enter the following:

- **Name**: `dumb`
- **Build method**: Select `Web editor`
- **Web editor**: Paste the DUMB `docker-compose` content

![Create Stack](../assets/images/portainer/create_stack.PNG)

---

### 5. Deploy the stack

Click **Deploy the stack** to launch DUMB.

![Deploy the Stack](../assets/images/portainer/deploy_the_stack.PNG)

---

## That’s it!

Once deployed, DUMB will initialize and make its services available at their respective ports (e.g., DUMB Frontend at `:3005`, API at `:8000`, etc.).

You can now manage DUMB entirely through the **[DUMB Frontend](../services/dumb/dumb-frontend.md)**, or explore the [Configuration](../features/configuration.md) docs to adjust settings as needed.

---

## Expose ports (direct access)

Portainer only exposes the ports listed in your Compose file. If a UI is not
reachable, confirm the port mapping exists in the stack.

Example:

```yaml
ports:
  - "3005:3005" # DUMB Frontend
  - "8000:8000" # DUMB API
  - "7878:7878" # Radarr
```

After editing ports, click **Update the stack** to redeploy.

!!! info "Reverse proxy or embedded UIs"

    If you use a reverse proxy (Traefik, Nginx, Caddy) or DUMB’s embedded UIs,
    you can avoid exposing every service port directly.

---

## Viewing Logs for DUMB

Once your stack is deployed, you can view logs for the DUMB container:

1. Navigate to **Containers** from the left sidebar.
2. Click on the **DUMB** container name.
3. Go to the **Logs** tab.
4. Logs will stream live by default. You can scroll or refresh for updates.

!!! note "This is helpful for debugging service startup or checking configuration issues."

---

## Attach to the Container

To view live output or run interactive commands:

1. From the **Containers** page, click on the **DUMB** container.
2. Click the **Attach Console** button
3. Choose a shell (e.g., `sh`, `bash`, or `/venv/bin/python`) and click **Connect**.

!!! note "Use this for tasks like inspecting running processes, modifying configs, or testing tools inside the container."

---

## Console Access

You can also use the **Console** option to access the container shell:

1. From the **Containers** tab, click on **DUMB**.
2. Click the **Console** tab.
3. Choose the shell you wish to run.
4. Click **Connect**.

!!! note "Great for quick inspection or administrative tasks inside the container."

---

## Update the stack

To update DUMB:

1. Open **Stacks**
2. Click the `dumb` stack
3. Click **Edit**
4. Replace the Compose content with the latest version
5. Click **Update the stack**

If you have auto-update enabled in DUMB, you may not need to redeploy the stack
for application updates, but you should still update the Compose file if it
changes.

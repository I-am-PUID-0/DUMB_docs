---
title: Deploying on Proxmox
icon: simple/proxmox
---

## Deploying DUMB on Proxmox (LXC Container)

This guide will walk you through deploying **DUMB** inside a lightweight **Ubuntu-based LXC container** on **Proxmox VE**.

---

## Prerequisites
- Proxmox VE installed
- Internet access on the host
- Basic knowledge of Proxmox shell and web UI

---

## Create an Ubuntu LXC Container
You can automate Ubuntu LXC creation with the following community script:

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/community-scripts/ProxmoxVE/main/ct/ubuntu.sh)"
```

!!! note "This will download and install an Ubuntu container in Proxmox."

---

## LXC Configuration for Docker + Fuse Support

To run nested Docker and FUSE workflows inside an LXC, update both the
**container config** and the **Proxmox host**, then make propagation persistent.
These settings materially reduce LXC isolation. Use a dedicated, trusted LXC;
do not treat it as a strong security boundary for untrusted workloads.

---

### Update the LXC Config File 
!!! note "`<CTID>` is the container ID."

1. **Stop the container:**

    ```bash
    pct stop <CTID>
    ```

2. **Edit the container config file:**

    ```bash
    nano /etc/pve/lxc/<CTID>.conf
    ```

3. **Ensure the following lines are present:**

    ```ini
    features: nesting=1
    lxc.cgroup2.devices.allow: a
    lxc.cgroup2.devices.allow: c 10:229 rwm
    lxc.mount.entry: /dev/fuse dev/fuse none bind,create=file
    lxc.mount.entry: /mnt/docker-mounts mnt/docker-mounts none bind,create=dir
    lxc.apparmor.profile: unconfined
    ```

!!! note
    Don't restart the LXC until the below sections have been completed. 
---

### Configure Host Bind Mount

1. On the **Proxmox host**, create the mount target and bind it:

    ```bash
    mkdir -p /mnt/docker-mounts
    mount --bind /mnt/docker-mounts /mnt/docker-mounts
    mount --make-rshared /mnt/docker-mounts
    ```

---

### Make the Mount Persistent (Recommended)

!!! tip "This ensures the bind mount is restored after reboots."

#### Option A: Use `/etc/fstab` and manually set the mount propagation after reboot

1. Open the file:

    ```bash
    nano /etc/fstab
    ```

2. Add this line at the bottom:

    ```bash
    /mnt/docker-mounts /mnt/docker-mounts none bind 0 0
    ```

3. After a reboot, paste the following 

    ```bash
    mount --make-rshared /mnt/docker-mounts
    ```

---

#### Option B: Automate `rshared` with `systemd` (Optional, but recommended)

!!! tip "This ensures the bind mount propagation is set after reboots."

To persist the `rshared` behavior across boots:

1. Create a new service file:

    ```bash
    nano /etc/systemd/system/mnt-docker-mounts-rshared.service
    ```

2. Paste the following:

    ```ini
    [Unit]
    Description=Make /mnt/docker-mounts rshared
    After=local-fs.target
    RequiresMountsFor=/mnt/docker-mounts

    [Service]
    Type=oneshot
    ExecStart=/bin/mount --make-rshared /mnt/docker-mounts
    RemainAfterExit=true

    [Install]
    WantedBy=multi-user.target
    ```

3. Reload systemd and enable the service:

    ```bash
    systemctl daemon-reexec
    systemctl enable --now mnt-docker-mounts-rshared.service
    ```

---

## Add and configure a Docker operator inside the LXC

Use a non-root host/LXC account to manage Compose and set its UID/GID as DUMB's
`PUID`/`PGID`. The container entrypoint itself still starts with the privileges
declared by the maintained Compose file so it can prepare users, devices, and
mounts; `PUID`/`PGID` control the managed service identity.

1. **Start/Restart the container:**

    ```bash
    pct start <CTID>
    ```

    !!! note "`systemctl restart pve-container@<CTID>` may need to be used for changes to apply"

2. If not already created in the LXC, add a user such as `ubuntu`:

    ```bash
    adduser ubuntu
    usermod -aG sudo ubuntu
    ```

    Avoid adding a broad passwordless-sudo rule solely for DUMB.

3. Find the UID/GID needed for Compose `PUID` and `PGID`:

    ```bash
    id ubuntu
    ```

    Example output:

    ```text
    uid=1000(ubuntu) gid=1000(ubuntu)
    ```

---

## Define the Directory Structure inside the LXC

!!! note
    If you already have a directory structure you'd like to use, then you can skip this step.

1. Switch to the `ubuntu` user:

    ```bash
    su - ubuntu
    ```

2. Create a directory for docker in your user directory and change directories to docker.
    ```bash
    cd ~ && mkdir docker && cd docker
    ```

3. Create the DUMB directories.
    ```bash
    mkdir -p DUMB/config DUMB/log DUMB/data DUMB/mnt/debrid
    ```


--- 

## Install Docker inside the LXC

1. Run the official Docker install script:

    ```bash
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    ```

2. After installing Docker, verify it:
    ```bash
    docker --version
    docker compose version
    ```

3. Add your user to the docker group:
    ```bash
    sudo usermod -aG docker $USER
    ```

    Log out and back in before running Docker without `sudo`.


---

## Install Portainer inside the LXC (Optional) 
If you want to manage Docker visually via Portainer:

1. Create the Portainer data volume:
    ```bash
    docker volume create portainer_data
    ```

2. Start the Portainer container:

    ```bash
    docker run -d \
    -p 8000:8000 \
    -p 9443:9443 \
    --name portainer \
    --restart=always \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v portainer_data:/data \
    portainer/portainer-ce:latest
    ```

You can now manage Docker containers via the browser at: `https://<ip>:9443`

!!! note 
    On the first run of Portainer, you need to access the Web UI quickly to create your initial administrator user, which is crucial for accessing and managing your Docker environment. 
    
!!! tip
    If you can't access the UI after the initial setup, ensure the Portainer container is running and that the correct port is open. 
    You might need to restart the container if it timed out. 

For more, see the [Portainer Deployment Guide](./portainer.md).

---

## Use the current DUMB mounts

Inside the Docker-capable LXC, use the maintained four-mount layout:

```yaml
volumes:
  - /home/ubuntu/docker/DUMB/config:/config
  - /home/ubuntu/docker/DUMB/log:/log
  - /home/ubuntu/docker/DUMB/data:/data
  - /mnt/docker-mounts:/mnt/debrid:rshared
```

The `/data` mount persists service application state. `/mnt/debrid` is the separate mount/link tree; give that mount `rshared` propagation only when DUMB-created FUSE/rclone submounts must appear outside the DUMB container. Consumer containers should normally receive the same host path at `/mnt/debrid` with `rslave` propagation.

---

## Next Steps
Now that Docker (and optionally Portainer) are installed, continue with:

- [Deploy DUMB via Docker Compose](./docker.md)
- [Configure your stack with Portainer](./portainer.md)

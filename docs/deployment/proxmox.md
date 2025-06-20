---
title: Deploying on Proxmox
---

## 🧱 Deploying DMB on Proxmox (LXC Container)

This guide will walk you through deploying **DMB** inside a lightweight **Ubuntu-based LXC container** on **Proxmox VE**.

---

## ✅ Prerequisites
- Proxmox VE installed
- Internet access on the host
- Basic knowledge of Proxmox shell and web UI

---

## 🐧 Create an Ubuntu LXC Container
You can automate Ubuntu LXC creation with the following community script:

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/community-scripts/ProxmoxVE/main/ct/ubuntu.sh)"
```

!!! note "This will download and install an Ubuntu container in Proxmox."

---

## 🛠️ LXC Configuration for Docker + Fuse Support

To ensure DMB works correctly inside your LXC container (especially with Docker, rclone, and bind mounts), you’ll need to update both the **container config**, the **Proxmox host**, and optionally configure persistence across reboots.

---

### 🔧 Update the LXC Config File 
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

### 📂 Configure Host Bind Mount

1. On the **Proxmox host**, create the mount target and bind it:

    ```bash
    mkdir -p /mnt/docker-mounts
    mount --bind /mnt/docker-mounts /mnt/docker-mounts
    mount --make-rshared /mnt/docker-mounts
    ```

---

### 💾 Make the Mount Persistent (Recommended)

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

## 👤 Add and Configure a User inside the LXC (Required) 
!!! warning "DMB must be ran as any user other than root"

1. **Start/Restart the container:**

    ```bash
    pct start <CTID>
    ```

    !!! note "`systemctl restart pve-container@<CTID>` may need to be used for changes to apply"

2. If not already created in the LXC, add a user (`ubuntu`) and configure passwordless sudo:

    ```bash
    adduser ubuntu
    usermod -aG sudo ubuntu
    ```

3. Enable passwordless sudo (Optional):
    ```
    echo "ubuntu ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/ubuntu
    chmod 440 /etc/sudoers.d/ubuntu
    ```

    !!! tip
        To find the UID and GID (needed for `PUID` and `PGID` in your DMB config):
        ```bash
        id ubuntu
        ```

        Example output:
        ```bash
        uid=1000(ubuntu) gid=1000(ubuntu)
        ```

        Use these values in your `dmb_config.json` or docker-compose:
        ```json
        "puid": 1000,
        "pgid": 1000,
        ```

---

## 📁 Define the Directory Structure inside the LXC

!!! note
    If you already have a directory structure you'd like to use, then you can skip this step.

1. Switch to the `ubuntu` user:

    ```bash
    su ubuntu
    ```

2. Create a directory for docker in your user directory and change directories to docker.
    ```bash
    cd ~ && mkdir docker && cd docker
    ```

3. Create the DMB directories.
    ```bash
    mkdir -p DMB/config DMB/log DMB/Zurg/RD DMB/Riven/data DMB/Riven/mnt DMB/PostgreSQL/data DMB/pgAdmin4/data DMB/Zilean/data
    ```


--- 

## 🐳 Install Docker inside the LXC

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
    sudo groupadd docker
    sudo usermod -aG docker $USER
    ```


---

## 🚢 Install Portainer inside the LXC (Optional) 
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

## 🐳 Update Docker Bind Mount (Important)

When launching DMB or your media server, make sure the following mount is used:

Replace:
```yaml
- /home/username/docker/DMB/Zurg/mnt:/data:shared
```

With:
```yaml
- /mnt/docker-mounts:/data:rshared
```

!!! tip "This ensures proper visibility between `zurg`, `rclone`, and your media server inside the LXC container."

---

## 🚀 Next Steps
Now that Docker (and optionally Portainer) are installed, continue with:

- [Deploy DMB via Docker Compose](./docker.md)
- [Configure your stack with Portainer](./portainer.md)



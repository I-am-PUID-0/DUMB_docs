---
title: Deploy with WSL
description: Install DUMB on Windows through WSL2 and Docker Engine with systemd, storage mounts, networking, permissions, and startup configuration.
icon: fontawesome/brands/windows
---

## Deploying DUMB on Windows Setup Guide (Docker/WSL)

!!! warning "Docker Desktop"
    Ensure that Docker Desktop is not installed; if so, uninstall and reboot before proceeding.

This guide will walk you through setting up DUMB on a Windows system using a **lightweight Docker + WSL2 setup**, without relying on Docker Desktop. 

!!! tip "Want a graphical Docker experience?"

    Use [Portainer](portainer.md) if you want to manage containers, stacks,
    logs, and updates through a web interface. Complete the **WSL Install**,
    **Docker Install**, and **Mirrored Mode Networking** sections below, then
    switch to the
    [Portainer deployment guide](portainer.md) before deploying DUMB. Do not
    deploy DUMB with the CLI Compose guide first.

----

### WSL Install

1. From the Microsoft Store, install **Windows Subsystem for Linux (WSL)**

2. From the Microsoft Store, install **Ubuntu 22.04 LTS**

3. Follow the setup to create your Ubuntu username and password

4. From a Windows Command Prompt, paste the following:

    ```bash
    cd C:\WINDOWS\system32
    ```

5. Then set Ubuntu 22.04 as the default distro:

    ```bash
    wsl --setdefault Ubuntu-22.04
    ```

6. From the Windows app menu, start **Ubuntu 22.04**, then paste the following inside the terminal:

    !!! note
        This step is only required if sharing the mount outside of the container - e.g., to another media server, etc. 

    ```bash
    sudo apt update
    sudo apt upgrade -y
    sudo mount --make-rshared /
    ```

    !!! note
        `sudo mount --make-rshared /` does **not** persist after reboots. You’ll need to run it each time WSL2 or Windows is restarted.  
        
        Alternatively, see the [Ubuntu systemd service](../faq/rclone.md#ubuntu-systemd-service) guide to automate this at startup.

----

### Docker Install

1. Follow the [official Docker Engine install guide for Ubuntu](https://docs.docker.com/engine/install/ubuntu/)

2. Once Docker is installed, you can either:

    - Use the standard Docker CLI to create the container
    - Or follow the [Docker Deployment](docker.md) or [Portainer Deployment](portainer.md) guides for predefined setups

----

### Accessing the Mount on Windows

!!! note
    These steps are only required if sharing the mount outside of the container - e.g., to another media server, etc. 

1. From the Ubuntu terminal, open File Explorer in the current directory:

    ```bash
    explorer.exe .
    ```

2. A new File Explorer window will appear — you’re now inside the Ubuntu file system

3. Navigate to the mount location and copy the full path from the Explorer address bar

4. In another File Explorer window:
    - Click **This PC**
    - Right-click in the blank space and select **Add a network location**

5. In the popup:
    - Click **Next** twice
    - Paste the WSL path you copied

6. Complete the remaining prompts to finalize the mount

---


### Mirrored Mode Networking

Starting with **Windows 11 22H2**, WSL2 supports a new networking mode called **mirrored networking**, which improves compatibility and unlocks several new features by mirroring Windows' network interfaces into Linux.

#### Benefits of Mirrored Networking

-  Full **IPv6** support  
-  Access **Windows services** from WSL using `127.0.0.1`  
-  Improved VPN support (VPNs work in both Windows and WSL)  
-  Multicast compatibility  
-  Reach WSL services through the Windows host's network interfaces

---

#### Enabling Mirrored Mode

1. Open (or create) the `.wslconfig` file in your Windows home directory:

    ```powershell
    notepad $env:USERPROFILE\.wslconfig
    ```

2. Add the following sections:

    ```ini
    [wsl2]
    networkingMode=mirrored

    [experimental]
    hostAddressLoopback=true
    ```

    `hostAddressLoopback=true` allows Windows and WSL to reach each other by an
    IPv4 address assigned to the Windows host, such as
    `http://<windows-ip>:3005`. Without it, `localhost` still works, but the
    Windows host's other IPv4 addresses do not loop back into WSL. This setting
    only applies when `networkingMode=mirrored`.

3. Save the file, then restart WSL for the changes to take effect:

    ```powershell
    wsl --shutdown
    ```

    Then restart your distro from the Windows menu or run:

    ```bash
    wsl
    ```

---

#### Additional Notes

- [`hostAddressLoopback`](https://learn.microsoft.com/en-us/windows/wsl/wsl-config#experimental-settings)
  currently supports only IPv4 host addresses.
- You can combine this with [`autoProxy=true`](https://learn.microsoft.com/en-us/windows/wsl/wsl-config#configuration-settings-for-wslconfig) if you're using a proxy.
- This setting applies globally across all WSL2 instances.
- Windows Firewall and the Hyper-V firewall can still restrict inbound
  connections. Allow only the DUMB ports and trusted network profiles you
  intend to expose.

Next, choose whether to publish selected ports or use host networking in
[Docker Networking and Ports](networking.md).

---

Now you’re ready to run DUMB inside WSL2 with full Docker support — no Docker Desktop required!

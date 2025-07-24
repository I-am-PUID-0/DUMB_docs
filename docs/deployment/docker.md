---
title: Deploy with Docker
---


## 📦 Deploying DUMB with Docker

This guide will walk you through every step, from installing Docker to setting up and running the DUMB container. 

Whether you're new to Docker or just need a quick refresher, you'll be up and running in no time.


## ✅ Prerequisites

Before you begin, make sure you have the following:

- A system running **Ubuntu 20.04 or later**  
- A **non-root user** with `sudo` privileges  
- An active internet connection  
- Basic familiarity with using the **terminal**

!!! tip
    This guide assumes you're installing Docker on a fresh Ubuntu setup. If you're on Windows, refer to the [Windows Setup Guide (Docker/WSL)](wsl.md).


## 🐳 Install Docker
1. From Ubuntu, install Docker by pasting the following into the Ubuntu Command Line Interface (CLI); follow the prompts. 
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

!!! note 
    If you receive the following prompt during the Docker install, then follow the steps here: [Windows Setup Guide (Docker/WSL)](wsl.md)
    ```bash
    WSL DETECTED: We recommend using Docker Desktop for Windows.
    Please get Docker Desktop from https://www.docker.com/products/docker-desktop/
    ```

----

### ✅ Confirm Docker Install
1. Enter the following command:
```bash
docker compose version
```
2. If the output is similar to the below, then docker and docker compose were successfully installed:
```bash
ubuntu@DUMB:~$ docker compose version
Docker Compose version v2.24.2
```

## 📁 Define the Directory Structure

!!! note
    If you already have a directory structure you'd like to use, then you can skip this step.

1. Create a directory for docker in your user directory and change directories to docker.
```bash
cd ~ && mkdir docker && cd docker
```

2. Create the DUMB directories.
```bash
mkdir -p DUMB/config DUMB/log DUMB/Zurg/RD DUMB/Riven/data DUMB/PostgreSQL/data DUMB/pgAdmin4/data DUMB/Zilean/data DUMB/plex_debrid DUMB/plex DUMB/decypharr DUMB/cli_debrid DUMB/phalanx_db DUMB/mnt/debrid
```


## ✏️ Download and Edit the docker-compose.yml
!!! important 
    The docker-compose.yml file will need to be edited to include the necessary environment variable values.

1. Download the latest docker-compose.yml from the GitHub repository with the following:
```bash
curl -O https://raw.githubusercontent.com/I-am-PUID-0/DUMB/master/docker-compose.yml
```

2. Run the following command to update the paths in the `docker-compose.yml`
```bash
sed -i "s|/home/username/docker/DUMB|$HOME/docker/DUMB|g" docker-compose.yml
```

3. Run the following command to update the `docker-compose.yml`
!!! note "timezone"
    The bellow command defaults to `TZ=UTC`, update while running the command if desired


```bash
read -p "Enter your timezone [UTC]: " TZ && TZ=${TZ:-UTC} && \
sed -i \
  -e "s|TZ=|TZ=$TZ|" \
  -e "s|PUID=|PUID=$(id -u)|" \
  -e "s|PGID=|PGID=$(id -g)|" \
  docker-compose.yml

```


----

## 🚀 Start up the Docker Compose

!!! note 
    The following command starts Docker Compose in detached mode, meaning it runs in the background and frees up your terminal.

    If you **omit the `-d` flag**, Docker Compose will run in the **foreground**, streaming all container logs directly to your terminal. 

    This is useful for debugging or monitoring in real time, but you will need to open another terminal to run additional commands while it's running.

    - **Pressing `Ctrl + C`** will **shut down** all running containers.
    - To **exit without stopping** the container(s), you must start Docker Compose in detached mode using `-d`.

    ⚠️ There is no built-in "detach shortcut" when running in the foreground — to keep containers running after exit, always use the below command

```bash
sudo docker compose up -d
```

Example output:
```bash
ubuntu@DUMB:~/docker$ sudo docker compose up -d
[+] Running 1/2
 ⠋ Network docker_default  Created                                                                                                                                                       1.1s 
 ✔ Container DUMB       Started  
```

✅ Once started, the container will run in the background.


## 🎉 That’s It!

Once deployed, DUMB will initialize and make its services available at their respective ports (e.g., DUMB Frontend at `:3005`, API at `:8000`, etc.).

You can now manage DUMB entirely through the **[DUMB Frontend](../services/dumb-frontend.md)**, or explore the [Configuration](../features/configuration.md) docs to adjust settings as needed.

---

## 🛠️ Additional Useful Commands


### ▶️ Attach to the Running Container

```bash
sudo docker attach DUMB
```

### 🔄 Detach Without Stopping the Container


Press Ctrl + P followed by Ctrl + Q.

This sequence sends a signal to Docker to detach from the container while leaving it running in the background.

!!! important 
    Use this sequence rather than simply closing the terminal window or using Ctrl + C, as those actions might stop the container.

!!! note
    Remember, Ctrl + P + Ctrl + Q must be pressed in quick succession.

    You press Ctrl + P first, and while holding Ctrl, press Q.

    After this, you will be returned to your host terminal, and the container will continue to run in the background.



### 📜 View Docker Container Logs

To view the container logs, enter the following:

```bash
sudo docker container logs DUMB
```

Alternatively, use -f to follow the logs in real-time. 
!!! note "You can exit with Ctrl + C (this does not stop the container)."

```bash
sudo docker logs -f DUMB
```

### 🧯 Shutdown Docker Compose

```bash
sudo docker compose down
```

Example output:
```bash
ubuntu@DUMB:~/docker$ sudo docker compose down
[+] Running 2/2
✔ Container DUMB       Removed                                                                                                                                                      10.4s 
✔ Network docker_default  Removed     
```

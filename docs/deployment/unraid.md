---
title: unRAID Deployment
---

## 🧱 Deploying DMB on unRAID

This guide will walk you through deploying **Debrid Media Bridge (DMB)** on **unRAID** using the Community Applications plugin and Docker.

---

## ✅ Prerequisites
Before proceeding, ensure you have the following:

- A running **unRAID server** with Docker enabled.
- The **Community Applications** plugin installed.
- At least one unRAID **share** for persistent storage (e.g., `/mnt/user/appdata/DMB`).
- An understanding of basic Docker container and volume mapping in unRAID.

Optional but recommended:

- Installed media server such as **Plex**, **Jellyfin**, or **Emby**.
- A valid **Plex Token** (if using Plex integration).

---

## 🚀 Quick Start

### 1. **Install the DMB Template**
- Navigate to the **Apps** tab in unRAID.
- Search for `DMB` and select the **Debrid Media Bridge** template.
- Click **Install**.

### 2. **Path and Variable Configuration**

Ensure your **paths and environment variables** are set correctly:
- Mount all relevant paths (e.g., `/mnt`, `/config`, `/cache`) to valid unRAID shares.
- Set your `PUID` to `99` and `PGID` to `100` (used for `nobody:users` on unRAID).
- Set your timezone (`TZ`) appropriately (e.g., `America/New_York`).

### 3. **Fix Permissions (First-Time Only)**

> Docker on unRAID may create directories as `root`, causing permission issues. Fix this using the following method:

#### Terminal Method:
```bash
chown -R 99:100 /mnt/user/appdata/DMB
```

#### WebUI Method:
1. Go to **Shares** > locate your DMB share.
2. Click the `+` to expand.
3. Under **Owner**, set to `nobody` (user ID 99).

### 4. **Start the Container**
- Click **Start** in the Docker tab.
- Open the **Logs** tab to confirm successful startup.
- Look for a confirmation message that `riven frontend` has started.

---

## 🔁 Matching Paths in Plex, Jellyfin, Emby

Your **Media Server (Plex, Jellyfin, or Emby)** must have the same paths as DMB:

- DMB mounts:
  - `/mnt` (contains both Riven and Zurg content)
- In your media server:
  - Mount `/mnt` to `/mnt` as well.
  - Only add the **Riven path** (e.g., `/mnt/movies`, `/mnt/shows`) as libraries.

> ⚠️ Do **NOT** add `/data` or Zurg’s full rclone mount as libraries. Use only the **Riven symlinked** content.

---

## 📷 Example Screenshots

- DMB Docker setup:

![unraid-dmb-setup-1](https://github.com/user-attachments/assets/c11f95fa-710f-4b1d-af07-be0a81dbface)
![unraid-dmb-setup-2](https://github.com/user-attachments/assets/cb0a02b9-c986-4de8-9751-f615d48c2716)


- Plex Docker container setup:

![plex-dmb-paths](https://github.com/user-attachments/assets/0f3a9286-f81d-4d24-ab9a-5cf9a5bcee25)


- Plex UI Library paths:

![plex-paths1](https://github.com/user-attachments/assets/d5a450fe-33e5-465f-bce8-aca1587723d3)
![plex-paths2](https://github.com/user-attachments/assets/0af17df8-a0e0-4514-8cb2-090a1e628138)

---

## 🛠️ Additional Configuration

### 📺 Plex Token Setup
To enable features like watchlist syncing, you may need your Plex token:

1. Visit `https://plex.tv`, login.
2. Open any item > click the 3 dots > **View XML**.
3. At the end of the URL, copy the value after `Plex-Token=`.

---

### 🧠 Advanced Tools

To troubleshoot permissions or inspect mounts:
```bash
docker exec -w /mnt/movies dmb ls -Rl
```
To enter the container interactively:
```bash
docker exec -it dmb sh
```
Install Midnight Commander (optional):
```bash
apk add mc && mc
```

---

## 🧪 Jellyfin and Emby Notes

Both **Jellyfin** and **Emby** can work with DMB:

- Map `/mnt` into the containers.
- Add **only the Riven subpaths** (`/mnt/movies`, `/mnt/shows`) as libraries.

---

## 🧰 Troubleshooting
- Check logs via **Docker tab** > select DMB > **Logs**.
- Use `docker exec` or Midnight Commander to inspect file/folder structure.
- Common issues:
  - Wrong `PUID/PGID`
  - Paths not matching between DMB and your media server
  - Invalid Plex token
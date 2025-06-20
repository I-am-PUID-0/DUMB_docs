---
title: General FAQ
---

# General FAQ

Below are some common questions and solutions related to **DMB** that apply across multiple services or the platform as a whole.

---

## ❓ Frequently Asked Questions (FAQ)

### 💾 Will DMB use a lot of storage space?

That depends on how you configure it. Most services (like Zurg and Rclone) operate by streaming content from the debrid service, so **very little is permanently stored** on your local system — unless you're using `rclone` with VFS caching enabled.

If you're using VFS cache (recommended for Plex), ensure that the cache size is managed appropriately. See the [rclone configuration](../services/rclone.md) for more.

---

### 🧱 Do I need to install every service?

No — DMB is modular. You can enable or disable services in `dmb_config.json` under each service section. Some services (like `riven_backend` or `zurg`) provide core functionality, but others (like `pgadmin`) are optional tools to help you manage your setup.

---

### 🌍 Can I run DMB offline?

Most DMB services interact with external APIs (e.g., Real-Debrid, Plex, Trakt, TMDB, etc.), so **internet access is required** for normal operation. However, local database tools (e.g., pgAdmin) and UIs may still function offline for inspection.

---

### 🔄 What happens when I update DMB?

DMB includes **auto-update** functionality for most services. Depending on your configuration (`auto_update` and `auto_update_interval`), the system will check for new versions of services like Zurg, Riven, Zilean, etc.

You can configure update frequency and behavior in each service’s section of `dmb_config.json`.

---

### 🔒 Is DMB secure?

DMB is intended to run on your **local or private server**. Most services are, by default, bound to `127.0.0.1` and not exposed publicly unless explicitly configured by exposing ports in the Docker compose or changing the bound address.

Most of the web-based UIs and APIs lack any form of authentication. 

If you're exposing services externally (e.g., via Traefik or NGINX), consider using authentication layers like OAuth2, HTTPS, and firewalls.

---

### 🛠️ Can I use my own custom version of a service?

Yes — you can point most services to a custom branch or fork by editing the `repo_owner`, `repo_name`, `branch`, or `release_version` in its config section in `dmb_config.json`. This is especially useful if you are testing development builds or your own patches.

---

### 📦 Can I back up my DMB setup?

Absolutely. The most important files to back up are:

- `dmb_config.json`
- Any data directories (e.g., `/riven/backend/data`, `/zilean/app/data`, `/pgadmin/data`, `postgres_data`)

Regularly backing these up allows you to quickly restore your environment.

!!! warning "Exclude mounted paths from your backup" 
    Be sure to exclude any mounted paths (e.g., /data/rclone_RD) when backing up. 
    Otherwise, you’ll unintentionally download and archive the entire contents of your debrid services, which can be massive and unnecessary.

    Don’t believe me? Just ask Mr. Krabs.

---

### 📈 Can I monitor the system?

Yes — the DMB Frontend shows real-time logs, service logs, service status, and allows interactive config management. You can also access logs from the filesystem or via the DMB API (see [API docs](../api/index.md)).

---

### 🔗 What’s the difference between using rclone/Zurg mounts vs. symlinks (Riven, etc.) in my media server?

DMB supports **two methods of exposing content to your media server**, each with its own use case:

#### 1. **Direct Mount (Zurg/rclone)**

Mounting the WebDAV or remote storage directly using `rclone` (which often connects to a Zurg instance) gives you full access to all files in your debrid account.

**✅ Pros:**

- Access to **all debrid content**, including content not added by Riven
- Instant visibility of new files from your debrid service
- Useful for manual browsing or catching content missed by automation
- Allows content orchestration with [Debrid Media Manager](https://github.com/debridmediamanager/debrid-media-manager) (DMM)
- Less complexity when sharing mounts across the host or network

**⚠️ Cons:**

- File/folder naming is often **inconsistent or messy**
- Can lead to **Plex/Emby/Jellyfin misidentification**
- Media scanners may perform poorly due to large, unorganized libraries

#### 2. **Symlinked Mount (via Riven)**

Riven creates cleanly named **symlinks** pointing to content in the underlying Zurg/rclone mount (usually in a shared directory like `/data`). 

These symlinks are stored in a separate directory (like `/mnt`) and represent only **curated content** Riven has identified and processed.

**✅ Pros:**

- Only includes content that’s been properly scraped and sorted
- Directory structure and filenames are optimized for media servers
- More accurate **library scans** and faster detection
- Ideal for fully automated Plex/Emby/Jellyfin setups

**⚠️ Cons:**

- Only includes what Riven has processed — not your full debrid library
- Requires Riven to stay running and correctly configured
- If Riven settings are misconfigured, some content may not appear
- If Riven's database is lost or reset, all content must be scraped and added again
- Symlinks add complexity by requiring your media server to share the same exact container paths as defined in DMB's `dmb_config.json` — e.g., `/mnt` & `/data` must exist **exactly** the same inside your media server container or on the host when the media server is not containerized  

---


## 📎 Related Pages

- [Configuration Guide](../features/configuration.md)
- [Service Overview](../services/index.md)
- [DMB Frontend](../services/dmb-frontend.md)
- [Deployment](../deployment/index.md)


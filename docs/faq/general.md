---
title: General FAQ
---

# General FAQ

Below are some common questions and solutions related to **DUMB** that apply across multiple services or the platform as a whole.

---

## ❓ Frequently Asked Questions (FAQ)

### 💾 Will DUMB use a lot of storage space?

That depends on how you configure it. Most services (like Zurg and Rclone) operate by streaming content from the debrid service, so **very little is permanently stored** on your local system — unless you're using `rclone` with VFS caching enabled.

If you're using VFS cache (recommended for Plex), ensure that the cache size is managed appropriately. See the [rclone configuration](../services/dependent/rclone.md) for more.

---

### 🧱 Do I need to install every service?

No — DUMB is modular. You can enable or disable services in `dumb_config.json` under each service section. Some [core services](../services/core/index.md) (like `riven_backend`, `cli_debrid`, etc.) provide core functionality and have required [dependent services](../services/dependent/index.md) (like `zurg`, `rclone`, `postgres`, etc.), but others (like `pgadmin`) are [optional service](../services/optional/index.md) tools to help you manage your setup.

---

### 🌍 Can I run DUMB offline?

Most DUMB services interact with external APIs (e.g., Real-Debrid, Plex, Trakt, TMDB, etc.), so **internet access is required** for normal operation. However, local database tools (e.g., pgAdmin) and UIs may still function offline for inspection.

---

### 🔄 What happens when I update DUMB?

The image maintained for DUMB is automatically updated when one of the embedded services (like `riven_backend`, `cli_debrid`, etc.) have a new release available; thus, reducing the need to update to the latest release inside the container. For more info, see the [DUMB FAQ](../faq/dumb.md#does-the-dumb-image-have-the-latest-version-of-x) regarding finding what versions are built into the image. 

Alternatively, DUMB also includes **auto-update** functionality for most [services](../services/index.md). Depending on your configuration (`auto_update` and `auto_update_interval`), the system will check for new versions of services like Zurg, Riven, Zilean, etc.

You can configure update frequency and behavior in each service’s section of `dumb_config.json`.

---

### 🔒 Is DUMB secure?

DUMB is intended to run on your **local or private server**. Most services are, by default, bound to `127.0.0.1` and not exposed publicly unless explicitly configured by exposing ports in the Docker compose or changing the bound address.

Most of the web-based UIs and APIs lack any form of authentication. 

If you're exposing services externally (e.g., via Traefik or NGINX), consider using authentication layers like OAuth2, HTTPS, and firewalls.

---

### 🛠️ Can I use my own custom version of a service?

Yes — you can point most services to a custom branch or fork by editing the `repo_owner`, `repo_name`, `branch`, or `release_version` in its config section in `dumb_config.json`. This is especially useful if you are testing development builds or your own patches.

---

### 📦 Can I back up my DUMB setup?

Absolutely. The most important files to back up are:

- `dumb_config.json`
- Any data directories (e.g., `/riven/backend/data`, `/zilean/app/data`, `/pgadmin/data`, `postgres_data`, `plex`, etc)

Regularly backing these up allows you to quickly restore your environment.

!!! warning "Exclude mounted paths from your backup" 
    Be sure to exclude any mounted paths (e.g., /mnt/debrid) when backing up. 
    Otherwise, you’ll unintentionally download and archive the entire contents of your debrid services, which can be massive and unnecessary.

    Don’t believe me? Just ask Mr. Krabs.

---

### 📈 Can I monitor the system?

Yes — the DUMB Frontend shows real-time logs, service logs, service status, and allows interactive config management. You can also access logs from the filesystem or via the DUMB API (see [API docs](../api/index.md)).

---

### 🔗 What’s the difference between using rclone/Zurg mounts vs. symlinks (Riven, CLI Debrid, Decypharr, etc.) in my media server?

DUMB supports **two methods of exposing content to your media server**, each with its own use case:

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

#### 2. **Symlinked Mount (via Riven as an example)**

Riven creates cleanly named **symlinks** pointing to content in the underlying Zurg/rclone mount (usually in a shared directory like `/mnt/debrid/riven`). 

These symlinks are stored in a separate directory (like `/mnt/debrid/riven_symlinks`) and represent only **curated content** Riven has identified and processed.

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
- Symlinks add complexity by requiring your media server to share the same exact container paths as defined in DUMB's `dumb_config.json` — e.g., `/mnt/debrid` must exist **exactly** the same inside your media server container or on the host when the media server is not containerized  

---

### Host-Based Media Server: Mount Path Consistency

If your media server (such as Plex) runs **directly on the host** (not in Docker), it will access media files using the host's file system. In this setup, any symlinks created inside the DUMB container must resolve correctly **on the host**. This means the media paths inside the container must exactly match the paths used by the host.

Symlink resolution is based on absolute paths. If those paths don't exist or don't match outside the container, the symlinks will be broken or unusable by the media server.

#### Example: Using Riven's Symlink Media Directory

Suppose your media is mounted on the host at:

```
/docker/DUMB/mnt/debrid
```

Since Plex (or another media server) and the DUMB container need to both access this path and resolve symlinks, your Docker bind mount must look like:

```yaml
/docker/DUMB/mnt/debrid:/docker/DUMB/mnt/debrid
```

!!! note "This differs from the the default `/docker/DUMB/mnt/debrid:/mnt/debrid` internal path for the container by prepending `/docker/DUMB` or whatever the host side absolute path is for the `/mnt/debrid` directory"


Then, inside the `dumb_config.json`, you would also need to make sure you define the updated internal path for symlinks:

```json
"riven_backend": {
  "symlink_library_path": "/docker/DUMB/mnt/debrid/riven_symlinks",
}
```


This ensures that any symlinks Riven creates will remain valid on the host.


#### Simplified Approach Using Standard Paths

To simplify configuration and reduce the need to hardcode deep paths, you can instead use standard directory mounts like `/mnt`.

Docker Compose example:

```yaml
/mnt/debrid:/mnt/debrid
```

And then update the configuration:

!!! note "The below is the default path used in the container when configured through the onboarding process"

```json
"riven_backend": {
  "symlink_library_path": "/mnt/debrid/riven_symlinks",
}
```

Using standardized top-level paths makes your setup more portable and ensures symlinks will resolve correctly regardless of the underlying directory structure.


!!! tip "also review the [Default Mount Structure](../services/dependent/rclone.md#-default-mount-structure) and [Mount Propagation](../services/dependent/rclone.md#-mount-propagation) sections for additional details!

---

## 📎 Related Pages

- [Configuration Guide](../features/configuration.md)
- [Service Overview](../services/index.md)
- [DUMB Frontend](../services/dumb/dumb-frontend.md)
- [Deployment](../deployment/index.md)


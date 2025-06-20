---
title: Plex FAQ
---

# Plex FAQ

Below are some common questions and solutions related to when using **Plex** alongside **DMB** with services like Zurg and Rclone.

---
## ❓ Frequently Asked Questions (FAQ)

### ⚙️ Recommended Library Settings
To reduce the risk of excessive API calls to Real-Debrid (which can result in `423 Locked` errors or rate limits), the following Plex library settings should be disabled for each media library:

#### Library Settings (Per Library):
- **Video Preview Thumbnails**
- **Credits Detection**
- **Voice Detection**
- **Empty trash automatically after every scan** *(this can trigger deletions unnecessarily when using symlinked content)*

#### Global Settings (Settings > Library):
- **Scan my library automatically**
- **Run a partial scan when changes are detected**

These settings reduce the number of filesystem scans Plex performs, which can otherwise generate a high number of requests to mounted Real-Debrid content.

---

### ⚠️ Plex buffers a lot when playing content mounted via rclone
This is often caused by the lack of caching when streaming large files from cloud-mounted storage.

#### ✅ Recommended Solution
Enable **VFS (Virtual File System) cache** in your `rclone` configuration.

When using DMB, set the following environment variables:
```bash
RCLONE_VFS_CACHE_MODE=full
RCLONE_VFS_CACHE_MAX_SIZE=100G
RCLONE_VFS_CACHE_MAX_AGE=6h
```

These flags ensure that:
- The full file is cached locally before playback.
- Plex can smoothly read data without constant remote fetches.

> See [rclone docs](https://rclone.org/docs/#environment-variables)  
> or refer to [rclone Flags via Environment Variables](../services/rclone.md#-rclone-flags-via-environment-variables) for examples and formatting guidance.


## 📎 Related Pages
- [Zurg FAQ](../faq/zurg.md)
- [Rclone Configuration](../services/rclone.md)


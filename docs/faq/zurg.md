---
title: Zurg FAQ
---

# Zurg FAQ

Below are some common questions and solutions related to Zurg when used with **DMB**.

---

## ❓ Frequently Asked Questions (FAQ)

### ⚠️ `ERROR - rclone w/ RealDebrid subprocess: : IO error: File is temporarily unavailable: 423 Locked`
This error generally indicates that a **rate limit is being enforced by Real-Debrid**. It often occurs during media server scans that hit the API too frequently.

To mitigate this:
- If you're using **Plex**, this is commonly caused by automatic scans that trigger repeatedly.
- Alternatively, you may also need to impose a transactions (requests) per second limit with rclone.

See the [Plex FAQ](../faq/plex.md/#-recommended-library-settings) for more Plex-specific recommendations and details.
See the [rclone FAQ](../faq/rclone.md#i-think-i-might-be-rate-limited-by-the-debrid-service---seeing-423-errors) for more rclone-specific recommendations and details.

---

## 📎 Related Pages
- [Zurg Configuration](../services/zurg.md)
---
title: Zilean FAQ
icon: lucide/book-open
---

# Zilean FAQ

Below are some common questions and solutions related to Zilean when used with **DUMB**.

---

## Frequently Asked Questions (FAQ)

### Why is Zilean spamming my logs!?!

This is normal for a first-time run of Zilean. 

Zilean parses all the [Debrid Media Manager](https://github.com/debridmediamanager/debrid-media-manager) (DMM) hash lists and saves them into the PostgreSQL database. 

Then, it will run a scheduled update to add/remove any new hash content. 

!!! note "Depending on the system, the first-time run can take hours to days."

### Why does `dotnet restore` say that no .NET SDKs were found?

The production DUMB image intentionally contains the .NET runtime without the
full build SDK. The prebuilt Zilean service does not need an SDK to run. DUMB
downloads a managed local .NET 10 SDK under `/zilean/.dotnet-sdk` only when a
release, branch, or fork must be rebuilt inside the running container.

Current DUMB startup verifies that the selected `dotnet` executable exposes the
required SDK immediately before restore and logs both the SDK major and binary
path. If restore still returns the runtime-only error (normally exit code 145),
DUMB resets the managed local SDK and retries once. A persistent failure remains
visible in DUMB logs while the DUMB API and Frontend stay available.

When reporting this issue, include the lines before `dotnet_env_restore` that
contain `Using .NET SDK` or `Retrying zilean restore`. A container recreated from
an older cached `dev` image should be pulled again before retesting.

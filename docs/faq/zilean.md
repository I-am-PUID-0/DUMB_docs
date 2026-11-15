---
title: Zilean FAQ
description: Diagnose Zilean import logs, database setup and startup issues in DUMB, and check whether the indexer is ready for your media workflow.
icon: lucide/book-open
---

# Zilean FAQ


---


## Why does Zilean produce so many import logs? { #why-is-zilean-spamming-my-logs }

An initial hash-list import can be busy. Progress messages are expected; repeated exceptions or failed PostgreSQL connections need investigation.

Zilean parses all the [Debrid Media Manager](https://github.com/debridmediamanager/debrid-media-manager) (DMM) hash lists and saves them into the PostgreSQL database. 

Then, it will run a scheduled update to add/remove any new hash content. 

Import time depends on the source lists, database performance, and host. Check that progress continues rather than treating every long run as healthy.

## Why does `dotnet restore` say that no .NET SDKs were found?

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

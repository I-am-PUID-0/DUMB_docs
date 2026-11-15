---
title: About DUMB
description: Learn what DUMB manages, how its bundled services fit together, and where to find source code, support, and contribution information.
icon: lucide/info
---

# About DUMB

**Distributed Unlimited Media Bridge (DUMB)** installs and manages media applications in one container. It supports Debrid and Usenet workflows, Arr applications, media servers, request tools, and supporting databases and mounts.

The Python backend coordinates installation, configuration, dependencies, and service processes. The [dmbdb dashboard](frontend/index.md) provides onboarding, configuration, logs, metrics, updates, and embedded application UIs.

## Why put the services together?

Running a workflow and its media server in the same container gives them a shared view of library paths and FUSE mounts. It reduces the host mount configuration needed for playback. External Arr applications and media servers are also supported, but their paths, mount propagation, and permissions need separate planning.

DUMB coordinates upstream applications rather than replacing them. You still choose providers, configure application accounts and libraries, and review changes that affect your data. Automatic setup covers supported integrations; account and library tasks still need review.

<!-- dev:start -->
The retained [setup checklist](features/setup-checklist.md) shows automatic, manual, and unverified integration work.
<!-- dev:end -->

## Project resources

| Resource | Where to go |
|---|---|
| Backend and container source | [I-am-PUID-0/DUMB](https://github.com/I-am-PUID-0/DUMB) |
| Dashboard source | [nicocapalbo/dmbdb](https://github.com/nicocapalbo/dmbdb) |
| Documentation source | [I-am-PUID-0/DUMB_docs](https://github.com/I-am-PUID-0/DUMB_docs) |
| Container images | [Docker Hub](https://hub.docker.com/r/iampuid0/dumb) |
| Bugs and feature requests | [GitHub issues](https://github.com/I-am-PUID-0/DUMB/issues) |
| Community support | [Discord](https://discord.gg/8dqKUBtbp5) |
| Financial support | [GitHub Sponsors](https://github.com/sponsors/I-am-PUID-0) |

DUMB and dmbdb are open source under GPL-3.0. Each bundled application retains its own license and upstream project.

For a first installation, [start here](getting-started/index.md). To help improve the project, see [Contributing](contributing.md).

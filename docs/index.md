---
title: DUMB documentation
description: Set up and manage your DUMB media stack. Find plain-language guides for Docker, Debrid, Usenet, Plex, Jellyfin, Arr apps, updates and troubleshooting.
icon: lucide/home
hide:
  - navigation
  - toc
---

<div class="docs-home" markdown>

<section class="home-hero home-hero--product" markdown>

<div class="home-intro" markdown>

<p class="eyebrow">Distributed Unlimited Media Bridge</p>

# Your media stack.<br>One place to manage it.

DUMB brings your media services together in one installation. Choose the
apps you need, follow the setup, and manage them from a shared dashboard.

These guides help you get running, connect your services, and work out what to
do when something needs attention.

<div class="home-actions" markdown>

[Install DUMB :lucide-arrow-right:](deployment/index.md){ .md-button .md-button--primary }
[Explore the interface](frontend/index.md#ui-examples){ .md-button }

</div>

<p class="home-footnote">Already installed? <a href="frontend/index.md#choose-a-task">Find the guide for your next task.</a></p>

</div>

</section>

<!-- docs:showcase -->

## Deployment guides

Choose the system or tool where you will install DUMB. Each link opens the full guide for that platform.

- [Docker Compose](deployment/docker.md) · [Portainer](deployment/portainer.md) · [Dockge](deployment/dockge.md)
- [Unraid](deployment/unraid.md) · [Synology](deployment/synology.md) · [QNAP](deployment/qnap.md) · [TrueNAS SCALE](deployment/truenas.md)
- [Windows / WSL2](deployment/wsl.md) · [Proxmox LXC](deployment/proxmox.md)

[Compare deployment options](deployment/index.md) · [Before you install](getting-started/installation.md)

## What do you want to do?

<div class="grid cards home-paths" markdown>

-   :lucide-package-open: **Install for the first time**

    Choose your platform, prepare storage, and open the dashboard.

    [Start with installation :lucide-arrow-right:](getting-started/installation.md)

-   :lucide-route: **Connect your services**

    Pick a workflow and find the setup guide for each app.

    [Browse the service guides :lucide-arrow-right:](services/index.md)

-   :lucide-monitor: **Use the dashboard**

    Start and stop services, edit settings, and read their logs.

    [Learn the everyday controls :lucide-arrow-right:](frontend/index.md)

-   :lucide-refresh-cw: **Update with confidence**

    Understand version choices, update checks, and recovery options.

    [Manage service updates :lucide-arrow-right:](features/auto-update.md)

-   :lucide-life-buoy: **Get something working again**

    Find answers to common startup, connection, and playback problems.

    [Open troubleshooting :lucide-arrow-right:](faq/general.md)

-   :lucide-network: **Understand the connections**

    Check ports, storage paths, and how DUMB fits your network.

    [Review networking :lucide-arrow-right:](deployment/networking.md)

</div>

<div class="home-next" markdown>

### A small start is a good start

You do not need every service. Start with one workflow and one media server,
check that a file plays, then add the tools you need. DUMB manages the apps;
you still provide accounts, provider credentials, and your library choices.

[Choose your workflow](getting-started/index.md)

</div>

<div class="home-next" markdown>

### Get help or support the project

[Ask the community](https://discord.gg/8dqKUBtbp5) for setup help, [report a problem](contributing.md#report-a-problem), or [support the DUMB maintainer](https://github.com/sponsors/I-am-PUID-0). Each integrated app also has its own maintainers; their support links belong in its service guide.

</div>

<div class="home-reference" markdown>

**Want to understand the internals or use another method?** Geek mode adds explanations, API and command-line alternatives, and manual configuration examples. The main guides use the dashboard. You can also go straight to the
[API](api/index.md), [configuration reference](reference/index.md), or
[architecture](architecture/index.md). [Text documentation for agents](llms.txt).

</div>

</div>

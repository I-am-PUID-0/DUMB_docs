---
title: DUMB documentation
description: Set up and manage your DUMB media stack. Find plain-language guides for Docker, Debrid, Usenet, Plex, Jellyfin, Arr apps, updates and troubleshooting.
icon: lucide/home
hide:
  - navigation
  - toc
---

<div class="docs-home" markdown>

<section class="home-hero" markdown>

<div class="home-intro" markdown>

<p class="eyebrow">Distributed Unlimited Media Bridge</p>

# Your media stack.<br>One place to manage it.

DUMB brings your media services together in one Docker container. Choose the
apps you need, follow the setup, and manage them from a shared dashboard.

These guides help you get running, connect your services, and work out what to
do when something needs attention.

<div class="home-actions" markdown>

[Set up DUMB :lucide-arrow-right:](getting-started/installation.md){ .md-button .md-button--primary }
[Explore the services](services/index.md){ .md-button }

</div>

<p class="home-footnote">Already installed? <a href="frontend/index.md">Find your way around the dashboard.</a></p>

</div>

<div class="stack-map" markdown>

<div class="stack-map-heading" markdown>

![DUMB bridge logo](assets/images/logo.png){ width="46" height="46" }

**Choose what you run**

One dashboard. Your choice of services.

</div>

<div class="stack-map-row" markdown>

:lucide-play: **Watch and listen**

Plex · Jellyfin · Emby

</div>

<div class="stack-map-row" markdown>

:lucide-library: **Organize your library**

Sonarr · Radarr · Lidarr · Whisparr

</div>

<div class="stack-map-row" markdown>

:lucide-workflow: **Build a workflow**

Debrid · Usenet · Requests · Indexers

</div>

<div class="stack-map-footer" markdown>

:lucide-sliders-horizontal: Service controls · Logs · Updates · Metrics

</div>

</div>

</section>

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

<div class="home-reference" markdown>

**Looking for the technical detail?** Turn on Geek mode in the header to expand
configuration examples and implementation notes, or go straight to the
[API](api/index.md), [configuration reference](reference/index.md), or
[architecture](architecture/index.md). [Text documentation for agents](llms.txt).

</div>

</div>

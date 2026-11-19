---
title: DUMB documentation
description: Set up and manage your DUMB media stack. Find plain-language guides for Docker, Debrid, Usenet, Plex, Jellyfin, Arr apps, updates and troubleshooting.
icon: lucide/home
overview_video:
  name: Meet DUMB
  description: A captioned tour of DUMB workflows, installation choices, dashboard controls, logs, updates, appearance and resource metrics.
  content: assets/images/guides/overview/v1/dumb-overview.mp4
  thumbnail: assets/images/guides/overview/v1/poster.webp
  duration: PT1M54S
  upload_date: "2026-11-19"
hide:
  - navigation
  - toc
---

<div class="docs-home" markdown>

<section class="home-hero" markdown>

<div class="home-intro" markdown>

<p class="eyebrow">Distributed Unlimited Media Bridge</p>

# Your media stack.<br>One place to manage it.

DUMB brings your media services together in one installation. Choose the
apps you need, follow the setup, and manage them from a shared dashboard.

These guides help you get running, connect your services, and work out what to
do when something needs attention.

<div class="home-actions" markdown>

[Install DUMB :lucide-arrow-right:](deployment/index.md){ .md-button .md-button--primary }
[Use the dashboard](frontend/index.md){ .md-button }
[Watch the tour](#overview){ .md-button }

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

## Meet DUMB in two minutes { #overview }

See how the pieces fit together, then follow a few everyday dashboard tasks. This tour has on-screen captions and no narration; you can also read the transcript below.

<figure class="docs-visual docs-overview-figure">
<video id="dumb-overview" class="docs-frontend-video" controls playsinline preload="none" poster="assets/images/guides/overview/v1/poster.webp" aria-label="Captioned DUMB overview" aria-describedby="overview-caption">
  <source src="assets/images/guides/overview/v1/dumb-overview.mp4" type="video/mp4">
  <track kind="captions" src="assets/images/guides/overview/v1/captions.vtt" srclang="en" label="English">
  <track kind="chapters" src="assets/images/guides/overview/v1/chapters.vtt" srclang="en" label="Tour chapters">
  <p><a href="assets/images/guides/overview/v1/dumb-overview.mp4">Open the overview video</a>, or read the transcript below.</p>
</video>
<figcaption id="overview-caption" class="docs-visual-caption">DUMB Frontend 1.91.0 · example data. The tour reviews controls; it does not install an update or change a live system. Other versions and enabled services may look different.</figcaption>
</figure>

<details markdown="1">
<summary>Read the overview transcript and chapter times</summary>

**0:00 — Meet DUMB.** DUMB brings your media tools into one dashboard. Choose the applications and workflow you need.

Set up and manage the applications that find, organize and play your media.

**0:07 — How the pieces work together.** Start with one workflow and one media server. DUMB manages the apps; you choose how your library works.

- **Find or request:** Search directly or use an optional request app.
- **Prepare the library:** Your selected workflow handles the item and its library path.
- **Watch or listen:** A media server reads the configured library.

You provide the accounts, provider access and library choices.

**0:19 — Install on the host you use.** Use the deployment guide for your platform. Keep configuration and application data in persistent storage.

- **Pick your host:** Docker, a NAS, Windows with WSL2, or native Proxmox LXC.
- **Keep your data:** Prepare persistent folders and the required access.
- **Open DUMB:** Follow first-run setup in the dashboard.

**0:29 — See your selected services.** The dashboard shows the services in your DUMB installation. Open a service to review its status and controls.

**0:39 — Work with one application.** A service page brings its controls, settings and logs together. Use the embedded application to finish its own setup.

**0:49 — Read and filter service logs.** Logs show what the selected service is doing. Filter messages by name or level to focus on the problem.

**1:05 — Check an update before installing.** Open Tools → Updates and check for an available version. Review the result before choosing to install; this example only checks.

**1:25 — Make the dashboard comfortable.** Use appearance settings to choose a comfortable dashboard view. These preferences change how the frontend is displayed.

**1:35 — Check resource use.** Metrics help you review resource use and spot pressure. Use the charts alongside the affected service's logs.

**1:45 — Try one complete workflow.** Follow the deployment guide, then complete first-run setup. Test one import and playback before expanding your stack.

- **Install DUMB:** Follow the guide for your host.
- **Set up your apps:** Add the accounts, providers and library paths they need.
- **Test one item:** Check an import and playback before adding more services.

</details>

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

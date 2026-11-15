---
title: Documentation versions and Geek mode
description: Choose documentation for the latest stable DUMB release or development, and use Geek mode to show technical details without losing the everyday steps.
icon: lucide/git-branch
---

# Choose the right documentation

The selector in the site header switches between **Latest release** and
**Development**. It shows the DUMB version each channel covers. These numbers
refer to DUMB itself, rather than the documentation site's own releases.

| Choose | When to use it |
| --- | --- |
| **Latest release** | You run a stable DUMB image, such as `iampuid0/dumb:latest` or a numbered stable tag. |
| **Development** | You run `iampuid0/dumb:dev`, or you want to read about work awaiting a stable release. |

Switching keeps you on the same guide where it exists. A feature that has not
shipped shows an availability page in the release channel with a link to its
development guide. If there is no matching page, the selector opens the other
channel's homepage.

Check the DUMB version shown in the dashboard's **Settings → About** if the
instructions do not match your installation. The dashboard updates independently:
an older dashboard may not show controls supported by its backend, while a newer
one cannot add a missing backend feature to an older DUMB image. Check both
versions in **About**. Individually pinned service versions may also differ from
the examples.

## Use Geek mode when you want more detail

The guides begin with the steps most users need. **Geek mode** in the shared
header opens their technical details: configuration examples, API commands,
and notes about how the software works. Open technical sections have a light green
background and a **Geek detail** label while the mode is on. The header shows
**On** or **Off**, and your browser remembers the choice.

Some overview pages have no hidden technical sections. They show that clearly
when Geek mode is on; the mode does not add extra content to those pages.

You can also open any technical section individually. Essential warnings,
prerequisites, and recovery steps stay visible in either mode. Direct links to
a heading inside a closed section open it for you.

The [API](../api/index.md), [configuration reference](index.md), and
[architecture](../architecture/index.md) remain directly available in either
mode. Geek mode changes how details are displayed; it does not remove content.

## Spot development additions

Each page identifies its documentation channel and DUMB version. **Released
docs** use a blue-green label; **Development docs** use amber. Words accompany
the colors so you can tell them apart without relying on color alone.

In development guides, amber panels and small **Dev** badges identify additions
beyond the released documentation snapshot. A development-only feature page
also states which stable DUMB release does not include that feature. A newly
written guide for an existing feature is labelled **New guide** instead.

## How release docs stay current

The release channel is a snapshot of reviewed documentation. Later development
edits do not silently change its description of the stable image.

A scheduled watcher checks DUMB releases every six hours. When a new stable
release matches the reviewed development version and includes the backend
source covered by that review, the watcher also checks that the compatible
dashboard code has a published stable release. The docs workflow promotes that snapshot,
builds both channels, checks links and metadata, and publishes the site. A
maintainer can run the workflow manually to check sooner.

If the release version or source does not match the reviewed documentation,
promotion stops for a maintainer review. This prevents development features
from being presented as released. Shared theme and accessibility fixes can
still apply to both channels.

## Documentation for AI agents

Each channel provides an [`llms.txt`](../llms.txt) index and
[`llms-full.txt`](../llms-full.txt) with its complete documentation text.
Use the files from the channel matching the installed backend. Technical
details are included regardless of the browser's Geek mode preference.

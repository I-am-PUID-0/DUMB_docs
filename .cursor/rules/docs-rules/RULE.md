---
description: Clear, task-first writing for the DUMB documentation site.
globs:
  - "docs/**/*"
---

# Writing DUMB documentation

Write for someone who can install an app but may not know Docker, networking,
or a database. Start with what they want to do, then give the steps and a way
to check the result. Define unfamiliar terms where they first matter.

- Use one H1, sentence-case headings, short paragraphs, and concrete UI labels.
- Use numbered lists for actions and narrow tables for comparable settings.
- Keep essential prerequisites, data-loss warnings, and recovery instructions
  visible. Link to the full procedure rather than repeating it on several pages.
- Ordinary users work in the frontend. A complete primary task names the page
  and controls, describes what to enter or choose, says how to save/apply, and
  explains the expected result and the next check if it fails.
- Put optional configuration examples and internals inside native
  `<details class="geek-details" markdown="1">` blocks with descriptive
  `<summary>` labels. Geek mode expands these. Do not hide a required step.
- Geek sections explain why/how the system works and offer alternative API,
  command-line, environment or manual configuration methods. A long frontend
  procedure remains a user procedure; split it into clear tasks instead of
  putting it in Geek mode. Community and maintainer-support links stay visible.
- Show a simple frontend workflow diagram before implementation diagrams where
  the process is complex. Label the technical diagram as an explanation of
  connections and data flow, not another required setup procedure.
- Keep code examples valid and complete enough to adapt. Name the file being
  edited. Explain which values the reader must replace and how to apply changes.
- Use reserved example names and addresses. Never add actual credentials,
  account IDs, private endpoints, or personal information.
- Prefer facts and limitations to marketing. Avoid invented testimonials,
  "seamless" integrations, and unsupported promises of automatic setup.
- Each page needs a useful title, unique description, and Lucide icon in YAML
  front matter. Preserve existing URLs and linked heading IDs.
- Use real links and descriptive image alt text. Link Markdown pages relatively.
  Do not insert raw HTML links ending in `.md`; use Markdown links.
- Use icons sparingly. Avoid decorative emoji in authored guides.
  Synced upstream changelogs retain their original formatting.
- Use labeled code fences and blank lines around headings, lists, tabs, and
  admonition bodies. Divs containing Markdown need `markdown`.

## Versions and sources

Check the current backend/frontend source and the tagged stable implementation
before changing a behavioral claim. See README.md for channel markers and the
release snapshot mechanism. A feature available in development may be absent
from the stable image even if a new dashboard can display its controls.

## Verify

Build both channels with `poetry run python scripts/build_docs.py`, then run the
generated SEO/link audits and tests described in README.md. Inspect the rendered
page for long guides and layout changes. A successful static build does not
prove a user's service configuration or playback works.

"""Render accepted, channel-specific application media into static documentation."""

from __future__ import annotations

import json
import posixpath
import re
import shutil
from html import escape
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined
import yaml

if __package__:
    from .refresh_frontend_media import validate_channel
else:
    from refresh_frontend_media import validate_channel

MARKER = re.compile(r"<!-- docs:(showcase|visual-gallery|visual\s+scenario=([a-z][a-z0-9-]*)\s+type=(image|video)) -->")
URL_PREFIX = "dumb-docs-media:"
URL_ATTRIBUTE = re.compile(r'(\b(?:href|src|srcset|poster|data-(?:light|dark)-(?:video|poster))=")([^"]+)(")')

# Capture descriptions instruct the media runner. Reader copy belongs here so
# editorial changes do not invalidate the immutable screenshot packages.
PANEL_DESCRIPTIONS = {
    "dashboard": "See which services are running and open the app you need.",
    "service-controls": "Check a service's status and find its start, stop and restart controls.",
    "service-logs": "Filter a service's messages and pause refresh to read them at your own pace.",
    "realtime-logs": "Follow messages from across your DUMB installation in one place.",
    "updates": "See installed versions and check which updates are available.",
    "dependencies": "See which services an app needs before it can start.",
    "auto-restart": "Choose when DUMB should try to recover a service that stops responding.",
    "configuration": "Find the settings managed by DUMB and the app's own configuration.",
    "disabled-services": "Use the sidebar filters to find services that are turned off.",
    "metrics": "See CPU, memory, storage and network activity.",
    "settings-overview": "Find settings for appearance, connections, access and alerts.",
    "settings-appearance": "Choose a light or dark theme, or follow your device's appearance.",
    "settings-about": "Check the installed DUMB, frontend and service versions.",
    "settings-tokens": "Add the Plex and GitHub credentials used by your installation.",
    "settings-log-timestamps": "Choose the date and time format used in logs.",
    "settings-embedded-uis": "Choose whether supported apps open inside DUMB.",
    "settings-authentication": "Manage sign-in and local accounts for your installation.",
    "settings-auth-provider": "Choose local sign-in, an identity provider, or both.",
    "settings-notifications": "Choose where alerts go and which events you want to receive.",
    "settings-backups": "Review your backup and restore options.",
    "settings-advanced": "Enable Geek Mode to show additional service information and diagnostics.",
    "settings-support": "Find help, project links and ways to support the maintainers.",
    "login": "Sign in with your DUMB account.",
    "account-setup": "Create the first account for your DUMB installation.",
    "ai-overview": "Choose the services, time period and question for AI Assist to investigate.",
    "ai-provider": "Choose a local model and its server address for AI Assist.",
    "onboarding-services": "Choose the apps you want DUMB to set up.",
    "onboarding-preflight": "Check that DUMB is ready before continuing with setup.",
    "onboarding-provider": "Enter the credentials for your chosen provider.",
    "onboarding-companions": "Choose optional apps to use alongside your main services.",
    "onboarding-options": "Review the options for your selected services.",
    "onboarding-embedded-uis": "Choose whether supported service pages open inside DUMB.",
    "onboarding-installation": "Review the installation choices before starting your services.",
    "onboarding-review": "Check your selected services and settings before starting setup.",
    "setup-connections": "Complete the remaining connections between your apps.",
    "settings-onboarding": "Open guided setup again to review or change your service choices.",
    "settings-contributors": "Meet the people who contribute to DUMB and its frontend.",
    "api-configuration": "Review the DUMB API's settings and find its temporary debug logging controls.",
    "onboarding-progress": "Follow the progress messages while your selected services start.",
    "onboarding-result": "See the confirmation shown when guided setup finishes.",
    "onboarding-error": "Read the problem reported during setup before reviewing your settings.",
    "ai-provider-openai": "Choose an OpenAI model and add its API key for AI Assist.",
    "ai-provider-gemini": "Choose a Gemini model and add its API key for AI Assist.",
    "embedded-sonarr": "Use Sonarr inside DUMB without changing browser tabs.",
    "database-health": "Find monitoring options for a service's database.",
    "library-protection": "Choose how DUMB protects your Plex library during storage outages.",
    "symlink-tools": "Repair library links, take snapshots and set backup schedules.",
    "rclone-optimizer": "Review safety limits and test settings for InfiniDysk streaming.",
    "infinidysk-v2-install": "Choose the mount and backup options for a new InfiniDysk 2 installation.",
    "infinidysk-namespace-migration": "Review the choices for moving an older NzbDAV setup to InfiniDysk.",
    "postgres-migration": "Review the checks, backup requirements and migration choices for PostgreSQL.",
}
PANEL_TITLES = {
    "settings-advanced": "Advanced settings",
    "onboarding-provider": "Provider credentials",
    "onboarding-progress": "Setup progress",
    "onboarding-result": "Setup complete",
    "onboarding-error": "Setup needs attention",
    "infinidysk-v2-install": "Install InfiniDysk 2",
    "infinidysk-namespace-migration": "Move from NzbDAV to InfiniDysk",
    "postgres-migration": "Move from SQLite to PostgreSQL",
}


def protect_urls(html: str) -> str:
    """Keep generated directory-relative HTML links out of Markdown rewriting.

    Zensical rebases href/src/srcset as authored Markdown links, but leaves
    posters and data attributes alone. A temporary URI scheme preserves one
    consistent URL convention until the generated HTML is restored below.
    """
    def protect(match: re.Match) -> str:
        value = match[2]
        if value.startswith(("#", "/")) or re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", value):
            return match[0]
        return match[1] + URL_PREFIX + value + match[3]
    return URL_ATTRIBUTE.sub(protect, html)


def restore_urls(text: str) -> str:
    return text.replace(URL_PREFIX, "")


def restore_site_urls(output: Path) -> None:
    for path in output.rglob("*"):
        if path.suffix not in {".html", ".json"} or not path.is_file():
            continue
        text = path.read_text()
        if URL_PREFIX in text:
            path.write_text(restore_urls(text))


class MediaRenderer:
    """Validate media once per build; never fall back to another channel."""

    def __init__(self, root: Path, channel: str, settings: dict):
        self.root = root
        accepted = json.loads((root / "frontend-media.json").read_text())
        if accepted.get("schema_version") != 1:
            raise ValueError("Unsupported frontend media catalog")
        record = accepted["channels"][channel]
        self.media = validate_channel(root, channel, record)
        self.plan = self.media["plan"]
        if channel == "release" and self.plan["backend"]["commit"] != settings["source"]:
            raise ValueError("Documentation and media backend source pins disagree")
        if channel == "release" and self.plan["backend"]["version"] != settings["version"]:
            raise ValueError("Documentation and media backend versions disagree")
        self.notice = ""
        if channel == "dev" and (self.plan["backend"]["commit"] != settings["source"] or self.plan["frontend"]["commit"] != settings["frontend_source"]):
            self.notice = "The development interface may differ from the guides. Match the available controls to the DUMB and frontend versions shown here."
        self.catalog = json.loads((root / "scripts/frontend-visuals/capture-catalog.json").read_text())
        environment = Environment(loader=FileSystemLoader(root / "overrides"), undefined=StrictUndefined, autoescape=True)
        self.template = environment.get_template("partials/frontend-visuals.html").module

    def write_share_previews(self, output: Path) -> None:
        """Publish stable README image URLs from this channel's accepted media."""
        destination = output / "assets/images/guides/showcase/preview"
        destination.mkdir(parents=True, exist_ok=True)
        for row in self.media["showcase"]["files"]:
            if row["role"] == "animated":
                shutil.copyfile(
                    self.media["showcase_path"].parent / row["path"],
                    destination / (row["theme"] + ".webp"),
                )

    def context(self, relative: Path) -> tuple[dict, dict]:
        # Raw HTML asset links resolve from the generated directory URL. MkDocs
        # does not rewrite video posters or picture source attributes.
        current = relative.parent.as_posix() if relative.name == "index.md" else relative.with_suffix("").as_posix()
        current = current if current != "." else ""

        def link(target: str) -> str:
            value = posixpath.relpath(target, current or ".")
            return value + "/" if target.endswith("/") else value

        def asset(kind: str, row: dict) -> str:
            base = self.media[kind + "_path"].parent.relative_to(self.root / "docs").as_posix()
            return link(base + "/" + row["path"])

        catalog = {"frontend": self.plan["frontend"], "backend": self.plan["backend"], "panels": [], "notice": self.notice}
        urls = {"screens": {}, "videos": {}, "guides": {}, "showcase": {}, "gallery": link("frontend/") + "#ui-examples"}
        coverage = {(row["id"], row["theme"]): row for row in self.media["package"]["coverage"]}
        for scenario in self.catalog["scenarios"]:
            identifier = scenario["id"]
            if identifier not in PANEL_DESCRIPTIONS:
                raise ValueError("Add reader-facing gallery copy for scenario: " + identifier)
            states = [coverage[(identifier, theme)] for theme in ("dark", "light")]
            captured = all(row["status"] == "captured" for row in states)
            reason = "; ".join(dict.fromkeys(row.get("reason", "") for row in states if row.get("reason")))
            catalog["panels"].append({**scenario, "title": PANEL_TITLES.get(identifier, scenario.get("title", identifier.replace("-", " ").capitalize())), "description": PANEL_DESCRIPTIONS[identifier], "status": "captured" if captured else "unavailable", "reason": "Not available with these DUMB and frontend versions." if not captured else "", "technical_reason": reason})
            if scenario.get("features"):
                guide = scenario["features"][0]
                target = guide.removesuffix("index") if guide == "index" or guide.endswith("/index") else guide + "/"
                urls["guides"][identifier] = link(target)
            for row in self.media["package"]["files"]:
                if row.get("scenario") != identifier:
                    continue
                key = "screens" if row["kind"] == "image" else "videos"
                urls[key].setdefault(identifier, {})[row["theme"]] = asset("package", row)
        for row in self.media["showcase"]["files"]:
            role = row["role"]
            if row.get("theme"):
                urls["showcase"].setdefault(row["theme"], {})[role] = asset("showcase", row)
            else:
                urls["showcase"][role] = asset("showcase", row)
        return catalog, urls

    def render(self, text: str, relative: Path, *, for_build: bool = False) -> str:
        if not MARKER.search(text):
            return text
        catalog, urls = self.context(relative)

        def replace(match: re.Match) -> str:
            if match[1] == "showcase":
                return str(self.template.render_showcase(catalog, urls))
            if match[1] == "visual-gallery":
                return str(self.template.render_gallery(catalog, urls))
            identifier, kind = match[2], match[3]
            panel = next((row for row in catalog["panels"] if row["id"] == identifier), None)
            if panel is None:
                raise ValueError("Unknown application media scenario: " + identifier)
            if panel["status"] != "captured":
                return (
                    '<aside class="docs-visual-availability"><p class="docs-visual-caption">'
                    f'This screen is unavailable with DUMB {escape(self.plan["backend"]["version"])} '
                    f'and frontend {escape(self.plan["frontend"]["version"])}. See the guide for supported versions.</p></aside>'
                )
            if kind == "image":
                return str(self.template.render_panel(panel, urls, catalog))
            videos = urls["videos"][identifier]
            screens = urls["screens"][identifier]
            title = escape(panel["description"], quote=True)
            return (
                '<figure class="docs-frontend-demo"><video class="docs-frontend-video" controls playsinline preload="none" '
                f'poster="{escape(screens["light"])}" data-ui-video data-light-video="{escape(videos["light"])}" '
                f'data-dark-video="{escape(videos["dark"])}" data-light-poster="{escape(screens["light"])}" '
                f'data-dark-poster="{escape(screens["dark"])}" aria-label="{title}">'
                f'<source src="{escape(videos["light"])}" type="video/webm">'
                f'<p><a href="{escape(videos["light"])}">Open the demonstration</a>.</p></video>'
                f'<figcaption class="docs-visual-caption">{escape(panel["description"])} '
                f'DUMB {escape(self.plan["backend"]["version"])} · Frontend {escape(self.plan["frontend"]["version"])} · Example data.</figcaption></figure>'
            )

        result = MARKER.sub(lambda match: protect_urls(replace(match)) if for_build else replace(match), text)
        if "<!-- docs:showcase -->" in text:
            # The primary structured video identity follows the accepted package.
            header, body = result.split("---\n", 2)[1:]
            meta = yaml.safe_load(header)
            base = self.media["showcase_path"].parent.relative_to(self.root / "docs").as_posix()
            meta["overview_video"] = {
                "name": "Inside DUMB", "description": "A short preview of DUMB's actual interface: dashboard, onboarding, service tools, settings and metrics, with example data.",
                "content": base + "/light/hero.mp4", "thumbnail": base + "/light/poster.webp",
                "duration": f'PT{self.media["showcase"]["duration_seconds"]}S',
                "upload_date": self.media["showcase"]["captured_at"],
            }
            result = "---\n" + yaml.safe_dump(meta, sort_keys=False) + "---\n" + body
        return result

"""Render accepted, channel-specific application media into static documentation."""

from __future__ import annotations

import json
import posixpath
import re
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
            self.notice = "These development screenshots were refreshed after the guide text was last reviewed. Use the application versions shown with each image."
        self.catalog = json.loads((root / "scripts/frontend-visuals/capture-catalog.json").read_text())
        environment = Environment(loader=FileSystemLoader(root / "overrides"), undefined=StrictUndefined, autoescape=True)
        self.template = environment.get_template("partials/frontend-visuals.html").module

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
            states = [coverage[(identifier, theme)] for theme in ("dark", "light")]
            captured = all(row["status"] == "captured" for row in states)
            reason = "; ".join(dict.fromkeys(row.get("reason", "") for row in states if row.get("reason")))
            catalog["panels"].append({**scenario, "title": scenario.get("title", identifier.replace("-", " ").capitalize()), "status": "captured" if captured else "unavailable", "reason": "Not supported by the selected frontend and DUMB versions." if not captured else "", "technical_reason": reason})
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
                    f'This view is unavailable with DUMB {escape(self.plan["backend"]["version"])} '
                    f'and frontend {escape(self.plan["frontend"]["version"])}. Read the guide for version availability.</p>'
                    '<details class="geek-details"><summary>Technical availability details</summary>'
                    f'<p>{escape(panel["technical_reason"])}</p></details></aside>'
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
                f'DUMB {escape(self.plan["backend"]["version"])} · Frontend {escape(self.plan["frontend"]["version"])} · isolated example data. '
                'Follow the written steps for your own installation.</figcaption></figure>'
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

#!/usr/bin/env python3
"""Check that normal readers can find deployment guides and complete UI paths."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

PLATFORMS = tuple(
    "docker portainer dockge unraid wsl proxmox synology qnap truenas".split()
)
HUBS = (
    "index.html",
    "getting-started/index.html",
    "getting-started/installation/index.html",
    "deployment/index.html",
)
SERVICES = {
    "infinidysk": "first-start",
    "decypharr": "first-start",
    "cli-debrid": "first-start",
    "riven-backend": "initial-setup-riven-backend",
    "altmount": "first-start-checklist",
}
VOID = set(
    "area base br col embed hr img input link meta param source track wbr".split()
)


@dataclass
class Context:
    tag: str = ""
    article: bool = False
    geek: bool = False
    hidden: bool = False
    code: bool = False
    header: bool = False


@dataclass
class Link:
    href: str
    article: bool
    geek: bool
    visible: bool
    classes: set[str]
    header: bool = False
    home: bool = False
    label: str = ""


class ReaderPage(HTMLParser):
    """Record actual reader links and diagrams, excluding navigation and code."""

    def __init__(self, html: str):
        super().__init__()
        self.canonical = ""
        self.links: list[Link] = []
        self.images: list[tuple[str, bool]] = []
        self.setup_headings: set[str] = set()
        self.mermaid: list[bool] = []
        self.stack = [Context()]
        self.active_link: Link | None = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        classes = set(str(values.get("class") or "").split())
        parent = self.stack[-1]
        context = Context(
            tag,
            parent.article or tag == "article",
            parent.geek or (tag == "details" and "geek-details" in classes),
            parent.hidden
            or "hidden" in values
            or values.get("aria-hidden") == "true"
            or (tag == "details" and "open" not in values),
            parent.code or tag in {"code", "pre", "script", "style"},
            parent.header or tag == "header",
        )
        visible = context.article and not context.geek and not context.hidden
        if tag == "link" and values.get("rel") == "canonical":
            self.canonical = str(values.get("href") or "")
        if tag == "a" and "href" in values and not context.code:
            self.active_link = Link(
                str(values["href"] or ""),
                context.article,
                context.geek,
                not context.hidden,
                classes,
                context.header,
                "data-docs-home" in values,
            )
            self.links.append(self.active_link)
        if tag == "img" and values.get("src") and not context.code:
            self.images.append((str(values["src"]), visible))
        if tag in {"h2", "h3"} and visible and values.get("id"):
            self.setup_headings.add(str(values["id"]))
        if context.article and classes.intersection({"mermaid", "language-mermaid"}):
            self.mermaid.append(context.geek)
        if tag not in VOID:
            self.stack.append(context)

    def handle_endtag(self, tag):
        if tag == "a":
            self.active_link = None
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if self.active_link and not self.stack[-1].code:
            self.active_link.label += data


def local_path(href: str, canonical: str, channel_url: str) -> str | None:
    target, home = urlparse(urljoin(canonical, href)), urlparse(channel_url)
    if (target.scheme, target.netloc) != (home.scheme, home.netloc):
        return None
    return unquote(target.path).rstrip("/") + "/"


def funding_link(href: str) -> bool:
    target = urlparse(href)
    host = (target.hostname or "").lower().removeprefix("www.")
    return host == "buymeacoffee.com" or (
        host == "github.com" and target.path.startswith("/sponsors/")
    )


def header_home_errors(document: ReaderPage, home_url: str, label: str) -> list[str]:
    anchors = [
        link
        for link in document.links
        if link.header and link.home and link.visible and not link.geek
    ]
    logos = [link for link in anchors if "md-logo" in link.classes]
    names = [link for link in anchors if "docs-brand" in link.classes]
    if len(logos) != 1 or len(names) != 1 or logos[0] is names[0]:
        return [f"{label}: header needs separate logo and DUMB home anchors"]
    errors = []
    if " ".join(names[0].label.split()) != "DUMB":
        errors.append(f"{label}: header brand must read DUMB")
    homepage = local_path("./", home_url, home_url)
    for link in (logos[0], names[0]):
        if local_path(link.href, document.canonical, home_url) != homepage:
            errors.append(
                f"{label}: header home anchor does not target its channel homepage"
            )
    return errors


def audit_reader_paths(site: Path) -> list[str]:
    errors: list[str] = []
    cache: dict[Path, ReaderPage] = {}

    def page(path: Path) -> ReaderPage | None:
        if not path.is_file():
            errors.append(f"{path.relative_to(site)}: missing reader page")
            return None
        if path not in cache:
            cache[path] = ReaderPage(path.read_text(encoding="utf-8"))
        return cache[path]

    for channel in ("", "dev"):
        root = site / channel
        home = page(root / "index.html")
        if home is None or not home.canonical:
            errors.append(f"{channel or 'release'}: homepage canonical URL is required")
            continue
        expected_hub = local_path("deployment/", home.canonical, home.canonical)
        for relative in HUBS:
            document = page(root / relative)
            if document is None:
                continue
            errors.extend(
                header_home_errors(
                    document, home.canonical, f"{channel or 'release'}/{relative}"
                )
            )
            body_paths = {
                local_path(link.href, document.canonical, home.canonical)
                for link in document.links
                if link.article and link.visible and not link.geek
            }
            for platform in PLATFORMS:
                expected = local_path(
                    f"deployment/{platform}/", home.canonical, home.canonical
                )
                if expected not in body_paths:
                    errors.append(
                        f"{channel or 'release'}/{relative}: no visible article link to {platform} deployment"
                    )
            if relative == "index.html" and expected_hub not in body_paths:
                errors.append(
                    f"{channel or 'release'}/index.html: no visible Deployment overview link"
                )
        if not any(
            "md-tabs__link" in link.classes
            and local_path(link.href, home.canonical, home.canonical) == expected_hub
            for link in home.links
        ):
            errors.append(
                f"{channel or 'release'}: Deployment is missing from the top navigation"
            )
        for service, heading in SERVICES.items():
            document = page(root / f"services/core/{service}/index.html")
            if document is None:
                continue
            errors.extend(
                header_home_errors(
                    document, home.canonical, f"{channel or 'release'}/{service}"
                )
            )
            asset = (
                "riven" if service == "riven-backend" else service
            ) + "-user-workflow.svg"
            if not any(
                Path(urlparse(source).path).name == asset and visible
                for source, visible in document.images
            ):
                errors.append(
                    f"{channel or 'release'}/{service}: frontend workflow figure is not visible outside Geek mode"
                )
            if heading not in document.setup_headings:
                errors.append(
                    f"{channel or 'release'}/{service}: frontend setup section is not visible outside Geek mode"
                )
            if not document.mermaid or not all(document.mermaid):
                errors.append(
                    f"{channel or 'release'}/{service}: detailed workflow must be inside Geek mode"
                )
            if service == "infinidysk" and not any(
                link.article
                and link.visible
                and not link.geek
                and urlparse(link.href).netloc == "buymeacoffee.com"
                and urlparse(link.href).path.rstrip("/") == "/hoivikaj"
                for link in document.links
            ):
                errors.append(
                    f"{channel or 'release'}/infinidysk: maintainer support link is not visible in the article"
                )
    for path in sorted(site.rglob("*.html")):
        document = page(path)
        if document:
            for link in document.links:
                if link.geek and funding_link(link.href):
                    errors.append(
                        f"{path.relative_to(site)}: maintainer support is hidden inside Geek mode"
                    )
    print(
        f"Reader paths: 2 channels, 18 priority pages, {len(cache)} HTML pages; errors: {len(errors)}"
    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site", nargs="?", type=Path, default=Path("site"))
    errors = audit_reader_paths(parser.parse_args().site)
    for error in errors:
        print("ERROR:", error)
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())

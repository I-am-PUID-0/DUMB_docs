#!/usr/bin/env python3
"""Audit one channel of the assembled DUMB documentation site."""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from collections import Counter
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

BASE_URL = "https://dumbarr.com/"
INDEX_ROBOTS = (
    "index, follow, max-image-preview:large, " "max-snippet:-1, max-video-preview:-1"
)
NOINDEX_ROBOTS = "noindex, follow"
NOT_FOUND_DESCRIPTION = "The requested DUMB documentation page could not be found."
ROBOTS_TEXT = "User-agent: *\nAllow: /\n\nSitemap: https://dumbarr.com/sitemap.xml\n"


class PageParser(HTMLParser):
    """Collect SEO metadata, fragment targets, and referenced resources."""

    def __init__(self) -> None:
        super().__init__()
        self.title_parts: list[str] = []
        self.in_title = False
        self.meta: list[dict[str, str | None]] = []
        self.links: list[dict[str, str | None]] = []
        self.hrefs: list[str] = []
        self.images: list[dict[str, str | None]] = []
        self.image_sources: list[str] = []
        self.ids: set[str] = set()
        self.h1_count = 0
        self.json_ld: list[str] = []
        self.in_json_ld = False
        self.json_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(str(values["id"]))
        if tag == "a" and values.get("name"):
            self.ids.add(str(values["name"]))
        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "meta":
            self.meta.append(values)
        elif tag == "link":
            self.links.append(values)
        elif tag == "a" and values.get("href"):
            self.hrefs.append(str(values["href"]))
        elif tag == "img":
            self.images.append(values)
        elif tag == "script" and values.get("type") == "application/ld+json":
            self.in_json_ld = True
            self.json_parts = []
        if tag in {"img", "source"} and values.get("srcset"):
            # A data URL can contain commas and is self-contained; ordinary
            # image candidates use a URL followed by an optional size descriptor.
            srcset = str(values["srcset"])
            if not srcset.lstrip().startswith("data:"):
                self.image_sources.extend(
                    entry.strip().split()[0]
                    for entry in srcset.split(",")
                    if entry.strip()
                )

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        elif tag == "script" and self.in_json_ld:
            self.in_json_ld = False
            self.json_ld.append("".join(self.json_parts).strip())

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self.in_json_ld:
            self.json_parts.append(data)


def meta_value(parser: PageParser, key: str, value: str) -> str:
    for attrs in parser.meta:
        if attrs.get(key) == value:
            return str(attrs.get("content") or "")
    return ""


def link_value(parser: PageParser, rel: str) -> str:
    for attrs in parser.links:
        if rel in str(attrs.get("rel") or "").split():
            return str(attrs.get("href") or "")
    return ""


def parse_page(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def page_url(site_dir: Path, path: Path, base_url: str = BASE_URL) -> str:
    """Return the channel URL corresponding to one generated HTML file."""
    relative = path.relative_to(site_dir).as_posix()
    base_url = base_url.rstrip("/") + "/"
    if relative == "index.html":
        return base_url
    if relative.endswith("/index.html"):
        relative = relative.removesuffix("index.html")
    return base_url + relative


def assembled_location(
    site_dir: Path, base_url: str, development: bool
) -> tuple[Path, str]:
    """Map this channel to its assembled root and public deployment prefix."""
    public_path = unquote(urlparse(base_url).path).rstrip("/") + "/"
    if development:
        # site/dev is one channel within the assembled site, which can itself
        # be served below a prefix such as /project/ on a GitHub Pages host.
        parent_path = public_path.rstrip("/").rsplit("/", 1)[0] + "/"
        return site_dir.resolve().parent, parent_path
    return site_dir.resolve(), public_path


def local_target(
    site_dir: Path,
    current_url: str,
    href: str,
    *,
    base_url: str = BASE_URL,
    development: bool = False,
) -> tuple[Path | None, str]:
    """Resolve a published local URL; external resources need no disk check."""
    target = urlparse(urljoin(current_url, href))
    base = urlparse(base_url)
    if (target.scheme.lower(), target.netloc.lower()) != (
        base.scheme.lower(),
        base.netloc.lower(),
    ):
        return None, ""
    root, prefix = assembled_location(site_dir, base_url, development)
    public_path = unquote(target.path)
    if not public_path.startswith(prefix):
        # Another site can own paths outside this deployment's public prefix.
        return None, ""
    candidate = (root / public_path.removeprefix(prefix)).resolve()
    if not candidate.is_relative_to(root):
        return root / "__invalid_path_outside_site__", unquote(target.fragment)
    if candidate.is_dir() or not candidate.suffix:
        candidate = candidate / "index.html"
    return candidate, unquote(target.fragment)


def resolve_local_target(
    site_dir: Path,
    current_url: str,
    href: str,
    *,
    base_url: str = BASE_URL,
    development: bool = False,
    parsed_pages: dict[Path, PageParser] | None = None,
) -> bool:
    """Validate local files and HTML fragments, including cross-channel links."""
    target, fragment = local_target(
        site_dir, current_url, href, base_url=base_url, development=development
    )
    if target is None:
        return True
    if not target.is_file():
        return False
    if fragment and target.suffix.lower() == ".html":
        cache = parsed_pages if parsed_pages is not None else {}
        if target not in cache:
            cache[target] = parse_page(target)
        return fragment in cache[target].ids
    return True


def audit_site(
    site_dir: Path, *, base_url: str | None = None, development: bool = False
) -> list[str]:
    """Audit one channel while resolving links within the assembled artifact."""
    base_url = (base_url or BASE_URL + ("dev/" if development else "")).rstrip(
        "/"
    ) + "/"
    site_dir = site_dir.resolve()
    errors: list[str] = []
    rows: list[dict[str, str]] = []
    html_paths = sorted(
        path
        for path in site_dir.rglob("*.html")
        if development or path.relative_to(site_dir).parts[0] != "dev"
    )
    parsed_pages: dict[Path, PageParser] = {}

    def resolves(current_url: str, reference: str) -> bool:
        return resolve_local_target(
            site_dir,
            current_url,
            reference,
            base_url=base_url,
            development=development,
            parsed_pages=parsed_pages,
        )

    if not html_paths:
        errors.append("No HTML pages found")

    for path in html_paths:
        parser = parsed_pages.setdefault(path, parse_page(path))
        relative = path.relative_to(site_dir).as_posix()
        current_url = page_url(site_dir, path, base_url)
        title = unescape("".join(parser.title_parts)).strip()
        description = meta_value(parser, "name", "description")
        robots = meta_value(parser, "name", "robots")
        canonical = link_value(parser, "canonical")
        og_title = meta_value(parser, "property", "og:title")
        og_description = meta_value(parser, "property", "og:description")
        og_url = meta_value(parser, "property", "og:url")
        twitter_title = meta_value(parser, "name", "twitter:title")
        twitter_description = meta_value(parser, "name", "twitter:description")
        rows.append(
            dict(
                relative=relative,
                title=title,
                description=description,
                robots=robots,
                canonical=canonical,
                og_title=og_title,
            )
        )

        if parser.h1_count != 1:
            errors.append(f"{relative}: expected one H1, found {parser.h1_count}")
        for href in parser.hrefs:
            if not resolves(current_url, href):
                errors.append(f"{relative}: unresolved href {href}")
        favicon = link_value(parser, "icon")
        if not favicon:
            errors.append(f"{relative}: missing favicon")
        elif not resolves(current_url, favicon):
            errors.append(f"{relative}: unresolved favicon {favicon}")
        for attrs in parser.images:
            if "alt" not in attrs:
                errors.append(f"{relative}: image missing alt attribute")
            source = str(attrs.get("src") or "")
            if not source:
                errors.append(f"{relative}: image missing src")
            elif not resolves(current_url, source):
                errors.append(f"{relative}: unresolved image {source}")
        for source in parser.image_sources:
            if not resolves(current_url, source):
                errors.append(f"{relative}: unresolved image source {source}")

        if relative == "404.html":
            if robots != "noindex, nofollow":
                errors.append(f"404 robots mismatch: {robots!r}")
            if canonical:
                errors.append("404 page unexpectedly has a canonical URL")
            if og_url:
                errors.append("404 page unexpectedly has Open Graph metadata")
            if description != NOT_FOUND_DESCRIPTION:
                errors.append("404 description mismatch")
            continue

        required = {
            "title": title,
            "description": description,
            "robots": robots,
            "canonical": canonical,
            "og:title": og_title,
            "og:description": og_description,
            "og:url": og_url,
            "twitter:title": twitter_title,
            "twitter:description": twitter_description,
        }
        for key in (
            "og:image",
            "og:image:secure_url",
            "og:image:type",
            "og:image:width",
            "og:image:height",
            "og:image:alt",
            "twitter:card",
            "twitter:image",
            "twitter:image:alt",
        ):
            required[key] = meta_value(
                parser, "property" if key.startswith("og:") else "name", key
            )
        for key, value in required.items():
            if not value:
                errors.append(f"{relative}: missing {key}")
        for key in ("og:image", "og:image:secure_url", "twitter:image"):
            value = required[key]
            if value and not resolves(current_url, value):
                errors.append(f"{relative}: unresolved {key} {value}")

        permitted = {NOINDEX_ROBOTS} if development else {INDEX_ROBOTS, NOINDEX_ROBOTS}
        if robots not in permitted:
            errors.append(f"{relative}: robots directive mismatch")
        if canonical != current_url:
            errors.append(f"{relative}: canonical URL mismatch; expected {current_url}")
        if canonical != og_url:
            errors.append(f"{relative}: canonical and og:url differ")
        if description != og_description or description != twitter_description:
            errors.append(f"{relative}: description metadata differs")
        if og_title != twitter_title:
            errors.append(f"{relative}: social titles differ")
        if not parser.json_ld:
            errors.append(f"{relative}: missing JSON-LD")
        for raw_json in parser.json_ld:
            try:
                structured = json.loads(raw_json)
            except json.JSONDecodeError as exc:
                errors.append(f"{relative}: invalid JSON-LD: {exc}")
                continue
            if not isinstance(structured, dict):
                errors.append(f"{relative}: JSON-LD must be an object")
                continue
            if relative == "index.html":
                types = {
                    item.get("@type")
                    for item in structured.get("@graph", [])
                    if isinstance(item, dict)
                }
                if types != {"WebSite", "SoftwareSourceCode"}:
                    errors.append(f"homepage structured-data types mismatch: {types}")
                continue
            if structured.get("@type") != "BreadcrumbList":
                errors.append(f"{relative}: missing BreadcrumbList type")
            items = structured.get("itemListElement", [])
            if not isinstance(items, list) or any(
                not isinstance(item, dict) for item in items
            ):
                errors.append(f"{relative}: invalid breadcrumb items")
                continue
            positions = [item.get("position") for item in items]
            if positions != list(range(1, len(items) + 1)):
                errors.append(
                    f"{relative}: non-contiguous breadcrumb positions {positions}"
                )
            if not items or items[0].get("item") != base_url:
                errors.append(f"{relative}: breadcrumb home URL mismatch")
            if not items or items[-1].get("item") != canonical:
                errors.append(f"{relative}: breadcrumb canonical URL mismatch")
            for item in items:
                item_url = item.get("item", "")
                if not isinstance(item_url, str) or not item_url.startswith(base_url):
                    errors.append(f"{relative}: noncanonical breadcrumb URL {item_url}")
                elif not resolves(current_url, item_url):
                    errors.append(f"{relative}: unresolved breadcrumb URL {item_url}")

    if not (site_dir / "404.html").is_file():
        errors.append("Missing noindex 404 page")
    content_rows = [row for row in rows if row["relative"] != "404.html"]
    indexable_rows = [row for row in content_rows if row["robots"] == INDEX_ROBOTS]
    for field in ("title", "description", "canonical", "og_title"):
        for value, count in Counter(row[field] for row in content_rows).items():
            if not value:
                errors.append(f"{field}: missing value")
            elif count > 1:
                errors.append(f"{field}: {count} occurrences of {value!r}")
    for row in content_rows:
        length = len(row["description"])
        if not 70 <= length <= 180:
            errors.append(
                f"{row['relative']}: description length {length} "
                "is outside 70-180 characters"
            )

    sitemap_urls: set[str] = set()
    try:
        root = ET.parse(site_dir / "sitemap.xml").getroot()
        sitemap_urls = {
            node.text or ""
            for node in root.findall(
                "sm:url/sm:loc",
                {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"},
            )
        }
    except (OSError, ET.ParseError) as exc:
        errors.append(f"Cannot read sitemap.xml: {exc}")
    sitemap_rows = content_rows if development else indexable_rows
    expected_sitemap = {row["canonical"] for row in sitemap_rows}
    if sitemap_urls != expected_sitemap:
        errors.append(
            f"sitemap mismatch missing={sorted(expected_sitemap - sitemap_urls)} "
            f"extra={sorted(sitemap_urls - expected_sitemap)}"
        )

    assembled_root, _ = assembled_location(site_dir, base_url, development)
    release_url = urljoin(base_url, "../") if development else base_url
    expected_robots = (
        "User-agent: *\nAllow: /\n\nSitemap: " + release_url + "sitemap.xml\n"
    )
    try:
        robots_text = (assembled_root / "robots.txt").read_text(encoding="utf-8")
        if robots_text != expected_robots:
            errors.append(f"robots.txt mismatch: {robots_text!r}")
    except OSError as exc:
        errors.append(f"Cannot read robots.txt: {exc}")

    lengths = [len(row["description"]) for row in content_rows]
    print(
        f"HTML pages: {len(rows)} ({len(indexable_rows)} indexable, "
        f"{len(content_rows) - len(indexable_rows)} noindex content, "
        f"{len(rows) - len(content_rows)} noindex 404)"
    )
    print(f"Unique titles: {len({row['title'] for row in content_rows})}")
    print(f"Unique descriptions: {len({row['description'] for row in content_rows})}")
    print(f"Unique Open Graph titles: {len({row['og_title'] for row in content_rows})}")
    if lengths:
        print(f"Description length: min={min(lengths)} max={max(lengths)}")
    print(f"Sitemap URLs: {len(sitemap_urls)}")
    print(f"Errors: {len(errors)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site_dir", nargs="?", default="site", type=Path)
    parser.add_argument(
        "--base-url",
        help="canonical URL of this channel (defaults to release root or /dev/)",
    )
    parser.add_argument(
        "--development",
        action="store_true",
        help="audit the noindex development channel inside the assembled site",
    )
    args = parser.parse_args()
    errors = audit_site(
        args.site_dir, base_url=args.base_url, development=args.development
    )
    for error in errors:
        print(f"ERROR: {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

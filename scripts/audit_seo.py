#!/usr/bin/env python3
"""Audit generated DUMB documentation for technical SEO regressions."""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from collections import Counter
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse


BASE_URL = "https://dumbarr.com/"
INDEX_ROBOTS = (
    "index, follow, max-image-preview:large, "
    "max-snippet:-1, max-video-preview:-1"
)
ROBOTS_TEXT = (
    "User-agent: *\n"
    "Allow: /\n"
    "\n"
    "Sitemap: https://dumbarr.com/sitemap.xml\n"
)


class PageParser(HTMLParser):
    """Collect the metadata and links needed by the generated-site audit."""

    def __init__(self) -> None:
        super().__init__()
        self.title_parts: list[str] = []
        self.in_title = False
        self.meta: list[dict[str, str | None]] = []
        self.links: list[dict[str, str | None]] = []
        self.hrefs: list[str] = []
        self.json_ld: list[str] = []
        self.in_json_ld = False
        self.json_parts: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        values = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            self.meta.append(values)
        elif tag == "link":
            self.links.append(values)
        elif tag == "a" and values.get("href"):
            self.hrefs.append(str(values["href"]))
        elif tag == "script" and values.get("type") == "application/ld+json":
            self.in_json_ld = True
            self.json_parts = []

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
    """Return one named or property-based meta value."""

    for attrs in parser.meta:
        if attrs.get(key) == value:
            return str(attrs.get("content") or "")
    return ""


def link_value(parser: PageParser, rel: str) -> str:
    """Return one link relation target."""

    for attrs in parser.links:
        if attrs.get("rel") == rel:
            return str(attrs.get("href") or "")
    return ""


def parse_page(path: Path) -> PageParser:
    """Parse a generated HTML page."""

    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def page_url(site_dir: Path, path: Path) -> str:
    """Convert a generated HTML path into its public URL."""

    relative = path.relative_to(site_dir).as_posix()
    if relative == "index.html":
        return BASE_URL
    if relative.endswith("/index.html"):
        return BASE_URL + relative.removesuffix("index.html")
    return BASE_URL + relative


def resolve_local_target(site_dir: Path, current_url: str, href: str) -> bool:
    """Return whether a local page link resolves in the generated site."""

    parsed = urlparse(href)
    if (
        parsed.scheme
        or parsed.netloc
        or href.startswith(("mailto:", "tel:", "#"))
    ):
        return True

    target_url = urljoin(current_url, parsed.path)
    if not target_url.startswith(BASE_URL):
        return True

    target_relative = target_url.removeprefix(BASE_URL)
    candidates = [site_dir / target_relative]
    if target_relative.endswith("/") or not Path(target_relative).suffix:
        candidates.append(site_dir / target_relative / "index.html")
    return any(candidate.is_file() for candidate in candidates)


def audit_site(site_dir: Path) -> list[str]:
    """Audit the generated site and return every validation error."""

    errors: list[str] = []
    rows: list[dict[str, str]] = []
    html_paths = sorted(site_dir.rglob("*.html"))

    for path in html_paths:
        parser = parse_page(path)
        relative = path.relative_to(site_dir).as_posix()
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
            {
                "relative": relative,
                "title": title,
                "description": description,
                "robots": robots,
                "canonical": canonical,
                "og_title": og_title,
            }
        )

        if relative == "404.html":
            if robots != "noindex, nofollow":
                errors.append(f"404 robots mismatch: {robots!r}")
            if canonical:
                errors.append("404 page unexpectedly has a canonical URL")
            if og_url:
                errors.append("404 page unexpectedly has Open Graph metadata")
            if description != (
                "The requested DUMB documentation page could not be found."
            ):
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
            "og:image": meta_value(parser, "property", "og:image"),
            "og:image:secure_url": meta_value(
                parser,
                "property",
                "og:image:secure_url",
            ),
            "og:image:type": meta_value(parser, "property", "og:image:type"),
            "og:image:width": meta_value(parser, "property", "og:image:width"),
            "og:image:height": meta_value(
                parser,
                "property",
                "og:image:height",
            ),
            "og:image:alt": meta_value(parser, "property", "og:image:alt"),
            "twitter:card": meta_value(parser, "name", "twitter:card"),
            "twitter:image": meta_value(parser, "name", "twitter:image"),
            "twitter:image:alt": meta_value(
                parser,
                "name",
                "twitter:image:alt",
            ),
        }
        for key, value in required.items():
            if not value:
                errors.append(f"{relative}: missing {key}")

        if robots != INDEX_ROBOTS:
            errors.append(f"{relative}: robots directive mismatch")
        if canonical != og_url:
            errors.append(f"{relative}: canonical and og:url differ")
        if (
            description != og_description
            or description != twitter_description
        ):
            errors.append(f"{relative}: description metadata differs")
        if og_title != twitter_title:
            errors.append(f"{relative}: social titles differ")
        if not parser.json_ld:
            errors.append(f"{relative}: missing JSON-LD")

        for raw_json in parser.json_ld:
            try:
                structured_data = json.loads(raw_json)
            except json.JSONDecodeError as exc:
                errors.append(f"{relative}: invalid JSON-LD: {exc}")
                continue

            if relative == "index.html":
                types = {
                    item.get("@type")
                    for item in structured_data.get("@graph", [])
                }
                if types != {"WebSite", "SoftwareSourceCode"}:
                    errors.append(
                        f"homepage structured-data types mismatch: {types}"
                    )
                continue

            if structured_data.get("@type") != "BreadcrumbList":
                errors.append(f"{relative}: missing BreadcrumbList type")
            items = structured_data.get("itemListElement", [])
            positions = [item.get("position") for item in items]
            if positions != list(range(1, len(items) + 1)):
                errors.append(
                    f"{relative}: non-contiguous breadcrumb positions "
                    f"{positions}"
                )
            if not items or items[0].get("item") != BASE_URL:
                errors.append(f"{relative}: breadcrumb home URL mismatch")
            if not items or items[-1].get("item") != canonical:
                errors.append(
                    f"{relative}: breadcrumb canonical URL mismatch"
                )
            for item in items:
                item_url = item.get("item", "")
                if not item_url.startswith(BASE_URL):
                    errors.append(
                        f"{relative}: noncanonical breadcrumb URL {item_url}"
                    )

        current_url = page_url(site_dir, path)
        for href in parser.hrefs:
            if not resolve_local_target(site_dir, current_url, href):
                errors.append(f"{relative}: unresolved href {href}")

    content_rows = [
        row for row in rows if row["relative"] != "404.html"
    ]
    for field in ("title", "description", "canonical", "og_title"):
        counts = Counter(row[field] for row in content_rows)
        for value, count in counts.items():
            if not value:
                errors.append(f"{field}: missing value")
            elif count > 1:
                errors.append(
                    f"{field}: {count} occurrences of {value!r}"
                )
    for row in content_rows:
        description_length = len(row["description"])
        if not 70 <= description_length <= 180:
            errors.append(
                f"{row['relative']}: description length "
                f"{description_length} is outside 70-180 characters"
            )

    sitemap_path = site_dir / "sitemap.xml"
    sitemap_root = ET.parse(sitemap_path).getroot()
    sitemap_namespace = {
        "sm": "http://www.sitemaps.org/schemas/sitemap/0.9"
    }
    sitemap_urls = {
        location.text or ""
        for location in sitemap_root.findall(
            "sm:url/sm:loc",
            sitemap_namespace,
        )
    }
    canonical_urls = {row["canonical"] for row in content_rows}
    if sitemap_urls != canonical_urls:
        errors.append(
            "sitemap mismatch "
            f"missing={sorted(canonical_urls - sitemap_urls)} "
            f"extra={sorted(sitemap_urls - canonical_urls)}"
        )

    robots_text = (site_dir / "robots.txt").read_text(encoding="utf-8")
    if robots_text != ROBOTS_TEXT:
        errors.append(f"robots.txt mismatch: {robots_text!r}")

    description_lengths = [
        len(row["description"]) for row in content_rows
    ]
    print(
        f"HTML pages: {len(rows)} "
        f"({len(content_rows)} indexable + 1 noindex 404)"
    )
    print(
        "Unique titles: "
        f"{len({row['title'] for row in content_rows})}"
    )
    print(
        "Unique descriptions: "
        f"{len({row['description'] for row in content_rows})}"
    )
    print(
        "Unique Open Graph titles: "
        f"{len({row['og_title'] for row in content_rows})}"
    )
    print(
        "Description length: "
        f"min={min(description_lengths)} max={max(description_lengths)}"
    )
    print(f"Sitemap URLs: {len(sitemap_urls)}")
    print(f"Errors: {len(errors)}")
    return errors


def main() -> int:
    """Run the generated-site audit."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "site_dir",
        nargs="?",
        default="site",
        type=Path,
        help="generated site directory (default: site)",
    )
    args = parser.parse_args()

    errors = audit_site(args.site_dir)
    for error in errors:
        print(f"ERROR: {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

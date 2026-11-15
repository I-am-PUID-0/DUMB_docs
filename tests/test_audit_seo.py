"""Regression cases for channel-aware SEO, links, images, and fragment checks."""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from html import escape
from pathlib import Path

from scripts.audit_seo import (
    BASE_URL,
    INDEX_ROBOTS,
    NOINDEX_ROBOTS,
    NOT_FOUND_DESCRIPTION,
    audit_site,
    page_url,
    resolve_local_target,
)


class AuditSiteTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        assets = self.root / "assets"
        assets.mkdir()
        (assets / "favicon.ico").write_bytes(b"icon fixture")
        (assets / "image.png").write_bytes(b"image fixture")
        (self.root / "robots.txt").write_text(
            "User-agent: *\nAllow: /\n\nSitemap: " + BASE_URL + "sitemap.xml\n"
        )
        self.write_page(self.root, "index.html", "DUMB documentation")
        self.write_page(self.root, "guide/index.html", "Guide")
        self.write_404(self.root)
        self.write_sitemap(self.root, [BASE_URL, BASE_URL + "guide/"])

    def write_page(
        self,
        channel,
        relative,
        title,
        *,
        base_url=BASE_URL,
        robots=INDEX_ROBOTS,
        body="",
    ):
        path = channel / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        canonical = page_url(channel, path, base_url)
        description = (
            f"Read the {title} documentation to configure DUMB services, "
            "understand the available controls, and check the result."
        )
        if relative == "index.html":
            structured = {
                "@context": "https://schema.org",
                "@graph": [
                    {"@type": "WebSite"},
                    {"@type": "SoftwareSourceCode"},
                ],
            }
        else:
            structured = {
                "@context": "https://schema.org",
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"position": 1, "name": "Home", "item": base_url},
                    {"position": 2, "name": title, "item": canonical},
                ],
            }
        head = [
            "<!doctype html><html><head>",
            f"<title>{escape(title)}</title>",
            f'<link rel="canonical" href="{canonical}">',
            f'<link rel="icon" href="{BASE_URL}assets/favicon.ico">',
        ]
        fields = {
            "description": description,
            "robots": robots,
            "og:title": title,
            "og:description": description,
            "og:url": canonical,
            "og:image": BASE_URL + "assets/image.png",
            "og:image:secure_url": BASE_URL + "assets/image.png",
            "og:image:type": "image/png",
            "og:image:width": "100",
            "og:image:height": "100",
            "og:image:alt": "DUMB documentation illustration",
            "twitter:card": "summary_large_image",
            "twitter:title": title,
            "twitter:description": description,
            "twitter:image": BASE_URL + "assets/image.png",
            "twitter:image:alt": "DUMB documentation illustration",
        }
        for name, value in fields.items():
            attribute = "property" if name.startswith("og:") else "name"
            head.append(
                f'<meta {attribute}="{name}" content="{escape(value, quote=True)}">'
            )
        head.append(
            '<script type="application/ld+json">' + json.dumps(structured) + "</script>"
        )
        path.write_text(
            "\n".join(head)
            + '</head><body><h1 id="start">'
            + escape(title)
            + '</h1><h2 id="configuration">Configuration</h2>'
            + '<h2 id="café">Encoded fragment</h2>'
            + body
            + "</body></html>"
        )
        return path

    def write_404(self, channel):
        channel.mkdir(parents=True, exist_ok=True)
        (channel / "404.html").write_text(
            "<html><head><title>Page not found</title>"
            '<meta name="robots" content="noindex, nofollow">'
            f'<meta name="description" content="{NOT_FOUND_DESCRIPTION}">'
            f'<link rel="icon" href="{BASE_URL}assets/favicon.ico">'
            "</head><body><h1>Page not found</h1></body></html>"
        )

    def write_sitemap(self, channel, urls):
        root = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
        for url in urls:
            entry = ET.SubElement(root, "url")
            ET.SubElement(entry, "loc").text = url
        ET.ElementTree(root).write(channel / "sitemap.xml", encoding="utf-8")

    def audit(self, channel=None, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return audit_site(channel or self.root, **kwargs)

    def test_valid_release_and_decorative_image(self):
        self.write_page(
            self.root,
            "guide/index.html",
            "Guide",
            body='<img src="../assets/image.png" alt="">',
        )
        self.assertEqual(self.audit(), [])

    def test_release_excludes_dev_subtree_and_noindex_stubs_from_sitemap(self):
        dev = self.root / "dev"
        dev.mkdir()
        (dev / "index.html").write_text('<h1 id="dev-start">Development</h1>')
        self.write_page(
            self.root, "beta/index.html", "Beta feature", robots=NOINDEX_ROBOTS
        )
        self.write_page(
            self.root,
            "guide/index.html",
            "Guide",
            body=f'<a href="{BASE_URL}dev/#dev-start">Development</a>',
        )
        self.assertEqual(self.audit(), [])
        self.write_sitemap(
            self.root, [BASE_URL, BASE_URL + "guide/", BASE_URL + "beta/"]
        )
        self.assertTrue(any("sitemap mismatch" in error for error in self.audit()))

    def test_development_resolves_release_absolute_and_relative_fragments(self):
        dev = self.root / "dev"
        dev_url = BASE_URL + "dev/"
        self.write_page(
            dev,
            "index.html",
            "DUMB development",
            base_url=dev_url,
            robots=NOINDEX_ROBOTS,
            body=(
                '<a href="../guide/#configuration">Release guide</a>'
                f'<a href="{BASE_URL}guide/#caf%C3%A9">Encoded fragment</a>'
            ),
        )
        self.write_page(
            dev,
            "guide/index.html",
            "Development guide",
            base_url=dev_url,
            robots=NOINDEX_ROBOTS,
        )
        self.write_404(dev)
        self.write_sitemap(dev, [dev_url, dev_url + "guide/"])
        self.assertEqual(self.audit(dev, development=True), [])
        self.assertEqual(self.audit(dev, base_url=dev_url, development=True), [])

    def test_development_cannot_accidentally_be_indexable(self):
        dev = self.root / "dev"
        self.write_page(dev, "index.html", "Development", base_url=BASE_URL + "dev/")
        self.write_404(dev)
        self.write_sitemap(dev, [BASE_URL + "dev/"])
        self.assertTrue(
            any(
                "robots directive mismatch" in error
                for error in self.audit(dev, development=True)
            )
        )

    def test_fragment_checks_same_page_relative_and_absolute_links(self):
        current = BASE_URL + "guide/"
        for href in (
            "#configuration",
            "../guide/#configuration",
            BASE_URL + "guide/#caf%C3%A9",
        ):
            with self.subTest(href=href):
                self.assertTrue(resolve_local_target(self.root, current, href))
        for href in ("#missing", "../guide/#missing", BASE_URL + "guide/#missing"):
            with self.subTest(href=href):
                self.assertFalse(resolve_local_target(self.root, current, href))
        self.write_page(
            self.root, "guide/index.html", "Guide", body='<a href="#missing">Broken</a>'
        )
        self.assertTrue(
            any("unresolved href #missing" in error for error in self.audit())
        )

    def test_external_links_are_not_network_probed(self):
        self.assertTrue(
            resolve_local_target(
                self.root, BASE_URL, "https://example.com/elsewhere/#missing"
            )
        )
        self.assertTrue(
            resolve_local_target(self.root, BASE_URL, "mailto:help@example.com")
        )
        self.assertTrue(
            resolve_local_target(self.root, BASE_URL, "data:image/png;base64,YQ==")
        )

    def test_prefixed_deployment_cross_channel_mapping(self):
        dev = self.root / "dev"
        dev.mkdir()
        (dev / "index.html").write_text('<h1 id="dev-start">Development</h1>')
        self.assertTrue(
            resolve_local_target(
                dev,
                "https://example.com/project/dev/",
                "/project/guide/#configuration",
                base_url="https://example.com/project/dev/",
                development=True,
            )
        )
        self.assertTrue(
            resolve_local_target(
                self.root,
                "https://example.com/project/",
                "/project/dev/#dev-start",
                base_url="https://example.com/project/",
            )
        )
        self.assertFalse(
            resolve_local_target(
                self.root,
                "https://example.com/project/",
                "/project/%2e%2e/secret.txt",
                base_url="https://example.com/project/",
            )
        )

    def test_image_favicon_and_srcset_failures_are_reported(self):
        page = self.write_page(
            self.root,
            "guide/index.html",
            "Guide",
            body='<img src="missing.png"><source srcset="missing.webp 1x, missing2.webp 2x">',
        )
        page.write_text(
            page.read_text().replace("assets/favicon.ico", "assets/missing.ico")
        )
        errors = self.audit()
        for expected in (
            "image missing alt",
            "unresolved image missing.png",
            "unresolved favicon",
            "unresolved image source missing.webp",
        ):
            self.assertTrue(any(expected in error for error in errors), expected)

    def test_exactly_one_h1_is_required(self):
        page = self.root / "guide/index.html"
        page.write_text(
            page.read_text().replace("</body>", "<h1>Duplicate</h1></body>")
        )
        self.assertTrue(
            any("expected one H1, found 2" in error for error in self.audit())
        )

    def test_404_is_noindex_and_has_no_canonical_or_social_url(self):
        path = self.root / "404.html"
        path.write_text(
            path.read_text()
            .replace("noindex, nofollow", NOINDEX_ROBOTS)
            .replace(
                "</head>",
                f'<link rel="canonical" href="{BASE_URL}404.html">'
                f'<meta property="og:url" content="{BASE_URL}404.html"></head>',
            )
        )
        errors = self.audit()
        for expected in (
            "404 robots mismatch",
            "404 page unexpectedly has a canonical",
            "404 page unexpectedly has Open Graph",
        ):
            self.assertTrue(any(expected in error for error in errors), expected)

    def test_metadata_uniqueness_and_canonical_identity_remain_checked(self):
        page = self.root / "guide/index.html"
        page.write_text(page.read_text().replace(BASE_URL + "guide/", BASE_URL))
        errors = self.audit()
        self.assertTrue(any("canonical URL mismatch" in error for error in errors))
        self.assertTrue(any("canonical: 2 occurrences" in error for error in errors))

    def test_empty_output_reports_errors_instead_of_crashing(self):
        empty = self.root / "empty"
        empty.mkdir()
        errors = self.audit(empty)
        self.assertIn("No HTML pages found", errors)
        self.assertIn("Missing noindex 404 page", errors)
        self.assertTrue(any("Cannot read sitemap.xml" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

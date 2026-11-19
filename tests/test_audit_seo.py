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
        video_nodes=(),
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
                    *video_nodes,
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

    def test_video_poster_clip_and_text_track_resolve(self):
        for name in ("poster.webp", "demo.webm", "captions.vtt"):
            (self.root / "assets" / name).write_bytes(b"media fixture")
        self.write_page(
            self.root,
            "guide/index.html",
            "Guide",
            body=(
                '<video controls playsinline preload="none" poster="../assets/poster.webp">'
                '<source src="../assets/demo.webm" type="video/webm">'
                '<track kind="captions" src="../assets/captions.vtt" srclang="en">'
                "</video>"
            ),
        )
        self.assertEqual(self.audit(), [])

    def test_broken_video_poster_fails_even_when_the_clip_exists(self):
        (self.root / "assets/demo.webm").write_bytes(b"clip fixture")
        self.write_page(
            self.root,
            "guide/index.html",
            "Guide",
            body=(
                '<video controls poster="../assets/missing.webp">'
                '<source src="../assets/demo.webm" type="video/webm"></video>'
            ),
        )
        self.assertTrue(
            any("unresolved video poster" in error for error in self.audit())
        )

    def test_broken_video_sources_fail_with_inline_or_child_source(self):
        for body, expected in (
            ('<video controls src="../assets/missing.webm"></video>', "video src"),
            (
                '<video controls><source src="../assets/missing.webm" type="video/webm"></video>',
                "source src",
            ),
        ):
            with self.subTest(expected=expected):
                self.write_page(self.root, "guide/index.html", "Guide", body=body)
                self.assertTrue(
                    any(f"unresolved {expected}" in error for error in self.audit())
                )

    def test_broken_text_track_fails_even_when_the_clip_exists(self):
        (self.root / "assets/demo.webm").write_bytes(b"clip fixture")
        self.write_page(
            self.root,
            "guide/index.html",
            "Guide",
            body=(
                '<video controls src="../assets/demo.webm">'
                '<track kind="captions" src="../assets/missing.vtt" srclang="en"></video>'
            ),
        )
        self.assertTrue(any("unresolved track src" in error for error in self.audit()))

    def write_homepage_video(
        self,
        *,
        channel=None,
        base_url=BASE_URL,
        robots=INDEX_ROBOTS,
        schema_changes=None,
        schema_count=1,
        body=None,
    ):
        (self.root / "assets/overview.mp4").write_bytes(b"overview video fixture")
        (self.root / "assets/poster.webp").write_bytes(b"overview poster fixture")
        node = {
            "@type": "VideoObject",
            "name": "See how DUMB works",
            "description": "Review the released frontend using public example data.",
            "uploadDate": "2026-11-19T12:00:00Z",
            "duration": "PT1M35S",
            "contentUrl": BASE_URL + "assets/overview.mp4",
            "thumbnailUrl": BASE_URL + "assets/poster.webp",
            "embedUrl": base_url + "#overview",
            **(schema_changes or {}),
        }
        if body is None:
            body = (
                '<section id="overview"><video controls poster="'
                + BASE_URL
                + 'assets/poster.webp"><source src="'
                + BASE_URL
                + 'assets/overview.mp4" type="video/mp4"></video></section>'
            )
        return self.write_page(
            channel or self.root,
            "index.html",
            "DUMB video overview",
            base_url=base_url,
            robots=robots,
            body=body,
            video_nodes=[node] * schema_count,
        )

    def test_homepage_video_schema_matches_inline_and_child_sources(self):
        for attributes, source in (
            ('src="assets/overview.mp4"', ""),
            ("", '<source src="assets/overview.mp4" type="video/mp4">'),
        ):
            with self.subTest(attributes=attributes):
                self.write_homepage_video(
                    body=(
                        '<section id="overview"><video controls poster="assets/poster.webp" '
                        + attributes
                        + ">"
                        + source
                        + "</video></section>"
                    )
                )
                self.assertEqual(self.audit(), [])

    def test_development_homepage_video_uses_its_own_embed_and_shared_assets(self):
        dev = self.root / "dev"
        dev_url = BASE_URL + "dev/"
        self.write_homepage_video(
            channel=dev,
            base_url=dev_url,
            robots=NOINDEX_ROBOTS,
            body=(
                '<section id="overview"><video controls poster="../assets/poster.webp">'
                '<source src="../assets/overview.mp4" type="video/mp4">'
                "</video></section>"
            ),
        )
        self.write_404(dev)
        self.write_sitemap(dev, [dev_url])
        self.assertEqual(self.audit(dev, development=True), [])

    def test_homepage_video_requires_exactly_one_video_object(self):
        for count in (0, 2):
            with self.subTest(count=count):
                self.write_homepage_video(schema_count=count)
                self.assertTrue(
                    any("expected exactly one VideoObject" in error for error in self.audit())
                )

    def test_homepage_without_video_rejects_video_object(self):
        self.write_homepage_video(body="<p>No playable video.</p>")
        self.assertTrue(
            any("structured-data types mismatch" in error for error in self.audit())
        )

    def test_homepage_video_schema_must_reference_actual_local_media(self):
        (self.root / "assets/other.mp4").write_bytes(b"unrelated video fixture")
        cases = (
            ("contentUrl", BASE_URL + "assets/other.mp4", "differs from the video"),
            ("thumbnailUrl", BASE_URL + "assets/image.png", "differs from the video"),
            ("contentUrl", BASE_URL + "assets/missing.mp4", "unresolved local"),
            ("thumbnailUrl", BASE_URL + "assets/missing.webp", "unresolved local"),
            ("contentUrl", "https://example.com/overview.mp4", "unresolved local"),
        )
        for field, value, expected in cases:
            with self.subTest(field=field, value=value):
                self.write_homepage_video(schema_changes={field: value})
                self.assertTrue(
                    any(
                        "VideoObject" in error and field in error and expected in error
                        for error in self.audit()
                    )
                )

    def test_homepage_video_schema_assets_must_exist_even_when_urls_match(self):
        for name, field in (
            ("overview.mp4", "contentUrl"),
            ("poster.webp", "thumbnailUrl"),
        ):
            with self.subTest(field=field):
                self.write_homepage_video()
                (self.root / "assets" / name).unlink()
                self.assertTrue(
                    any(f"unresolved local {field}" in error for error in self.audit())
                )

    def test_homepage_video_upload_date_must_be_a_real_iso_date(self):
        for value in (
            "",
            "November 19, 2026",
            "2026-02-30",
            "2026-11-19T12:00:00",
            "2026-11-19T25:00:00Z",
            "2026-11-19T12:00:00+25:00",
        ):
            with self.subTest(value=value):
                self.write_homepage_video(schema_changes={"uploadDate": value})
                self.assertTrue(any("invalid ISO uploadDate" in error for error in self.audit()))
        for value in ("2026-11-19", "2026-11-19T12:00:00+00:00"):
            with self.subTest(value=value):
                self.write_homepage_video(schema_changes={"uploadDate": value})
                self.assertEqual(self.audit(), [])

    def test_homepage_video_duration_must_be_positive_iso_time(self):
        for value in ("", "95", "1:35", "P", "PT", "PT0S", "PT-1S", "P1DT"):
            with self.subTest(value=value):
                self.write_homepage_video(schema_changes={"duration": value})
                self.assertTrue(any("invalid ISO duration" in error for error in self.audit()))
        for value in ("PT95S", "PT1M35.5S", "PT1H2M3S"):
            with self.subTest(value=value):
                self.write_homepage_video(schema_changes={"duration": value})
                self.assertEqual(self.audit(), [])

    def test_homepage_video_needs_descriptive_text_and_canonical_overview_embed(self):
        for field in ("name", "description"):
            with self.subTest(field=field):
                self.write_homepage_video(schema_changes={field: "   "})
                self.assertTrue(any(f"VideoObject: missing {field}" in error for error in self.audit()))
        self.write_homepage_video(schema_changes={"embedUrl": BASE_URL + "#start"})
        self.assertTrue(any("embedUrl must target canonical #overview" in error for error in self.audit()))
        path = self.write_homepage_video()
        path.write_text(path.read_text().replace('id="overview"', 'id="elsewhere"'))
        self.assertTrue(any("missing overview fragment target" in error for error in self.audit()))

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

    def test_literal_table_continuations_are_reported(self):
        self.write_page(
            self.root,
            "guide/index.html",
            "Guide",
            body=(
                "<table><tr><th>Service</th><th>Role</th></tr>"
                "<tr><td>Plex</td><td>Video</td></tr></table>"
                '<p>| <a href="#configuration">Seerr</a> | Requests |\n'
                "| <code>Audiobookshelf</code> | Books |</p>"
            ),
        )
        self.assertTrue(
            any("unrendered Markdown table rows" in error for error in self.audit())
        )

    def test_rendered_tables_and_code_examples_are_not_raw_table_errors(self):
        self.write_page(
            self.root,
            "guide/index.html",
            "Guide",
            body=(
                "<table><tr><th>Service</th><th>Role</th></tr>"
                "<tr><td>Plex</td><td>Video | audio</td></tr></table>"
                "<pre><code>| Example | Value |\n|---|---|</code></pre>"
                "<p><code>| Literal | row |</code></p>"
                "<p>Choose <code>fresh | migrate</code> or <code>rclone | fuse</code>.</p>"
            ),
        )
        self.assertFalse(
            any("unrendered Markdown table rows" in error for error in self.audit())
        )


if __name__ == "__main__":
    unittest.main()

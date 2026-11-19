"""Media slots keep channel provenance and useful static HTML at every depth."""

import copy
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urljoin, urlsplit

import yaml

from scripts import media_render
from scripts.refresh_frontend_media import SyncError

ROOT = Path(__file__).resolve().parents[1]
BACKEND = "a" * 40
FRONTEND = "b" * 40


class HTML(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.elements = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


class MediaRendererTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        templates = self.root / "overrides/partials"
        templates.mkdir(parents=True)
        shutil.copyfile(
            ROOT / "overrides/partials/frontend-visuals.html",
            templates / "frontend-visuals.html",
        )
        self.catalog = [
            {
                "id": "dashboard",
                "description": "Inspect example service health.",
                "features": ["frontend/dashboard"],
                "kinds": ["image"],
            },
            {
                "id": "service-logs",
                "description": "Choose Logs and inspect the example messages.",
                "features": ["frontend/service-pages"],
                "kinds": ["image", "video"],
            },
            {
                "id": "settings-backups",
                "description": "Review installation backups.",
                "features": ["features/installation-backups"],
                "kinds": ["image"],
            },
        ]
        source_catalog = self.root / "scripts/frontend-visuals/capture-catalog.json"
        source_catalog.parent.mkdir(parents=True)
        source_catalog.write_text(
            json.dumps({"schema_version": 1, "scenarios": self.catalog})
        )
        self.settings = {
            "version": "2.23.0",
            "source": BACKEND,
            "frontend_source": FRONTEND,
        }
        self.accepted = {
            "schema_version": 1,
            "channels": {"release": {"name": "release"}, "dev": {"name": "dev"}},
        }
        self.write_catalog()

    def write_catalog(self):
        (self.root / "frontend-media.json").write_text(json.dumps(self.accepted))

    def media(self, channel="release"):
        coverage, files = [], []
        for scenario in self.catalog:
            for theme in ("dark", "light"):
                captured = scenario["id"] != "settings-backups"
                row = {
                    "id": scenario["id"],
                    "theme": theme,
                    "status": "captured" if captured else "skipped",
                    "required": captured,
                    "artifacts": [],
                }
                if not captured:
                    row["reason"] = (
                        "The selected backend does not advertise installation_backup."
                    )
                else:
                    for kind in scenario["kinds"]:
                        filename = f"{theme}/{scenario['id']}.{'webp' if kind == 'image' else 'webm'}"
                        row["artifacts"].append(filename)
                        files.append(
                            {
                                "scenario": scenario["id"],
                                "theme": theme,
                                "kind": kind,
                                "path": filename,
                            }
                        )
                coverage.append(row)
        showcase = []
        for theme in ("dark", "light"):
            for role, filename, kind in (
                ("video", "hero.mp4", "video"),
                ("poster", "poster.webp", "image"),
                ("animated", "animated.webp", "image"),
            ):
                showcase.append(
                    {
                        "path": theme + "/" + filename,
                        "role": role,
                        "kind": kind,
                        "theme": theme,
                    }
                )
        for role, filename in (
            ("captions", "captions.vtt"),
            ("chapters", "chapters.vtt"),
            ("transcript", "transcript.txt"),
        ):
            showcase.append({"path": filename, "role": role, "kind": "text"})
        return {
            "plan": {
                "channel": channel,
                "frontend": {"version": "1.91.0", "commit": FRONTEND},
                "backend": {"version": "2.23.0", "commit": BACKEND},
            },
            "package": {
                "coverage": coverage,
                "files": files,
                "captured_at": "2026-11-21T09:30:00Z",
            },
            "showcase": {
                "files": showcase,
                "duration_seconds": 28,
                "captured_at": "2026-11-21T09:30:00Z",
            },
            "package_path": self.root
            / f"docs/assets/images/guides/frontend/channels/{channel}/immutable-pair/manifest.json",
            "showcase_path": self.root
            / f"docs/assets/images/guides/showcase/channels/{channel}/immutable-pair/manifest.json",
        }

    def renderer(self, channel="release", media=None, settings=None):
        with patch.object(
            media_render, "validate_channel", return_value=media or self.media(channel)
        ) as validator:
            result = media_render.MediaRenderer(
                self.root, channel, settings or self.settings
            )
        self.assertEqual(validator.call_args.args[:2], (self.root, channel))
        self.assertEqual(
            validator.call_args.args[2], self.accepted["channels"][channel]
        )
        return result

    def test_missing_channel_and_invalid_package_never_fall_back(self):
        del self.accepted["channels"]["dev"]
        self.write_catalog()
        with patch.object(media_render, "validate_channel") as validator:
            with self.assertRaises(KeyError):
                media_render.MediaRenderer(self.root, "dev", self.settings)
            validator.assert_not_called()
        with patch.object(
            media_render,
            "validate_channel",
            side_effect=SyncError("Partial capture coverage"),
        ):
            with self.assertRaisesRegex(SyncError, "Partial"):
                media_render.MediaRenderer(self.root, "release", self.settings)

    def test_stable_backend_source_and_version_must_match_prose(self):
        for field, value in (("source", "c" * 40), ("version", "2.24.0")):
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, "backend"):
                    self.renderer(settings={**self.settings, field: value})

    def test_development_captures_can_advance_without_relabeling_reviewed_prose(self):
        actual = self.media("dev")
        actual["plan"]["backend"] = {"version": "2.24.0", "commit": "c" * 40}
        actual["plan"]["frontend"] = {"version": "1.92.0", "commit": "d" * 40}
        before = copy.deepcopy(self.settings)
        renderer = self.renderer("dev", actual)
        rendered = renderer.render(
            "<!-- docs:visual-gallery -->", Path("frontend/index.md")
        )
        self.assertEqual(self.settings, before)
        self.assertIn("1.92.0", rendered)
        self.assertIn("2.24.0", rendered)
        self.assertIn('class="ui-gallery-notice"', rendered)

    def test_asset_urls_resolve_within_selected_channel_at_every_page_depth(self):
        pages = {
            Path("index.md"): "",
            Path("frontend/index.md"): "frontend/",
            Path("frontend/service-pages.md"): "frontend/service-pages/",
            Path("features/nested/task.md"): "features/nested/task/",
        }
        for channel in ("release", "dev"):
            renderer = self.renderer(channel)
            prefix = "/docs/" + ("dev/" if channel == "dev" else "")
            for relative, route in pages.items():
                with self.subTest(channel=channel, relative=relative):
                    catalog, urls = renderer.context(relative)
                    base = "https://docs.example" + prefix + route
                    image = urljoin(base, urls["screens"]["dashboard"]["light"])
                    self.assertEqual(
                        urlsplit(image).path,
                        prefix
                        + f"assets/images/guides/frontend/channels/{channel}/immutable-pair/light/dashboard.webp",
                    )
                    self.assertEqual(
                        urlsplit(urljoin(base, urls["guides"]["dashboard"])).path,
                        prefix + "frontend/dashboard/",
                    )
                    self.assertEqual(
                        urlsplit(urljoin(base, urls["gallery"])).path,
                        prefix + "frontend/",
                    )
                    self.assertEqual(
                        urlsplit(urljoin(base, urls["gallery"])).fragment, "ui-examples"
                    )

    def test_gallery_has_real_static_images_and_source_links_without_javascript(self):
        rendered = self.renderer().render(
            "<!-- docs:visual-gallery -->", Path("frontend/index.md")
        )
        elements = HTML(rendered).elements
        images = [attrs for tag, attrs in elements if tag == "img"]
        self.assertGreaterEqual(len(images), 2)
        self.assertTrue(all(attrs.get("src") and attrs.get("alt") for attrs in images))
        self.assertTrue(
            any(
                tag == "a" and attrs.get("href", "").endswith("/light/dashboard.webp")
                for tag, attrs in elements
            )
        )
        self.assertIn("installation_backup", rendered)
        self.assertNotIn("<script", rendered)
        self.assertNotIn("<!-- docs:", rendered)

    def test_unavailable_feature_slot_explains_versions_without_fabricated_image(self):
        rendered = self.renderer().render(
            "<!-- docs:visual scenario=settings-backups type=image -->",
            Path("features/installation-backups.md"),
        )
        self.assertIn("unavailable", rendered)
        self.assertIn("installation_backup", rendered)
        self.assertNotIn("<img", rendered)
        self.assertNotIn("<video", rendered)

    def test_image_and_video_slots_include_actual_versions_and_example_scope(self):
        renderer = self.renderer()
        for kind, scenario in (("image", "dashboard"), ("video", "service-logs")):
            with self.subTest(kind=kind):
                rendered = renderer.render(
                    f"<!-- docs:visual scenario={scenario} type={kind} -->",
                    Path("frontend/service-pages.md"),
                )
                self.assertIn("1.91.0", rendered)
                self.assertIn("2.23.0", rendered)
                self.assertIn("example data", rendered.lower())
        video = next(attrs for tag, attrs in HTML(rendered).elements if tag == "video")
        self.assertIn("controls", video)
        self.assertEqual(video["preload"], "none")
        self.assertNotIn("autoplay", video)
        self.assertIn("poster", video)

    def test_showcase_updates_seo_from_actual_media_identity_and_capture_date(self):
        source = "---\ntitle: Home\ndescription: Existing SEO description\n---\n# DUMB\n\n<!-- docs:showcase -->"
        rendered = self.renderer().render(source, Path("index.md"))
        metadata = yaml.safe_load(rendered.split("---\n", 2)[1])
        self.assertEqual(metadata["description"], "Existing SEO description")
        self.assertEqual(metadata["overview_video"]["duration"], "PT28S")
        self.assertTrue(
            metadata["overview_video"]["upload_date"].startswith("2026-11-21")
        )
        self.assertIn(
            "channels/release/immutable-pair/light/hero.mp4",
            metadata["overview_video"]["content"],
        )
        elements = HTML(rendered).elements
        self.assertTrue(
            any(
                tag == "img" and attrs.get("src", "").endswith("light/poster.webp")
                for tag, attrs in elements
            )
        )
        self.assertTrue(
            any(
                tag == "source" and attrs.get("src", "").endswith("light/hero.mp4")
                for tag, attrs in elements
            )
        )

    def test_unsupported_slot_fails_and_unmarked_prose_stays_identical(self):
        renderer = self.renderer()
        with self.assertRaisesRegex(ValueError, "Unknown"):
            renderer.render(
                "<!-- docs:visual scenario=typo type=image -->", Path("index.md")
            )
        source = "# Existing guide\n\nKeep the useful prose.\n"
        self.assertEqual(renderer.render(source, Path("features/task.md")), source)

    def test_real_zensical_build_preserves_generated_media_and_authored_link_rules(
        self,
    ):
        """Exercise the Markdown engine: raw src and poster follow different rules."""
        shutil.copyfile(ROOT / "overrides/main.html", self.root / "overrides/main.html")
        routes = {
            Path("index.md"): "",
            Path("frontend/index.md"): "frontend/",
            Path("features/nested/task.md"): "features/nested/task/",
        }
        for channel, prefix in (("release", "mirror/"), ("dev", "mirror/dev/")):
            with self.subTest(channel=channel):
                project = self.root / ("mini-" + channel)
                docs = project / "docs"
                docs.mkdir(parents=True)
                media = self.media(channel)
                renderer = self.renderer(channel, media)
                for kind in ("package", "showcase"):
                    asset_base = media[kind + "_path"].parent.relative_to(
                        self.root / "docs"
                    )
                    for row in media[kind]["files"]:
                        target = docs / asset_base / row["path"]
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(b"URL regression asset")
                (docs / "assets/authored.svg").write_text(
                    '<svg xmlns="http://www.w3.org/2000/svg"/>'
                )
                for relative in (
                    "authored.md",
                    "frontend/dashboard.md",
                    "frontend/service-pages.md",
                    "features/installation-backups.md",
                ):
                    target = docs / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text("# Written guide\n")
                for relative in routes:
                    depth = len(relative.parent.parts)
                    authored_prefix = "../" * depth
                    source = (
                        "---\ntitle: URL regression\ndescription: Preserve canonical metadata\n---\n# UI examples\n\n"
                        f"[Authored Markdown contract]({authored_prefix}authored.md)\n\n"
                        f'<a id="authored-html" href="{authored_prefix}authored.md">Written HTML link</a>\n\n'
                        f"![Authored diagram]({authored_prefix}assets/authored.svg)\n\n"
                        "<!-- docs:visual scenario=dashboard type=image -->\n\n"
                        "<!-- docs:visual scenario=service-logs type=video -->\n\n"
                        "<!-- docs:showcase -->\n\n"
                        "<!-- docs:visual-gallery -->\n"
                    )
                    rendered = renderer.render(source, relative, for_build=True)
                    self.assertIn(media_render.URL_PREFIX, rendered)
                    self.assertIn(f'href="{authored_prefix}authored.md"', rendered)
                    metadata = yaml.safe_load(rendered.split("---\n", 2)[1])
                    self.assertNotIn(media_render.URL_PREFIX, json.dumps(metadata))
                    target = docs / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(rendered)
                site_url = "https://docs.example/" + prefix
                config = {
                    "site_name": "Media URL regression",
                    "site_url": site_url,
                    "docs_dir": "docs",
                    "site_dir": "site",
                    "theme": {
                        "name": "material",
                        "custom_dir": str(self.root / "overrides"),
                        "font": False,
                    },
                    "extra": {
                        "docs_channel": channel,
                        "docs_version": "2.23.0",
                        "docs_release_version": "2.23.0",
                        "docs_release_available_pages": list(routes.values()),
                    },
                }
                config_path = project / "mkdocs.yml"
                config_path.write_text(yaml.safe_dump(config, sort_keys=False))
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "zensical",
                        "build",
                        "--clean",
                        "--strict",
                        "--config-file",
                        str(config_path),
                    ],
                    cwd=project,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                self.assertEqual(
                    result.returncode, 0, (result.stdout + result.stderr)[-6000:]
                )
                site = project / "site"
                self.assertIn(
                    media_render.URL_PREFIX,
                    (site / "features/nested/task/index.html").read_text(),
                )
                media_render.restore_site_urls(site)
                for target in site.rglob("*"):
                    if target.is_file() and target.suffix in {".html", ".json"}:
                        self.assertNotIn(
                            media_render.URL_PREFIX, target.read_text(), target
                        )
                for relative, route in routes.items():
                    generated = site / route / "index.html"
                    html = generated.read_text()
                    parsed = HTML(html).elements
                    current_url = site_url + route
                    canonical = [
                        attrs["href"]
                        for tag, attrs in parsed
                        if tag == "link" and attrs.get("rel") == "canonical"
                    ]
                    self.assertEqual(canonical, [current_url])
                    markdown_link = re.search(
                        r'<a href="([^"]+)">Authored Markdown contract</a>', html
                    )
                    self.assertIsNotNone(markdown_link)
                    self.assertEqual(
                        urljoin(current_url, markdown_link[1]), site_url + "authored/"
                    )
                    authored = next(
                        attrs["href"]
                        for tag, attrs in parsed
                        if tag == "a" and attrs.get("id") == "authored-html"
                    )
                    self.assertEqual(
                        urljoin(current_url, authored), site_url + "authored/"
                    )
                    authored_image = next(
                        attrs["src"]
                        for tag, attrs in parsed
                        if tag == "img" and attrs.get("alt") == "Authored diagram"
                    )
                    self.assertEqual(
                        urljoin(current_url, authored_image),
                        site_url + "assets/authored.svg",
                    )
                    checked = set()
                    for tag, attrs in parsed:
                        for attribute in (
                            "src",
                            "srcset",
                            "href",
                            "poster",
                            "data-light-video",
                            "data-dark-video",
                            "data-light-poster",
                            "data-dark-poster",
                        ):
                            value = attrs.get(attribute, "")
                            if "/channels/" not in value:
                                continue
                            url = urljoin(current_url, value.split(",")[0].split()[0])
                            self.assertTrue(
                                url.startswith(site_url + "assets/images/guides/"),
                                (relative, tag, attribute, value, url),
                            )
                            self.assertIn(f"/channels/{channel}/immutable-pair/", url)
                            local = site / url.removeprefix(site_url)
                            self.assertTrue(local.is_file(), (relative, attribute, url))
                            checked.add(attribute)
                    self.assertEqual(
                        checked,
                        {
                            "src",
                            "srcset",
                            "href",
                            "poster",
                            "data-light-video",
                            "data-dark-video",
                            "data-light-poster",
                            "data-dark-poster",
                        },
                    )
                    tracks = [
                        urljoin(current_url, attrs["src"])
                        for tag, attrs in parsed
                        if tag == "track"
                    ]
                    self.assertEqual(len(tracks), 2)
                    self.assertTrue(
                        all(
                            url.startswith(
                                site_url
                                + f"assets/images/guides/showcase/channels/{channel}/immutable-pair/"
                            )
                            for url in tracks
                        )
                    )
                    if relative.name == "index.md" and relative.parent == Path("."):
                        graphs = [
                            json.loads(value)
                            for value in re.findall(
                                r'<script[^>]+type="application/ld\+json"[^>]*>([\s\S]*?)</script>',
                                html,
                            )
                        ]
                        videos = [
                            node
                            for graph in graphs
                            for node in graph.get("@graph", [])
                            if node.get("@type") == "VideoObject"
                        ]
                        self.assertEqual(len(videos), 1)
                        self.assertEqual(
                            videos[0]["contentUrl"],
                            site_url
                            + f"assets/images/guides/showcase/channels/{channel}/immutable-pair/light/hero.mp4",
                        )
                        self.assertEqual(
                            videos[0]["thumbnailUrl"],
                            site_url
                            + f"assets/images/guides/showcase/channels/{channel}/immutable-pair/light/poster.webp",
                        )


if __name__ == "__main__":
    unittest.main()

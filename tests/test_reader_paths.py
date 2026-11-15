"""Reader contracts are about reachable, visible tasks rather than prose keywords."""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from scripts.audit_reader_paths import HUBS, PLATFORMS, SERVICES, audit_reader_paths


class ReaderPathTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for channel in ("", "dev"):
            for relative in HUBS:
                self.write_page(
                    channel, relative, self.platform_links(channel), nav=True
                )
            for service, heading in SERVICES.items():
                asset = (
                    "riven" if service == "riven-backend" else service
                ) + "-user-workflow.svg"
                support = (
                    '<a href="https://buymeacoffee.com/hoivikaj">Support the maintainer</a>'
                    if service == "infinidysk"
                    else ""
                )
                self.write_page(
                    channel,
                    f"services/core/{service}/index.html",
                    f'<h2 id="{heading}">Frontend setup</h2><img src="../../assets/{asset}" alt="Workflow"><details class="geek-details"><summary>How it works</summary><pre class="mermaid">flowchart TD</pre></details>{support}',
                    nav=True,
                )

    def platform_links(self, channel):
        prefix = "/dev/" if channel else "/"
        return (
            '<a href="'
            + prefix
            + 'deployment/">Choose a deployment</a>'
            + "".join(
                f'<a href="{prefix}deployment/{platform}/">{platform}</a>'
                for platform in PLATFORMS
            )
        )

    def write_page(self, channel, relative, body, *, nav=False):
        prefix = "/dev/" if channel else "/"
        canonical = (
            "https://example.test" + prefix + relative.removesuffix("index.html")
        )
        path = self.root / channel / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        navigation = (
            f'<nav><a class="md-tabs__link" href="{prefix}deployment/">Deployment</a></nav>'
            if nav
            else ""
        )
        header = (
            f'<header><a class="md-logo" href="{prefix}" data-docs-home><img alt="DUMB logo" src="logo.png"></a>'
            f'<a class="docs-brand" href="{prefix}" data-docs-home>DUMB</a></header>'
        )
        path.write_text(
            f'<html><head><link rel="canonical" href="{canonical}"></head><body>{header}{navigation}<article>{body}</article></body></html>'
        )
        return path

    def audit(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return audit_reader_paths(self.root)

    def test_both_channel_reader_paths_pass(self):
        self.assertEqual(self.audit(), [])

    def test_missing_platform_link_fails(self):
        path = self.root / "deployment/index.html"
        path.write_text(
            path.read_text().replace('<a href="/deployment/qnap/">qnap</a>', "")
        )
        self.assertTrue(
            any(
                "deployment/index.html" in error and "qnap deployment" in error
                for error in self.audit()
            )
        )

    def test_navigation_link_does_not_replace_an_article_link(self):
        path = self.root / "getting-started/index.html"
        path.write_text(
            path.read_text()
            .replace('<a href="/deployment/docker/">docker</a>', "")
            .replace("<article>", '<a href="/deployment/docker/">Docker</a><article>')
        )
        self.assertTrue(
            any(
                "getting-started/index.html" in error and "docker deployment" in error
                for error in self.audit()
            )
        )

    def test_closed_details_do_not_provide_the_visible_platform_route(self):
        path = self.root / "index.html"
        path.write_text(
            path.read_text().replace(
                '<a href="/deployment/docker/">docker</a>',
                '<details><summary>Extra details</summary><a href="/deployment/docker/">docker</a></details>',
            )
        )
        self.assertTrue(any("docker deployment" in error for error in self.audit()))

    def test_buried_support_fails_even_with_another_visible_copy(self):
        path = self.root / "services/core/infinidysk/index.html"
        path.write_text(
            path.read_text().replace(
                '<pre class="mermaid">',
                '<a href="https://buymeacoffee.com/hoivikaj">Support</a><pre class="mermaid">',
            )
        )
        self.assertTrue(any("support is hidden" in error for error in self.audit()))

    def test_missing_visible_support_link_fails(self):
        path = self.root / "services/core/infinidysk/index.html"
        path.write_text(
            path.read_text().replace(
                '<a href="https://buymeacoffee.com/hoivikaj">Support the maintainer</a>',
                "",
            )
        )
        self.assertTrue(
            any("support link is not visible" in error for error in self.audit())
        )

    def test_funding_code_example_is_not_a_reader_link(self):
        path = self.root / "services/core/infinidysk/index.html"
        path.write_text(
            path.read_text().replace(
                '<pre class="mermaid">',
                '<code><a href="https://github.com/sponsors/example">Example markup</a></code><pre class="mermaid">',
            )
        )
        self.assertEqual(self.audit(), [])

    def test_frontend_figure_must_remain_outside_geek_details(self):
        path = self.root / "services/core/altmount/index.html"
        text = path.read_text()
        figure = '<img src="../../assets/altmount-user-workflow.svg" alt="Workflow">'
        path.write_text(
            text.replace(figure, "").replace(
                '<pre class="mermaid">', figure + '<pre class="mermaid">'
            )
        )
        self.assertTrue(
            any("frontend workflow figure" in error for error in self.audit())
        )

    def test_detailed_graph_must_not_replace_visible_frontend_steps(self):
        path = self.root / "services/core/decypharr/index.html"
        path.write_text(
            path.read_text().replace(
                '<details class="geek-details"><summary>How it works</summary><pre class="mermaid">flowchart TD</pre></details>',
                '<pre class="mermaid">flowchart TD</pre>',
            )
        )
        self.assertTrue(any("detailed workflow" in error for error in self.audit()))

    def test_frontend_setup_cannot_be_hidden_with_technical_graph(self):
        path = self.root / "services/core/cli-debrid/index.html"
        text = path.read_text()
        heading = '<h2 id="first-start">Frontend setup</h2>'
        path.write_text(
            text.replace(heading, "").replace(
                '<pre class="mermaid">', heading + '<pre class="mermaid">'
            )
        )
        self.assertTrue(
            any("frontend setup section" in error for error in self.audit())
        )

    def test_top_navigation_needs_the_deployment_route(self):
        path = self.root / "dev/index.html"
        path.write_text(
            path.read_text().replace('class="md-tabs__link"', 'class="other-link"')
        )
        self.assertTrue(any("top navigation" in error for error in self.audit()))

    def test_relative_links_use_the_page_canonical_location(self):
        path = self.root / "dev/getting-started/installation/index.html"
        text = path.read_text()
        for platform in PLATFORMS:
            text = text.replace(
                f'href="/dev/deployment/{platform}/"',
                f'href="../../deployment/{platform}/"',
            )
        path.write_text(text)
        self.assertEqual(self.audit(), [])

    def test_deep_header_links_resolve_to_each_channel_home(self):
        for channel in ("", "dev"):
            prefix = "/dev/" if channel else "/"
            path = self.root / channel / "services/core/infinidysk/index.html"
            path.write_text(
                path.read_text().replace(
                    f'href="{prefix}" data-docs-home', 'href="../../../" data-docs-home'
                )
            )
        self.assertEqual(self.audit(), [])

    def test_homepage_header_links_accept_empty_relative_hrefs(self):
        for channel in ("", "dev"):
            prefix = "/dev/" if channel else "/"
            path = self.root / channel / "index.html"
            path.write_text(
                path.read_text().replace(
                    f'href="{prefix}" data-docs-home', 'href="" data-docs-home'
                )
            )
        self.assertEqual(self.audit(), [])

    def test_deep_header_links_cannot_use_empty_relative_hrefs(self):
        for channel in ("", "dev"):
            prefix = "/dev/" if channel else "/"
            path = self.root / channel / "services/core/infinidysk/index.html"
            path.write_text(
                path.read_text().replace(
                    f'href="{prefix}" data-docs-home', 'href="" data-docs-home'
                )
            )
        errors = self.audit()
        for channel in ("release", "dev"):
            self.assertTrue(
                any(
                    error.startswith(f"{channel}/infinidysk:")
                    and "header home anchor" in error
                    for error in errors
                )
            )

    def test_dev_brand_cannot_send_readers_to_release_home(self):
        path = self.root / "dev/services/core/infinidysk/index.html"
        path.write_text(
            path.read_text().replace(
                'class="docs-brand" href="/dev/"', 'class="docs-brand" href="/"'
            )
        )
        self.assertTrue(any("header home anchor" in error for error in self.audit()))

    def test_header_logo_cannot_send_readers_to_another_origin(self):
        path = self.root / "services/core/infinidysk/index.html"
        path.write_text(
            path.read_text().replace(
                'class="md-logo" href="/"',
                'class="md-logo" href="https://elsewhere.example/"',
            )
        )
        self.assertTrue(any("header home anchor" in error for error in self.audit()))

    def test_header_brand_uses_the_project_name(self):
        path = self.root / "index.html"
        path.write_text(
            path.read_text().replace(
                "data-docs-home>DUMB</a>", "data-docs-home>DUMB docs</a>"
            )
        )
        self.assertTrue(any("brand must read DUMB" in error for error in self.audit()))

    def test_logo_and_name_are_separate_home_controls(self):
        path = self.root / "index.html"
        text = path.read_text().replace('class="md-logo"', 'class="md-logo docs-brand"')
        text = text.replace(
            '<a class="docs-brand" href="/" data-docs-home>DUMB</a>', ""
        )
        path.write_text(text)
        self.assertTrue(
            any("separate logo and DUMB" in error for error in self.audit())
        )

    def test_body_brand_does_not_replace_the_header_control(self):
        path = self.root / "index.html"
        text = path.read_text().replace(
            '<a class="docs-brand" href="/" data-docs-home>DUMB</a>', ""
        )
        path.write_text(
            text.replace(
                "<article>",
                '<article><a class="docs-brand" href="/" data-docs-home>DUMB</a>',
            )
        )
        self.assertTrue(
            any("separate logo and DUMB" in error for error in self.audit())
        )

    def test_home_controls_have_the_navigation_hook(self):
        path = self.root / "index.html"
        path.write_text(
            path.read_text().replace(
                'class="md-logo" href="/" data-docs-home', 'class="md-logo" href="/"'
            )
        )
        self.assertTrue(
            any("separate logo and DUMB" in error for error in self.audit())
        )


if __name__ == "__main__":
    unittest.main()

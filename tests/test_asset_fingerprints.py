"""Cache-safe shared UI assets must stay local and leave old URLs available."""

import hashlib
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.asset_fingerprints import fingerprint_assets


class AssetFingerprintTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.docs = self.root / "docs"
        (self.docs / "assets").mkdir(parents=True)
        self.asset = self.docs / "assets/main.css"
        self.asset.write_text("body { color: green; }\n")

    def test_stable_content_has_stable_url_and_retains_original(self):
        source = "extra_css:\n  - assets/main.css\n"
        actual = fingerprint_assets(source, self.docs)
        self.assertEqual(actual, fingerprint_assets(source, self.docs))
        self.assertEqual(actual, fingerprint_assets(actual, self.docs))
        digest = hashlib.sha256(self.asset.read_bytes()).hexdigest()[:12]
        self.assertIn(f"assets/main.{digest}.css", actual)
        self.assertTrue(self.asset.is_file())
        self.assertEqual(
            (self.docs / f"assets/main.{digest}.css").read_bytes(),
            self.asset.read_bytes(),
        )

    def test_changed_content_gets_new_url(self):
        source = "extra_css: [assets/main.css]\n"
        before = fingerprint_assets(source, self.docs)
        self.asset.write_text("body { color: purple; }\n")
        after = fingerprint_assets(source, self.docs)
        self.assertNotEqual(before, after)
        old_name = yaml.safe_load(before)["extra_css"][0]
        self.assertTrue((self.docs / old_name).is_file())

    def test_only_asset_entries_change_and_remote_urls_stay_untouched(self):
        (self.docs / "assets/docs.js").write_text("window.geek = true;\n")
        source = (
            "extra_css:\n"
            "  - assets/main.css # local stylesheet\n"
            "  - https://cdn.example.com/main.css\n"
            "  - /assets/shared.css\n"
            "extra_javascript: [assets/docs.js, '//cdn.example.com/docs.js']\n"
            "markdown_extensions:\n"
            "  - pymdownx.emoji:\n"
            "      emoji_index: !!python/name:zensical.extensions.emoji.twemoji\n"
            "extra:\n  example: assets/main.css\n"
        )
        actual = fingerprint_assets(source, self.docs)
        self.assertIn("# local stylesheet", actual)
        self.assertIn("https://cdn.example.com/main.css", actual)
        self.assertIn("/assets/shared.css", actual)
        self.assertIn("'//cdn.example.com/docs.js'", actual)
        self.assertIn("!!python/name:zensical.extensions.emoji.twemoji", actual)
        self.assertIn("example: assets/main.css", actual)
        self.assertTrue((self.docs / "assets/docs.js").is_file())

    def test_traversal_and_escaping_symlinks_fail_without_writing_outside(self):
        outside = self.root / "outside.css"
        outside.write_text("original")
        (self.docs / "assets/escape.css").symlink_to(outside)
        for entry in (
            "../outside.css",
            "assets/%2e%2e/%2e%2e/outside.css",
            "assets/%5c..%5coutside.css",
            "assets/escape.css",
        ):
            with self.subTest(entry=entry), self.assertRaises(ValueError):
                fingerprint_assets(f"extra_css: ['{entry}']\n", self.docs)
        self.assertEqual(outside.read_text(), "original")
        self.assertEqual(list(self.root.glob("outside.*.css")), [])

    def test_query_fragment_and_encoded_local_paths_are_preserved(self):
        asset = self.docs / "assets/geek mode.js"
        asset.write_text("window.geek = true;\n")
        actual = fingerprint_assets(
            "extra_javascript: ['assets/geek%20mode.js?v=2#entry']\n", self.docs
        )
        value = yaml.safe_load(actual)["extra_javascript"][0]
        self.assertIn("geek%20mode.", value)
        self.assertTrue(value.endswith(".js?v=2#entry"))

    def test_missing_and_non_asset_strings_remain_unchanged(self):
        source = "extra_css: [assets/missing.css, assets/image.png]\nextra_javascript: [{path: assets/docs.js}]\n"
        self.assertEqual(fingerprint_assets(source, self.docs), source)


if __name__ == "__main__":
    unittest.main()

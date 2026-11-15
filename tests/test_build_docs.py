"""Channel boundaries must survive content edits and release promotion."""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from scripts import build_docs as builder

from scripts.build_docs import (
    filter_content,
    filter_nav,
    frontmatter,
    markdown_url,
    validate_output,
    block_signature,
    mark_development_block,
)


class ChannelContentTests(unittest.TestCase):
    def test_development_notes_are_labelled_with_the_release_boundary(self):
        source = "Common\n<!-- dev:start -->\n## New capability\n\nUse the new tool.\n<!-- dev:end -->"
        result = filter_content(
            source, True, mark_development=True, release_version="2.23.0"
        )
        self.assertIn('class="docs-dev-section"', result)
        self.assertIn("not in the released 2.23.0 docs", result)
        self.assertIn("## New capability", result)

    def test_table_row_badges_preserve_table_structure(self):
        source = "\n| New app | `left \\| right` |\n"
        result = mark_development_block(source, "2.23.0")
        self.assertIn('data-channel="dev"', result)
        self.assertIn(">Dev</span> New app", result)
        self.assertNotIn("<div", result)
        self.assertEqual(result.count("|"), source.count("|"))
        self.assertIn("`left \\| right`", result)

    def test_list_item_badges_keep_numbering(self):
        result = mark_development_block("\n5. Complete setup\n", "2.23.0")
        self.assertIn('5. <span class="docs-channel-badge"', result)
        self.assertNotIn("<div", result)

    def test_promoted_blocks_are_not_labelled_development_only(self):
        body = "\nA feature that shipped.\n"
        source = "<!-- dev:start -->" + body + "<!-- dev:end -->"
        result = filter_content(
            source,
            True,
            mark_development=True,
            release_version="2.24.0",
            released_blocks={block_signature(body)},
        )
        self.assertEqual(result, body)
        self.assertNotIn("docs-dev-section", result)

    def test_new_notes_after_a_promoted_snapshot_are_labelled(self):
        source = "<!-- dev:start -->A newer capability.<!-- dev:end -->"
        result = filter_content(
            source,
            True,
            mark_development=True,
            release_version="2.24.0",
            released_blocks={block_signature("A feature that shipped.")},
        )
        self.assertIn("not in the released 2.24.0 docs", result)

    def test_channel_markers_do_not_change_released_copy(self):
        source = "Shared\n<!-- dev:start -->New feature<!-- dev:end -->"
        result = filter_content(
            source, False, mark_development=True, release_version="2.23.0"
        )
        self.assertNotIn("New feature", result)
        self.assertNotIn("docs-channel-badge", result)

    def test_release_and_development_choose_complete_blocks(self):
        source = "Common\n<!-- dev:start -->\nNew feature\n<!-- dev:end -->\n<!-- release:start -->\nStable instructions\n<!-- release:end -->"
        stable = filter_content(source, False)
        dev = filter_content(source, True)
        self.assertIn("Common", stable)
        self.assertIn("Stable instructions", stable)
        self.assertNotIn("New feature", stable)
        self.assertIn("New feature", dev)
        self.assertNotIn("Stable instructions", dev)
        self.assertNotIn("<!--", stable + dev)

    def test_invalid_blocks_fail_instead_of_leaking_dev_content(self):
        for source in (
            "<!-- dev:start -->unclosed",
            "<!-- dev:end -->",
            "<!-- dev:start --><!-- release:end -->",
            "<!-- dev:start --><!-- release:start --><!-- release:end --><!-- dev:end -->",
        ):
            with self.subTest(source=source), self.assertRaises(ValueError):
                filter_content(source, False)

    def test_filtered_navigation_removes_empty_groups(self):
        source = [
            {"Guides": [{"Stable": "a.md"}, {"New": "b.md"}]},
            {"New only": [{"New": "c.md"}]},
        ]
        self.assertEqual(
            filter_nav(source, {"a.md"}), [{"Guides": [{"Stable": "a.md"}]}]
        )

    def test_markdown_paths_match_directory_urls(self):
        self.assertEqual(markdown_url(Path("index.md")), "")
        self.assertEqual(markdown_url(Path("api/index.md")), "api/")
        self.assertEqual(markdown_url(Path("api/setup.md")), "api/setup/")

    def test_page_metadata_controls_availability(self):
        self.assertIs(
            frontmatter("---\ndevelopment_only: true\n---\n# Page")["development_only"],
            True,
        )
        self.assertEqual(frontmatter("# Plain page"), {})

    def test_repository_pages_have_balanced_markers(self):
        root = Path(__file__).resolve().parents[1]
        for path in (root / "docs").rglob("*.md"):
            with self.subTest(path=str(path)):
                filter_content(path.read_text(), False)
                filter_content(path.read_text(), True)

    def test_output_never_overwrites_authored_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "checkout"
            root.mkdir()
            for path in (
                root,
                root / "docs/services",
                root / ".git",
                root / ".docs-build",
                root.parent,
            ):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    validate_output(path, root)
            validate_output(root / "site", root)
            external = Path(directory) / "output"
            external.mkdir()
            (external / "keep.txt").write_text("user data")
            with self.assertRaises(ValueError):
                validate_output(external, root)
            (external / ".dumb-docs-output").touch()
            validate_output(external, root)


class ReleaseOverrideTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "checkout"
        self.docs = self.root / "frozen-docs"
        (self.docs / "guides").mkdir(parents=True)
        self.page = self.docs / "guides/page.md"
        self.page.write_text("Frozen stable prose")
        self.override = self.root / "release-overrides/2.23.0/guides/page.md"
        self.override.parent.mkdir(parents=True)
        self.override.write_text("Corrected stable prose")

    def apply(self, channel="release", version="2.23.0"):
        return builder.apply_release_overrides(channel, version, self.docs, self.root)

    def test_exact_version_replaces_only_existing_release_prose(self):
        self.assertEqual(self.apply(), ["guides/page.md"])
        self.assertEqual(self.page.read_text(), "Corrected stable prose")
        self.assertEqual(self.override.read_text(), "Corrected stable prose")

    def test_development_and_next_release_ignore_old_override(self):
        self.assertEqual(self.apply("dev"), [])
        self.assertEqual(self.apply(version="2.24.0"), [])
        self.assertEqual(self.page.read_text(), "Frozen stable prose")

    def test_new_route_or_asset_refuses_all_replacements(self):
        for name in ("new-guide.md", "navigation.yml", "image.png"):
            with self.subTest(name=name):
                extra = self.override.parent / name
                extra.write_text("Must not be copied")
                try:
                    with self.assertRaises(ValueError):
                        self.apply()
                    self.assertEqual(self.page.read_text(), "Frozen stable prose")
                finally:
                    extra.unlink()

    def test_new_directory_is_not_created_in_frozen_snapshot(self):
        extra = self.root / "release-overrides/2.23.0/new-section"
        extra.mkdir()
        (extra / "index.md").write_text("New route")
        with self.assertRaisesRegex(ValueError, "directory is absent"):
            self.apply()
        self.assertFalse((self.docs / "new-section").exists())

    def test_source_file_and_directory_symlinks_are_rejected(self):
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        (outside / "secret.md").write_text("Outside evidence must remain untouched")
        link = self.override.parent / "linked.md"
        link.symlink_to(outside / "secret.md")
        with self.assertRaisesRegex(ValueError, "symlinks"):
            self.apply()
        link.unlink()
        link = self.override.parent / "linked-directory"
        link.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlinks"):
            self.apply()
        self.assertEqual(self.page.read_text(), "Frozen stable prose")
        self.assertEqual(
            (outside / "secret.md").read_text(),
            "Outside evidence must remain untouched",
        )

    def test_version_directory_symlink_and_path_traversal_are_rejected(self):
        version = self.root / "release-overrides/2.24.0"
        version.symlink_to(self.override.parent.parent, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlinks"):
            self.apply(version="2.24.0")
        with self.assertRaisesRegex(ValueError, "SemVer"):
            self.apply(version="../../outside")

    def test_target_parent_symlink_cannot_escape_the_document_root(self):
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        (outside / "page.md").write_text("Outside target")
        self.page.unlink()
        self.page.parent.rmdir()
        self.page.parent.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "escapes"):
            self.apply()
        self.assertEqual((outside / "page.md").read_text(), "Outside target")

    def test_frozen_snapshot_ignores_dev_edits_and_accepts_only_stable_correction(self):
        # Model immutable Git objects without configuring or fabricating an author.
        # snapshot() still performs its actual filesystem writes and reads the
        # worktree separately for development.
        live = self.root / "docs"
        (live / "guides").mkdir(parents=True)
        (live / "guides/page.md").write_text("Old worktree")
        (self.root / "mkdocs.yml").write_text("nav: []\ntheme: {}\n")
        frozen_sha = "a" * 40

        def git_object(command, **kwargs):
            if command[1] == "ls-tree":
                return b"docs/guides/page.md\0"
            if command[2] == f"{frozen_sha}:docs/guides/page.md":
                return b"Frozen source from reviewed commit"
            if command[2] == f"{frozen_sha}:mkdocs.yml":
                return b"nav: []\ntheme: {}\n"
            raise AssertionError(command)

        stable = self.root / "release-build"
        development = self.root / "development-build"
        (live / "guides/page.md").write_text("New development-only instructions")
        with (
            patch.object(builder, "ROOT", self.root),
            patch.object(builder.subprocess, "check_output", side_effect=git_object),
        ):
            builder.snapshot(frozen_sha, stable)
            builder.snapshot("WORKTREE", development)
        stable_page = stable / "docs/guides/page.md"
        dev_page = development / "docs/guides/page.md"
        self.assertEqual(stable_page.read_text(), "Frozen source from reviewed commit")
        self.assertEqual(dev_page.read_text(), "New development-only instructions")
        builder.apply_release_overrides("release", "2.23.0", stable / "docs", self.root)
        builder.apply_release_overrides(
            "dev", "2.23.0", development / "docs", self.root
        )
        self.assertEqual(stable_page.read_text(), "Corrected stable prose")
        self.assertEqual(dev_page.read_text(), "New development-only instructions")
        self.assertEqual(
            (live / "guides/page.md").read_text(), "New development-only instructions"
        )


if __name__ == "__main__":
    unittest.main()

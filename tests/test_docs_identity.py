"""Artifact provenance must never turn an untagged preview into a release."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.docs_identity import IdentityError, agent_identity, documentation_identity


class DocumentationIdentityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "pyproject.toml").write_text(
            '[project]\nname = "dumb-docs"\nversion = "1.24.30"\n'
        )
        (self.root / ".github").mkdir()
        self.manifest = self.root / ".github/.release-please-manifest.json"
        self.manifest.write_text(json.dumps({".": "1.24.30"}))
        self.head = "a" * 40
        self.tag_target = self.head
        self.status = ""
        self.commands = []

        def git(root, *arguments):
            self.assertEqual(root, self.root)
            self.commands.append(arguments)
            if arguments == ("rev-parse", "--show-toplevel"):
                return str(self.root)
            if arguments == ("rev-parse", "--verify", "HEAD^{commit}"):
                return self.head
            if arguments == ("status", "--porcelain=v1", "--untracked-files=normal"):
                return self.status
            if arguments == ("rev-parse", "--verify", "refs/tags/1.24.30^{commit}"):
                return self.tag_target
            raise subprocess.CalledProcessError(128, ["git", *arguments])

        self.git = patch("scripts.docs_identity._git", side_effect=git)
        self.git.start()
        self.addCleanup(self.git.stop)

    def test_preview_requires_no_release_claim_even_at_an_exact_clean_tag(self):
        identity = documentation_identity(self.root)
        self.assertEqual(identity["kind"], "preview")
        self.assertIsNone(identity["tag"])
        self.assertIsNone(identity["release_url"])
        self.assertFalse(identity["dirty"])
        self.assertIn("preview (unreleased)", agent_identity(identity))
        self.assertNotIn("Release notes:", agent_identity(identity))

    def test_explicit_release_peels_tag_to_commit_and_preserves_full_provenance(self):
        identity = documentation_identity(self.root, "1.24.30")
        self.assertEqual(identity["kind"], "release")
        self.assertEqual(identity["tag"], "1.24.30")
        self.assertEqual(identity["commit"], "a" * 40)
        self.assertTrue(identity["source_url"].endswith("/commit/" + "a" * 40))
        self.assertTrue(identity["release_url"].endswith("/releases/tag/1.24.30"))
        # ^{commit} handles an annotated tag instead of comparing its tag-object SHA.
        self.assertIn(
            ("rev-parse", "--verify", "refs/tags/1.24.30^{commit}"), self.commands
        )

    def test_nonstable_and_optionlike_tags_are_rejected(self):
        for tag in ["v1.24.30", "1.24.30-rc.1", "01.24.30", "--all", ""]:
            with self.subTest(tag=tag), self.assertRaises(IdentityError):
                documentation_identity(self.root, tag)

    def test_package_and_manifest_must_both_match_release_tag(self):
        with self.assertRaisesRegex(IdentityError, "must match"):
            documentation_identity(self.root, "1.24.31")
        self.manifest.write_text(json.dumps({".": "1.24.29"}))
        with self.assertRaisesRegex(IdentityError, "must match"):
            documentation_identity(self.root, "1.24.30")

    def test_a_matching_ancestor_or_invalid_tag_target_cannot_label_head(self):
        for target in ["b" * 40, "not-a-commit"]:
            self.tag_target = target
            with (
                self.subTest(target=target),
                self.assertRaisesRegex(IdentityError, "exact source HEAD"),
            ):
                documentation_identity(self.root, "1.24.30")

    def test_tracked_and_untracked_changes_are_disclosed_and_block_releases(self):
        for status in [" M docs/index.md", "?? new-guide.md"]:
            self.status = status
            with self.subTest(status=status):
                preview = documentation_identity(self.root)
                self.assertTrue(preview["dirty"])
                self.assertIn("local changes", agent_identity(preview))
                with self.assertRaisesRegex(IdentityError, "clean source"):
                    documentation_identity(self.root, "1.24.30")

    def test_source_export_has_no_fabricated_commit_or_release_links(self):
        with patch("scripts.docs_identity._git", side_effect=FileNotFoundError):
            preview = documentation_identity(self.root)
            self.assertIsNone(preview["commit"])
            self.assertIsNone(preview["source_url"])
            self.assertIsNone(preview["dirty"])
            with self.assertRaisesRegex(IdentityError, "verified Git source"):
                documentation_identity(self.root, "1.24.30")

    def test_source_export_inside_another_repository_does_not_borrow_its_commit(self):
        with patch("scripts.docs_identity._git", return_value=str(self.root.parent)):
            identity = documentation_identity(self.root)
            self.assertIsNone(identity["commit"])
            self.assertIsNone(identity["source_url"])
            with self.assertRaisesRegex(IdentityError, "verified Git source"):
                documentation_identity(self.root, "1.24.30")

    def test_unreadable_status_is_not_treated_as_a_clean_release(self):
        with patch(
            "scripts.docs_identity._git",
            side_effect=[
                str(self.root),
                self.head,
                subprocess.CalledProcessError(128, "git"),
            ],
        ):
            preview = documentation_identity(self.root)
        self.assertEqual(preview["commit"], self.head)
        self.assertIsNone(preview["dirty"])
        with (
            patch(
                "scripts.docs_identity._git",
                side_effect=[
                    str(self.root),
                    self.head,
                    subprocess.CalledProcessError(128, "git"),
                ],
            ),
            self.assertRaisesRegex(IdentityError, "verified Git source"),
        ):
            documentation_identity(self.root, "1.24.30")

    def test_missing_tag_is_an_actionable_release_failure(self):
        with (
            patch(
                "scripts.docs_identity._git",
                side_effect=[
                    str(self.root),
                    self.head,
                    "",
                    subprocess.CalledProcessError(128, "git"),
                ],
            ),
            self.assertRaisesRegex(IdentityError, "exact docs release tag"),
        ):
            documentation_identity(self.root, "1.24.30")


if __name__ == "__main__":
    unittest.main()

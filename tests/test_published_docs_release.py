"""Only the latest published docs release can authorize an artifact's source."""

from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import published_docs_release as published

COMMIT = "1" * 40
MOVED = "2" * 40
ANNOTATION = "3" * 40
NESTED = "4" * 40
TAG = "1.24.29"
URL = f"https://github.com/{published.DOCS}/releases/tag/{TAG}"


def release(tag=TAG, **changes):
    value = {
        "tag_name": tag,
        "draft": False,
        "prerelease": False,
        "html_url": f"https://github.com/{published.DOCS}/releases/tag/{tag}",
    }
    value.update(changes)
    return value


def tag_ref(sha=COMMIT, kind="commit", tag=TAG):
    return {"ref": f"refs/tags/{tag}", "object": {"type": kind, "sha": sha}}


class ReadOnlyGitHub:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def request(self, path, data=None, method="GET"):
        if data is not None or method != "GET":
            raise AssertionError(
                "The published-release verifier attempted an API mutation"
            )
        self.calls.append(path)
        if not self.replies:
            raise AssertionError(f"Unexpected API request {path}")
        value = self.replies.pop(0)
        if isinstance(value, Exception):
            raise value
        return value


class PublishedReleaseTests(unittest.TestCase):
    def test_latest_release_can_be_behind_unreleased_master(self):
        for status in ("ahead", "identical"):
            with self.subTest(status=status):
                api = ReadOnlyGitHub([release(), tag_ref(), {"status": status}])
                self.assertEqual(
                    published.resolve_latest(api),
                    {
                        "tag": TAG,
                        "commit_sha": COMMIT,
                        "version": TAG,
                        "release_url": URL,
                    },
                )
                self.assertEqual(
                    api.calls,
                    [
                        f"/repos/{published.DOCS}/releases/latest",
                        f"/repos/{published.DOCS}/git/ref/tags/{TAG}",
                        f"/repos/{published.DOCS}/compare/{COMMIT}...master",
                    ],
                )

    def test_requested_older_release_cannot_roll_back_publication(self):
        api = ReadOnlyGitHub([release("1.24.30")])
        with self.assertRaisesRegex(published.SyncError, "not the latest"):
            published.resolve_latest(api, TAG, COMMIT)
        self.assertEqual(len(api.calls), 1)

    def test_revalidation_rejects_latest_release_changing_in_either_direction(self):
        for latest in ("1.24.28", "1.24.30"):
            with self.subTest(latest=latest):
                api = ReadOnlyGitHub([release(latest)])
                with self.assertRaisesRegex(published.SyncError, "not the latest"):
                    published.resolve_latest(api, TAG, COMMIT)

    def test_revalidation_rejects_tag_movement(self):
        api = ReadOnlyGitHub([release(), tag_ref(MOVED)])
        with self.assertRaisesRegex(published.SyncError, "tag moved"):
            published.resolve_latest(api, TAG, COMMIT)
        self.assertEqual(len(api.calls), 2)

    def test_matching_prepared_identity_is_rechecked(self):
        api = ReadOnlyGitHub([release(), tag_ref(), {"status": "ahead"}])
        self.assertEqual(
            published.resolve_latest(api, TAG, COMMIT)["commit_sha"], COMMIT
        )
        self.assertEqual(len(api.calls), 3)

    def test_tag_must_be_in_master_ancestry(self):
        for comparison in ({"status": "behind"}, {"status": "diverged"}, {}, [], None):
            with self.subTest(comparison=comparison):
                api = ReadOnlyGitHub([release(), tag_ref(), comparison])
                with self.assertRaisesRegex(published.SyncError, "master ancestry"):
                    published.resolve_latest(api)

    def test_drafts_prereleases_and_non_semver_are_rejected(self):
        for candidate in (
            release(draft=True),
            release(prerelease=True),
            release("1.24.30-rc.1"),
            release("1.24.30+build.1"),
            release("latest"),
            release("01.24.29"),
            release(None),
            [],
            None,
        ):
            with (
                self.subTest(candidate=candidate),
                self.assertRaises(published.SyncError),
            ):
                published.resolve_latest(ReadOnlyGitHub([candidate]))

    def test_docs_tags_must_not_have_a_v_prefix(self):
        with self.assertRaisesRegex(published.SyncError, "unprefixed"):
            published.resolve_latest(ReadOnlyGitHub([release("v1.24.29")]))
        api = ReadOnlyGitHub([])
        with self.assertRaisesRegex(published.SyncError, "unprefixed"):
            published.resolve_latest(api, "v1.24.29")
        self.assertEqual(api.calls, [])

    def test_wrong_repository_and_noncanonical_release_urls_are_rejected(self):
        for url in (
            "https://github.com/another-owner/DUMB_docs/releases/tag/1.24.29",
            "https://github.com/I-am-PUID-0/DUMB/releases/tag/1.24.29",
            "https://example.com/I-am-PUID-0/DUMB_docs/releases/tag/1.24.29",
            "http://github.com/I-am-PUID-0/DUMB_docs/releases/tag/1.24.29",
            URL + "?redirect=another-release",
            URL + "/",
            None,
        ):
            with self.subTest(url=url):
                api = ReadOnlyGitHub([release(html_url=url)])
                with self.assertRaisesRegex(
                    published.SyncError, "canonical repository"
                ):
                    published.resolve_latest(api)
                self.assertEqual(len(api.calls), 1)

    def test_nested_annotated_tags_are_resolved_in_canonical_repository(self):
        ref = tag_ref(ANNOTATION, "tag")
        ref["object"][
            "url"
        ] = "https://api.github.com/repos/another/repo/git/tags/untrusted"
        api = ReadOnlyGitHub(
            [
                release(),
                ref,
                {"object": {"type": "tag", "sha": NESTED}},
                {"object": {"type": "commit", "sha": COMMIT}},
                {"status": "ahead"},
            ]
        )
        self.assertEqual(
            published.resolve_latest(api, TAG, COMMIT)["commit_sha"], COMMIT
        )
        self.assertEqual(
            api.calls[2:4],
            [
                f"/repos/{published.DOCS}/git/tags/{ANNOTATION}",
                f"/repos/{published.DOCS}/git/tags/{NESTED}",
            ],
        )

    def test_wrong_tag_reference_and_malformed_tag_sha_are_rejected(self):
        for ref in (tag_ref(tag="1.24.28"), tag_ref("master")):
            with self.subTest(ref=ref), self.assertRaises(published.SyncError):
                published.resolve_latest(ReadOnlyGitHub([release(), ref]))

    def test_expected_head_must_be_an_immutable_sha(self):
        for sha in ("master", "1" * 39, "1" * 41, "A" * 40):
            with self.subTest(sha=sha):
                api = ReadOnlyGitHub([])
                with self.assertRaisesRegex(
                    published.SyncError, "immutable commit SHA"
                ):
                    published.resolve_latest(api, expected_head=sha)
                self.assertEqual(api.calls, [])


def artifact_identity():
    return {"tag": TAG, "commit_sha": COMMIT, "version": TAG, "release_url": URL}


def write_artifact(root):
    documentation = {
        "version": TAG,
        "kind": "release",
        "commit": COMMIT,
        "tag": TAG,
        "release_url": URL,
        "source_url": f"https://github.com/{published.DOCS}/commit/{COMMIT}",
        "dirty": False,
    }
    html = f"""<!doctype html><html><head>
<meta name="dumb-docs-package-version" content="{TAG}">
<meta name="dumb-docs-build-kind" content="release">
<meta name="dumb-docs-build-commit" content="{COMMIT}">
<meta name="dumb-docs-release-tag" content="{TAG}">
</head><body><div class="docs-build-identity" data-docs-build-kind="release">
<span>Documentation release {TAG}</span><a href="{URL}">Release notes</a>
<a href="{documentation['source_url']}">Source {COMMIT[:8]}</a>
</div></body></html>"""
    for channel, directory, backend in (
        ("release", root, "2.23.0"),
        ("dev", root / "dev", "2.24.0"),
    ):
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "channel.json").write_text(
            json.dumps(
                {"channel": channel, "version": backend, "documentation": documentation}
            )
        )
        (directory / "index.html").write_text(html)


class PublishedArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        write_artifact(self.root)

    def test_both_backend_channels_share_one_independently_versioned_docs_release(self):
        published.verify_artifact(self.root, artifact_identity())

    def test_preview_wrong_source_or_unclean_identity_is_rejected_in_either_channel(
        self,
    ):
        for channel in ("release", "dev"):
            for key, value in (
                ("version", "1.24.30"),
                ("kind", "preview"),
                ("commit", MOVED),
                ("tag", "1.24.28"),
                ("release_url", "https://github.com/another/repo/releases/tag/1.24.29"),
                ("source_url", f"https://github.com/another/repo/commit/{COMMIT}"),
                ("dirty", True),
                ("dirty", 0),
                ("dirty", None),
            ):
                with self.subTest(channel=channel, key=key, value=value):
                    write_artifact(self.root)
                    path = self.root / (
                        "dev/channel.json" if channel == "dev" else "channel.json"
                    )
                    manifest = json.loads(path.read_text())
                    manifest["documentation"][key] = value
                    path.write_text(json.dumps(manifest))
                    with self.assertRaisesRegex(published.SyncError, "validated clean"):
                        published.verify_artifact(self.root, artifact_identity())

    def test_swapped_channel_locations_are_rejected(self):
        path = self.root / "dev/channel.json"
        manifest = json.loads(path.read_text())
        manifest["channel"] = "release"
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(published.SyncError, "channel does not match"):
            published.verify_artifact(self.root, artifact_identity())

    def test_missing_or_invalid_channel_json_is_rejected(self):
        for content in ("invalid json", "null", "[]", "{}", '{"channel":"release"}'):
            with self.subTest(content=content):
                (self.root / "channel.json").write_text(content)
                with self.assertRaises(published.SyncError):
                    published.verify_artifact(self.root, artifact_identity())
        (self.root / "channel.json").unlink()
        with self.assertRaisesRegex(published.SyncError, "Cannot read"):
            published.verify_artifact(self.root, artifact_identity())

    def test_channels_must_agree_even_on_additional_identity_fields(self):
        path = self.root / "dev/channel.json"
        manifest = json.loads(path.read_text())
        manifest["documentation"]["extra"] = "different build"
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(published.SyncError, "channels disagree"):
            published.verify_artifact(self.root, artifact_identity())

    def test_stale_or_duplicate_html_metadata_is_rejected_in_either_channel(self):
        for channel in ("release", "dev"):
            for original, replacement in (
                (
                    f'name="dumb-docs-package-version" content="{TAG}"',
                    'name="dumb-docs-package-version" content="1.24.28"',
                ),
                (
                    'name="dumb-docs-build-kind" content="release"',
                    'name="dumb-docs-build-kind" content="preview"',
                ),
                (
                    f'name="dumb-docs-build-commit" content="{COMMIT}"',
                    f'name="dumb-docs-build-commit" content="{MOVED}"',
                ),
                (
                    f'name="dumb-docs-release-tag" content="{TAG}"',
                    'name="dumb-docs-release-tag" content="1.24.28"',
                ),
                (
                    "</head>",
                    '<meta name="dumb-docs-build-kind" content="release"></head>',
                ),
            ):
                with self.subTest(channel=channel, original=original):
                    write_artifact(self.root)
                    path = self.root / (
                        "dev/index.html" if channel == "dev" else "index.html"
                    )
                    path.write_text(path.read_text().replace(original, replacement))
                    with self.assertRaisesRegex(published.SyncError, "HTML metadata"):
                        published.verify_artifact(self.root, artifact_identity())

    def test_footer_must_identify_the_same_release_and_source(self):
        for original, replacement in (
            ('class="docs-build-identity"', 'class="different-footer"'),
            ('data-docs-build-kind="release"', 'data-docs-build-kind="preview"'),
            (f"Documentation release {TAG}", f"Documentation preview {TAG}"),
            (
                f'href="{URL}"',
                'href="https://github.com/another/repo/releases/tag/1.24.29"',
            ),
            (f"/commit/{COMMIT}", f"/commit/{MOVED}"),
            ("</div>", "<span>Local changes</span></div>"),
        ):
            with self.subTest(original=original):
                write_artifact(self.root)
                path = self.root / "index.html"
                path.write_text(path.read_text().replace(original, replacement))
                with self.assertRaisesRegex(published.SyncError, "footer"):
                    published.verify_artifact(self.root, artifact_identity())

    def test_missing_homepage_is_rejected(self):
        (self.root / "dev/index.html").unlink()
        with self.assertRaisesRegex(
            published.SyncError, "Cannot read the dev artifact homepage"
        ):
            published.verify_artifact(self.root, artifact_identity())


class PublishedReleaseCLITests(unittest.TestCase):
    def test_success_emits_pinned_identity_and_optional_json(self):
        api = ReadOnlyGitHub([release(), tag_ref(), {"status": "ahead"}])
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "github-output"
            manifest = Path(directory) / "release.json"
            artifact = Path(directory) / "site"
            write_artifact(artifact)
            with (
                patch.dict(os.environ, {"GITHUB_OUTPUT": str(output)}, clear=True),
                patch.object(published, "GitHub", return_value=api),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                status = published.main(
                    [
                        "--tag",
                        TAG,
                        "--expected-head",
                        COMMIT,
                        "--output",
                        str(manifest),
                        "--artifact",
                        str(artifact),
                    ]
                )
            self.assertEqual(status, 0)
            identity = json.loads(manifest.read_text())
            self.assertEqual(identity["tag"], TAG)
            self.assertEqual(identity["commit_sha"], COMMIT)
            self.assertEqual(identity["version"], TAG)
            self.assertEqual(identity["release_url"], URL)
            self.assertEqual(
                dict(line.split("=", 1) for line in output.read_text().splitlines()),
                identity,
            )

    def test_failed_revalidation_emits_nothing_and_preserves_existing_manifest(self):
        api = ReadOnlyGitHub([release(), tag_ref(MOVED)])
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "github-output"
            manifest = Path(directory) / "release.json"
            manifest.write_text("previous validated identity\n")
            errors = io.StringIO()
            with (
                patch.dict(os.environ, {"GITHUB_OUTPUT": str(output)}, clear=True),
                patch.object(published, "GitHub", return_value=api),
                contextlib.redirect_stderr(errors),
            ):
                status = published.main(
                    ["--tag", TAG, "--expected-head", COMMIT, "--output", str(manifest)]
                )
            self.assertEqual(status, 1)
            self.assertIn("tag moved", errors.getvalue())
            self.assertFalse(output.exists())
            self.assertEqual(manifest.read_text(), "previous validated identity\n")

    def test_api_failure_is_not_inferred_as_a_release(self):
        api = ReadOnlyGitHub([published.SyncError("GitHub API returned HTTP 403")])
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(published, "GitHub", return_value=api),
            contextlib.redirect_stderr(io.StringIO()) as errors,
        ):
            self.assertEqual(published.main([]), 1)
        self.assertIn("HTTP 403", errors.getvalue())

    def test_artifact_checks_run_before_workflow_outputs_are_emitted(self):
        api = ReadOnlyGitHub([release(), tag_ref(), {"status": "ahead"}])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_artifact(root)
            manifest = root / "dev/channel.json"
            contents = json.loads(manifest.read_text())
            contents["documentation"]["kind"] = "preview"
            manifest.write_text(json.dumps(contents))
            output = root / "github-output"
            with (
                patch.dict(os.environ, {"GITHUB_OUTPUT": str(output)}, clear=True),
                patch.object(published, "GitHub", return_value=api),
                contextlib.redirect_stderr(io.StringIO()) as errors,
            ):
                status = published.main(
                    ["--tag", TAG, "--expected-head", COMMIT, "--artifact", str(root)]
                )
            self.assertEqual(status, 1)
            self.assertIn("validated clean", errors.getvalue())
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()

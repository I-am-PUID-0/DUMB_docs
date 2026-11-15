"""Release promotion must preserve reviewed-source and Git publication boundaries."""

from __future__ import annotations

import copy
import contextlib
import io
import os
import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

SPEC = importlib.util.spec_from_file_location(
    "sync_release", Path(__file__).resolve().parents[1] / "scripts/sync_release.py"
)
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)

OLD = "1" * 40
DEV = "2" * 40
RELEASE = "3" * 40
DOCS_HEAD = "4" * 40
TREE = "5" * 40
NEW_TREE = "6" * 40
NEW_COMMIT = "7" * 40
TAG = "8" * 40
FRONTEND_DEV = "a" * 40
FRONTEND_RELEASE = "b" * 40
FRONTEND_TAG = "c" * 40


def metadata():
    return {
        "release": {
            "version": "2.23.0",
            "source": OLD,
            "label": "Latest release",
            "docs_ref": "9" * 40,
            "include_development": False,
        },
        "dev": {"version": "2.24.0", "source": DEV, "label": "Development"},
    }


class FakeGitHub:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def request(self, path, data=None, method="GET"):
        self.calls.append((path, data, method))
        if not self.replies:
            raise AssertionError(f"Unexpected API request {method} {path}")
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply


class ReleaseSelectionTests(unittest.TestCase):
    def test_same_release_does_not_require_ancestry_or_change_snapshot(self):
        current = metadata()
        proposed = sync.select_release(
            current, {"tag_name": "v2.23.0"}, OLD, DOCS_HEAD, FakeGitHub([])
        )
        self.assertEqual(proposed, current)
        self.assertIsNot(proposed, current)

    def test_existing_tag_must_not_move(self):
        with self.assertRaisesRegex(sync.SyncError, "tag moved"):
            sync.select_release(
                metadata(), {"tag_name": "2.23.0"}, RELEASE, DOCS_HEAD, FakeGitHub([])
            )

    def test_promotion_freezes_reviewed_head_and_preserves_labels(self):
        for status in ["ahead", "identical"]:
            with self.subTest(status=status):
                original = metadata()
                before = copy.deepcopy(original)
                api = FakeGitHub([{"status": status}])
                proposed = sync.select_release(
                    original, {"tag_name": "v2.24.0"}, RELEASE, DOCS_HEAD, api
                )
                self.assertEqual(original, before)
                self.assertEqual(proposed["dev"], original["dev"])
                self.assertEqual(
                    proposed["release"],
                    {
                        "version": "2.24.0",
                        "source": RELEASE,
                        "label": "Latest release",
                        "docs_ref": DOCS_HEAD,
                        "include_development": True,
                    },
                )
                self.assertEqual(
                    api.calls,
                    [(f"/repos/{sync.BACKEND}/compare/{DEV}...{RELEASE}", None, "GET")],
                )

    def test_unreviewed_version_is_not_relabelled(self):
        with self.assertRaisesRegex(
            sync.SyncError, "no reviewed documentation candidate"
        ):
            sync.select_release(
                metadata(), {"tag_name": "2.25.0"}, RELEASE, DOCS_HEAD, FakeGitHub([])
            )

    def test_release_must_contain_reviewed_source(self):
        for status in ["behind", "diverged", None, "unknown"]:
            with (
                self.subTest(status=status),
                self.assertRaisesRegex(sync.SyncError, "does not contain"),
            ):
                sync.select_release(
                    metadata(),
                    {"tag_name": "2.24.0"},
                    RELEASE,
                    DOCS_HEAD,
                    FakeGitHub([{"status": status}]),
                )

    def test_prereleases_drafts_and_non_semver_tags_are_rejected(self):
        for release in [
            {"tag_name": "2.24.0", "prerelease": True},
            {"tag_name": "2.24.0", "draft": True},
            {"tag_name": "2.24.0-rc.1"},
            {"tag_name": "latest"},
            {"tag_name": "02.24.0"},
        ]:
            with self.subTest(release=release), self.assertRaises(sync.SyncError):
                sync.select_release(
                    metadata(), release, RELEASE, DOCS_HEAD, FakeGitHub([])
                )

    def test_regressed_latest_release_is_rejected(self):
        with self.assertRaisesRegex(sync.SyncError, "older than"):
            sync.select_release(
                metadata(), {"tag_name": "2.22.0"}, RELEASE, DOCS_HEAD, FakeGitHub([])
            )

    def test_source_must_be_immutable(self):
        current = metadata()
        current["dev"]["source"] = "dev"
        with self.assertRaisesRegex(sync.SyncError, "immutable"):
            sync.select_release(
                current, {"tag_name": "2.24.0"}, RELEASE, DOCS_HEAD, FakeGitHub([])
            )


class FrontendReleaseTests(unittest.TestCase):
    def test_current_backend_release_never_queries_new_frontend(self):
        current = metadata()
        current["dev"]["frontend_source"] = FRONTEND_DEV
        api = FakeGitHub([])
        proposed = sync.select_release(
            current, {"tag_name": "2.23.0"}, OLD, DOCS_HEAD, api
        )
        self.assertEqual(proposed, current)
        self.assertEqual(api.calls, [])

    def test_pending_frontend_prevents_backend_docs_promotion(self):
        for status in ["behind", "diverged", None]:
            with self.subTest(status=status):
                current = metadata()
                current["dev"]["frontend_source"] = FRONTEND_DEV
                before = copy.deepcopy(current)
                api = FakeGitHub(
                    [
                        {"status": "ahead"},
                        {"tag_name": "v1.91.0"},
                        {
                            "ref": "refs/tags/v1.91.0",
                            "object": {"type": "commit", "sha": FRONTEND_RELEASE},
                        },
                        {"status": status},
                    ]
                )
                with self.assertRaisesRegex(
                    sync.SyncError, "Publish the compatible dmbdb release first"
                ):
                    sync.select_release(
                        current, {"tag_name": "2.24.0"}, RELEASE, DOCS_HEAD, api
                    )
                self.assertEqual(current, before)
                self.assertTrue(all(method == "GET" for _, _, method in api.calls))
                self.assertEqual(
                    api.calls[-1][0],
                    f"/repos/{sync.FRONTEND}/compare/{FRONTEND_DEV}...{FRONTEND_RELEASE}",
                )

    def test_compatible_independently_versioned_frontend_is_recorded(self):
        for status in ["ahead", "identical"]:
            with self.subTest(status=status):
                current = metadata()
                current["dev"]["frontend_source"] = FRONTEND_DEV
                api = FakeGitHub(
                    [
                        {"status": "ahead"},
                        {"tag_name": "v1.93.0"},
                        {
                            "ref": "refs/tags/v1.93.0",
                            "object": {"type": "tag", "sha": FRONTEND_TAG},
                        },
                        {"object": {"type": "commit", "sha": FRONTEND_RELEASE}},
                        {"status": status},
                    ]
                )
                proposed = sync.select_release(
                    current, {"tag_name": "2.24.0"}, RELEASE, DOCS_HEAD, api
                )
                self.assertEqual(proposed["release"]["version"], "2.24.0")
                self.assertEqual(proposed["release"]["source"], RELEASE)
                self.assertEqual(proposed["release"]["frontend_version"], "1.93.0")
                self.assertEqual(
                    proposed["release"]["frontend_source"], FRONTEND_RELEASE
                )
                self.assertEqual(proposed["release"]["label"], "Latest release")
                self.assertEqual(proposed["dev"], current["dev"])
                self.assertIn(
                    (f"/repos/{sync.FRONTEND}/git/tags/{FRONTEND_TAG}", None, "GET"),
                    api.calls,
                )

    def test_absent_frontend_requirement_preserves_backward_compatibility(self):
        api = FakeGitHub([{"status": "ahead"}])
        proposed = sync.select_release(
            metadata(), {"tag_name": "2.24.0"}, RELEASE, DOCS_HEAD, api
        )
        self.assertNotIn("frontend_source", proposed["release"])
        self.assertNotIn("frontend_version", proposed["release"])
        self.assertEqual(len(api.calls), 1)
        self.assertTrue(api.calls[0][0].startswith(f"/repos/{sync.BACKEND}/"))

    def test_nonstable_frontend_does_not_authorize_promotion(self):
        current = metadata()
        current["dev"]["frontend_source"] = FRONTEND_DEV
        for release in [
            {"tag_name": "v1.92.0", "draft": True},
            {"tag_name": "v1.92.0", "prerelease": True},
            {"tag_name": "v1.92.0-rc.1"},
        ]:
            with self.subTest(release=release), self.assertRaises(sync.SyncError):
                sync.select_release(
                    current,
                    {"tag_name": "2.24.0"},
                    RELEASE,
                    DOCS_HEAD,
                    FakeGitHub([{"status": "ahead"}, release]),
                )


class TagResolutionTests(unittest.TestCase):
    def test_lightweight_tag(self):
        api = FakeGitHub(
            [{"ref": "refs/tags/v2.24.0", "object": {"type": "commit", "sha": RELEASE}}]
        )
        self.assertEqual(sync.release_commit(api, "v2.24.0"), RELEASE)
        self.assertEqual(len(api.calls), 1)

    def test_nested_annotated_tags_are_peeled(self):
        api = FakeGitHub(
            [
                {"ref": "refs/tags/2.24.0", "object": {"type": "tag", "sha": TAG}},
                {"object": {"type": "tag", "sha": OLD}},
                {"object": {"type": "commit", "sha": RELEASE}},
            ]
        )
        self.assertEqual(sync.release_commit(api, "2.24.0"), RELEASE)
        self.assertEqual(
            [call[0] for call in api.calls][1:],
            [
                f"/repos/{sync.BACKEND}/git/tags/{TAG}",
                f"/repos/{sync.BACKEND}/git/tags/{OLD}",
            ],
        )

    def test_wrong_reference_is_rejected(self):
        api = FakeGitHub(
            [{"ref": "refs/tags/other", "object": {"type": "commit", "sha": RELEASE}}]
        )
        with self.assertRaisesRegex(sync.SyncError, "did not match"):
            sync.release_commit(api, "2.24.0")

    def test_cycles_and_noncommit_targets_are_rejected(self):
        for replies in [
            [{"ref": "refs/tags/2.24.0", "object": {"type": "blob", "sha": TAG}}],
            [
                {"ref": "refs/tags/2.24.0", "object": {"type": "tag", "sha": TAG}},
                {"object": {"type": "tag", "sha": TAG}},
            ],
        ]:
            with self.subTest(replies=replies), self.assertRaises(sync.SyncError):
                sync.release_commit(FakeGitHub(replies), "2.24.0")


class PublicationTests(unittest.TestCase):
    def test_only_metadata_path_is_published_with_a_fast_forward_lease(self):
        api = FakeGitHub(
            [
                {"object": {"sha": DOCS_HEAD}},
                {"tree": {"sha": TREE}},
                {"sha": NEW_TREE},
                {"sha": NEW_COMMIT},
                {},
            ]
        )
        candidate = metadata()
        self.assertEqual(sync.publish(api, DOCS_HEAD, candidate), NEW_COMMIT)
        tree_path, tree_body, tree_method = api.calls[2]
        self.assertEqual(
            (tree_path, tree_method), (f"/repos/{sync.DOCS}/git/trees", "POST")
        )
        self.assertEqual(tree_body["base_tree"], TREE)
        self.assertEqual(len(tree_body["tree"]), 1)
        entry = tree_body["tree"][0]
        self.assertEqual(entry["path"], "docs-versions.json")
        self.assertEqual(entry["mode"], "100644")
        self.assertEqual(json.loads(entry["content"]), candidate)
        commit_body = api.calls[3][1]
        self.assertEqual(commit_body["parents"], [DOCS_HEAD])
        self.assertNotIn("author", commit_body)
        self.assertNotIn("committer", commit_body)
        self.assertEqual(
            api.calls[-1],
            (
                f"/repos/{sync.DOCS}/git/refs/heads/master",
                {"sha": NEW_COMMIT, "force": False},
                "PATCH",
            ),
        )

    def test_stale_head_refuses_all_mutations(self):
        api = FakeGitHub([{"object": {"sha": RELEASE}}])
        with self.assertRaisesRegex(sync.SyncError, "branch changed"):
            sync.publish(api, DOCS_HEAD, metadata())
        self.assertEqual(len(api.calls), 1)

    def test_concurrent_commit_rejection_is_not_forced_or_retried(self):
        api = FakeGitHub(
            [
                {"object": {"sha": DOCS_HEAD}},
                {"tree": {"sha": TREE}},
                {"sha": NEW_TREE},
                {"sha": NEW_COMMIT},
                sync.SyncError("Not a fast forward"),
            ]
        )
        with self.assertRaisesRegex(sync.SyncError, "fast forward"):
            sync.publish(api, DOCS_HEAD, metadata())
        self.assertEqual(len(api.calls), 5)
        self.assertIs(api.calls[-1][1]["force"], False)

    def test_final_head_guard_rejects_stale_artifact(self):
        with self.assertRaisesRegex(sync.SyncError, "must not be deployed"):
            sync.assert_current(FakeGitHub([{"object": {"sha": RELEASE}}]), NEW_COMMIT)

    def test_api_errors_do_not_log_tokens_or_response_bodies(self):
        token = "secret-token-for-test"
        error = HTTPError(
            "https://api.github.com/", 403, "sensitive response", {}, None
        )
        with patch.object(sync, "urlopen", side_effect=error):
            with self.assertRaises(sync.SyncError) as result:
                sync.GitHub(token).request(f"/repos/{sync.BACKEND}/releases/latest")
        self.assertNotIn(token, str(result.exception))
        self.assertNotIn("sensitive", str(result.exception))
        self.assertIn("403", str(result.exception))

    def test_only_explicit_optional_get_accepts_a_missing_resource(self):
        error = HTTPError("https://api.github.com/", 404, "missing", {}, None)
        with patch.object(sync, "urlopen", side_effect=error):
            api = sync.GitHub("test-token")
            self.assertIsNone(
                api.request(
                    f"/repos/{sync.DOCS}/actions/variables/RECEIPT", missing_ok=True
                )
            )
            with self.assertRaisesRegex(sync.SyncError, "404"):
                api.request(f"/repos/{sync.DOCS}/actions/variables/RECEIPT")

    def test_optional_get_does_not_hide_permission_errors(self):
        error = HTTPError("https://api.github.com/", 403, "denied", {}, None)
        with patch.object(sync, "urlopen", side_effect=error):
            with self.assertRaisesRegex(sync.SyncError, "403"):
                sync.GitHub("test-token").request(
                    f"/repos/{sync.DOCS}/actions/variables/RECEIPT", missing_ok=True
                )

    def test_mutations_cannot_allow_missing_resources(self):
        with patch.object(sync, "urlopen") as request:
            with self.assertRaisesRegex(sync.SyncError, "Only read requests"):
                sync.GitHub("test-token").request(
                    f"/repos/{sync.DOCS}/actions/variables", {}, "POST", missing_ok=True
                )
        request.assert_not_called()

    def test_successful_empty_mutation_responses_are_supported(self):
        from unittest.mock import MagicMock

        for method in ("POST", "PATCH"):
            with self.subTest(method=method):
                response = MagicMock()
                response.__enter__.return_value.read.return_value = b""
                with patch.object(sync, "urlopen", return_value=response):
                    self.assertIsNone(
                        sync.GitHub("test-token").request(
                            f"/repos/{sync.DOCS}/actions/variables", {}, method
                        )
                    )

    def test_successful_empty_get_is_not_a_valid_api_response(self):
        from unittest.mock import MagicMock

        response = MagicMock()
        response.__enter__.return_value.read.return_value = b""
        with patch.object(sync, "urlopen", return_value=response):
            with self.assertRaisesRegex(sync.SyncError, "empty read response"):
                sync.GitHub("test-token").request(f"/repos/{sync.DOCS}")


class PublisherAuthorityTests(unittest.TestCase):
    def test_admin_actor_passes_a_read_only_authority_check(self):
        api = FakeGitHub([{"permissions": {"admin": True}}])
        sync.assert_publisher(api)
        self.assertEqual(api.calls, [(f"/repos/{sync.DOCS}", None, "GET")])

    def test_missing_or_nonadmin_authority_is_rejected(self):
        for repository in [
            {},
            {"permissions": None},
            {"permissions": {}},
            {"permissions": {"admin": False}},
            {"permissions": {"admin": "true"}},
        ]:
            with self.subTest(repository=repository):
                api = FakeGitHub([repository])
                with self.assertRaisesRegex(
                    sync.SyncError, "repository admin authority"
                ):
                    sync.assert_publisher(api)
                self.assertEqual(api.calls, [(f"/repos/{sync.DOCS}", None, "GET")])


class PublicationCLITests(unittest.TestCase):
    def invoke(self, api, validated):
        api.token = "publishing-token-fixture"
        environment = {
            "GITHUB_REPOSITORY": sync.DOCS,
            "GITHUB_TOKEN": api.token,
            "DOCS_PROMOTION_METADATA": json.dumps(validated),
        }
        errors = io.StringIO()
        with (
            patch.dict(os.environ, environment, clear=True),
            patch.object(sync, "GitHub", return_value=api),
            patch.object(
                sync.subprocess, "check_output", return_value=json.dumps(metadata())
            ) as source_reader,
            contextlib.redirect_stderr(errors),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            status = sync.main(["--publish", "--expected-head", DOCS_HEAD])
            self.source_reads = list(source_reader.mock_calls)
        return status, errors.getvalue()

    def test_nonadmin_publisher_fails_before_source_reads_or_any_write(self):
        api = FakeGitHub([{"permissions": {"admin": False}}])
        status, error = self.invoke(api, metadata())
        self.assertEqual(status, 1)
        self.assertIn("repository admin authority", error)
        self.assertEqual(self.source_reads, [])
        self.assertEqual(api.calls, [(f"/repos/{sync.DOCS}", None, "GET")])

    def test_noop_publication_still_checks_admin_without_branch_mutation(self):
        api = FakeGitHub(
            [
                {"permissions": {"admin": True}},
                {"tag_name": "2.23.0"},
                {"ref": "refs/tags/2.23.0", "object": {"type": "commit", "sha": OLD}},
                {"object": {"sha": DOCS_HEAD}},
            ]
        )
        status, error = self.invoke(api, metadata())
        self.assertEqual(status, 0, error)
        self.assertEqual(api.calls[0], (f"/repos/{sync.DOCS}", None, "GET"))
        self.assertTrue(all(method == "GET" for _, _, method in api.calls))

    def test_modified_validated_metadata_cannot_be_published(self):
        api = FakeGitHub(
            [
                {"permissions": {"admin": True}},
                {"tag_name": "2.24.0"},
                {
                    "ref": "refs/tags/2.24.0",
                    "object": {"type": "commit", "sha": RELEASE},
                },
                {"status": "ahead"},
            ]
        )
        validated = metadata()
        validated["release"].update(
            version="2.24.0",
            source=RELEASE,
            docs_ref=DOCS_HEAD,
            include_development=True,
        )
        validated["release"]["label"] = "Modified after validation"
        status, error = self.invoke(api, validated)
        self.assertEqual(status, 1)
        self.assertIn("differs from the current verified proposal", error)
        self.assertTrue(all(method == "GET" for _, _, method in api.calls))

    def test_upstream_advancement_between_jobs_requires_a_new_build(self):
        api = FakeGitHub(
            [
                {"permissions": {"admin": True}},
                {"tag_name": "2.25.0"},
                {
                    "ref": "refs/tags/2.25.0",
                    "object": {"type": "commit", "sha": RELEASE},
                },
            ]
        )
        validated = metadata()
        validated["release"].update(
            version="2.24.0",
            source=RELEASE,
            docs_ref=DOCS_HEAD,
            include_development=True,
        )
        status, error = self.invoke(api, validated)
        self.assertEqual(status, 1)
        self.assertIn("no reviewed documentation candidate", error)
        self.assertTrue(all(method == "GET" for _, _, method in api.calls))


if __name__ == "__main__":
    unittest.main()

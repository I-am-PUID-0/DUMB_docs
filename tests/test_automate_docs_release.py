"""Automatic admin merges must remain restricted to verified release metadata."""

from __future__ import annotations

import base64
import contextlib
import copy
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from scripts import automate_docs_release as release

BASE, HEAD, MERGED, OTHER = (digit * 40 for digit in "1234")
NUMBER = 166
OLD, NEW = "1.24.29", "1.25.0"


def candidate():
    return {
        "number": NUMBER,
        "state": "open",
        "merged": False,
        "draft": False,
        "title": f"chore(master): release {NEW}",
        "body": f"{release.BODY_START}\n\n## [{NEW}](https://github.com/{release.DOCS}/compare/{OLD}...{NEW}) (2026-11-15)\n\n{release.BODY_END}",
        "user": {"login": release.AUTHOR},
        "labels": [{"name": "autorelease: pending"}],
        "head": {
            "sha": HEAD,
            "ref": release.BRANCH,
            "repo": {"full_name": release.DOCS},
        },
        "base": {"sha": BASE, "ref": "master", "repo": {"full_name": release.DOCS}},
    }


def contents():
    old_changelog = (
        "# Changelog\n\n\n## [1.24.29](old-release)\n\n* Previous release.\n"
    )
    new_changelog = (
        f"# Changelog\n\n\n## [{NEW}](https://github.com/{release.DOCS}/compare/{OLD}...{NEW}) (2026-11-15)\n"
        "\n### Documentation\n\n* Improve the guides.\n\n"
        + old_changelog[old_changelog.index("## ") :]
    )
    return {
        BASE: {
            ".github/.release-please-manifest.json": json.dumps({".": OLD}),
            "pyproject.toml": f'[project]\nname = "dumb-docs"\nversion = "{OLD}"\ndependencies = []\n',
            "CHANGELOG.md": old_changelog,
        },
        HEAD: {
            ".github/.release-please-manifest.json": json.dumps({".": NEW}),
            "pyproject.toml": f'[project]\nname = "dumb-docs"\nversion = "{NEW}"\ndependencies = []\n',
            "CHANGELOG.md": new_changelog,
        },
    }


class FakeGitHub:
    def __init__(self):
        self.pr = candidate()
        self.master = BASE
        self.admin = True
        self.files = [
            {"filename": path, "status": "modified"} for path in sorted(release.FILES)
        ]
        self.contents = contents()
        self.checks = [
            {
                "id": index,
                "name": name,
                "app": {"slug": app},
                "head_sha": HEAD,
                "status": "completed",
                "conclusion": "success",
            }
            for index, (name, app) in enumerate(sorted(release.CHECKS), 1)
        ]
        self.workflows = [
            {
                "id": index,
                "path": path,
                "event": event,
                "head_sha": HEAD,
                "run_attempt": 1,
                "status": "completed",
                "conclusion": "success",
            }
            for index, (path, event) in enumerate(sorted(release.WORKFLOWS), 100)
        ]
        self.comparison = {
            "status": "ahead",
            "behind_by": 0,
            "base_commit": {"sha": BASE},
            "merge_base_commit": {"sha": BASE},
        }
        self.merge_response = {"merged": True, "sha": MERGED}
        self.calls = []
        self.check_reads = 0
        self.workflow_reads = 0
        self.pr_reads = 0
        self.master_reads = 0
        self.hook = lambda path: None

    def request(self, path, data=None, method="GET"):
        self.calls.append((path, data, method))
        self.hook(path)
        prefix = f"/repos/{release.DOCS}"
        if path == prefix:
            result = {"permissions": {"admin": self.admin}}
        elif path == f"{prefix}/pulls/{NUMBER}":
            self.pr_reads += 1
            result = self.pr
        elif path == f"{prefix}/git/ref/heads/master":
            self.master_reads += 1
            result = {"object": {"sha": self.master}}
        elif path.startswith(f"{prefix}/compare/"):
            result = self.comparison
        elif path == f"{prefix}/pulls/{NUMBER}/files?per_page=100":
            result = self.files
        elif path.startswith(f"{prefix}/contents/"):
            url = urlparse(path)
            ref = parse_qs(url.query)["ref"][0]
            content = self.contents[ref][url.path.split("/contents/", 1)[1]].encode()
            result = {
                "type": "file",
                "encoding": "base64",
                "content": base64.b64encode(content).decode(),
            }
        elif "/check-runs?" in path:
            self.check_reads += 1
            page = int(parse_qs(urlparse(path).query)["page"][0])
            result = {
                "total_count": len(self.checks),
                "check_runs": self.checks[(page - 1) * 100 : page * 100],
            }
        elif "/actions/runs?" in path:
            self.workflow_reads += 1
            page = int(parse_qs(urlparse(path).query)["page"][0])
            result = {
                "total_count": len(self.workflows),
                "workflow_runs": self.workflows[(page - 1) * 100 : page * 100],
            }
        elif path == f"{prefix}/pulls/{NUMBER}/merge" and method == "PUT":
            result = self.merge_response
        else:
            raise AssertionError(f"Unexpected API call: {method} {path}")
        return copy.deepcopy(result)

    @property
    def merges(self):
        return [call for call in self.calls if call[2] != "GET"]


class AutomaticReleaseTests(unittest.TestCase):
    def setUp(self):
        self.api = FakeGitHub()

    def run_release(self, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return release.automate(
                self.api, NUMBER, wait=kwargs.pop("wait", 0), **kwargs
            )

    def assert_rejected(self, message):
        with self.assertRaisesRegex(release.SyncError, message):
            self.run_release()
        self.assertEqual(self.api.merges, [])

    def test_validated_release_merges_only_its_exact_head(self):
        result = self.run_release()
        self.assertEqual(
            result, {"result": "merged", "pull_request": "166", "commit_sha": MERGED}
        )
        self.assertEqual(
            self.api.merges,
            [
                (
                    f"/repos/{release.DOCS}/pulls/166/merge",
                    {"sha": HEAD, "merge_method": "squash"},
                    "PUT",
                )
            ],
        )
        self.assertEqual(self.api.check_reads, 2)

    def test_generated_identity_is_required_not_just_a_label(self):
        changes = [
            lambda pr: pr.update(draft=True),
            lambda pr: pr.update(title="chore: release 1.25.0"),
            lambda pr: pr.update(body="Please merge this release"),
            lambda pr: pr.update(labels=[]),
            lambda pr: pr["user"].update(login="someone-else"),
            lambda pr: pr["head"].update(ref="lookalike-release"),
            lambda pr: pr["head"]["repo"].update(full_name="example/fork"),
            lambda pr: pr["base"].update(ref="dev"),
            lambda pr: pr["base"]["repo"].update(full_name="example/other"),
        ]
        for change in changes:
            with self.subTest(change=changes.index(change)):
                self.api = FakeGitHub()
                change(self.api.pr)
                self.assert_rejected("expected managed")

    def test_non_admin_token_stops_before_reading_or_changing_the_pr(self):
        self.api.admin = False
        self.assert_rejected("admin")
        self.assertEqual(len(self.api.calls), 1)

    def test_closed_release_is_an_idempotent_noop(self):
        self.api.pr.update(state="closed", merged=True)
        self.assertEqual(self.run_release()["result"], "noop")
        self.assertEqual(self.api.merges, [])

    def test_code_or_workflow_changes_are_not_release_metadata(self):
        self.api.files.append(
            {"filename": ".github/workflows/deploy.yml", "status": "modified"}
        )
        self.assert_rejected("only the three")

    def test_renamed_or_created_metadata_requires_manual_review(self):
        for status in ("renamed", "added", "removed"):
            with self.subTest(status=status):
                self.api = FakeGitHub()
                self.api.files[0]["status"] = status
                self.assert_rejected("only the three")

    def test_manifest_cannot_change_another_package(self):
        self.api.contents[HEAD][".github/.release-please-manifest.json"] = json.dumps(
            {".": NEW, "other": "1.0.0"}
        )
        self.assert_rejected("root package version")

    def test_title_manifest_and_package_versions_must_agree(self):
        self.api.contents[HEAD][".github/.release-please-manifest.json"] = json.dumps(
            {".": "1.25.1"}
        )
        self.assert_rejected("root package version")

    def test_body_release_heading_must_match_the_title(self):
        self.api.pr["body"] = self.api.pr["body"].replace(f"## [{NEW}]", "## [1.25.1]")
        self.assert_rejected("expected managed")

    def test_body_compare_must_match_the_actual_version_advance(self):
        self.api.pr["body"] = self.api.pr["body"].replace(
            f"{OLD}...{NEW}", f"1.24.28...{NEW}"
        )
        self.assert_rejected("exactly the new release")

    def test_release_version_cannot_stay_unchanged_or_go_backwards(self):
        for version in (OLD, "1.24.28"):
            with self.subTest(version=version):
                self.api = FakeGitHub()
                self.api.pr["title"] = f"chore(master): release {version}"
                self.api.pr["body"] = self.api.pr["body"].replace(NEW, version)
                self.api.contents[HEAD][".github/.release-please-manifest.json"] = (
                    json.dumps({".": version})
                )
                self.assert_rejected("root package version")

    def test_pyproject_dependency_changes_are_rejected(self):
        self.api.contents[HEAD]["pyproject.toml"] = self.api.contents[HEAD][
            "pyproject.toml"
        ].replace("dependencies = []", 'dependencies = ["another-package"]')
        self.assert_rejected("only its version-line")

    def test_changelog_history_cannot_be_rewritten(self):
        self.api.contents[HEAD]["CHANGELOG.md"] = self.api.contents[HEAD][
            "CHANGELOG.md"
        ].replace("Previous release.", "Rewritten history.")
        self.assert_rejected("existing history")

    def test_changelog_cannot_add_another_release_section(self):
        self.api.contents[HEAD]["CHANGELOG.md"] = self.api.contents[HEAD][
            "CHANGELOG.md"
        ].replace("### Documentation", "## [9.0.0](other)\n\n### Documentation")
        self.assert_rejected("exactly the new release")

    def test_missing_check_does_not_inherit_another_contexts_success(self):
        self.api.checks = [run for run in self.api.checks if run["name"] != "CodeQL"]
        self.assertEqual(self.run_release()["result"], "noop")
        self.assertEqual(self.api.merges, [])

    def test_wrong_app_cannot_impersonate_the_security_gate(self):
        next(run for run in self.api.checks if run["name"] == "CodeQL")["app"][
            "slug"
        ] = "github-actions"
        self.assertEqual(self.run_release()["result"], "noop")
        self.assertEqual(self.api.merges, [])

    def test_latest_pending_failed_or_skipped_rerun_overrides_old_success(self):
        for status, conclusion in (
            ("in_progress", None),
            ("completed", "failure"),
            ("completed", "skipped"),
            ("completed", "cancelled"),
        ):
            with self.subTest(status=status, conclusion=conclusion):
                self.api = FakeGitHub()
                rerun = copy.deepcopy(self.api.checks[0])
                rerun.update(id=100, status=status, conclusion=conclusion)
                self.api.checks.append(rerun)
                self.assertEqual(self.run_release()["result"], "noop")
                self.assertEqual(self.api.merges, [])

    def test_successful_check_must_belong_to_exact_head(self):
        self.api.checks[0]["head_sha"] = OTHER
        self.assert_rejected("does not belong")

    def test_check_pagination_is_not_silently_truncated(self):
        self.api.checks[:0] = [
            {"id": index + 10, "name": "Unrelated", "app": {"slug": "example"}}
            for index in range(100)
        ]
        self.assertEqual(self.run_release()["result"], "merged")
        self.assertEqual(self.api.check_reads, 4)

    def test_queued_workflow_rerun_blocks_even_when_old_job_checks_pass(self):
        for index in range(len(self.api.workflows)):
            for status in ("queued", "in_progress"):
                with self.subTest(index=index, status=status):
                    self.api = FakeGitHub()
                    rerun = copy.deepcopy(self.api.workflows[index])
                    rerun.update(id=1000, status=status, conclusion=None)
                    self.api.workflows.append(rerun)
                    self.assertEqual(self.run_release()["result"], "noop")
                    self.assertEqual(self.api.merges, [])

    def test_latest_workflow_failure_overrides_old_workflow_success(self):
        rerun = copy.deepcopy(self.api.workflows[0])
        rerun.update(id=1000, conclusion="failure")
        self.api.workflows.append(rerun)
        self.assertEqual(self.run_release()["result"], "noop")
        self.assertEqual(self.api.merges, [])

    def test_updated_workflow_attempt_blocks_old_attempt_success(self):
        rerun = copy.deepcopy(self.api.workflows[0])
        rerun.update(run_attempt=2, status="queued", conclusion=None)
        self.api.workflows.append(rerun)
        self.assertEqual(self.run_release()["result"], "noop")
        self.assertEqual(self.api.merges, [])

    def test_required_workflow_must_belong_to_the_exact_head(self):
        self.api.workflows[0]["head_sha"] = OTHER
        self.assert_rejected("workflow result does not belong")

    def test_unrelated_failing_workflows_do_not_block_the_release(self):
        unrelated = copy.deepcopy(self.api.workflows[0])
        unrelated.update(
            id=1000, path=".github/workflows/other.yml", conclusion="failure"
        )
        self.api.workflows.append(unrelated)
        self.assertEqual(self.run_release()["result"], "merged")

    def test_another_event_cannot_replace_the_required_pr_workflow(self):
        self.api.workflows[0]["event"] = "push"
        self.assertEqual(self.run_release()["result"], "noop")
        self.assertEqual(self.api.merges, [])

    def test_workflow_pagination_preserves_the_required_results(self):
        self.api.workflows[:0] = [
            {"id": index + 1000, "path": "other", "event": "push"}
            for index in range(100)
        ]
        self.assertEqual(self.run_release()["result"], "merged")
        self.assertEqual(self.api.workflow_reads, 4)

    def test_excess_workflow_pages_fail_closed(self):
        response = {"total_count": 1001, "workflow_runs": []}
        with patch.object(self.api, "request", return_value=response):
            with self.assertRaisesRegex(release.SyncError, "Too many workflow"):
                release.workflows_ready(self.api, HEAD)
        self.assertEqual(self.api.merges, [])

    def test_workflow_rerun_queued_during_final_check_blocks_merge(self):
        def change(path):
            if "/actions/runs?" in path and self.api.workflow_reads == 1:
                self.api.workflows[0].update(
                    run_attempt=2, status="queued", conclusion=None
                )

        self.api.hook = change
        self.assertEqual(self.run_release()["result"], "noop")
        self.assertEqual(self.api.merges, [])

    def test_stale_release_branch_is_not_merged(self):
        self.api.comparison.update(status="diverged", behind_by=1)
        self.assertEqual(self.run_release()["result"], "noop")
        self.assertEqual(self.api.merges, [])

    def test_waiting_can_observe_checks_finish_without_reusing_stale_results(self):
        self.api.checks[0].update(status="in_progress", conclusion=None)
        elapsed = [0]

        def sleep(seconds):
            elapsed[0] += seconds
            self.api.checks[0].update(status="completed", conclusion="success")

        result = self.run_release(
            wait=30, interval=10, clock=lambda: elapsed[0], sleep=sleep
        )
        self.assertEqual(result["result"], "merged")
        self.assertEqual(elapsed[0], 10)

    def test_wait_timeout_is_bounded_and_does_not_merge(self):
        self.api.checks[0].update(status="queued", conclusion=None)
        elapsed, sleeps = [0], []

        def sleep(seconds):
            elapsed[0] += seconds
            sleeps.append(seconds)

        result = self.run_release(
            wait=12, interval=10, clock=lambda: elapsed[0], sleep=sleep
        )
        self.assertEqual(result["result"], "noop")
        self.assertEqual(sleeps, [10, 2])
        self.assertEqual(self.api.merges, [])

    def test_content_api_symlink_and_invalid_encoding_are_rejected(self):
        for blob in (
            {"type": "symlink", "encoding": "base64", "content": ""},
            {"type": "file", "encoding": "base64", "content": "invalid!"},
        ):
            with (
                self.subTest(blob=blob),
                patch.object(self.api, "request", return_value=blob),
            ):
                with self.assertRaises(release.SyncError):
                    release.read_file(self.api, "pyproject.toml", HEAD)

    def test_head_change_while_waiting_is_a_noop(self):
        self.api.checks[0].update(status="in_progress", conclusion=None)
        elapsed = [0]

        def sleep(seconds):
            elapsed[0] += seconds
            self.api.pr["head"]["sha"] = OTHER

        self.assertEqual(
            self.run_release(wait=30, clock=lambda: elapsed[0], sleep=sleep)["result"],
            "noop",
        )
        self.assertEqual(self.api.merges, [])

    def test_new_failure_during_final_check_blocks_merge(self):
        def change(path):
            if "/check-runs?" in path and self.api.check_reads == 1:
                self.api.checks[0]["conclusion"] = "failure"

        self.api.hook = change
        self.assertEqual(self.run_release()["result"], "noop")
        self.assertEqual(self.api.merges, [])

    def test_master_change_after_checks_blocks_merge(self):
        def change(path):
            if path.endswith("/git/ref/heads/master") and self.api.check_reads == 2:
                self.api.master = OTHER

        self.api.hook = change
        self.assertEqual(self.run_release()["result"], "noop")
        self.assertEqual(self.api.merges, [])

    def test_refused_merge_is_not_reported_as_success(self):
        self.api.merge_response = {"merged": False}
        with self.assertRaisesRegex(release.SyncError, "did not accept"):
            self.run_release()

    def test_cli_requires_canonical_workflow_and_publishing_token(self):
        with (
            patch.dict(os.environ, {}, clear=True),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            self.assertEqual(release.main(["--pr", "166", "--wait", "0"]), 1)
        self.assertEqual(self.api.calls, [])

    def test_cli_emits_machine_readable_merge_outputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "output"
            environment = {
                "GITHUB_REPOSITORY": release.DOCS,
                "GITHUB_TOKEN": "fixture-token",
                "GITHUB_OUTPUT": str(output),
            }
            with (
                patch.dict(os.environ, environment, clear=True),
                patch.object(release, "GitHub", return_value=self.api),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(release.main(["--pr", "166", "--wait", "0"]), 0)
            self.assertIn("result=merged\n", output.read_text())
            self.assertIn(f"commit_sha={MERGED}\n", output.read_text())


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Promote reviewed development docs when that exact candidate reaches a release.

The read/check path is safe to run locally. Publication is a separate operation
for CI after building and auditing the proposed metadata. It changes only
``docs-versions.json`` and never configures a Git author or forces a branch ref.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BACKEND = "I-am-PUID-0/DUMB"
FRONTEND = "nicocapalbo/dmbdb"
DOCS = "I-am-PUID-0/DUMB_docs"
METADATA_PATH = "docs-versions.json"
SHA = re.compile(r"[0-9a-f]{40}\Z")
VERSION = re.compile(r"v?(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\Z")


class SyncError(RuntimeError):
    """A release needs human review or a publication precondition changed."""


class GitHub:
    def __init__(self, token: str | None = None):
        self.token = token

    def request(self, path: str, data: dict | None = None, method: str = "GET"):
        if not path.startswith("/repos/"):
            raise SyncError("Only repository API paths are supported.")
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
            "User-Agent": "DUMB-docs-release-sync",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        payload = None
        if data is not None:
            payload = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = Request(
            "https://api.github.com" + path,
            data=payload,
            headers=headers,
            method=method,
        )
        try:
            with urlopen(request, timeout=30) as response:
                return json.load(response)
        except HTTPError as error:
            # Never echo response bodies, headers, or credentials into CI logs.
            raise SyncError(
                f"GitHub API returned HTTP {error.code}; check repository access "
                "and retry. No release selection was inferred from this failure."
            ) from None
        except (URLError, TimeoutError, json.JSONDecodeError):
            raise SyncError(
                "GitHub API request failed; retry the release check."
            ) from None


def checked_sha(value, name: str) -> str:
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise SyncError(f"{name} must be a full immutable commit SHA.")
    return value


def stable_version(tag: str) -> str:
    match = VERSION.fullmatch(tag) if isinstance(tag, str) else None
    if not match:
        raise SyncError(
            "The latest release tag is not stable SemVer; review it manually."
        )
    return ".".join(match.groups())


def release_commit(api: GitHub, tag: str, repository: str = BACKEND) -> str:
    """Resolve an exact lightweight or annotated tag without trusting target URLs."""
    ref = api.request(f"/repos/{repository}/git/ref/tags/{quote(tag, safe='')}")
    if ref.get("ref") != f"refs/tags/{tag}":
        raise SyncError("The release tag reference did not match the requested tag.")
    target = ref.get("object", {})
    seen: set[str] = set()
    for _ in range(8):
        sha = checked_sha(target.get("sha"), "Release tag target")
        kind = target.get("type")
        if kind == "commit":
            return sha
        if kind != "tag" or sha in seen:
            raise SyncError("The release tag does not resolve to a unique commit.")
        seen.add(sha)
        target = api.request(f"/repos/{repository}/git/tags/{sha}").get("object", {})
    raise SyncError("The release tag has too many annotated-tag indirections.")


def select_release(
    metadata: dict, release: dict, source: str, docs_head: str, api: GitHub
) -> dict:
    """Return a metadata proposal only for an ancestor-verified reviewed candidate."""
    if release.get("draft") or release.get("prerelease"):
        raise SyncError(
            "The upstream latest release is not a published stable release."
        )
    version = stable_version(release.get("tag_name"))
    source = checked_sha(source, "Release source")
    docs_head = checked_sha(docs_head, "Documentation source")
    try:
        current = metadata["release"]
        development = metadata["dev"]
        current_version = stable_version(current["version"])
        development_version = stable_version(development["version"])
        current_source = checked_sha(current["source"], "Recorded release source")
        development_source = checked_sha(
            development["source"], "Reviewed development source"
        )
    except (KeyError, TypeError):
        raise SyncError(
            "Release metadata is incomplete; review docs-versions.json."
        ) from None
    if version == current_version:
        if source != current_source:
            raise SyncError(
                "The existing release tag moved; review its source before changing docs."
            )
        return copy.deepcopy(metadata)
    if tuple(map(int, version.split("."))) < tuple(
        map(int, current_version.split("."))
    ):
        raise SyncError(
            "The upstream latest release is older than the documented release; review manually."
        )
    if version != development_version:
        raise SyncError(
            f"DUMB {version} has no reviewed documentation candidate. Review its "
            "changes, update dev.version and dev.source in docs-versions.json, "
            "then rerun this workflow. The released docs have not been relabeled."
        )
    comparison = api.request(
        f"/repos/{BACKEND}/compare/{development_source}...{source}"
    )
    if comparison.get("status") not in {"ahead", "identical"}:
        raise SyncError(
            "The stable release does not contain the reviewed development source. "
            "Review the release ancestry and docs candidate before promotion."
        )
    frontend_metadata = {}
    reviewed_frontend = development.get("frontend_source")
    if reviewed_frontend is not None:
        reviewed_frontend = checked_sha(reviewed_frontend, "Reviewed frontend source")
        frontend_release = api.request(f"/repos/{FRONTEND}/releases/latest")
        if frontend_release.get("draft") or frontend_release.get("prerelease"):
            raise SyncError(
                "The latest dashboard release is not a published stable release."
            )
        frontend_tag = frontend_release.get("tag_name")
        frontend_version = stable_version(frontend_tag)
        frontend_source = release_commit(api, frontend_tag, repository=FRONTEND)
        frontend_comparison = api.request(
            f"/repos/{FRONTEND}/compare/{reviewed_frontend}...{frontend_source}"
        )
        if frontend_comparison.get("status") not in {"ahead", "identical"}:
            raise SyncError(
                "The latest stable dashboard release does not contain the reviewed "
                "frontend source. Publish the compatible dmbdb release first, or "
                "review the docs candidate and image pairing before promotion."
            )
        frontend_metadata = {
            "frontend_version": frontend_version,
            "frontend_source": frontend_source,
        }
    proposed = copy.deepcopy(metadata)
    proposed["release"].update(frontend_metadata)
    proposed["release"].update(
        version=version,
        source=source,
        docs_ref=docs_head,
        include_development=True,
    )
    return proposed


def proposal(metadata: dict, docs_head: str, api: GitHub) -> dict:
    latest = api.request(f"/repos/{BACKEND}/releases/latest")
    tag = latest.get("tag_name")
    stable_version(tag)
    source = release_commit(api, tag)
    return select_release(metadata, latest, source, docs_head, api)


def assert_publisher(api: GitHub) -> None:
    """Verify the configured actor satisfies the repository's admin bypass policy.

    This is a read-only capability check. It intentionally runs for no-op
    publication checks too, so normal deployments exercise the configured token
    without waiting for the next backend release to require a metadata commit.
    """
    repository = api.request(f"/repos/{DOCS}")
    permissions = repository.get("permissions")
    if not isinstance(permissions, dict) or permissions.get("admin") is not True:
        raise SyncError(
            "The configured publishing token does not have repository admin "
            "authority required by the docs branch policy. Configure the "
            "existing release automation credential; no branch write was attempted."
        )


def assert_current(api: GitHub, expected_head: str) -> None:
    expected_head = checked_sha(expected_head, "Validated documentation head")
    actual = (
        api.request(f"/repos/{DOCS}/git/ref/heads/master").get("object", {}).get("sha")
    )
    if actual != expected_head:
        raise SyncError(
            "The docs branch changed during validation. Rerun the workflow against "
            "the current master; this older artifact must not be deployed."
        )


def publish(api: GitHub, expected_head: str, metadata: dict) -> str:
    """Publish exactly one metadata path with a non-forced fast-forward update."""
    assert_current(api, expected_head)
    parent = api.request(f"/repos/{DOCS}/git/commits/{expected_head}")
    base_tree = checked_sha(
        parent.get("tree", {}).get("sha"), "Validated documentation tree"
    )
    content = json.dumps(metadata, indent=2) + "\n"
    tree = api.request(
        f"/repos/{DOCS}/git/trees",
        {
            "base_tree": base_tree,
            "tree": [
                {
                    "path": METADATA_PATH,
                    "mode": "100644",
                    "type": "blob",
                    "content": content,
                }
            ],
        },
        "POST",
    )
    tree_sha = checked_sha(tree.get("sha"), "Promotion tree")
    # Omitted author/committer are populated by GitHub's authenticated actor.
    # This does not alter the operator's configured Git identity.
    commit = api.request(
        f"/repos/{DOCS}/git/commits",
        {
            "message": f"docs: promote verified DUMB {metadata['release']['version']} release guide",
            "tree": tree_sha,
            "parents": [expected_head],
        },
        "POST",
    )
    commit_sha = checked_sha(commit.get("sha"), "Promotion commit")
    # A concurrent master commit diverges from this sole-parent commit, so
    # force:false rejects it atomically rather than overwriting or merging it.
    api.request(
        f"/repos/{DOCS}/git/refs/heads/master",
        {"sha": commit_sha, "force": False},
        "PATCH",
    )
    return commit_sha


def write_outputs(values: dict[str, str]) -> None:
    destination = os.environ.get("GITHUB_OUTPUT")
    if destination:
        with open(destination, "a", encoding="utf-8") as handle:
            for key, value in values.items():
                handle.write(f"{key}={value}\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--write",
        action="store_true",
        help="Write a proposed local metadata update before building",
    )
    group.add_argument(
        "--publish",
        action="store_true",
        help="Publish metadata supplied in DOCS_PROMOTION_METADATA after validation",
    )
    group.add_argument(
        "--assert-current",
        action="store_true",
        help="Refuse deployment if master has advanced",
    )
    parser.add_argument(
        "--expected-head",
        help="Validated source head, required for publication/deployment",
    )
    args = parser.parse_args(argv)
    if (args.publish or args.assert_current) and not args.expected_head:
        parser.error("--expected-head is required for publication or deployment checks")
    api = GitHub(os.environ.get("GITHUB_TOKEN"))
    try:
        head = (
            args.expected_head
            or subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip()
        )
        head = checked_sha(head, "Documentation head")
        if args.assert_current:
            assert_current(api, head)
            print("Validated documentation head is still current.")
            return 0
        if args.publish:
            if os.environ.get("GITHUB_REPOSITORY") != DOCS or not api.token:
                raise SyncError(
                    "Publication requires the canonical docs workflow and its configured publishing token."
                )
            assert_publisher(api)
            raw = subprocess.check_output(
                ["git", "show", f"{head}:{METADATA_PATH}"], cwd=ROOT, text=True
            )
            original = json.loads(raw)
            validated = json.loads(os.environ.get("DOCS_PROMOTION_METADATA", "null"))
            expected = proposal(original, head, api)
            if validated != expected:
                raise SyncError(
                    "Validated metadata differs from the current verified proposal; rerun the build."
                )
            commit = head if expected == original else publish(api, head, validated)
            assert_current(api, commit)
            write_outputs({"commit_sha": commit})
            print(
                "Release metadata is current and the validated head is ready for deployment."
            )
            return 0
        path = ROOT / METADATA_PATH
        current = json.loads(path.read_text(encoding="utf-8"))
        proposed = proposal(current, head, api)
        changed = proposed != current
        if args.write and changed:
            path.write_text(json.dumps(proposed, indent=2) + "\n", encoding="utf-8")
        write_outputs(
            {
                "changed": str(changed).lower(),
                "metadata": json.dumps(proposed, separators=(",", ":")),
            }
        )
        print(
            "A verified release promotion is ready for build validation."
            if changed
            else "Release documentation is already current."
        )
        return 0
    except (
        SyncError,
        json.JSONDecodeError,
        OSError,
        subprocess.CalledProcessError,
    ) as error:
        # subprocess commands contain only public repository paths and SHAs.
        print(f"Release sync stopped: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

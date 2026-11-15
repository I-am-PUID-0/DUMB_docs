#!/usr/bin/env python3
"""Verify the canonical published docs release before building or publishing.

The release tag identifies the documentation source; ``master`` may already
contain later, unreleased work. Run again with the selected tag and commit
immediately before publishing Pages or its mirror. This module performs only
GitHub reads and never changes a Git ref or creates a release.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from html.parser import HTMLParser
from pathlib import Path

if __package__:
    from .sync_release import (
        DOCS,
        GitHub,
        SyncError,
        checked_sha,
        release_commit,
        stable_version,
        write_outputs,
    )
else:
    from sync_release import (
        DOCS,
        GitHub,
        SyncError,
        checked_sha,
        release_commit,
        stable_version,
        write_outputs,
    )


def docs_version(tag: str) -> str:
    """Docs release-please tags use the package's unprefixed stable SemVer."""
    version = stable_version(tag)
    if tag != version:
        raise SyncError("Documentation release tags must be unprefixed stable SemVer.")
    return version


def resolve_latest(
    api: GitHub,
    requested_tag: str | None = None,
    expected_head: str | None = None,
) -> dict[str, str]:
    """Select the latest stable docs release and verify its immutable source.

    Passing both returned ``tag`` and ``commit_sha`` back into this function
    revalidates a prepared artifact. A new latest release, moved tag or release
    outside master ancestry refuses publication rather than replacing the source.
    """
    if requested_tag is not None:
        docs_version(requested_tag)
    if expected_head is not None:
        expected_head = checked_sha(
            expected_head, "Expected documentation release head"
        )

    release = api.request(f"/repos/{DOCS}/releases/latest")
    if not isinstance(release, dict):
        raise SyncError("The latest documentation release response is invalid.")
    if release.get("draft") or release.get("prerelease"):
        raise SyncError("The latest documentation release is not published and stable.")
    tag = release.get("tag_name")
    version = docs_version(tag)
    if requested_tag is not None and requested_tag != tag:
        raise SyncError(
            "The requested documentation tag is not the latest published stable "
            "release. Rerun preparation; an older release must not be deployed."
        )
    release_url = f"https://github.com/{DOCS}/releases/tag/{tag}"
    if release.get("html_url") != release_url:
        raise SyncError(
            "The documentation release URL is not the canonical repository release."
        )

    source = release_commit(api, tag, repository=DOCS)
    if expected_head is not None and source != expected_head:
        raise SyncError(
            "The documentation release tag moved from the validated commit. "
            "Rerun preparation before publishing."
        )
    comparison = api.request(f"/repos/{DOCS}/compare/{source}...master")
    if not isinstance(comparison, dict) or comparison.get("status") not in {
        "ahead",
        "identical",
    }:
        raise SyncError(
            "The published documentation release is not contained in master "
            "ancestry. Review the release source before publishing."
        )
    return {
        "tag": tag,
        "commit_sha": source,
        "version": version,
        "release_url": release_url,
    }


class _ArtifactPage(HTMLParser):
    """Read release metadata and the visible build footer without dependencies."""

    def __init__(self):
        super().__init__()
        self.meta: dict[str, list[str | None]] = {}
        self.footer_kinds: list[str | None] = []
        self.footer_links: list[str | None] = []
        self.footer_text: list[str] = []
        self._footer_depth = 0

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "meta" and values.get("name"):
            self.meta.setdefault(values["name"], []).append(values.get("content"))
        if tag == "div":
            if "docs-build-identity" in values.get("class", "").split():
                self.footer_kinds.append(values.get("data-docs-build-kind"))
                self._footer_depth += 1
            elif self._footer_depth:
                self._footer_depth += 1
        if self._footer_depth and tag == "a":
            self.footer_links.append(values.get("href"))

    def handle_endtag(self, tag):
        if tag == "div" and self._footer_depth:
            self._footer_depth -= 1

    def handle_data(self, data):
        if self._footer_depth:
            self.footer_text.append(data)


def verify_artifact(path: Path | str, identity: dict[str, str]) -> None:
    """Refuse preview or mismatched artifacts in either documentation channel."""
    root = Path(path)
    tag = identity["tag"]
    version = docs_version(tag)
    commit = checked_sha(identity["commit_sha"], "Artifact documentation source")
    release_url = f"https://github.com/{DOCS}/releases/tag/{tag}"
    source_url = f"https://github.com/{DOCS}/commit/{commit}"
    if identity.get("version") != version or identity.get("release_url") != release_url:
        raise SyncError("The expected artifact release identity is inconsistent.")
    expected = {
        "version": version,
        "kind": "release",
        "commit": commit,
        "tag": tag,
        "release_url": release_url,
        "source_url": source_url,
        "dirty": False,
    }
    first_documentation = None
    for channel, directory in (("release", root), ("dev", root / "dev")):
        try:
            manifest = json.loads(
                (directory / "channel.json").read_text(encoding="utf-8")
            )
        except (OSError, ValueError) as error:
            raise SyncError(
                f"Cannot read the {channel} artifact channel identity."
            ) from error
        if not isinstance(manifest, dict) or manifest.get("channel") != channel:
            raise SyncError(
                f"The {channel} artifact channel does not match its location."
            )
        documentation = manifest.get("documentation")
        if (
            not isinstance(documentation, dict)
            or any(documentation.get(key) != value for key, value in expected.items())
            or documentation.get("dirty") is not False
        ):
            raise SyncError(
                f"The {channel} artifact is not the validated clean documentation release."
            )
        if first_documentation is not None and documentation != first_documentation:
            raise SyncError("The artifact channels disagree on documentation identity.")
        first_documentation = documentation

        try:
            html = (directory / "index.html").read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise SyncError(f"Cannot read the {channel} artifact homepage.") from error
        page = _ArtifactPage()
        page.feed(html)
        expected_meta = {
            "dumb-docs-package-version": version,
            "dumb-docs-build-kind": "release",
            "dumb-docs-build-commit": commit,
            "dumb-docs-release-tag": tag,
        }
        if any(page.meta.get(key) != [value] for key, value in expected_meta.items()):
            raise SyncError(
                f"The {channel} artifact HTML metadata does not match its release."
            )
        footer = " ".join(" ".join(page.footer_text).split())
        if (
            page.footer_kinds != ["release"]
            or f"Documentation release {version}" not in footer
            or release_url not in page.footer_links
            or source_url not in page.footer_links
            or "Local changes" in footer
        ):
            raise SyncError(
                f"The {channel} artifact footer does not match its release."
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tag", help="Require this tag to remain the latest stable docs release"
    )
    parser.add_argument(
        "--expected-head",
        help="Require the release tag to resolve to this full commit SHA",
    )
    parser.add_argument(
        "--output", type=Path, help="Write the verified release identity as JSON"
    )
    parser.add_argument(
        "--artifact",
        type=Path,
        help="Verify both channels and homepage identities in this built artifact",
    )
    args = parser.parse_args(argv)
    try:
        identity = resolve_latest(
            GitHub(os.environ.get("GITHUB_TOKEN")), args.tag, args.expected_head
        )
        if args.artifact is not None:
            verify_artifact(args.artifact, identity)
        if args.output is not None:
            args.output.write_text(
                json.dumps(identity, indent=2) + "\n", encoding="utf-8"
            )
        write_outputs(identity)
        print(
            f"Verified published documentation {identity['tag']} "
            f"at {identity['commit_sha']}."
        )
        return 0
    except (SyncError, OSError) as error:
        print(f"Documentation release check stopped: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

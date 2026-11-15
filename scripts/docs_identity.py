"""Identify a documentation artifact without confusing it with a DUMB version."""

from __future__ import annotations

import json
import re
import subprocess
import tomllib
from pathlib import Path

REPOSITORY = "https://github.com/I-am-PUID-0/DUMB_docs"
STABLE_VERSION = re.compile(
    r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\Z"
)
COMMIT = re.compile(r"[0-9a-f]{40}\Z")


class IdentityError(ValueError):
    """The requested artifact identity cannot be established from its source."""


def _git(root: Path, *arguments: str) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=root, text=True, stderr=subprocess.DEVNULL
    ).strip()


def documentation_identity(root: Path, release_tag: str | None = None) -> dict:
    """Return shared build provenance; release claims require explicit validation.

    The caller verifies GitHub publication before passing ``release_tag``. This
    local check deliberately performs no network requests. Ignored build output
    and installed dependencies do not make a checkout dirty; tracked changes and
    untracked source files do.
    """
    try:
        version = tomllib.loads((root / "pyproject.toml").read_text())["project"][
            "version"
        ]
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise IdentityError("Cannot read the documentation package version") from error
    if not isinstance(version, str) or not version.strip():
        raise IdentityError("The documentation package version must be a string")

    commit = None
    dirty = None
    try:
        if Path(_git(root, "rev-parse", "--show-toplevel")).resolve() != root.resolve():
            raise OSError("The source directory is not this Git checkout's root")
        head = _git(root, "rev-parse", "--verify", "HEAD^{commit}")
        if COMMIT.fullmatch(head):
            commit = head
        dirty = bool(_git(root, "status", "--porcelain=v1", "--untracked-files=normal"))
    except (OSError, subprocess.SubprocessError):
        # Source exports and local previews need no invented commit or clean state.
        pass

    identity = {
        "version": version,
        "kind": "preview",
        "commit": commit,
        "tag": None,
        "release_url": None,
        "source_url": f"{REPOSITORY}/commit/{commit}" if commit else None,
        "dirty": dirty,
    }
    if release_tag is None:
        return identity

    if not STABLE_VERSION.fullmatch(release_tag):
        raise IdentityError("The docs release tag must be plain stable SemVer (X.Y.Z)")
    try:
        manifest_version = json.loads(
            (root / ".github/.release-please-manifest.json").read_text()
        )["."]
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise IdentityError("Cannot read the documentation release manifest") from error
    if release_tag != version or release_tag != manifest_version:
        raise IdentityError(
            "The docs release tag, package version, and release manifest must match"
        )
    if commit is None or dirty is None:
        raise IdentityError("A docs release requires verified Git source and status")
    if dirty:
        raise IdentityError("A docs release requires a clean source checkout")
    try:
        tagged_commit = _git(
            root, "rev-parse", "--verify", f"refs/tags/{release_tag}^{{commit}}"
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise IdentityError("The exact docs release tag is unavailable") from error
    if not COMMIT.fullmatch(tagged_commit) or tagged_commit != commit:
        raise IdentityError("The docs release tag must identify the exact source HEAD")
    identity.update(
        kind="release",
        tag=release_tag,
        release_url=f"{REPOSITORY}/releases/tag/{release_tag}",
    )
    return identity


def agent_identity(identity: dict) -> str:
    """Describe the same provenance in plain-text agent exports."""
    state = "release" if identity["kind"] == "release" else "preview (unreleased)"
    text = f"Documentation artifact: {state} {identity['version']}."
    if identity["commit"]:
        text += f" Source commit: {identity['commit']}."
    if identity["dirty"]:
        text += " Includes local changes."
    if identity["release_url"]:
        text += f" Release notes: {identity['release_url']}."
    return text + "\n\n"

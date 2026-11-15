#!/usr/bin/env python3
"""Merge only a generated, current and independently validated docs release PR."""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import os
import re
import sys
import time
import tomllib
from urllib.parse import quote

if __package__:
    from .sync_release import (
        DOCS,
        GitHub,
        SyncError,
        assert_publisher,
        checked_sha,
        write_outputs,
    )
else:
    from sync_release import (
        DOCS,
        GitHub,
        SyncError,
        assert_publisher,
        checked_sha,
        write_outputs,
    )

BRANCH = "release-please--branches--master"
AUTHOR = "I-am-PUID-0"
SEMVER = r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
TITLE = re.compile(rf"chore\(master\): release ({SEMVER})\Z")
FILES = {".github/.release-please-manifest.json", "CHANGELOG.md", "pyproject.toml"}
CHECKS = {
    ("Validate release and development docs", "github-actions"),
    ("Analyze (python)", "github-actions"),
    ("Analyze (actions)", "github-actions"),
    ("CodeQL", "github-advanced-security"),
}
WORKFLOWS = {
    (".github/workflows/deploy.yml", "pull_request"),
    ("dynamic/github-code-scanning/codeql", "dynamic"),
}
BODY_START = ":robot: I have created a release *beep* *boop*\n---"
BODY_END = (
    "This PR was generated with [Release Please]"
    "(https://github.com/googleapis/release-please). See [documentation]"
    "(https://github.com/googleapis/release-please#release-please)."
)


def release_pr(api: GitHub, number: int) -> dict:
    pr = api.request(f"/repos/{DOCS}/pulls/{number}")
    if not isinstance(pr, dict) or pr.get("number") != number:
        raise SyncError("The pull request response does not match the requested PR.")
    if pr.get("state") != "open" or pr.get("merged"):
        return {}
    title = TITLE.fullmatch(pr.get("title") or "")
    body = pr.get("body") or ""
    labels = {label.get("name") for label in pr.get("labels", [])}
    if (
        pr.get("draft") is not False
        or pr.get("user", {}).get("login") != AUTHOR
        or pr.get("head", {}).get("ref") != BRANCH
        or pr.get("head", {}).get("repo", {}).get("full_name") != DOCS
        or pr.get("base", {}).get("ref") != "master"
        or pr.get("base", {}).get("repo", {}).get("full_name") != DOCS
        or "autorelease: pending" not in labels
        or not title
        or not body.startswith(BODY_START)
        or not body.rstrip().endswith(BODY_END)
        or not re.match(rf"\s*## \[{re.escape(title[1])}\]\(", body[len(BODY_START) :])
    ):
        raise SyncError("The PR is not the expected managed docs release candidate.")
    return {
        "head": checked_sha(pr["head"].get("sha"), "Release PR head"),
        "base": checked_sha(pr["base"].get("sha"), "Release PR base"),
        "version": title[1],
        "body": body,
    }


def master_head(api: GitHub) -> str:
    ref = api.request(f"/repos/{DOCS}/git/ref/heads/master")
    return checked_sha(ref.get("object", {}).get("sha"), "Current master head")


def read_file(api: GitHub, path: str, ref: str) -> str:
    blob = api.request(f"/repos/{DOCS}/contents/{quote(path)}?ref={ref}")
    if blob.get("type") != "file" or blob.get("encoding") != "base64":
        raise SyncError("Release metadata must be ordinary base64-encoded files.")
    try:
        content = "".join(blob["content"].split())
        return base64.b64decode(content, validate=True).decode("utf-8")
    except (KeyError, AttributeError, binascii.Error, UnicodeDecodeError):
        raise SyncError("Release metadata content could not be decoded.") from None


def validate_changes(api: GitHub, number: int, candidate: dict) -> None:
    files = api.request(f"/repos/{DOCS}/pulls/{number}/files?per_page=100")
    if (
        not isinstance(files, list)
        or len(files) != len(FILES)
        or {entry.get("filename") for entry in files} != FILES
        or any(
            entry.get("status") != "modified" or "previous_filename" in entry
            for entry in files
        )
    ):
        raise SyncError("The release PR must modify only the three generated files.")
    before = {path: read_file(api, path, candidate["base"]) for path in sorted(FILES)}
    after = {path: read_file(api, path, candidate["head"]) for path in sorted(FILES)}
    try:
        old_manifest = json.loads(before[".github/.release-please-manifest.json"])
        new_manifest = json.loads(after[".github/.release-please-manifest.json"])
        old = old_manifest["."]
        new = new_manifest["."]
        if (
            set(old_manifest) != {"."}
            or set(new_manifest) != {"."}
            or not isinstance(old, str)
            or not re.fullmatch(SEMVER, old)
            or new != candidate["version"]
            or tuple(map(int, new.split("."))) <= tuple(map(int, old.split(".")))
        ):
            raise ValueError
        for content, version in ((before, old), (after, new)):
            if (
                tomllib.loads(content["pyproject.toml"])["project"]["version"]
                != version
            ):
                raise ValueError
    except (KeyError, TypeError, ValueError, tomllib.TOMLDecodeError):
        raise SyncError(
            "The release must consistently advance only the root package version."
        ) from None
    version_line = re.compile(
        r"(?m)^(version[ \t]*=[ \t]*)([\"'])" + re.escape(old) + r"(\2[^\r\n]*)$"
    )
    expected, count = version_line.subn(
        lambda match: match[1] + match[2] + new + match[3], before["pyproject.toml"]
    )
    if count != 1 or expected != after["pyproject.toml"]:
        raise SyncError("The pyproject change must contain only its version-line bump.")
    previous = re.search(r"(?m)^## ", before["CHANGELOG.md"])
    if (
        not previous
        or before["CHANGELOG.md"][: previous.start()].strip() != "# Changelog"
    ):
        raise SyncError("The existing changelog layout needs manual release review.")
    history = before["CHANGELOG.md"][previous.start() :]
    changelog = after["CHANGELOG.md"]
    if not changelog.startswith("# Changelog\n") or not changelog.endswith(history):
        raise SyncError("The release changelog must preserve its existing history.")
    addition = changelog[len("# Changelog\n") : -len(history)].strip()
    heading = re.compile(
        rf"## \[{re.escape(new)}\]\(https://github\.com/{re.escape(DOCS)}/compare/"
        rf"{re.escape(old)}\.\.\.{re.escape(new)}\) \(\d{{4}}-\d{{2}}-\d{{2}}\)\n"
    )
    if (
        not heading.match(addition + "\n")
        or not heading.match(candidate["body"][len(BODY_START) :].lstrip())
        or len(re.findall(r"(?m)^## ", addition)) != 1
    ):
        raise SyncError("The changelog must prepend exactly the new release section.")


def workflows_ready(api: GitHub, head: str) -> bool:
    """A queued rerun blocks release before it creates replacement job checks."""
    latest: dict[tuple[str, str], dict] = {}
    for page in range(1, 11):
        response = api.request(
            f"/repos/{DOCS}/actions/runs?head_sha={head}&per_page=100&page={page}"
        )
        runs = response.get("workflow_runs")
        if not isinstance(runs, list) or not isinstance(
            response.get("total_count"), int
        ):
            raise SyncError("The current-head workflow results are incomplete.")
        for run in runs:
            key = (run.get("path"), run.get("event"))
            if key not in WORKFLOWS:
                continue
            if (
                run.get("head_sha") != head
                or not isinstance(run.get("id"), int)
                or not isinstance(run.get("run_attempt"), int)
                or run["run_attempt"] < 1
            ):
                raise SyncError(
                    "A required workflow result does not belong to this PR head."
                )
            rank = (run["id"], run["run_attempt"])
            if key not in latest or rank > (
                latest[key]["id"],
                latest[key]["run_attempt"],
            ):
                latest[key] = run
        if page * 100 >= response["total_count"]:
            break
    else:
        raise SyncError(
            "Too many workflow results to verify this release automatically."
        )
    return all(
        key in latest
        and latest[key].get("status") == "completed"
        and latest[key].get("conclusion") == "success"
        for key in WORKFLOWS
    )


def checks_ready(api: GitHub, head: str) -> bool:
    latest: dict[tuple[str, str], dict] = {}
    for page in range(1, 11):
        response = api.request(
            f"/repos/{DOCS}/commits/{head}/check-runs?filter=all&per_page=100&page={page}"
        )
        runs = response.get("check_runs")
        if not isinstance(runs, list) or not isinstance(
            response.get("total_count"), int
        ):
            raise SyncError("The current-head check results are incomplete.")
        for run in runs:
            key = (run.get("name"), run.get("app", {}).get("slug"))
            if key not in CHECKS:
                continue
            if run.get("head_sha") != head or not isinstance(run.get("id"), int):
                raise SyncError(
                    "A required check result does not belong to this PR head."
                )
            if key not in latest or run["id"] > latest[key]["id"]:
                latest[key] = run
        if page * 100 >= response["total_count"]:
            break
    else:
        raise SyncError("Too many check results to verify this release automatically.")
    return all(
        key in latest
        and latest[key].get("status") == "completed"
        and latest[key].get("conclusion") == "success"
        for key in CHECKS
    ) and workflows_ready(api, head)


def automate(
    api: GitHub,
    number: int,
    wait: float = 600,
    interval: float = 10,
    *,
    clock=time.monotonic,
    sleep=time.sleep,
) -> dict[str, str]:
    assert_publisher(api)
    candidate = release_pr(api, number)

    def noop(reason):
        return {"result": "noop", "pull_request": str(number), "reason": reason}

    if not candidate:
        return noop("The release PR is already closed.")
    if master_head(api) != candidate["base"]:
        return noop("The release PR needs regeneration against current master.")
    comparison = api.request(
        f"/repos/{DOCS}/compare/{candidate['base']}...{candidate['head']}"
    )
    if (
        comparison.get("status") != "ahead"
        or comparison.get("behind_by") != 0
        or comparison.get("base_commit", {}).get("sha") != candidate["base"]
        or comparison.get("merge_base_commit", {}).get("sha") != candidate["base"]
    ):
        return noop("The release branch does not contain current master.")
    validate_changes(api, number, candidate)
    deadline = clock() + wait
    while True:
        if (
            release_pr(api, number) != candidate
            or master_head(api) != candidate["base"]
        ):
            return noop("The release PR or master changed during validation.")
        if checks_ready(api, candidate["head"]):
            break
        remaining = deadline - clock()
        if remaining <= 0:
            return noop(
                "The current-head release checks and workflows have not all passed."
            )
        print("Waiting for current-head release checks and workflows.", flush=True)
        sleep(min(interval, remaining))
    # Re-read identities and checks before merging. REST atomically pins only
    # the PR head; the final master read is not an atomic base lease.
    if release_pr(api, number) != candidate or master_head(api) != candidate["base"]:
        return noop("The release PR or master changed before merge.")
    if not checks_ready(api, candidate["head"]):
        return noop("A current-head release check or workflow changed before merge.")
    if master_head(api) != candidate["base"]:
        return noop("Master advanced before merge.")
    merged = api.request(
        f"/repos/{DOCS}/pulls/{number}/merge",
        {"sha": candidate["head"], "merge_method": "squash"},
        "PUT",
    )
    if merged.get("merged") is not True:
        raise SyncError("GitHub did not accept the exact-head release merge.")
    return {
        "result": "merged",
        "pull_request": str(number),
        "commit_sha": checked_sha(merged.get("sha"), "Merged release commit"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pr", required=True, type=int, help="Generated release PR number"
    )
    parser.add_argument(
        "--wait", default=600, type=float, help="Check wait limit in seconds"
    )
    parser.add_argument(
        "--interval", default=10, type=float, help="Polling interval in seconds"
    )
    args = parser.parse_args(argv)
    if args.pr <= 0 or not 0 <= args.wait <= 1800 or not 1 <= args.interval <= 60:
        parser.error("Use a positive PR number, wait 0–1800 and interval 1–60 seconds.")
    try:
        token = os.environ.get("GITHUB_TOKEN")
        if os.environ.get("GITHUB_REPOSITORY") != DOCS or not token:
            raise SyncError(
                "Release merging requires the canonical docs workflow and publishing token."
            )
        result = automate(GitHub(token), args.pr, args.wait, args.interval)
        write_outputs(result)
        print(f"Docs release: {result['result']}. {result.get('reason', '')}".rstrip())
        return 0
    except (SyncError, OSError) as error:
        print(f"Docs release stopped: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Announce an explicitly requested, deployed docs release at most once.

The publication workflow serializes this operation. A durable pending receipt is
written before sending; uncertain delivery requires inspection, never a retry.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

if __package__:
    from .published_docs_release import docs_version, resolve_latest
    from .sync_release import DOCS, GitHub, SyncError, checked_sha
else:
    from published_docs_release import docs_version, resolve_latest
    from sync_release import DOCS, GitHub, SyncError, checked_sha

RECEIPT = "DOCS_DISCORD_ANNOUNCEMENT"
VARIABLES = f"/repos/{DOCS}/actions/variables"
RECEIPT_PATH = f"{VARIABLES}/{RECEIPT}"
SITE = "https://dumbarr.com/"


def webhook_url(value: str) -> str:
    """Accept only Discord webhook execution URLs and request confirmation."""
    try:
        parsed = urlsplit(value)
        valid = (
            parsed.scheme == "https"
            and parsed.hostname == "discord.com"
            and parsed.port in (None, 443)
            and parsed.username is None
            and parsed.password is None
            and not parsed.fragment
            and re.fullmatch(
                r"/api(?:/v10)?/webhooks/[0-9]+/[A-Za-z0-9._-]+", parsed.path
            )
        )
        if valid:
            query = [
                (k, v)
                for k, v in parse_qsl(parsed.query, keep_blank_values=True)
                if k != "wait"
            ]
            return urlunsplit(
                parsed._replace(query=urlencode(query + [("wait", "true")]))
            )
    except (ValueError, TypeError):
        pass
    raise SyncError("A valid HTTPS Discord webhook execution URL is required.")


def payload(identity: dict, body: str, mention: str) -> dict:
    role = re.fullmatch(r"<@&([0-9]+)>", mention)
    if not role:
        raise SyncError("The release mention must identify exactly one Discord role.")
    prefix = f"{mention} **DUMB documentation {identity['version']} is live**\n\n"
    suffix = f"\n\nRelease notes: {identity['release_url']}\nDocumentation: {SITE}"

    # Discord's character accounting must also fit astral Unicode characters.
    def units(value):
        return len(value.encode("utf-16-le")) // 2

    budget = 2000 - units(prefix + suffix)
    if budget < 1:
        raise SyncError("The release announcement identity is too long.")
    notes = body.strip()
    if units(notes) > budget:
        selected, used = [], 0
        for character in notes:
            cost = 2 if ord(character) > 0xFFFF else 1
            if used + cost > budget - 1:
                break
            selected.append(character)
            used += cost
        notes = "".join(selected) + "…"
    return {
        "content": prefix + notes + suffix,
        "flags": 4,
        "allowed_mentions": {"parse": [], "roles": [role[1]]},
    }


def write_receipt(api: GitHub, identity: dict, state: str, *, create=False) -> None:
    api.request(
        VARIABLES if create else RECEIPT_PATH,
        {
            "name": RECEIPT,
            "value": json.dumps({**identity, "state": state}, separators=(",", ":")),
        },
        "POST" if create else "PATCH",
    )


def claim(api: GitHub, identity: dict) -> bool:
    variable = api.request(RECEIPT_PATH, missing_ok=True)
    if variable is not None:
        try:
            if variable.get("name") != RECEIPT:
                raise ValueError
            previous = json.loads(variable["value"])
            if set(previous) != {"version", "commit", "release_id", "state"}:
                raise ValueError
            docs_version(previous["version"])
            checked_sha(previous["commit"], "Recorded announcement source")
            if type(previous["release_id"]) is not int or previous["release_id"] <= 0:
                raise ValueError
            if previous["state"] not in {"pending", "sent"}:
                raise ValueError
        except (KeyError, TypeError, ValueError, AttributeError):
            raise SyncError(
                "The announcement receipt needs manual inspection."
            ) from None
        if previous["state"] == "pending":
            raise SyncError(
                "An announcement is pending; inspect it before any further send."
            )
        if previous == {**identity, "state": "sent"}:
            return False
        if tuple(map(int, identity["version"].split("."))) <= tuple(
            map(int, previous["version"].split("."))
        ):
            raise SyncError(
                "The announcement would repeat, change or roll back a recorded version."
            )
    write_receipt(api, identity, "pending", create=variable is None)
    return True


def send_discord(url: str, message: dict) -> None:
    request = Request(
        url,
        data=json.dumps(message).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "DUMB-docs-release"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            if not 200 <= response.status < 300:
                raise ValueError
            result = json.load(response)
        if not isinstance(result, dict) or not re.fullmatch(
            r"[1-9][0-9]*", result.get("id") or ""
        ):
            raise ValueError
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, TypeError) as error:
        if isinstance(error, HTTPError):
            error.close()
        raise SyncError(
            "Discord delivery was not confirmed. The pending receipt is retained; inspect before retrying."
        ) from None


def announce(
    api: GitHub, tag: str, expected_head: str, webhook: str, mention: str
) -> str:
    url = webhook_url(webhook)
    identity = resolve_latest(api, tag, expected_head)
    release = api.request(f"/repos/{DOCS}/releases/tags/{quote(tag, safe='')}")
    if (
        not isinstance(release, dict)
        or release.get("tag_name") != tag
        or release.get("draft")
        or release.get("prerelease")
        or release.get("html_url") != identity["release_url"]
        or type(release.get("id")) is not int
        or release["id"] <= 0
        or (release.get("body") is not None and not isinstance(release["body"], str))
    ):
        raise SyncError("The canonical release announcement details are invalid.")
    message = payload(identity, release.get("body") or "", mention)
    receipt = {
        "version": identity["version"],
        "commit": identity["commit_sha"],
        "release_id": release["id"],
    }
    if not claim(api, receipt):
        return "already sent"
    send_discord(url, message)
    try:
        write_receipt(api, receipt, "sent")
    except SyncError:
        raise SyncError(
            "Delivery succeeded but receipt confirmation failed; inspect before any further send."
        ) from None
    return "sent"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--expected-head", required=True)
    args = parser.parse_args(argv)
    try:
        if (
            os.environ.get("GITHUB_REPOSITORY") != DOCS
            or os.environ.get("GITHUB_ACTIONS") != "true"
            or os.environ.get("DOCS_ANNOUNCE_RELEASE") != "true"
            or not os.environ.get("GITHUB_TOKEN")
            or not os.environ.get("DISCORD_WEBHOOK_URL")
            or not os.environ.get("DISCORD_RELEASE_MENTION")
        ):
            raise SyncError(
                "Announcement requires explicit canonical Actions authorization and configured secrets."
            )
        result = announce(
            GitHub(os.environ["GITHUB_TOKEN"]),
            args.tag,
            args.expected_head,
            os.environ["DISCORD_WEBHOOK_URL"],
            os.environ["DISCORD_RELEASE_MENTION"],
        )
        print(f"Documentation release announcement: {result}.")
        return 0
    except (SyncError, UnicodeError) as error:
        # Never print webhook URLs, returned message IDs, or remote response bodies.
        message = (
            str(error)
            if isinstance(error, SyncError)
            else "Announcement text is not valid Unicode."
        )
        print(f"Documentation announcement stopped: {message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

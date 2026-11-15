"""Announcement receipts prevent duplicate delivery, including uncertain results."""

from __future__ import annotations

import contextlib
import io
import json
import os
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit

from scripts import announce_docs_release as announce

TAG = "1.25.1"
SHA = "1" * 40
OLD = "2" * 40
ROLE = "<@&123>"
WEBHOOK = "https://discord.com/api/webhooks/456/test-token"
URL = f"https://github.com/{announce.DOCS}/releases/tag/{TAG}"
IDENTITY = {"version": TAG, "commit": SHA, "release_id": 101}
PUBLISHED = {"version": TAG, "commit_sha": SHA, "release_url": URL, "tag": TAG}


class FakeGitHub:
    def __init__(self, receipt=None):
        self.variable = None
        if receipt is not None:
            self.variable = {"name": announce.RECEIPT, "value": json.dumps(receipt)}
        self.calls = []
        self.fail_claim = False
        self.fail_sent = False
        self.release = {
            "id": 101,
            "tag_name": TAG,
            "html_url": URL,
            "draft": False,
            "prerelease": False,
            "body": "Clearer browser setup guides.",
        }

    def request(self, path, data=None, method="GET", *, missing_ok=False):
        self.calls.append((path, data, method, missing_ok))
        if path == f"/repos/{announce.DOCS}/releases/latest":
            return self.release
        if path == f"/repos/{announce.DOCS}/git/ref/tags/{TAG}":
            return {"ref": f"refs/tags/{TAG}", "object": {"type": "commit", "sha": SHA}}
        if path == f"/repos/{announce.DOCS}/compare/{SHA}...master":
            return {"status": "ahead"}
        if path == f"/repos/{announce.DOCS}/releases/tags/{TAG}":
            return self.release
        if path == announce.RECEIPT_PATH and method == "GET":
            if not missing_ok:
                raise AssertionError(
                    "Receipt read must explicitly allow only a missing variable"
                )
            return self.variable
        if path in {announce.VARIABLES, announce.RECEIPT_PATH} and method in {
            "POST",
            "PATCH",
        }:
            receipt = json.loads(data["value"])
            if receipt["state"] == "sent" and self.fail_sent:
                raise announce.SyncError("GitHub API returned HTTP 403")
            self.variable = dict(data)
            if receipt["state"] == "pending" and self.fail_claim:
                raise announce.SyncError("GitHub API request failed")
            return None
        raise AssertionError(f"Unexpected GitHub request: {method} {path}")

    def receipt(self):
        return json.loads(self.variable["value"])


class AnnouncementTests(unittest.TestCase):
    def invoke(self, api):
        return announce.announce(api, TAG, SHA, WEBHOOK, ROLE)

    def test_new_receipt_is_claimed_before_send_and_confirmed_without_discord_ids(self):
        api = FakeGitHub()

        def send(url, message):
            self.assertEqual(api.receipt(), {**IDENTITY, "state": "pending"})
            self.assertEqual(parse_qs(urlsplit(url).query)["wait"], ["true"])
            self.assertIn(TAG, message["content"])

        with patch.object(announce, "send_discord", side_effect=send) as sender:
            self.assertEqual(self.invoke(api), "sent")
        self.assertEqual(sender.call_count, 1)
        self.assertEqual(api.receipt(), {**IDENTITY, "state": "sent"})
        writes = [(path, method) for path, _, method, _ in api.calls if method != "GET"]
        self.assertEqual(
            writes, [(announce.VARIABLES, "POST"), (announce.RECEIPT_PATH, "PATCH")]
        )
        self.assertTrue(all("/actions/variables" in path for path, _ in writes))

    def test_exact_sent_release_is_a_read_only_noop(self):
        api = FakeGitHub({**IDENTITY, "state": "sent"})
        with patch.object(announce, "send_discord") as sender:
            self.assertEqual(self.invoke(api), "already sent")
        sender.assert_not_called()
        self.assertTrue(all(method == "GET" for _, _, method, _ in api.calls))

    def test_an_older_sent_receipt_can_be_replaced_by_a_newer_release(self):
        api = FakeGitHub(
            {"version": "1.25.0", "commit": OLD, "release_id": 100, "state": "sent"}
        )
        with patch.object(announce, "send_discord"):
            self.assertEqual(self.invoke(api), "sent")
        self.assertEqual(api.receipt(), {**IDENTITY, "state": "sent"})
        writes = [method for _, _, method, _ in api.calls if method != "GET"]
        self.assertEqual(writes, ["PATCH", "PATCH"])

    def test_any_pending_receipt_blocks_every_further_send(self):
        for version in ("1.25.0", TAG, "1.26.0"):
            with self.subTest(version=version):
                api = FakeGitHub({**IDENTITY, "version": version, "state": "pending"})
                with patch.object(announce, "send_discord") as sender:
                    with self.assertRaisesRegex(announce.SyncError, "pending"):
                        self.invoke(api)
                sender.assert_not_called()
                self.assertTrue(all(method == "GET" for _, _, method, _ in api.calls))

    def test_same_version_different_commit_or_release_id_and_rollback_are_rejected(
        self,
    ):
        for changes in ({"commit": OLD}, {"release_id": 102}, {"version": "1.26.0"}):
            with self.subTest(changes=changes):
                api = FakeGitHub({**IDENTITY, **changes, "state": "sent"})
                with patch.object(announce, "send_discord") as sender:
                    with self.assertRaisesRegex(announce.SyncError, "recorded version"):
                        self.invoke(api)
                sender.assert_not_called()

    def test_malformed_receipt_is_not_overwritten(self):
        for receipt in (
            {},
            {**IDENTITY, "state": "unknown"},
            {**IDENTITY, "state": "sent", "message_id": "999"},
        ):
            with self.subTest(receipt=receipt):
                api = FakeGitHub(receipt)
                with patch.object(announce, "send_discord") as sender:
                    with self.assertRaises(announce.SyncError):
                        self.invoke(api)
                sender.assert_not_called()
                self.assertEqual(api.receipt(), receipt)

    def test_claim_failure_never_sends_and_preserves_an_uncertain_pending_write(self):
        api = FakeGitHub()
        api.fail_claim = True
        with patch.object(announce, "send_discord") as sender:
            with self.assertRaises(announce.SyncError):
                self.invoke(api)
        sender.assert_not_called()
        self.assertEqual(api.receipt()["state"], "pending")

    def test_timeout_leaves_pending_and_a_second_invocation_cannot_retry(self):
        api = FakeGitHub()
        with patch.object(
            announce,
            "send_discord",
            side_effect=announce.SyncError("Unconfirmed delivery"),
        ) as sender:
            with self.assertRaises(announce.SyncError):
                self.invoke(api)
            with self.assertRaisesRegex(announce.SyncError, "pending"):
                self.invoke(api)
        self.assertEqual(sender.call_count, 1)
        self.assertEqual(api.receipt()["state"], "pending")

    def test_sent_receipt_failure_keeps_pending_instead_of_sending_again(self):
        api = FakeGitHub()
        api.fail_sent = True
        with patch.object(announce, "send_discord") as sender:
            with self.assertRaisesRegex(
                announce.SyncError, "receipt confirmation failed"
            ):
                self.invoke(api)
        self.assertEqual(sender.call_count, 1)
        self.assertEqual(api.receipt()["state"], "pending")

    def test_wrong_latest_tag_or_invalid_release_details_never_claim_or_send(self):
        for field, value in (
            ("tag_name", "1.25.2"),
            ("id", True),
            ("id", 0),
            ("body", ["notes"]),
            ("body", []),
            ("body", False),
            ("prerelease", True),
        ):
            with self.subTest(field=field):
                api = FakeGitHub()
                api.release[field] = value
                with patch.object(announce, "send_discord") as sender:
                    with self.assertRaises(announce.SyncError):
                        self.invoke(api)
                sender.assert_not_called()
                self.assertIsNone(api.variable)


class PayloadAndTransportTests(unittest.TestCase):
    def test_long_unicode_notes_keep_both_links_and_stay_within_utf16_budget(self):
        for body in ("x" * 5000, "🚀" * 5000, "x🚀" * 5000):
            with self.subTest(character=body[:1]):
                message = announce.payload(PUBLISHED, body, ROLE)
                self.assertLessEqual(
                    len(message["content"].encode("utf-16-le")) // 2, 2000
                )
                self.assertIn("…", message["content"])
                self.assertTrue(
                    message["content"].endswith(f"Documentation: {announce.SITE}")
                )
                self.assertIn(URL, message["content"])
                self.assertEqual(message["flags"], 4)

    def test_only_the_configured_role_is_mentionable(self):
        message = announce.payload(PUBLISHED, "@everyone @here <@789> <@&789>", ROLE)
        self.assertEqual(message["allowed_mentions"], {"parse": [], "roles": ["123"]})
        for role in ("@everyone", "<@123>", "<@&123> <@&456>", "", ROLE + "\n"):
            with self.subTest(role=role), self.assertRaises(announce.SyncError):
                announce.payload(PUBLISHED, "notes", role)

    def test_webhook_url_is_discord_only_and_forces_wait_without_losing_query(self):
        for path in (
            "/api/webhooks/456/test-token",
            "/api/v10/webhooks/456/test-token",
        ):
            result = announce.webhook_url(
                f"https://discord.com{path}?thread_id=789&wait=false&wait=0"
            )
            self.assertEqual(
                parse_qs(urlsplit(result).query),
                {"thread_id": ["789"], "wait": ["true"]},
            )
        for value in (
            "http://discord.com/api/webhooks/456/test-token",
            "https://discord.com.example.com/api/webhooks/456/test-token",
            "https://discordapp.com/api/webhooks/456/test-token",
            "https://user@discord.com/api/webhooks/456/test-token",
            "https://discord.com:8443/api/webhooks/456/test-token",
            WEBHOOK + "#fragment",
            "https://discord.com/api/webhooks/456/test-token/messages/999",
        ):
            with self.subTest(value=value), self.assertRaises(announce.SyncError):
                announce.webhook_url(value)

    def test_waiting_request_requires_a_returned_message_id(self):
        response = io.BytesIO(b'{"id":"999"}')
        response.status = 200
        with patch.object(announce, "urlopen", return_value=response) as opener:
            announce.send_discord(announce.webhook_url(WEBHOOK), {"content": "notes"})
        request = opener.call_args.args[0]
        self.assertEqual(request.method, "POST")
        self.assertEqual(parse_qs(urlsplit(request.full_url).query)["wait"], ["true"])
        self.assertEqual(json.loads(request.data), {"content": "notes"})
        self.assertEqual(opener.call_args.kwargs["timeout"], 30)

    def test_http_network_and_invalid_responses_are_sanitized_without_retry(self):
        private = "private-webhook-token-or-body"
        http = HTTPError(WEBHOOK, 429, private, {}, io.BytesIO(private.encode()))
        for failure in (http, URLError(private), TimeoutError(private)):
            with self.subTest(failure=type(failure).__name__):
                with patch.object(announce, "urlopen", side_effect=failure) as opener:
                    with self.assertRaises(announce.SyncError) as caught:
                        announce.send_discord(announce.webhook_url(WEBHOOK), {})
                self.assertNotIn(private, str(caught.exception))
                self.assertNotIn(WEBHOOK, str(caught.exception))
                self.assertEqual(opener.call_count, 1)
        self.assertTrue(http.closed)
        for body in (b"{}", b'{"id":null}', b'{"id":999}', b"private response text"):
            with self.subTest(body=body):
                response = io.BytesIO(body)
                response.status = 200
                with patch.object(announce, "urlopen", return_value=response):
                    with self.assertRaises(announce.SyncError) as caught:
                        announce.send_discord(announce.webhook_url(WEBHOOK), {})
                self.assertNotIn(body.decode(), str(caught.exception))


class AnnouncementCLITests(unittest.TestCase):
    def environment(self):
        return {
            "GITHUB_REPOSITORY": announce.DOCS,
            "GITHUB_ACTIONS": "true",
            "DOCS_ANNOUNCE_RELEASE": "true",
            "GITHUB_TOKEN": "test-publishing-token",
            "DISCORD_WEBHOOK_URL": WEBHOOK,
            "DISCORD_RELEASE_MENTION": ROLE,
        }

    def test_missing_authorization_or_secrets_stops_before_api_or_discord(self):
        for field in self.environment():
            environment = self.environment()
            environment.pop(field)
            with self.subTest(field=field):
                with (
                    patch.dict(os.environ, environment, clear=True),
                    patch.object(announce, "GitHub") as api,
                    patch.object(announce, "send_discord") as sender,
                    contextlib.redirect_stderr(io.StringIO()) as errors,
                ):
                    self.assertEqual(
                        announce.main(["--tag", TAG, "--expected-head", SHA]), 1
                    )
                api.assert_not_called()
                sender.assert_not_called()
                self.assertNotIn(WEBHOOK, errors.getvalue())

    def test_explicit_request_uses_publishing_token_and_reports_no_private_values(self):
        environment = self.environment()
        with (
            patch.dict(os.environ, environment, clear=True),
            patch.object(announce, "GitHub") as api,
            patch.object(announce, "announce", return_value="sent") as deliver,
            contextlib.redirect_stdout(io.StringIO()) as output,
        ):
            self.assertEqual(announce.main(["--tag", TAG, "--expected-head", SHA]), 0)
        api.assert_called_once_with(environment["GITHUB_TOKEN"])
        deliver.assert_called_once_with(api.return_value, TAG, SHA, WEBHOOK, ROLE)
        for private in (ROLE, WEBHOOK, environment["GITHUB_TOKEN"]):
            self.assertNotIn(private, output.getvalue())


if __name__ == "__main__":
    unittest.main()

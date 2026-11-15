"""Preserve the release announcement and its successful-deployment boundary."""

import unittest
from pathlib import Path

import yaml


class AnnouncementWorkflowTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        self.workflow = yaml.load(
            (root / ".github/workflows/publish-release.yml").read_text(),
            Loader=yaml.BaseLoader,
        )

    def test_announcement_is_wired_after_successful_publication(self):
        job = self.workflow["jobs"]["announce"]
        self.assertIn("deploy", job["needs"])
        self.assertIn("resolve", job["needs"])
        self.assertIn("needs.deploy.result == 'success'", job["if"])
        self.assertNotIn("always()", job["if"])
        delivery = [
            step
            for step in job["steps"]
            if "scripts/announce_docs_release.py" in step.get("run", "")
        ]
        self.assertEqual(len(delivery), 1)
        self.assertEqual(
            delivery[0]["env"]["DISCORD_WEBHOOK_URL"],
            "${{ secrets.DISCORD_WEBHOOK_URL }}",
        )
        self.assertEqual(delivery[0]["env"]["DOCS_ANNOUNCE_RELEASE"], "true")
        self.assertEqual(
            delivery[0]["env"]["DISCORD_RELEASE_MENTION"],
            "${{ secrets.DISCORD_RELEASE_MENTION }}",
        )

    def test_ordinary_rebuilds_do_not_send_announcements(self):
        inputs = self.workflow["on"]["workflow_dispatch"]["inputs"]
        self.assertEqual(inputs["announce_release"]["type"], "boolean")
        self.assertEqual(inputs["announce_release"]["default"], "false")
        condition = self.workflow["jobs"]["announce"]["if"]
        self.assertIn("github.event_name == 'workflow_dispatch'", condition)
        self.assertIn("inputs.announce_release", condition)

    def test_new_release_dispatch_requests_the_announcement(self):
        dispatch = self.workflow["jobs"]["dispatch"]
        self.assertIn("github.event_name == 'release'", dispatch["if"])
        self.assertIn("!github.event.release.prerelease", dispatch["if"])
        commands = "\n".join(step.get("run", "") for step in dispatch["steps"])
        self.assertIn("announce_release=true", commands)

    def test_rebuilds_cannot_replace_a_pending_release_announcement(self):
        self.assertEqual(self.workflow["concurrency"]["queue"], "max")
        self.assertEqual(self.workflow["concurrency"]["cancel-in-progress"], "false")


if __name__ == "__main__":
    unittest.main()

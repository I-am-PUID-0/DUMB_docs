"""A disposable embedded app may never clean up an unrelated container or path."""

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SOURCE = (
    Path(__file__).resolve().parents[1] / "scripts/frontend-visuals/demo-service.py"
)
SPEC = importlib.util.spec_from_file_location("docs_demo_service", SOURCE)
demo = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(demo)


class DemoOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="dumb-docs-sonarr-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "config").mkdir()
        self.identity, self.container = "a" * 32, "b" * 64
        (self.root / ".docs-demo").write_text(self.identity)
        self.state = {
            "identity": self.identity,
            "container_id": self.container,
            "data_root": str(self.root),
        }
        self.record = {
            "Id": self.container,
            "Config": {"Labels": {demo.LABEL: self.identity}},
            "Mounts": [{"Type": "bind", "Source": str(self.root / "config")}],
        }

    def inspection(self, record=None):
        return subprocess.CompletedProcess(
            [], 0, stdout=json.dumps([record or self.record]), stderr=""
        )

    def test_forged_container_label_is_rejected_before_any_mutation(self):
        self.record["Config"]["Labels"][demo.LABEL] = "c" * 32
        with patch.object(demo, "docker", return_value=self.inspection()) as docker:
            with self.assertRaisesRegex(ValueError, "task label"):
                demo.validate_owned(self.state)
        self.assertEqual(
            [call.args for call in docker.call_args_list], [("inspect", self.container)]
        )
        self.assertTrue(self.root.is_dir())

    def test_wrong_mount_or_second_bind_cannot_authorize_cleanup(self):
        variants = [
            [{"Type": "bind", "Source": "/reserved-example/unrelated"}],
            self.record["Mounts"]
            + [{"Type": "bind", "Source": "/reserved-example/unrelated"}],
        ]
        for mounts in variants:
            with self.subTest(mounts=mounts):
                self.record["Mounts"] = mounts
                with patch.object(
                    demo, "docker", return_value=self.inspection()
                ) as docker:
                    with self.assertRaisesRegex(ValueError, "bind mounts"):
                        demo.validate_owned(self.state)
                    self.assertTrue(
                        all(call.args[0] == "inspect" for call in docker.call_args_list)
                    )

    def test_wrong_directory_marker_stops_before_docker_access(self):
        (self.root / ".docs-demo").write_text("different task")
        with patch.object(demo, "docker") as docker:
            with self.assertRaisesRegex(ValueError, "marker"):
                demo.validate_owned(self.state)
            docker.assert_not_called()

    def test_stop_uses_exact_validated_id_and_verifies_container_absence(self):
        state_directory = tempfile.TemporaryDirectory(prefix="dumb-docs-state-")
        self.addCleanup(state_directory.cleanup)
        state_path = Path(state_directory.name) / "private-state.json"
        state_path.write_text(json.dumps(self.state))
        absent = subprocess.CompletedProcess([], 1, stdout="", stderr="")
        responses = [
            self.inspection(),
            self.inspection(),
            subprocess.CompletedProcess([], 0),
            absent,
        ]
        with patch.object(demo, "docker", side_effect=responses) as docker:
            with patch("builtins.print"):
                demo.stop(state_path)
        self.assertIn(
            ("rm", "--force", "--volumes", self.container),
            [call.args for call in docker.call_args_list],
        )
        self.assertEqual(docker.call_args_list[-1].args, ("inspect", self.container))
        self.assertFalse(self.root.exists())


if __name__ == "__main__":
    unittest.main()

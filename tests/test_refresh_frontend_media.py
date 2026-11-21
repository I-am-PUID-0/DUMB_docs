"""Refreshes may propose data changes; partial or misidentified data is refused."""

import base64
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import refresh_frontend_media as media

SHA = "a" * 40
FRONT = "b" * 40
HEAD = "c" * 40


class API:
    def __init__(self):
        self.calls = []
        self.front = FRONT
        self.backend = SHA
        self.master = HEAD
        self.tag = "1.91.0"
        self.tag_source = FRONT
        self.backend_release_version = "2.23.0"
        self.backend_release_source = SHA

    def request(self, path, **kwargs):
        self.calls.append(path)
        frontend = f"/repos/{media.FRONTEND}/" in path
        if path.endswith("/git/ref/heads/master"):
            return {"object": {"sha": self.master}}
        if "/releases/tags/" in path:
            return {
                "tag_name": self.backend_release_version,
                "draft": False,
                "prerelease": False,
            }
        if path.endswith("/releases/latest"):
            return {
                "tag_name": self.tag if frontend else self.backend_release_version,
                "draft": False,
                "prerelease": False,
            }
        if "/git/ref/tags/" in path:
            tag = self.tag if frontend else self.backend_release_version
            return {
                "ref": "refs/tags/" + tag,
                "object": {
                    "type": "commit",
                    "sha": self.tag_source if frontend else self.backend_release_source,
                },
            }
        if path.endswith("/commits/dev"):
            return {"sha": self.front if frontend else self.backend}
        if "/contents/" in path:
            content = (
                json.dumps({"version": self.tag}).encode()
                if frontend
                else f'[project]\nversion = "{self.backend_release_version}"\n'.encode()
            )
            return {
                "type": "file",
                "encoding": "base64",
                "content": base64.b64encode(content).decode(),
            }
        if "/compare/" in path:
            return {"status": "ahead"}
        raise AssertionError("Unexpected API request: " + path)


class MediaRefreshTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.tools = self.root / media.TOOLS
        self.tools.mkdir(parents=True)
        self.scenarios = [
            {
                "id": "dashboard",
                "kinds": ["image"],
                "required_capabilities": [],
                "features": ["frontend/dashboard"],
            }
        ]
        media.dump(
            self.tools / "capture-catalog.json",
            {"schema_version": 1, "scenarios": self.scenarios},
        )
        (self.tools / "dataset.json").write_text('{"name":"Example"}')
        (self.tools / "capture.mjs").write_text("// reviewed capture tool\n")
        media.dump(
            self.tools / "showcase-scenes.json",
            {
                "duration_seconds": 28,
                "scenes": [
                    {"id": str(index), "duration_seconds": 4} for index in range(7)
                ],
            },
        )
        media.dump(
            self.root / "docs-versions.json",
            {
                "release": {"version": "2.23.0", "source": SHA},
                "dev": {"version": "2.24.0", "source": "d" * 40},
            },
        )
        self.api = API()

    def plan(self):
        selection = media.discover(self.root, self.api, HEAD, ["release"])
        pair = selection["channels"]["release"]
        plan = {
            "schema_version": 1,
            "channel": "release",
            **pair,
            "scenarios": ["dashboard"],
            "required_scenarios": ["dashboard"],
            "themes": ["dark", "light"],
            "capabilities": {},
            "capability_source_sha256": "e" * 64,
        }
        plan["plan_sha256"] = media.canonical_hash(plan)
        return selection, plan

    def package(self, plan, directory=None, showcase=False):
        directory = directory or self.root / "package"
        directory.mkdir(parents=True)
        rows, coverage = [], []
        for theme in plan["themes"]:
            filename = f"{theme}/dashboard.webp"
            data = b"RIFF1234WEBPexample"
            if showcase:
                filename, data = f"{theme}/hero.mp4", b"0000ftypisom1234"
            path = directory / filename
            path.parent.mkdir(parents=True)
            path.write_bytes(data)
            row = {
                "path": filename,
                "kind": "video" if showcase else "image",
                "scenario": "dashboard",
                "theme": theme,
                "sha256": media.digest(data),
                "bytes": len(data),
            }
            if showcase:
                row.update(
                    role="video",
                    duration_seconds=28,
                    viewport={"width": 1920, "height": 1280},
                )
                for role in ("poster", "animated"):
                    filename = f"{theme}/{role}.webp"
                    image = b"RIFF1234WEBPexample"
                    (directory / filename).write_bytes(image)
                    rows.append(
                        {
                            "path": filename,
                            "kind": "image",
                            "role": role,
                            "theme": theme,
                            "sha256": media.digest(image),
                            "bytes": len(image),
                            "viewport": (
                                {"width": 1280, "height": 854}
                                if role == "animated"
                                else {"width": 1920, "height": 1280}
                            ),
                        }
                    )
            rows.append(row)
            coverage.append(
                {
                    "id": "dashboard",
                    "theme": theme,
                    "status": "captured",
                    "required": True,
                    "features": ["frontend/dashboard"],
                    "artifacts": [filename],
                }
            )
        manifest = {
            "schema_version": 2,
            "captured_at": "2026-11-19T10:00:00Z",
            "complete": True,
            "coverage_complete": True,
            "coverage": coverage,
            "files": rows,
            **{
                key: plan[key]
                for key in (
                    "channel",
                    "frontend",
                    "backend",
                    "plan_sha256",
                    "catalog_sha256",
                    "dataset_sha256",
                    "tooling_sha256",
                )
            },
        }
        if showcase:
            for role in ("captions", "chapters", "transcript"):
                filename = role + (".txt" if role == "transcript" else ".vtt")
                data = b"Example transcript" if role == "transcript" else b"WEBVTT\n\n"
                (directory / filename).write_bytes(data)
                rows.append(
                    {
                        "path": filename,
                        "role": role,
                        "kind": "text",
                        "bytes": len(data),
                        "sha256": media.digest(data),
                    }
                )
            scenes = media.load(self.tools / "showcase-scenes.json")
            manifest.update(
                themes=plan["themes"],
                viewport={"width": 1920, "height": 1280},
                duration_seconds=28,
                scenes=scenes["scenes"],
                showcase_plan_sha256=media.digest(
                    (self.tools / "showcase-scenes.json").read_bytes()
                ),
            )
            manifest["input_package_manifest_sha256"] = media.digest(
                (directory.parent / "frontend/manifest.json").read_bytes()
            )
        media.dump(directory / "manifest.json", manifest)
        return directory, manifest

    def test_discovery_tracks_explicit_dev_branches_without_relabeling_prose(self):
        before = (self.root / "docs-versions.json").read_bytes()
        selected = media.discover(self.root, self.api, HEAD, ["dev"])
        self.assertEqual(selected["channels"]["dev"]["frontend"]["ref"], "dev")
        self.assertIn(f"/repos/{media.FRONTEND}/commits/dev", self.api.calls)
        self.assertEqual((self.root / "docs-versions.json").read_bytes(), before)

    def test_fresh_catalog_noops_but_backend_or_tooling_changes_recapture(self):
        selection = media.discover(self.root, self.api, HEAD, ["dev"])
        media.dump(self.root / media.CATALOG, selection)
        self.assertFalse(media.discover(self.root, self.api, HEAD, ["dev"])["channels"])
        self.api.backend = "d" * 40
        self.assertIn(
            "dev", media.discover(self.root, self.api, HEAD, ["dev"])["channels"]
        )
        self.api.backend = SHA
        (self.tools / "capture.mjs").write_text("// improved fixture")
        self.assertIn(
            "dev", media.discover(self.root, self.api, HEAD, ["dev"])["channels"]
        )

    def test_frontend_release_change_captures_again_without_backend_promotion(self):
        first = media.discover(self.root, self.api, HEAD, ["release"])
        media.dump(self.root / media.CATALOG, first)
        self.api.tag, self.api.tag_source = "1.92.0", "d" * 40
        changed = media.discover(self.root, self.api, HEAD, ["release"])
        self.assertEqual(changed["channels"]["release"]["backend"]["commit"], SHA)
        self.assertEqual(
            changed["channels"]["release"]["frontend"]["version"], "1.92.0"
        )

    def test_moved_documented_backend_tag_is_refused(self):
        metadata = media.load(self.root / "docs-versions.json")
        metadata["release"]["source"] = "d" * 40
        media.dump(self.root / "docs-versions.json", metadata)
        with self.assertRaisesRegex(media.SyncError, "tag moved"):
            media.discover(self.root, self.api, HEAD, ["release"])

    def test_reviewed_backend_promotion_and_media_are_proposed_together(self):
        metadata = media.load(self.root / "docs-versions.json")
        metadata["dev"] = {
            "version": "2.24.0",
            "source": "d" * 40,
            "frontend_source": FRONT,
        }
        media.dump(self.root / "docs-versions.json", metadata)
        self.api.backend_release_version = "2.24.0"
        self.api.backend_release_source = "d" * 40
        selected = media.discover(self.root, self.api, HEAD, ["release"])
        self.assertEqual(selected["docs_versions"]["release"]["version"], "2.24.0")
        self.assertEqual(
            selected["channels"]["release"]["backend"]["version"], "2.24.0"
        )
        self.assertEqual(selected["docs_versions"]["dev"], metadata["dev"])
        self.assertEqual(media.load(self.root / "docs-versions.json"), metadata)

    def test_unreviewed_backend_release_cannot_advance_media_or_prose(self):
        self.api.backend_release_version = "2.25.0"
        self.api.backend_release_source = "d" * 40
        with self.assertRaisesRegex(
            media.SyncError, "no reviewed documentation candidate"
        ):
            media.discover(self.root, self.api, HEAD, ["release"])
        self.assertFalse((self.root / media.CATALOG).exists())

    def test_source_identity_serializes_canonical_repository_url(self):
        selection = media.discover(self.root, self.api, HEAD, ["dev"])
        self.assertEqual(
            selection["channels"]["dev"]["frontend"]["repository"],
            "https://github.com/" + media.FRONTEND,
        )

    def test_new_frontend_routes_or_settings_sections_require_catalog_review(self):
        frontend = self.root / "frontend-source"
        (frontend / "pages").mkdir(parents=True)
        (frontend / "components").mkdir()
        (frontend / "pages/index.vue").write_text(
            "<template><h1>Dashboard</h1></template>"
        )
        settings = frontend / "pages/settings.vue"
        settings.write_text(
            '<template><SettingsSection section-id="appearance" /></template>'
        )
        home = frontend / "pages/home.vue"
        home.write_text(
            '<script setup lang="ts">\n</script><template>\n</template><style scoped>\n</style>'
        )
        catalog = {
            "scenarios": [
                {"id": "dashboard", "route": "/"},
                {"id": "appearance", "route": "/settings#appearance"},
            ],
            "excluded_frontend_pages": [
                {"path": "pages/home.vue", "reason": "Empty retained template"}
            ],
        }
        inventory = media.frontend_inventory(frontend, catalog)
        self.assertEqual(
            [row["path"] for row in inventory["pages"]],
            ["pages/index.vue", "pages/settings.vue"],
        )
        self.assertEqual(inventory["excluded_pages"][0]["path"], "pages/home.vue")
        unknown = frontend / "pages/new-tool.vue"
        unknown.write_text("<template>New actual interface</template>")
        with self.assertRaisesRegex(media.SyncError, "uncatalogued pages"):
            media.frontend_inventory(frontend, catalog)
        unknown.unlink()
        settings.write_text(
            '<template><SettingsSection section-id="appearance" /><SettingsSection section-id="new-section" /></template>'
        )
        with self.assertRaisesRegex(media.SyncError, "uncatalogued Settings section"):
            media.frontend_inventory(frontend, catalog)
        settings.write_text(
            '<template><SettingsSection section-id="appearance" /></template>'
        )
        home.write_text("<template><h1>New home interface</h1></template>")
        with self.assertRaisesRegex(media.SyncError, "gained content"):
            media.frontend_inventory(frontend, catalog)

    def test_dynamic_service_route_and_component_settings_are_inventoried(self):
        frontend = self.root / "frontend-source"
        (frontend / "pages/services/[serviceId]").mkdir(parents=True)
        (frontend / "pages/services/[serviceId]/index.vue").write_text(
            "<template>Service</template>"
        )
        (frontend / "components").mkdir()
        (frontend / "components/NotificationSettings.vue").write_text(
            '<SettingsSection section-id="notifications" />'
        )
        catalog = {
            "scenarios": [
                {"id": "service", "route": "/services/Sonarr"},
                {
                    "id": "notifications",
                    "route": "/settings#notifications",
                    "settings_source": "components/NotificationSettings.vue",
                },
            ]
        }
        inventory = media.frontend_inventory(frontend, catalog)
        self.assertEqual(inventory["pages"][0]["scenarios"], ["service"])
        self.assertEqual(inventory["settings_sections"][0]["id"], "notifications")

    def test_canonical_hash_matches_utf8_javascript_serialization(self):
        value = {"z": "café", "a": {"second": 2, "first": 1}}
        self.assertEqual(
            media.canonical_hash(value),
            media.digest('{"a":{"first":1,"second":2},"z":"café"}'.encode()),
        )

    def test_frontend_source_omissions_are_explicit_not_selector_failures(self):
        source = self.root / "frontend"
        (source / "pages").mkdir(parents=True)
        (source / "pages/settings.vue").write_text(
            '<SettingsSection section-id="appearance">'
        )
        self.assertIsNone(
            media.frontend_absence(source, {"settings_section": "appearance"})
        )
        self.assertIn(
            "backups", media.frontend_absence(source, {"settings_section": "backups"})
        )
        self.assertIn(
            "StepArrangement.vue",
            media.frontend_absence(
                source,
                {
                    "required_frontend_files": [
                        "components/onboarding/StepArrangement.vue"
                    ]
                },
            ),
        )
        with self.assertRaises(media.SyncError):
            media.frontend_absence(source, {"required_frontend_files": ["../private"]})

    def test_native_prerequisite_pins_are_literal_data_not_executed_code(self):
        catalog = {"scenarios": [{"required_prerequisites": ["sonarr"]}]}
        (self.tools / "demo-service.py").write_text(
            'raise RuntimeError("never execute this file")\n'
            'IMAGE = "lscr.io/linuxserver/sonarr@sha256:' + "a" * 64 + '"\n'
            'SONARR_VERSION = "4.0.20.3014"\n'
        )
        self.assertEqual(
            media.native_app_pins(self.root, catalog)["sonarr"]["version"],
            "4.0.20.3014",
        )
        (self.tools / "demo-service.py").write_text("IMAGE = runtime_image()\n")
        with self.assertRaisesRegex(media.SyncError, "exact official image"):
            media.native_app_pins(self.root, catalog)

    def test_complete_source_matched_package_is_accepted(self):
        _, plan = self.plan()
        directory, manifest = self.package(plan)
        self.assertEqual(media.verify_package(self.root, plan, directory), manifest)

    def test_capture_timestamp_requires_a_timezone_and_valid_iso_date(self):
        _, plan = self.plan()
        directory, manifest = self.package(plan)
        for value in (
            None,
            "2026-11-19",
            "2026-11-19T10:00:00",
            "2026-19-41T10:00:00Z",
        ):
            with self.subTest(value=value):
                media.dump(
                    directory / "manifest.json", {**manifest, "captured_at": value}
                )
                with self.assertRaisesRegex(media.SyncError, "ISO capture timestamp"):
                    media.verify_package(self.root, plan, directory)

    def test_embedded_native_observation_must_match_exact_app_version_and_image(self):
        _, plan = self.plan()
        self.scenarios[0]["id"] = "embedded-sonarr"
        media.dump(self.tools / "capture-catalog.json", {"scenarios": self.scenarios})
        plan["scenarios"] = plan["required_scenarios"] = ["embedded-sonarr"]
        plan["native_apps"] = {
            "sonarr": {
                "application": "Sonarr",
                "version": "4.0.20.3014",
                "image": "lscr.io/linuxserver/sonarr@sha256:" + "a" * 64,
            }
        }
        directory, manifest = self.package(plan)
        for row in [*manifest["coverage"], *manifest["files"]]:
            if "id" in row:
                row["id"] = "embedded-sonarr"
            if "scenario" in row:
                row["scenario"] = "embedded-sonarr"
        manifest["native_apps"] = plan["native_apps"]
        manifest["native_app_observations"] = {
            "sonarr": {**plan["native_apps"]["sonarr"], "verified": True}
        }
        media.dump(directory / "manifest.json", manifest)
        media.verify_package(self.root, plan, directory)
        for key, value in (
            ("application", "Substitute"),
            ("version", "4.0.0.0"),
            ("image", "sonarr:latest"),
            ("verified", False),
        ):
            with self.subTest(key=key):
                changed = copy.deepcopy(manifest)
                changed["native_app_observations"]["sonarr"][key] = value
                media.dump(directory / "manifest.json", changed)
                with self.assertRaisesRegex(media.SyncError, "verified observation"):
                    media.verify_package(self.root, plan, directory)

    def test_showcase_propagates_timestamp_and_exact_source_package_hash(self):
        selection, plan = self.plan()
        channel = self.root / "artifacts/release"
        media.dump(channel / "plan.json", plan)
        self.package(plan, channel / "frontend")
        _, showcase = self.package(plan, channel / "showcase", showcase=True)
        for change in (
            {"captured_at": "2026-11-20T10:00:00Z"},
            {"input_package_manifest_sha256": "f" * 64},
        ):
            with self.subTest(change=change):
                media.dump(channel / "showcase/manifest.json", {**showcase, **change})
                with self.assertRaises(media.SyncError):
                    media.apply_packages(
                        self.root, selection, channel.parent, self.api, HEAD
                    )
                self.assertFalse((self.root / media.CATALOG).exists())

    def test_showcase_requires_both_themes_and_every_accessible_role(self):
        _, plan = self.plan()
        channel = self.root / "artifacts/release"
        self.package(plan, channel / "frontend")
        directory, manifest = self.package(plan, channel / "showcase", showcase=True)
        media.verify_package(self.root, plan, directory, showcase=True)
        for filename in (
            "dark/poster.webp",
            "captions.vtt",
            "chapters.vtt",
            "transcript.txt",
        ):
            with self.subTest(filename=filename):
                path = directory / filename
                original = path.read_bytes()
                path.unlink()
                changed = {
                    **manifest,
                    "files": [
                        row for row in manifest["files"] if row["path"] != filename
                    ],
                }
                media.dump(directory / "manifest.json", changed)
                with self.assertRaisesRegex(
                    media.SyncError, "theme role or accessible text track"
                ):
                    media.verify_package(self.root, plan, directory, showcase=True)
                path.write_bytes(original)
        media.dump(directory / "manifest.json", {**manifest, "themes": ["light"]})
        with self.assertRaisesRegex(media.SyncError, "both planned"):
            media.verify_package(self.root, plan, directory, showcase=True)

    def test_showcase_wrong_frame_duration_or_scene_plan_is_refused(self):
        _, plan = self.plan()
        channel = self.root / "artifacts/release"
        self.package(plan, channel / "frontend")
        directory, manifest = self.package(plan, channel / "showcase", showcase=True)
        for change in (
            {"viewport": {"width": 1280, "height": 800}},
            {"duration_seconds": 40},
            {"showcase_plan_sha256": "f" * 64},
        ):
            with self.subTest(change=change):
                media.dump(directory / "manifest.json", {**manifest, **change})
                with self.assertRaises(media.SyncError):
                    media.verify_package(self.root, plan, directory, showcase=True)

    def test_source_mismatch_and_partial_coverage_are_refused(self):
        _, plan = self.plan()
        directory, manifest = self.package(plan)
        for change in (
            {"coverage_complete": False},
            {"frontend": {"commit": "f" * 40}},
            {"coverage": manifest["coverage"][:1]},
        ):
            with self.subTest(change=change):
                media.dump(directory / "manifest.json", {**manifest, **change})
                with self.assertRaises(media.SyncError):
                    media.verify_package(self.root, plan, directory)

    def test_claimed_success_missing_clip_is_refused(self):
        _, plan = self.plan()
        self.scenarios[0]["kinds"].append("video")
        media.dump(self.tools / "capture-catalog.json", {"scenarios": self.scenarios})
        directory, _ = self.package(plan)
        with self.assertRaisesRegex(media.SyncError, "still or clip"):
            media.verify_package(self.root, plan, directory)

    def test_required_selector_failure_cannot_be_hidden_as_skip(self):
        _, plan = self.plan()
        directory, manifest = self.package(plan)
        manifest["coverage"][0].update(
            status="skipped", reason="selector not found", artifacts=[]
        )
        media.dump(directory / "manifest.json", manifest)
        with self.assertRaisesRegex(media.SyncError, "required scenario"):
            media.verify_package(self.root, plan, directory)

    def test_hash_mismatch_unlisted_file_and_symlink_are_refused(self):
        _, plan = self.plan()
        directory, _ = self.package(plan)
        image = directory / "dark/dashboard.webp"
        original = image.read_bytes()
        image.write_bytes(original[:-1] + b"!")
        with self.assertRaisesRegex(media.SyncError, "hash"):
            media.verify_package(self.root, plan, directory)
        image.write_bytes(original)
        extra = directory / "unlisted.txt"
        extra.write_text("unlisted")
        with self.assertRaisesRegex(media.SyncError, "unlisted"):
            media.verify_package(self.root, plan, directory)
        extra.unlink()
        image.unlink()
        image.symlink_to(directory / "light/dashboard.webp")
        with self.assertRaisesRegex(media.SyncError, "symbolic"):
            media.verify_package(self.root, plan, directory)

    def test_path_traversal_and_html_disguised_as_image_are_refused(self):
        for value in ("../secret.txt", "/secret.txt", "dark/../../x", "dark\\x", "./x"):
            with self.subTest(value=value), self.assertRaises(media.SyncError):
                media.safe_file(self.root, value)
        _, plan = self.plan()
        directory, manifest = self.package(plan)
        data = b"<html>not a screenshot</html>"
        (directory / "dark/dashboard.webp").write_bytes(data)
        manifest["files"][0].update(bytes=len(data), sha256=media.digest(data))
        media.dump(directory / "manifest.json", manifest)
        with self.assertRaisesRegex(media.SyncError, "signature"):
            media.verify_package(self.root, plan, directory)

    def test_stale_docs_or_upstream_head_prevents_any_asset_write(self):
        selection, _ = self.plan()
        self.api.master = "d" * 40
        with self.assertRaisesRegex(media.SyncError, "branch changed"):
            media.apply_packages(
                self.root, selection, self.root / "missing", self.api, HEAD
            )
        self.api.master = HEAD
        self.api.tag, self.api.tag_source = "1.92.0", "d" * 40
        with self.assertRaisesRegex(media.SyncError, "changed during"):
            media.apply_packages(
                self.root, selection, self.root / "missing", self.api, HEAD
            )
        self.assertFalse((self.root / media.CATALOG).exists())

    def test_apply_creates_cache_safe_paths_and_offline_validatable_catalog(self):
        selection, plan = self.plan()
        artifacts = self.root / "artifacts"
        channel = artifacts / "release"
        media.dump(channel / "plan.json", plan)
        self.package(plan, channel / "frontend")
        self.package(plan, channel / "showcase", showcase=True)
        proposed = media.apply_packages(self.root, selection, artifacts, self.api, HEAD)
        first = proposed["channels"]["release"]
        validated = media.validate_channel(self.root, "release", first)
        self.assertTrue(validated["package"]["coverage_complete"])
        self.assertRegex(
            first["package_manifest"], r"a{12}-b{12}-[0-9a-f]{12}/manifest.json$"
        )
        old_path = first["package_manifest"]
        manifest_path = channel / "showcase/manifest.json"
        manifest = media.load(manifest_path)
        manifest["render_revision"] = "changed pacing"
        media.dump(manifest_path, manifest)
        updated = media.apply_packages(self.root, selection, artifacts, self.api, HEAD)
        self.assertNotEqual(
            updated["channels"]["release"]["package_manifest"], old_path
        )
        self.assertTrue((self.root / old_path).is_file())

    def assert_named_workflow_artifacts_apply(self, channels):
        workflow_path = (
            Path(__file__).resolve().parents[1]
            / ".github/workflows/refresh-frontend-media.yml"
        )
        workflow = yaml.load(workflow_path.read_text(), Loader=yaml.BaseLoader)
        downloads = {
            step.get("with", {}).get("name"): step["with"]
            for step in workflow["jobs"]["propose"]["steps"]
            if step.get("uses", "").startswith("actions/download-artifact@")
        }
        selection = media.discover(self.root, self.api, HEAD, list(channels))
        for channel, pair in selection["channels"].items():
            artifact_name = "frontend-media-" + channel
            self.assertIn(
                artifact_name,
                downloads,
                "The media proposal needs a deterministic named-artifact destination",
            )
            plan = {
                "schema_version": 1,
                "channel": channel,
                **pair,
                "scenarios": ["dashboard"],
                "required_scenarios": ["dashboard"],
                "themes": ["dark", "light"],
                "capabilities": {},
                "capability_source_sha256": "e" * 64,
            }
            plan["plan_sha256"] = media.canonical_hash(plan)
            uploaded = self.root / "uploaded" / artifact_name
            media.dump(uploaded / "plan.json", plan)
            self.package(plan, uploaded / "frontend")
            self.package(plan, uploaded / "showcase", showcase=True)
            archive = self.root / (artifact_name + ".zip")
            with zipfile.ZipFile(archive, "w") as artifact:
                for filename in uploaded.rglob("*"):
                    if filename.is_file():
                        artifact.write(filename, filename.relative_to(uploaded))

            destination = self.root / downloads[artifact_name]["path"]
            self.assertEqual(destination, self.root / "proposals" / channel)
            # download-artifact v8 extracts a named artifact directly into
            # `path`, including when only one channel produced an artifact.
            with zipfile.ZipFile(archive) as artifact:
                artifact.extractall(destination)
            selected_plan = media.safe_file(destination, "plan.json")
            self.assertEqual(media.load(selected_plan), plan)

        proposed = media.apply_packages(
            self.root, selection, self.root / "proposals", self.api, HEAD
        )
        self.assertEqual(set(proposed["channels"]), set(channels))
        self.assertEqual(
            {path.name for path in (self.root / "proposals").iterdir()}, set(channels)
        )
        for channel in channels:
            accepted = media.validate_channel(
                self.root, channel, proposed["channels"][channel]
            )
            self.assertTrue(accepted["package"]["coverage_complete"])

    def test_named_artifact_handoff_applies_release_only(self):
        self.assert_named_workflow_artifacts_apply(("release",))

    def test_named_artifact_handoff_applies_dev_only(self):
        self.assert_named_workflow_artifacts_apply(("dev",))

    def test_named_artifact_handoff_applies_both_channels(self):
        self.assert_named_workflow_artifacts_apply(("release", "dev"))

    def test_renderer_rejects_changed_capture_tooling_and_cross_channel_assets(self):
        selection, plan = self.plan()
        channel = self.root / "artifacts/release"
        media.dump(channel / "plan.json", plan)
        self.package(plan, channel / "frontend")
        self.package(plan, channel / "showcase", showcase=True)
        accepted = media.apply_packages(
            self.root, selection, channel.parent, self.api, HEAD
        )["channels"]["release"]
        wrong = copy.deepcopy(accepted)
        wrong["package_manifest"] = accepted["package_manifest"].replace(
            "/release/", "/dev/"
        )
        with self.assertRaisesRegex(media.SyncError, "outside"):
            media.validate_channel(self.root, "release", wrong)
        (self.tools / "capture.mjs").write_text("// changed selector")
        with self.assertRaisesRegex(media.SyncError, "regenerate"):
            media.validate_channel(self.root, "release", accepted)


class CapabilityExtractionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "api/routers").mkdir(parents=True)
        (self.root / "utils").mkdir()

    def source(self, body):
        (self.root / "api/routers/process.py").write_text(body)

    def test_literals_imported_service_keys_and_unknown_runtime_are_distinct(self):
        self.source("""from utils.example import SERVICES
async def get_capabilities():
    return {"auth_oidc": True, "installation_backup": False, "service_keys": sorted(SERVICES), "runtime": dangerous_call()}
""")
        (self.root / "utils/example.py").write_text(
            'raise RuntimeError("must never import")\nSERVICES = frozenset({"sonarr", "radarr"})\n'
        )
        snapshot = media.StaticCapabilities(self.root).extract("2.23.0")
        self.assertTrue(snapshot["capabilities"]["auth_oidc"])
        self.assertFalse(snapshot["capabilities"]["installation_backup"])
        self.assertEqual(snapshot["capabilities"]["service_keys"], ["radarr", "sonarr"])
        self.assertNotIn("runtime", snapshot["capabilities"])
        self.assertEqual(snapshot["unresolved_capabilities"], ["runtime"])

    def test_unknown_dictionary_expansion_and_changed_endpoint_fail_closed(self):
        for source in (
            "async def get_capabilities():\n    return {**unknown_capabilities()}\n",
            "async def get_capabilities():\n    return runtime_mapping()\n",
        ):
            with self.subTest(source=source):
                self.source(source)
                with self.assertRaises(media.SyncError):
                    media.StaticCapabilities(self.root).extract("2.24.0")

    def test_changed_capability_admission_is_never_executed_or_guessed(self):
        self.source(
            "async def get_capabilities():\n    return {**versioned_capabilities(get_project_version(pyproject_file()))}\n"
        )
        (self.root / "utils/infinidysk_v2_support.py").write_text(
            'def api_version_supported(version):\n    return True\ndef versioned_capabilities(version):\n    return {"infinidysk_v2": True}\n'
        )
        with self.assertRaisesRegex(media.SyncError, "Versioned"):
            media.StaticCapabilities(self.root).extract("2.24.0")

    def test_static_reader_refuses_external_modules_and_symlink_sources(self):
        reader = media.StaticCapabilities(self.root)
        with self.assertRaises(ValueError):
            reader.module("os")
        (self.root / "utils/link.py").symlink_to(self.root / "api/routers/process.py")
        with self.assertRaises(ValueError):
            reader.module("utils.link")


class MediaWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = (
            Path(__file__).resolve().parents[1]
            / ".github/workflows/refresh-frontend-media.yml"
        )
        cls.text = cls.path.read_text()
        cls.workflow = yaml.load(cls.text, Loader=yaml.BaseLoader)

    def test_schedule_source_triggers_and_trusted_master_only(self):
        events = self.workflow["on"]
        self.assertIn("schedule", events)
        self.assertIn("workflow_dispatch", events)
        self.assertIn("docs-versions.json", events["push"]["paths"])
        self.assertIn("scripts/frontend-visuals/**", events["push"]["paths"])
        self.assertNotIn("pull_request_target", events)
        self.assertIn(
            "github.ref == 'refs/heads/master'", self.workflow["jobs"]["discover"]["if"]
        )

    def test_upstream_execution_has_no_write_token_and_uses_frozen_sources(self):
        capture = self.workflow["jobs"]["capture"]
        self.assertEqual(capture["permissions"], {"contents": "read"})
        self.assertNotIn("secrets.", json.dumps(capture))
        source_checkouts = [
            step for step in capture["steps"] if step.get("with", {}).get("repository")
        ]
        self.assertEqual(
            {step["with"]["repository"] for step in source_checkouts},
            {media.BACKEND, media.FRONTEND},
        )
        for step in source_checkouts:
            self.assertEqual(step["with"]["persist-credentials"], "false")
            self.assertIn("_commit", step["with"]["ref"])
        self.assertIn("pnpm install --frozen-lockfile", json.dumps(capture))
        self.assertNotIn(
            "sources/backend/",
            "\n".join(step.get("run", "") for step in capture["steps"]),
        )

    def test_real_embedded_service_has_cleanup_and_complete_capture_gate(self):
        capture = self.workflow["jobs"]["capture"]
        commands = "\n".join(step.get("run", "") for step in capture["steps"])
        self.assertIn("demo-service.py start --network-host", commands)
        self.assertIn("demo-service.py stop", commands)
        self.assertIn("trap cleanup EXIT", commands)
        self.assertIn("--embedded-sonarr-origin", commands)
        self.assertIn(
            "package.mjs --plan result/plan.json --captures raw-captures --out result/frontend",
            commands,
        )
        self.assertIn(
            "showcase.mjs --frontend-root sources/frontend --media result/frontend --out result/showcase --theme both",
            commands,
        )
        self.assertNotIn(
            "showcase.mjs --frontend-root sources/frontend --media result/frontend --plan result/plan.json",
            commands,
        )
        self.assertEqual(commands.count("refresh_frontend_media.py verify"), 2)
        self.assertIn(
            "needs.capture.result == 'success'", self.workflow["jobs"]["propose"]["if"]
        )

    def test_media_downloads_use_selected_channel_names_and_fixed_destinations(self):
        downloads = [
            step
            for step in self.workflow["jobs"]["propose"]["steps"]
            if step.get("uses", "").startswith("actions/download-artifact@")
            and step.get("with", {}).get("name", "").startswith("frontend-media-")
        ]
        self.assertEqual(
            {step["with"]["name"] for step in downloads},
            {"frontend-media-release", "frontend-media-dev"},
        )
        self.assertEqual(len(downloads), 2)
        for step in downloads:
            values = step["with"]
            channel = values["name"].removeprefix("frontend-media-")
            self.assertEqual(values["path"], "proposals/" + channel)
            self.assertEqual(values.get("digest-mismatch"), "error")
            self.assertNotIn("pattern", values)
            for other_run in ("run-id", "repository", "github-token"):
                self.assertNotIn(other_run, values)
            condition = step.get("if", "").removeprefix("${{").removesuffix("}}")
            self.assertEqual(
                "".join(condition.split()),
                "contains(fromJSON(needs.discover.outputs.matrix).include.*.channel,'"
                + channel
                + "')",
            )

    def test_proposal_only_writes_scoped_media_pr_after_trusted_revalidation(self):
        proposal = self.workflow["jobs"]["propose"]
        steps = proposal["steps"]
        self.assertEqual(steps[0]["with"]["persist-credentials"], "false")
        revalidation = next(
            index
            for index, step in enumerate(steps)
            if "refresh_frontend_media.py apply" in step.get("run", "")
        )
        publishing = next(
            index
            for index, step in enumerate(steps)
            if step.get("uses", "").startswith("peter-evans/create-pull-request")
        )
        self.assertLess(revalidation, publishing)
        paths = steps[publishing]["with"]["add-paths"].splitlines()
        self.assertEqual(
            paths,
            [
                "docs-versions.json",
                "frontend-media.json",
                "docs/assets/images/guides/frontend/channels/",
                "docs/assets/images/guides/showcase/channels/",
            ],
        )
        self.assertNotIn("gh pr merge", self.text)
        self.assertNotIn("auto-approve", self.text)
        self.assertNotIn("deploy-pages", self.text)
        self.assertNotIn("DISCORD_WEBHOOK", self.text)


if __name__ == "__main__":
    unittest.main()

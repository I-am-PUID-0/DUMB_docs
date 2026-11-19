#!/usr/bin/env python3
"""Resolve, validate and stage reviewable, source-pinned frontend media refreshes.

Discovery is the only network-dependent operation. Builds of accepted docs use
their committed catalog offline. Backend files are parsed as data, never imported
or executed; the capture fixture remains separate from a real installation.
"""

from __future__ import annotations

import argparse
import ast
import base64
import copy
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tomllib
from urllib.parse import quote, unquote, urlsplit

if __package__:
    from . import sync_release
else:
    import sync_release

BACKEND = sync_release.BACKEND
DOCS = sync_release.DOCS
FRONTEND = sync_release.FRONTEND
GitHub = sync_release.GitHub
SyncError = sync_release.SyncError
assert_current = sync_release.assert_current
checked_sha = sync_release.checked_sha
proposal = sync_release.proposal
release_commit = sync_release.release_commit
stable_version = sync_release.stable_version
write_outputs = sync_release.write_outputs

ROOT = Path(__file__).resolve().parents[1]
CATALOG = "frontend-media.json"
TOOLS = "scripts/frontend-visuals"
CHANNELS = ("release", "dev")
HEX256 = re.compile(r"[0-9a-f]{64}\Z")
MAX_FILE = 25 * 1024 * 1024
MAX_PACKAGE = 300 * 1024 * 1024


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_hash(value: dict) -> str:
    return digest(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode()
    )


def load(path: Path) -> dict:
    try:
        value = json.loads(path.read_text())
    except (OSError, ValueError):
        raise SyncError(f"Cannot read JSON metadata: {path.name}.") from None
    if not isinstance(value, dict):
        raise SyncError(f"JSON metadata must be an object: {path.name}.")
    return value


def dump(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def fingerprints(root: Path) -> dict:
    directory = root / TOOLS
    files = sorted(
        (*directory.glob("*.mjs"), *directory.glob("*.json"), *directory.glob("*.py"))
    )
    if not files or any(path.is_symlink() for path in files):
        raise SyncError("Media tooling is absent or contains symbolic links.")
    catalog = directory / "capture-catalog.json"
    dataset = directory / "dataset.json"
    tooling = {path.name: digest(path.read_bytes()) for path in files}
    helper = root / "scripts/refresh_frontend_media.py"
    if helper.exists():
        tooling["../refresh_frontend_media.py"] = digest(helper.read_bytes())
    return {
        "catalog_sha256": digest(catalog.read_bytes()),
        "dataset_sha256": digest(dataset.read_bytes()),
        "tooling_sha256": canonical_hash(tooling),
    }


def source_file(api: GitHub, repository: str, commit: str, path: str) -> bytes:
    response = api.request(
        f"/repos/{repository}/contents/{path}?ref={checked_sha(commit, 'Source')}"
    )
    if response.get("type") != "file" or response.get("encoding") != "base64":
        raise SyncError("The selected source metadata is not a regular source file.")
    try:
        return base64.b64decode("".join(response["content"].split()), validate=True)
    except (KeyError, ValueError, TypeError):
        raise SyncError("Invalid source metadata encoding.") from None


def project_version(data: bytes, frontend: bool = False) -> str:
    try:
        value = (
            json.loads(data)["version"]
            if frontend
            else tomllib.loads(data.decode())["project"]["version"]
        )
        return stable_version(value)
    except (KeyError, TypeError, ValueError, UnicodeError):
        raise SyncError("The selected source has no stable package version.") from None


def identity(repository: str, ref: str, commit: str, version: str, tag=None) -> dict:
    if repository not in {BACKEND, FRONTEND}:
        raise SyncError(
            "Media sources must use the canonical application repositories."
        )
    return {
        "repository": "https://github.com/" + repository,
        "ref": ref,
        "tag": tag,
        "commit": checked_sha(commit, "Media source"),
        "version": stable_version(version),
    }


def branch_identity(api: GitHub, repository: str) -> dict:
    commit = checked_sha(
        api.request(f"/repos/{repository}/commits/dev").get("sha"), "Development source"
    )
    frontend = repository == FRONTEND
    filename = "package.json" if frontend else "pyproject.toml"
    version = project_version(source_file(api, repository, commit, filename), frontend)
    return identity(repository, "dev", commit, version)


def release_identity(api: GitHub, repository: str, metadata: dict) -> dict:
    if repository == BACKEND:
        selected = metadata["release"]
        version = stable_version(selected["version"])
        release = None
        for tag in (version, "v" + version):
            release = api.request(
                f"/repos/{repository}/releases/tags/{quote(tag, safe='')}",
                missing_ok=True,
            )
            if release is not None:
                break
        if release is None:
            raise SyncError("The documented stable backend has no published release.")
    else:
        release = api.request(f"/repos/{repository}/releases/latest")
    if release.get("draft") or release.get("prerelease"):
        raise SyncError("Media release sources must be published stable releases.")
    tag = release.get("tag_name")
    version = stable_version(tag)
    commit = release_commit(api, tag, repository)
    if repository == BACKEND and (
        version != stable_version(metadata["release"]["version"])
        or commit != checked_sha(metadata["release"]["source"], "Documented release")
    ):
        raise SyncError(
            "The documented backend tag moved; media promotion requires review."
        )
    filename = "package.json" if repository == FRONTEND else "pyproject.toml"
    if (
        project_version(
            source_file(api, repository, commit, filename), repository == FRONTEND
        )
        != version
    ):
        raise SyncError("The release tag and package version disagree.")
    return identity(repository, tag, commit, version, tag)


def discover(
    root: Path, api: GitHub, docs_head: str, channels: list[str], force=False
) -> dict:
    metadata = load(root / "docs-versions.json")
    reviewed_metadata = (
        proposal(metadata, docs_head, api) if "release" in channels else metadata
    )
    existing = load(root / CATALOG) if (root / CATALOG).exists() else {}
    selected = {}
    hashes = fingerprints(root)
    for channel in channels:
        pair = {
            kind: (
                release_identity(api, repository, reviewed_metadata)
                if channel == "release"
                else branch_identity(api, repository)
            )
            for kind, repository in (("frontend", FRONTEND), ("backend", BACKEND))
        }
        pair.update(hashes)
        old = existing.get("channels", {}).get(channel, {})
        if (
            force
            or (channel == "release" and reviewed_metadata != metadata)
            or any(old.get(key) != value for key, value in pair.items())
        ):
            selected[channel] = pair
    return {
        "schema_version": 1,
        "docs_head": checked_sha(docs_head, "Documentation source"),
        "docs_versions": reviewed_metadata,
        "channels": selected,
    }


class StaticCapabilities:
    """A deliberately small AST reader; unsupported expressions stay unknown."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.modules = {}
        self.read_files = {}
        self.active = set()

    def module(self, name: str):
        if not re.fullmatch(r"(?:api|utils)(?:\.[a-zA-Z_][a-zA-Z_0-9]*)+", name):
            raise ValueError("External or unsafe module")
        if name not in self.modules:
            path = self.root.joinpath(*name.split(".")).with_suffix(".py")
            if path.is_symlink() or self.root not in path.resolve().parents:
                raise ValueError("Unsafe source path")
            data = path.read_bytes()
            if len(data) > 2 * 1024 * 1024:
                raise ValueError("Source file too large")
            self.read_files[path.relative_to(self.root).as_posix()] = digest(data)
            self.modules[name] = ast.parse(data)
        return self.modules[name]

    def name(self, name: str, module: str):
        key = (module, name)
        if key in self.active or len(self.active) > 16:
            raise ValueError("Recursive static value")
        self.active.add(key)
        try:
            tree = self.module(module)
            for node in tree.body:
                if isinstance(node, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == name for t in node.targets
                ):
                    return self.value(node.value, module)
                if (
                    isinstance(node, ast.AnnAssign)
                    and isinstance(node.target, ast.Name)
                    and node.target.id == name
                ):
                    return self.value(node.value, module)
                if isinstance(node, ast.ImportFrom) and node.level == 0:
                    for alias in node.names:
                        if (alias.asname or alias.name) == name:
                            return self.name(alias.name, node.module)
            raise ValueError("No static binding")
        finally:
            self.active.remove(key)

    def value(self, node, module: str):
        if isinstance(node, ast.Constant) and isinstance(
            node.value, (str, bool, int, float, type(None))
        ):
            return node.value
        if isinstance(node, ast.Name):
            return self.name(node.id, module)
        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            values = [self.value(item, module) for item in node.elts]
            return set(values) if isinstance(node, ast.Set) else values
        if isinstance(node, ast.Dict):
            # Only keys are needed for the sorted service-key capabilities.
            return {self.value(key, module): None for key in node.keys}
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            return set(self.value(node.left, module)) | set(
                self.value(node.right, module)
            )
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in {"set", "frozenset", "sorted", "list", "tuple"}
            and len(node.args) == 1
            and not node.keywords
        ):
            value = self.value(node.args[0], module)
            return sorted(value) if node.func.id == "sorted" else set(value)
        raise ValueError("Runtime expression is not a verified capability")

    def versioned(self, version: str) -> dict:
        module = "utils.infinidysk_v2_support"
        tree = self.module(module)
        functions = {
            node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)
        }
        # This reviewed adapter must fail if the application's admission semantics
        # change. It does not evaluate arbitrary Python from an upstream branch.
        expected = ast.parse("""def api_version_supported(version):
    if not isinstance(version, str):
        return False
    match = _STABLE_VERSION.fullmatch(version)
    if not match:
        return False
    numbers = tuple(map(int, match.groups()[:3]))
    return numbers > (2, 24, 0) or (numbers == (2, 24, 0) and match[4] is None)
""").body[0]
        if ast.dump(functions.get("api_version_supported")) != ast.dump(expected):
            raise ValueError(
                "InfiniDysk version admission changed; review the static adapter"
            )
        function = functions["versioned_capabilities"]
        if len(function.body) != 2 or not isinstance(function.body[0], ast.Assign):
            raise ValueError("Versioned capability shape changed")
        assignment = function.body[0]
        if ast.dump(assignment.value) != ast.dump(
            ast.parse("api_version_supported(version)", mode="eval").body
        ):
            raise ValueError("Versioned capability admission changed")
        result = function.body[1].value
        if not isinstance(result, ast.Dict):
            raise ValueError("Versioned capabilities must be a dictionary")
        supported = tuple(map(int, stable_version(version).split("."))) >= (2, 24, 0)
        values = {}
        for key, value in zip(result.keys, result.values):
            name = self.value(key, module)
            if isinstance(value, ast.Name) and value.id == "supported":
                values[name] = supported
            elif ast.dump(value) == ast.dump(
                ast.parse("str(version)", mode="eval").body
            ):
                values[name] = version
            else:
                values[name] = self.value(value, module)
        return values

    def extract(self, version: str) -> dict:
        module = "api.routers.process"
        functions = [
            node
            for node in self.module(module).body
            if isinstance(node, ast.AsyncFunctionDef)
            and node.name == "get_capabilities"
        ]
        if (
            len(functions) != 1
            or len(functions[0].body) != 1
            or not isinstance(functions[0].body[0], ast.Return)
        ):
            raise SyncError(
                "Backend capability endpoint changed; review the static adapter."
            )
        returned = functions[0].body[0].value
        if not isinstance(returned, ast.Dict):
            raise SyncError("Backend capabilities are no longer an explicit mapping.")
        values, unresolved = {}, []
        for key, expression in zip(returned.keys, returned.values):
            try:
                if key is None:
                    expected = ast.parse(
                        "versioned_capabilities(get_project_version(pyproject_file()))",
                        mode="eval",
                    ).body
                    if ast.dump(expression) != ast.dump(expected):
                        raise ValueError("Unknown capability expansion")
                    values.update(self.versioned(version))
                else:
                    name = self.value(key, module)
                    value = self.value(expression, module)
                    if isinstance(value, set):
                        value = sorted(value)
                    values[name] = value
            except (ValueError, KeyError, OSError, TypeError, AttributeError):
                if key is None:
                    raise SyncError(
                        "Versioned backend capabilities changed; review is required."
                    ) from None
                unresolved.append(
                    key.value if isinstance(key, ast.Constant) else "unknown-key"
                )
        values.setdefault("api_version", version)
        return {
            "capabilities": values,
            "unresolved_capabilities": sorted(unresolved),
            "capability_source_sha256": canonical_hash(self.read_files),
        }


def check_tree(root: Path, source: dict, frontend: bool) -> None:
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    if result.stdout.strip() != source["commit"]:
        raise SyncError(
            "The checked-out application does not match its immutable source pin."
        )
    filename = "package.json" if frontend else "pyproject.toml"
    if project_version((root / filename).read_bytes(), frontend) != source["version"]:
        raise SyncError(
            "The checked-out package version does not match its source pin."
        )


def make_plan(
    root: Path, selection: dict, channel: str, backend_root: Path, frontend_root: Path
) -> dict:
    pair = selection["channels"][channel]
    if any(pair.get(key) != value for key, value in fingerprints(root).items()):
        raise SyncError(
            "Media tooling changed after source selection; replan the capture."
        )
    check_tree(backend_root, pair["backend"], False)
    check_tree(frontend_root, pair["frontend"], True)
    snapshot = StaticCapabilities(backend_root).extract(pair["backend"]["version"])
    catalog = load(root / TOOLS / "capture-catalog.json")
    required, unavailable = [], {}
    for row in catalog["scenarios"]:
        gates = row.get("required_capabilities", [])
        if any(
            key in snapshot["unresolved_capabilities"]
            for key in [*gates, *row.get("required_protocols", {})]
        ):
            raise SyncError(
                "A required scenario depends on an unresolved backend capability."
            )
        applicable = all(snapshot["capabilities"].get(key) is True for key in gates)
        for key, value in row.get("required_protocols", {}).items():
            applicable = applicable and snapshot["capabilities"].get(key) == value
        missing = frontend_absence(frontend_root, row)
        if missing:
            unavailable[row["id"]] = missing
            applicable = False
        if applicable and not row.get("optional_for_automation", False):
            required.append(row["id"])
    plan = {
        "schema_version": 1,
        "channel": channel,
        **pair,
        **snapshot,
        "scenarios": [row["id"] for row in catalog["scenarios"]],
        "required_scenarios": required,
        "themes": ["dark", "light"],
        "frontend_unavailable_scenarios": unavailable,
        "native_apps": native_app_pins(root, catalog),
        "frontend_inventory": frontend_inventory(frontend_root, catalog),
    }
    plan["plan_sha256"] = canonical_hash(plan)
    return plan


def native_app_pins(root: Path, catalog: dict) -> dict:
    prerequisites = {
        name
        for row in catalog["scenarios"]
        for name in row.get("required_prerequisites", [])
    }
    if not prerequisites:
        return {}
    if prerequisites != {"sonarr"}:
        raise SyncError(
            "A native capture prerequisite needs a reviewed isolated fixture."
        )
    path = root / TOOLS / "demo-service.py"
    if path.is_symlink():
        raise SyncError("Native fixture pin source may not be a symbolic link.")
    constants = {}
    for node in ast.parse(path.read_bytes()).body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    constants[target.id] = node.value.value
    image, version = constants.get("IMAGE"), constants.get("SONARR_VERSION")
    if (
        not isinstance(image, str)
        or not re.fullmatch(r"lscr\.io/linuxserver/sonarr@sha256:[0-9a-f]{64}", image)
        or not isinstance(version, str)
        or not re.fullmatch(r"\d+\.\d+\.\d+\.\d+", version)
    ):
        raise SyncError(
            "Native Sonarr capture requires an exact official image and application version pin."
        )
    return {"sonarr": {"application": "Sonarr", "image": image, "version": version}}


def frontend_absence(root: Path, scenario: dict) -> str | None:
    """Only immutable source omissions qualify; browser failures never do."""
    for filename in scenario.get("required_frontend_files", []):
        relative = PurePosixPath(filename)
        if relative.is_absolute() or ".." in relative.parts:
            raise SyncError("Unsafe frontend applicability source path.")
        path = root / filename
        if path.is_symlink():
            raise SyncError("Frontend applicability source may not be a symbolic link.")
        if not path.is_file():
            return "Selected frontend source does not contain " + filename
    if scenario.get("settings_section"):
        filename = scenario.get("settings_source", "pages/settings.vue")
        relative = PurePosixPath(filename)
        if relative.is_absolute() or ".." in relative.parts:
            raise SyncError("Unsafe settings applicability source path.")
        path = root / filename
        if not path.is_file() or path.is_symlink():
            return (
                "Selected frontend source does not contain its Settings section source"
            )
        section = re.escape(scenario["settings_section"])
        if not re.search(
            r"(?:section-id|id)\s*=\s*[\"\x27]" + section + r"[\"\x27]",
            path.read_text(),
        ):
            return (
                "Selected frontend source does not contain Settings section "
                + scenario["settings_section"]
            )
    return None


def frontend_inventory(root: Path, catalog: dict) -> dict:
    """Require a catalog decision for every actual route and Settings section."""
    pages = {
        path.relative_to(root).as_posix(): path
        for path in (root / "pages").rglob("*.vue")
    }
    if not pages or any(path.is_symlink() for path in pages.values()):
        raise SyncError(
            "Frontend route inventory is missing or contains symbolic links."
        )
    mapped = {filename: [] for filename in pages}
    for scenario in catalog["scenarios"]:
        route = unquote(urlsplit(scenario["route"]).path).strip("/")
        if route.startswith("services/"):
            candidates = ["pages/services/[serviceId]/index.vue"]
        elif not route:
            candidates = ["pages/index.vue"]
        else:
            candidates = [f"pages/{route}.vue", f"pages/{route}/index.vue"]
        for filename in candidates:
            if filename in mapped:
                mapped[filename].append(scenario["id"])
    exclusions = {}
    for row in catalog.get("excluded_frontend_pages", []):
        filename, reason = row.get("path"), row.get("reason")
        if filename not in pages or not isinstance(reason, str) or not reason.strip():
            raise SyncError(
                "Frontend page exclusion needs an existing page and a review reason."
            )
        text = re.sub(r"<!--[\s\S]*?-->", "", pages[filename].read_text())
        blocks = re.findall(r"<(script|template|style)\b[^>]*>([\s\S]*?)</\1>", text)
        remainder = re.sub(r"<(script|template|style)\b[^>]*>[\s\S]*?</\1>", "", text)
        if not blocks or any(body.strip() for _, body in blocks) or remainder.strip():
            raise SyncError(
                "An excluded frontend template gained content; review its capture coverage."
            )
        exclusions[filename] = reason
    unknown = sorted(
        filename
        for filename, scenarios in mapped.items()
        if not scenarios and filename not in exclusions
    )
    if unknown:
        raise SyncError(
            "Frontend has uncatalogued pages; add capture coverage: "
            + ", ".join(unknown)
        )
    known_sections = {}
    for scenario in catalog["scenarios"]:
        route = urlsplit(scenario["route"])
        section = scenario.get("settings_section") or (
            route.fragment if route.path == "/settings" else None
        )
        if section:
            key = (scenario.get("settings_source", "pages/settings.vue"), section)
            known_sections.setdefault(key, []).append(scenario["id"])
    sections = []
    for directory in (root / "pages", root / "components"):
        for path in sorted(directory.rglob("*.vue")):
            if path.is_symlink():
                raise SyncError(
                    "Frontend Settings inventory may not follow symbolic links."
                )
            filename = path.relative_to(root).as_posix()
            for attrs in re.findall(r"<SettingsSection\b([\s\S]*?)>", path.read_text()):
                match = re.search(
                    r"(?<!:)\bsection-id\s*=\s*['\"]([^'\"]+)['\"]", attrs
                )
                if not match or (filename, match[1]) not in known_sections:
                    raise SyncError(
                        "Frontend has an uncatalogued Settings section; review capture coverage: "
                        + filename
                        + ("#" + match[1] if match else " (dynamic section)")
                    )
                sections.append(
                    {
                        "path": filename,
                        "id": match[1],
                        "scenarios": known_sections[(filename, match[1])],
                    }
                )
    return {
        "pages": [
            {
                "path": filename,
                "sha256": digest(path.read_bytes()),
                "scenarios": mapped[filename],
            }
            for filename, path in sorted(pages.items())
            if filename not in exclusions
        ],
        "excluded_pages": [
            {
                "path": filename,
                "sha256": digest(pages[filename].read_bytes()),
                "reason": reason,
            }
            for filename, reason in sorted(exclusions.items())
        ],
        "settings_sections": sections,
    }


def safe_file(directory: Path, relative: str) -> Path:
    if not isinstance(relative, str) or "\\" in relative or "\x00" in relative:
        raise SyncError("Unsafe media artifact path.")
    parts = PurePosixPath(relative)
    if (
        parts.is_absolute()
        or not parts.parts
        or any(part in {".", ".."} for part in parts.parts)
        or parts.as_posix() != relative
    ):
        raise SyncError("Unsafe media artifact path.")
    path = directory
    for part in parts.parts:
        path = path / part
        if path.is_symlink():
            raise SyncError("Media artifacts may not contain symbolic links.")
    if not path.is_file():
        raise SyncError("A listed media artifact is missing or is not a regular file.")
    return path


def verify_package(root: Path, plan: dict, directory: Path, showcase=False) -> dict:
    if directory.is_symlink():
        raise SyncError("Media package must be a real directory.")
    manifest = load(safe_file(directory, "manifest.json"))
    if manifest.get("schema_version") != 2 or manifest.get("complete") is not True:
        raise SyncError("Only completed schema2 media packages can be accepted.")
    try:
        captured_at = manifest["captured_at"]
        if (
            not isinstance(captured_at, str)
            or "T" not in captured_at
            or datetime.fromisoformat(captured_at.replace("Z", "+00:00")).utcoffset()
            is None
        ):
            raise ValueError
    except (KeyError, TypeError, ValueError):
        raise SyncError(
            "Media package requires a valid ISO capture timestamp with a timezone."
        ) from None
    for key in (
        "channel",
        "frontend",
        "backend",
        "plan_sha256",
        "catalog_sha256",
        "dataset_sha256",
        "tooling_sha256",
    ):
        if manifest.get(key) != plan.get(key):
            raise SyncError(f"Media package has a mismatched {key}.")
    for key in ("errors", "blocked_requests", "unexpected_fixture_requests"):
        if manifest.get(key, []) != []:
            raise SyncError("Media package contains unresolved capture errors.")
    rows = manifest.get("files")
    if not isinstance(rows, list) or not rows:
        raise SyncError("Media package has no artifact inventory.")
    inventory, total = {}, 0
    for row in rows:
        filename = row.get("path")
        path = safe_file(directory, filename)
        size = path.stat().st_size
        if not 0 < size <= MAX_FILE or size != row.get("bytes"):
            raise SyncError("Media artifact exceeds its budget or recorded size.")
        data = path.read_bytes()
        if digest(data) != row.get("sha256") or filename in inventory:
            raise SyncError("Media artifact hash is wrong or its path is duplicated.")
        suffix = path.suffix
        magic_ok = {
            ".webp": data[:4] == b"RIFF" and data[8:12] == b"WEBP",
            ".webm": data[:4] == b"\x1aE\xdf\xa3",
            ".mp4": len(data) > 12 and data[4:8] == b"ftyp",
            ".vtt": data.startswith(b"WEBVTT"),
            ".txt": b"\x00" not in data,
            ".json": False,
        }.get(suffix, False)
        if not magic_ok:
            raise SyncError("Unsupported media artifact format or file signature.")
        inventory[filename] = row
        total += size
    if total > MAX_PACKAGE:
        raise SyncError("Media package exceeds its total asset budget.")
    actual = {
        path.relative_to(directory).as_posix()
        for path in directory.rglob("*")
        if path.is_file() or path.is_symlink()
    }
    if actual != set(inventory) | {"manifest.json"}:
        raise SyncError("Media package contains unlisted files.")
    for row in rows:
        if row.get("poster") and row["poster"] not in inventory:
            raise SyncError("A video poster is absent from the package inventory.")
    if showcase:
        verify_showcase(root, plan, manifest)
        return manifest
    if manifest.get("coverage_complete") is not True:
        raise SyncError("Partial capture coverage cannot enter a media refresh PR.")
    catalog = load(root / TOOLS / "capture-catalog.json")
    coverage = manifest.get("coverage")
    if not isinstance(coverage, list):
        raise SyncError("Media package has no scenario coverage report.")
    indexed = {}
    for row in coverage:
        key = (row.get("id"), row.get("theme"))
        if key in indexed:
            raise SyncError("Duplicate scenario coverage row.")
        indexed[key] = row
    if any(
        row.get("id") == "embedded-sonarr" and row.get("status") == "captured"
        for row in coverage
    ):
        expected_app = plan.get("native_apps", {}).get("sonarr")
        observed = manifest.get("native_app_observations", {}).get("sonarr", {})
        if (
            not expected_app
            or manifest.get("native_apps") != plan["native_apps"]
            or observed.get("verified") is not True
            or any(
                observed.get(key) != expected_app.get(key)
                for key in ("application", "version", "image")
            )
        ):
            raise SyncError(
                "Embedded Sonarr lacks a verified observation matching the pinned native application."
            )
    expected = {
        (scenario, theme) for scenario in plan["scenarios"] for theme in plan["themes"]
    }
    if set(indexed) != expected:
        raise SyncError("Capture coverage does not cover the entire planned catalog.")
    for scenario in catalog["scenarios"]:
        for theme in plan["themes"]:
            row = indexed[(scenario["id"], theme)]
            required = scenario["id"] in plan["required_scenarios"]
            if row.get("required") is not required:
                raise SyncError(
                    "Scenario coverage changed its required audience contract."
                )
            if row.get("status") == "captured":
                files = row.get("artifacts", [])
                if not files or any(name not in inventory for name in files):
                    raise SyncError(
                        "Captured scenario is missing its inventoried artifacts."
                    )
                kinds = {
                    inventory[name].get("kind")
                    for name in files
                    if inventory[name].get("scenario") == scenario["id"]
                    and inventory[name].get("theme") == theme
                }
                if kinds != set(scenario["kinds"]):
                    raise SyncError(
                        "A captured scenario is missing a required still or clip."
                    )
            elif row.get("status") in {"blocked", "skipped"}:
                if required or not row.get("reason") or row.get("artifacts") != []:
                    raise SyncError(
                        "A required scenario was blocked, skipped or fabricated."
                    )
                unavailable = any(
                    plan["capabilities"].get(key) is not True
                    for key in scenario.get("required_capabilities", [])
                )
                unavailable = (
                    unavailable
                    or any(
                        plan["capabilities"].get(key) != value
                        for key, value in scenario.get("required_protocols", {}).items()
                    )
                    or scenario["id"] in plan.get("frontend_unavailable_scenarios", {})
                )
                optional = scenario.get("optional_for_automation") and scenario.get(
                    "required_prerequisites"
                )
                if not unavailable and not (optional and row["status"] == "blocked"):
                    raise SyncError(
                        "A noncaptured scenario has no verified capability or prerequisite reason."
                    )
            else:
                raise SyncError("Unknown scenario coverage status.")
    return manifest


def verify_showcase(root: Path, plan: dict, manifest: dict) -> None:
    scene_path = root / TOOLS / "showcase-scenes.json"
    scenes = load(scene_path)
    duration = scenes.get("duration_seconds")
    if manifest.get("themes") != plan["themes"] or set(plan["themes"]) != {
        "dark",
        "light",
    }:
        raise SyncError("Showcase must cover both planned appearance themes.")
    if (
        not isinstance(duration, (int, float))
        or not 20 <= duration <= 30
        or manifest.get("duration_seconds") != duration
        or manifest.get("scenes") != scenes.get("scenes")
        or manifest.get("showcase_plan_sha256") != digest(scene_path.read_bytes())
    ):
        raise SyncError(
            "Showcase does not match its supported scene plan and duration."
        )
    if manifest.get("viewport") != {"width": 1920, "height": 1280}:
        raise SyncError(
            "Showcase frame must preserve the supported 1920 by 1280 viewport."
        )
    indexed = {}
    for row in manifest["files"]:
        key = (row.get("theme"), row.get("role"))
        if key in indexed:
            raise SyncError("Showcase contains an ambiguous theme or track role.")
        indexed[key] = row
    expected = {
        (theme, role)
        for theme in plan["themes"]
        for role in ("video", "poster", "animated")
    } | {(None, role) for role in ("captions", "chapters", "transcript")}
    if set(indexed) != expected:
        raise SyncError("Showcase is missing a theme role or accessible text track.")
    for (theme, role), row in indexed.items():
        if theme:
            viewport = (
                {"width": 1280, "height": 854}
                if role == "animated"
                else manifest["viewport"]
            )
            if (
                row.get("kind") != ("video" if role == "video" else "image")
                or row.get("viewport") != viewport
                or (role == "video" and row.get("duration_seconds") != duration)
            ):
                raise SyncError(
                    "Showcase artifact kind, frame or duration is inconsistent."
                )
        elif row.get("kind") != "text" or not row["path"].endswith(
            ".txt" if role == "transcript" else ".vtt"
        ):
            raise SyncError("Showcase accessible text track has the wrong format.")


def verify_pair(package: dict, showcase: dict, package_path: Path) -> None:
    if showcase["captured_at"] != package["captured_at"]:
        raise SyncError("Frontend and showcase capture timestamps disagree.")
    if showcase.get("input_package_manifest_sha256") != digest(
        package_path.read_bytes()
    ):
        raise SyncError(
            "Showcase was not generated from the accepted frontend package."
        )


def validate_channel(root: Path, channel_name: str, channel_config: dict) -> dict:
    """Validate an accepted channel offline; return manifests for the renderer.

    No live upstream lookup occurs during frozen documentation builds. Freshness
    against moving branches is a responsibility of the refresh workflow.
    """
    if channel_name not in CHANNELS:
        raise SyncError("Unknown frontend media channel.")
    plan = channel_config.get("plan")
    if not isinstance(plan, dict) or plan.get("channel") != channel_name:
        raise SyncError("Accepted frontend media has no matching capture plan.")
    unsigned = {key: value for key, value in plan.items() if key != "plan_sha256"}
    if plan.get("plan_sha256") != canonical_hash(unsigned):
        raise SyncError("Accepted frontend capture plan has an invalid digest.")
    for key in ("frontend", "backend", "plan_sha256", *fingerprints(root)):
        if channel_config.get(key) != plan.get(key):
            raise SyncError("Accepted frontend media catalog and plan disagree.")
    for key, value in fingerprints(root).items():
        if plan.get(key) != value:
            raise SyncError(
                "Frontend capture tooling changed; regenerate media before publication."
            )
    result = {"plan": plan}
    for key, showcase in (("package", False), ("showcase", True)):
        filename = channel_config.get(key + "_manifest")
        required_prefix = f"docs/assets/images/guides/{'showcase' if showcase else 'frontend'}/channels/{channel_name}/"
        if (
            not isinstance(filename, str)
            or not filename.startswith(required_prefix)
            or not filename.endswith("/manifest.json")
        ):
            raise SyncError(
                "Accepted frontend media catalog points outside its channel assets."
            )
        manifest_path = safe_file(root, filename)
        result[key] = verify_package(root, plan, manifest_path.parent, showcase)
        result[key + "_path"] = manifest_path
    verify_pair(result["package"], result["showcase"], result["package_path"])
    return result


def apply_packages(
    root: Path, selection: dict, artifacts: Path, api: GitHub, expected_head: str
) -> dict:
    if selection.get("docs_head") != checked_sha(expected_head, "Expected docs source"):
        raise SyncError("The refresh selection belongs to another docs commit.")
    assert_current(api, expected_head)
    current = discover(
        root, api, expected_head, list(selection["channels"]), force=True
    )
    if current != selection:
        raise SyncError(
            "Application source or capture tooling changed during the refresh; replan."
        )
    catalog = (
        load(root / CATALOG)
        if (root / CATALOG).exists()
        else {"schema_version": 1, "channels": {}}
    )
    proposed = copy.deepcopy(catalog)
    packages = []
    for channel, pair in selection["channels"].items():
        directory = artifacts / channel
        plan = load(safe_file(directory, "plan.json"))
        unsigned = {key: value for key, value in plan.items() if key != "plan_sha256"}
        if (
            plan.get("plan_sha256") != canonical_hash(unsigned)
            or any(plan.get(key) != value for key, value in pair.items())
            or plan.get("channel") != channel
        ):
            raise SyncError(
                "Downloaded capture plan does not match the trusted selection."
            )
        revision = digest(
            (directory / "frontend" / "manifest.json").read_bytes()
            + (directory / "showcase" / "manifest.json").read_bytes()
        )[:12]
        pair_id = (
            pair["backend"]["commit"][:12]
            + "-"
            + pair["frontend"]["commit"][:12]
            + "-"
            + revision
        )
        record = {**pair, "plan_sha256": plan["plan_sha256"], "plan": plan}
        for kind, subtree in (("frontend", "frontend"), ("showcase", "showcase")):
            source = directory / kind
            manifest = verify_package(root, plan, source, showcase=kind == "showcase")
            destination = (
                f"docs/assets/images/guides/{subtree}/channels/{channel}/{pair_id}"
            )
            if kind == "frontend":
                record["package_manifest"] = destination + "/manifest.json"
            else:
                record["showcase_manifest"] = destination + "/manifest.json"
            packages.append((source, root / destination, manifest))
        verify_pair(
            packages[-2][2], packages[-1][2], directory / "frontend/manifest.json"
        )
        proposed.setdefault("channels", {})[channel] = record
    # Everything is validated before any accepted asset or catalog is written.
    assert_current(api, expected_head)
    for source, destination, manifest in packages:
        if destination.is_symlink():
            raise SyncError("The media destination is a symbolic link.")
        destination.mkdir(parents=True, exist_ok=True)
        for filename in ["manifest.json", *(row["path"] for row in manifest["files"])]:
            target = destination / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.is_symlink():
                raise SyncError("The media destination contains a symbolic link.")
            shutil.copyfile(source / filename, target)
    dump(root / CATALOG, proposed)
    if selection["docs_versions"] != load(root / "docs-versions.json"):
        dump(root / "docs-versions.json", selection["docs_versions"])
    return proposed


def refresh_report(selection: dict) -> str:
    lines = [
        "Captures the actual packaged frontends against isolated public example data.",
        "",
        "| Channel | DUMB backend | Frontend |",
        "| --- | --- | --- |",
    ]
    for channel, pair in selection["channels"].items():
        backend, frontend = pair["backend"], pair["frontend"]
        lines.append(
            f"| {channel} | {backend['version']} (`{backend['commit'][:12]}`) | {frontend['version']} (`{frontend['commit'][:12]}`) |"
        )
    lines.extend(
        [
            "",
            "The committed media catalog contains exact source pins, complete capture plans, tooling/data fingerprints and scenario/theme coverage. All packaged assets were checked against their hashes and required still/clip inventory.",
            "",
            "Review both channel galleries, the homepage showcase, captions and example-data scope. A screenshot establishes the displayed frontend; example responses do not establish real provider, installation, backup or playback success.",
            "",
            "This PR is not approved or merged automatically. Development prose pins stay unchanged. Any included stable channel promotion passed the existing reviewed-version, ancestry and independently released frontend checks, and its media was regenerated together. Accepted changes use the existing docs release, Pages and Discord pipeline.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    commands = parser.add_subparsers(dest="command", required=True)
    discovery = commands.add_parser("discover")
    discovery.add_argument("--channels", choices=("both", *CHANNELS), default="both")
    discovery.add_argument("--docs-head", required=True)
    discovery.add_argument("--out", type=Path, required=True)
    discovery.add_argument("--force", action="store_true")
    planning = commands.add_parser("plan")
    planning.add_argument("--selection", type=Path, required=True)
    planning.add_argument("--channel", choices=CHANNELS, required=True)
    planning.add_argument("--backend-root", type=Path, required=True)
    planning.add_argument("--frontend-root", type=Path, required=True)
    planning.add_argument("--out", type=Path, required=True)
    verification = commands.add_parser("verify")
    verification.add_argument("--plan", type=Path, required=True)
    verification.add_argument("--package", type=Path, required=True)
    verification.add_argument("--showcase", action="store_true")
    applying = commands.add_parser("apply")
    applying.add_argument("--selection", type=Path, required=True)
    applying.add_argument("--artifacts", type=Path, required=True)
    applying.add_argument("--expected-head", required=True)
    applying.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    try:
        api = GitHub(os.environ.get("GITHUB_TOKEN"))
        if args.command == "discover":
            channels = list(CHANNELS) if args.channels == "both" else [args.channels]
            selection = discover(args.root, api, args.docs_head, channels, args.force)
            dump(args.out, selection)
            matrix = {
                "include": [
                    {
                        "channel": channel,
                        "frontend_commit": pair["frontend"]["commit"],
                        "backend_commit": pair["backend"]["commit"],
                    }
                    for channel, pair in selection["channels"].items()
                ]
            }
            write_outputs(
                {
                    "changed": str(bool(selection["channels"])).lower(),
                    "matrix": json.dumps(matrix, separators=(",", ":")),
                }
            )
            print(
                json.dumps(
                    {
                        "changed_channels": list(selection["channels"]),
                        "docs_head": args.docs_head,
                    }
                )
            )
            if os.environ.get("GITHUB_STEP_SUMMARY"):
                Path(os.environ["GITHUB_STEP_SUMMARY"]).write_text(
                    refresh_report(selection)
                    if selection["channels"]
                    else "Both accepted frontend media channels match their selected source pins and capture tooling. No recapture is needed.\n"
                )
        elif args.command == "plan":
            dump(
                args.out,
                make_plan(
                    args.root,
                    load(args.selection),
                    args.channel,
                    args.backend_root,
                    args.frontend_root,
                ),
            )
        elif args.command == "verify":
            verify_package(args.root, load(args.plan), args.package, args.showcase)
            print("Verified complete source-pinned media package.")
        else:
            selection = load(args.selection)
            apply_packages(
                args.root, selection, args.artifacts, api, args.expected_head
            )
            if args.report:
                args.report.write_text(refresh_report(selection))
            print(
                "Staged validated media and source pins for review; nothing was published."
            )
    except (
        SyncError,
        OSError,
        KeyError,
        ValueError,
        subprocess.CalledProcessError,
    ) as error:
        print(f"Frontend media refresh stopped: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

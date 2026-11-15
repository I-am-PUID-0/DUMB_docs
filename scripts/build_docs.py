#!/usr/bin/env python3
"""Build frozen release docs and current development docs as one Pages artifact."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MARKER = re.compile(r"<!-- (dev|release):(start|end) -->")


def filter_content(text: str, include_development: bool) -> str:
    """Select complete channel blocks; reject nested or incomplete blocks."""
    parts: list[str] = []
    cursor = 0
    active: str | None = None
    for marker in MARKER.finditer(text):
        channel, action = marker.groups()
        if action == "start":
            if active is not None:
                raise ValueError("Channel blocks cannot nest")
            parts.append(text[cursor : marker.start()])
            active = channel
        else:
            if active != channel:
                raise ValueError(f"Unmatched {channel}:end marker")
            if (channel == "dev") == include_development:
                parts.append(text[cursor : marker.start()])
            active = None
        cursor = marker.end()
    if active:
        raise ValueError(f"Unclosed {active}:start marker")
    parts.append(text[cursor:])
    return "".join(parts)


def frontmatter(text: str) -> dict:
    if text.startswith("---\n"):
        return yaml.safe_load(text.split("---\n", 2)[1]) or {}
    return {}


def filter_nav(items: list, available: set[str]) -> list:
    result = []
    for item in items:
        if isinstance(item, str):
            if item in available or item.startswith("https://"):
                result.append(item)
            continue
        for label, value in item.items():
            if isinstance(value, list):
                children = filter_nav(value, available)
                if children:
                    result.append({label: children})
            elif value in available or str(value).startswith("https://"):
                result.append({label: value})
    return result


def markdown_url(path: Path) -> str:
    value = path.as_posix()
    return (
        value.removesuffix("index.md")
        if path.name == "index.md"
        else value.removesuffix(".md") + "/"
    )


def validate_output(output: Path, root: Path = ROOT) -> None:
    """Only replace known generated output, never authored or repository state."""
    output = output.resolve()
    root = root.resolve()
    if root.is_relative_to(output) or (
        output.is_relative_to(root) and output != root / "site"
    ):
        raise ValueError("In-repository output must be the generated site directory")
    if output != root / "site" and output.exists() and any(output.iterdir()):
        if not (output / ".dumb-docs-output").is_file():
            raise ValueError(
                "External output must be empty or marked .dumb-docs-output"
            )


def snapshot(ref: str, destination: Path) -> str:
    """Read only committed docs paths; never change the user's branch/index."""
    destination.mkdir(parents=True)
    if ref == "WORKTREE":
        shutil.copytree(ROOT / "docs", destination / "docs")
        return (ROOT / "mkdocs.yml").read_text()
    if not re.fullmatch(r"[0-9a-f]{40}", ref):
        raise ValueError(
            "release.docs_ref must be an immutable 40-character commit SHA"
        )
    listing = subprocess.check_output(
        ["git", "ls-tree", "-rz", "--name-only", ref, "--", "docs"], cwd=ROOT
    )
    for raw in listing.split(b"\0"):
        if not raw:
            continue
        relative = Path(raw.decode())
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(
            subprocess.check_output(
                ["git", "show", f"{ref}:{relative.as_posix()}"], cwd=ROOT
            )
        )
    return subprocess.check_output(
        ["git", "show", f"{ref}:mkdocs.yml"], cwd=ROOT
    ).decode()


def apply_release_overrides(
    channel: str, version: str, docs: Path, root: Path | None = None
) -> list[str]:
    """Apply reviewed prose corrections to existing pages of one frozen release.

    The version directory mirrors ``docs/``. A complete preflight rejects new
    routes, assets, links, or escaping parents before any replacement is written.
    Development builds and other release versions never consume these files.
    """
    if channel != "release":
        return []
    if not re.fullmatch(
        r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)", version
    ):
        raise ValueError("Release override version must be plain stable SemVer")
    root = ROOT if root is None else root
    base = root / "release-overrides"
    selected = base / version
    if base.is_symlink() or selected.is_symlink():
        raise ValueError("Release override directories must not be symlinks")
    if not selected.exists():
        return []
    if not selected.is_dir():
        raise ValueError("Release override version must identify a directory")
    if docs.is_symlink() or not docs.is_dir():
        raise ValueError("Frozen documentation root must be a real directory")
    if base.exists() and not base.is_dir():
        raise ValueError("Release override root must identify a directory")
    document_root = docs.resolve()
    replacements: list[tuple[Path, str, str]] = []

    def inspect(directory: Path) -> None:
        for source in sorted(directory.iterdir()):
            if source.is_symlink():
                raise ValueError("Release overrides must not contain symlinks")
            relative = source.relative_to(selected)
            target = docs / relative
            if not target.resolve().is_relative_to(document_root):
                raise ValueError("Release override target escapes the frozen docs")
            if source.is_dir():
                if not target.is_dir() or target.is_symlink():
                    raise ValueError(
                        f"Release override directory is absent from snapshot: {relative}"
                    )
                inspect(source)
                continue
            if not source.is_file() or source.suffix != ".md":
                raise ValueError(
                    f"Release overrides may only replace Markdown pages: {relative}"
                )
            if not target.is_file() or target.is_symlink():
                raise ValueError(
                    f"Release override page is absent from snapshot: {relative}"
                )
            # Reject a symlink in any target parent, even when it resolves within
            # the document root. Overrides never adopt aliased output paths.
            for parent in target.parents:
                if parent == docs:
                    break
                if parent.is_symlink():
                    raise ValueError(
                        "Release override target parents must not be symlinks"
                    )
            replacements.append(
                (target, source.read_text(encoding="utf-8"), relative.as_posix())
            )

    inspect(selected)
    for target, text, _ in replacements:
        target.write_text(text, encoding="utf-8")
    return [relative for _, _, relative in replacements]


def build_channel(
    channel: str, metadata: dict, scratch: Path, output: Path, site_url: str
) -> list[str]:
    settings = metadata[channel]
    work = scratch / channel
    snapshot_config = snapshot(settings.get("docs_ref", "WORKTREE"), work)
    # Freeze prose/navigation while keeping dependency and theme configuration
    # aligned with the current shared templates and assets.
    config = (ROOT / "mkdocs.yml").read_text()
    destination = output
    output = work / "site"
    shutil.copytree(ROOT / "overrides", work / "overrides")
    docs = work / "docs"
    apply_release_overrides(channel, settings["version"], docs)
    include_dev = channel == "dev" or settings.get("include_development", False)
    unavailable: set[str] = set()
    pages = []
    text_pages: list[tuple[str, str, str]] = []
    for path in sorted(docs.rglob("*.md")):
        relative = path.relative_to(docs)
        text = path.read_text()
        meta = frontmatter(text)
        text = filter_content(text, include_dev)
        if meta.get("development_only") and not include_dev:
            unavailable.add(relative.as_posix())
            title = meta.get("title", relative.stem.replace("-", " ").title())
            # A real page preserves bookmarks and offers the exact dev destination.
            text = (
                "---\ntitle: " + json.dumps(str(title)) + "\n"
                "description: "
                + json.dumps(
                    f"Availability of {title} in the released DUMB documentation. Open the development guide for features that have not shipped yet."
                )
                + "\n"
                "icon: lucide/git-branch\nrelease_unavailable: true\nsearch:\n  exclude: true\n---\n\n"
                f"# {title}\n\n"
                f"This feature is not included in DUMB {metadata['release']['version']}.\n\n"
                f"[Read the development guide]({site_url}dev/{markdown_url(relative)})"
                "{ .md-button .md-button--primary }\n\n"
                "Use the documentation selector in the header to change channels. "
                "Check your DUMB image and API version before following development instructions.\n"
            )
        # Only the release owns robots.txt and the root sitemap reference.
        path.write_text(text)
        page_path = markdown_url(relative)
        pages.append(page_path)
        if relative.as_posix() not in unavailable:
            body = text.split("---\n", 2)[2] if text.startswith("---\n") else text
            text_pages.append(
                (str(meta.get("title", relative.stem)), page_path, body.strip())
            )

    # Shared UI fixes apply to both channels, independently of frozen prose.
    for directory in ("assets/css", "assets/js"):
        target = docs / directory
        shutil.rmtree(target, ignore_errors=True)
        shutil.copytree(ROOT / "docs" / directory, target)
    for image in ("logo.png", "favicon.ico", "DUMB.png", "DUMB.webp"):
        shutil.copy2(
            ROOT / "docs" / "assets/images" / image, docs / "assets/images" / image
        )
    if channel == "dev":
        (docs / "robots.txt").unlink(missing_ok=True)
    else:
        (docs / "robots.txt").write_text(
            f"User-agent: *\nAllow: /\n\nSitemap: {site_url}sitemap.xml\n"
        )

    raw_nav = yaml.load(snapshot_config, Loader=yaml.BaseLoader)["nav"]
    available = {
        p.relative_to(docs).as_posix() for p in docs.rglob("*.md")
    } - unavailable
    nav_text = yaml.safe_dump(
        {"nav": filter_nav(raw_nav, available)}, sort_keys=False, allow_unicode=True
    )
    config = re.sub(
        r"^nav:\n.*?(?=^theme:)", nav_text + "\n", config, flags=re.S | re.M
    )
    base_path = "../" if channel == "dev" else "./"
    extra = {
        "docs_channel": channel,
        "docs_version": settings["version"],
        "docs_release_version": metadata["release"]["version"],
        "docs_dev_version": metadata["dev"]["version"],
        "docs_root": base_path,
        "docs_release_pages": metadata.get("_release_pages", pages),
        "docs_dev_pages": metadata["_dev_pages"],
    }
    # Preserve extension Python tags as authored; don't evaluate YAML constructors here.
    config = config.replace(
        "extra:\n", yaml.safe_dump({"extra": extra}, sort_keys=False).rstrip() + "\n", 1
    )
    channel_url = site_url + ("dev/" if channel == "dev" else "")
    config = re.sub(
        r"^site_url:.*$", "site_url: " + json.dumps(channel_url), config, flags=re.M
    )
    config = re.sub(r"^  custom_dir:.*$", "  custom_dir: overrides", config, flags=re.M)
    config += "\ndocs_dir: docs\nsite_dir: site\n"
    config_path = work / "mkdocs.yml"
    config_path.write_text(config)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "zensical",
            "build",
            "--clean",
            "--strict",
            "--config-file",
            str(config_path),
        ],
        cwd=work,
        check=True,
    )
    if unavailable:
        sitemap = output / "sitemap.xml"
        tree = ET.parse(sitemap)
        namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        hidden_urls = {channel_url + markdown_url(Path(p)) for p in unavailable}
        for entry in list(tree.getroot()):
            if entry.findtext(namespace + "loc") in hidden_urls:
                tree.getroot().remove(entry)
        ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
        tree.write(sitemap, encoding="utf-8", xml_declaration=True)
        # Avoid retaining Zensical's pre-filter sitemap in compressed form.
        import gzip

        with gzip.open(output / "sitemap.xml.gz", "wb") as compressed:
            compressed.write(sitemap.read_bytes())
    intro = (
        f"# DUMB {settings['label']} documentation ({settings['version']})\n\n"
        f"> Channel: {channel}. Canonical base: {channel_url}\n\n"
        "DUMB coordinates media services. Match instructions to the installed backend version. "
        "Development guides can describe features absent from the latest release.\n\n"
    )
    (output / "llms.txt").write_text(
        intro
        + "## Documentation\n\n"
        + "\n".join(f"- [{title}]({channel_url}{url})" for title, url, _ in text_pages)
        + f"\n\nFull text: {channel_url}llms-full.txt\n"
    )
    (output / "llms-full.txt").write_text(
        intro
        + "\n\n---\n\n".join(
            f"Source: {channel_url}{url}\n\n{body}" for _, url, body in text_pages
        )
        + "\n"
    )
    (output / "channel.json").write_text(
        json.dumps(
            {"channel": channel, "version": settings["version"], "pages": pages},
            indent=2,
        )
        + "\n"
    )
    shutil.copytree(output, destination)
    return pages


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "site")
    parser.add_argument("--site-url", default="https://dumbarr.com/")
    args = parser.parse_args()
    output = args.output.resolve()
    try:
        validate_output(output)
    except ValueError as error:
        parser.error(str(error))
    metadata = json.loads((ROOT / "docs-versions.json").read_text())
    metadata["_dev_pages"] = [
        markdown_url(p.relative_to(ROOT / "docs"))
        for p in (ROOT / "docs").rglob("*.md")
    ]
    scratch = ROOT / ".docs-build"
    try:
        shutil.rmtree(scratch, ignore_errors=True)
        shutil.rmtree(output, ignore_errors=True)
        metadata["_release_pages"] = build_channel(
            "release", metadata, scratch, output, args.site_url.rstrip("/") + "/"
        )
        build_channel(
            "dev", metadata, scratch, output / "dev", args.site_url.rstrip("/") + "/"
        )
        (output / ".nojekyll").touch()
        (output / ".dumb-docs-output").touch()
        print(
            f"Built release {metadata['release']['version']} and development {metadata['dev']['version']} in {output}"
        )
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    main()

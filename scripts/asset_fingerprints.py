"""Give shared styles/scripts content-addressed URLs without rewriting YAML tags."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit

import yaml


def fingerprint_assets(config: str, docs: Path) -> str:
    """Copy local CSS/JS to hashed names in staged docs and update their entries.

    Original filenames remain available for older pages. YAML node offsets let
    us change only asset string tokens, leaving Python extension tags, comments,
    and every unrelated setting exactly as authored.
    """
    tree = yaml.compose(config, Loader=yaml.BaseLoader)
    if not isinstance(tree, yaml.MappingNode):
        return config
    root = docs.resolve()
    replacements: dict[tuple[int, int], str] = {}
    for key, values in tree.value:
        if key.value not in {"extra_css", "extra_javascript"} or not isinstance(
            values, yaml.SequenceNode
        ):
            continue
        for entry in values.value:
            if not isinstance(entry, yaml.ScalarNode):
                continue
            url = urlsplit(entry.value)
            if url.scheme or url.netloc or url.path.startswith("/"):
                continue
            local_path = unquote(url.path)
            relative = Path(local_path)
            if ".." in relative.parts or "\\" in local_path:
                raise ValueError("Shared assets must not traverse outside staged docs")
            source = docs / relative
            if not source.resolve().is_relative_to(root):
                raise ValueError("Shared asset resolves outside staged docs")
            if source.suffix not in {".css", ".js"} or not source.is_file():
                continue
            content = source.read_bytes()
            digest = hashlib.sha256(content).hexdigest()[:12]
            stem = re.sub(r"\.[0-9a-f]{12}$", "", source.stem)
            target = source.with_name(f"{stem}.{digest}{source.suffix}")
            if target != source:
                target.write_bytes(content)
            path = quote(target.relative_to(docs).as_posix(), safe="/")
            value = urlunsplit(("", "", path, url.query, url.fragment))
            replacements[(entry.start_mark.index, entry.end_mark.index)] = json.dumps(
                value
            )
    for (start, end), value in sorted(replacements.items(), reverse=True):
        config = config[:start] + value + config[end:]
    return config

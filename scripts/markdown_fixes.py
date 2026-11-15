"""Repair table row boundaries after documentation channel filtering.

Removing a channel marker or a row can leave blank lines in a Markdown table.
Python-Markdown ends the table at that gap and emits the remaining rows as
literal pipe-separated paragraphs. Join only matching continuation rows after
an established header and delimiter; leave prose, new tables, and code alone.
"""

from __future__ import annotations

import re

FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
DELIMITER = re.compile(r":?-{3,}:?\Z")


def table_cells(line: str) -> tuple[str, list[str]] | None:
    """Return indentation and pipe-delimited cells for an ordinary table row."""
    content = line.lstrip(" \t")
    indentation = line[: len(line) - len(content)]
    content = content.rstrip()
    if not content.startswith("|") or not content.endswith("|"):
        return None
    cells: list[str] = []
    start = 1
    index = 1
    while index < len(content):
        if content[index] == "`":
            opening = re.match(r"`+", content[index:]).group()
            closing = re.search(
                rf"(?<!`)`{{{len(opening)}}}(?!`)", content[index + len(opening) :]
            )
            if closing:
                # Zensical supports pipe characters inside code spans. They are
                # cell content, as in the rclone filtering regex examples.
                index += len(opening) + closing.end()
                continue
            index += len(opening)
            continue
        if content[index] != "|":
            index += 1
            continue
        preceding = 0
        cursor = index - 1
        while cursor >= 0 and content[cursor] == "\\":
            preceding += 1
            cursor -= 1
        if preceding % 2:
            index += 1
            continue
        cells.append(content[start:index].strip())
        start = index + 1
        index += 1
    if start != len(content) or not cells:
        return None
    return indentation, cells


def is_delimiter(row: tuple[str, list[str]] | None) -> bool:
    return bool(row and all(DELIMITER.fullmatch(cell) for cell in row[1]))


def repair_table_continuations(text: str) -> str:
    """Remove blank gaps only when they split rows of one existing table."""
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    fence: tuple[str, int] | None = None
    index = 0
    while index < len(lines):
        line = lines[index]
        marker = FENCE.match(line)
        if marker:
            value = marker.group(1)
            if fence is None:
                fence = value[0], len(value)
            elif value[0] == fence[0] and len(value) >= fence[1]:
                fence = None
            output.append(line)
            index += 1
            continue
        header = table_cells(line) if fence is None else None
        delimiter = table_cells(lines[index + 1]) if index + 1 < len(lines) else None
        if not (
            header
            and is_delimiter(delimiter)
            and header[0] == delimiter[0]
            and len(header[1]) == len(delimiter[1])
        ):
            output.append(line)
            index += 1
            continue
        output.extend(lines[index : index + 2])
        index += 2
        while index < len(lines):
            following = index
            while following < len(lines) and not lines[following].strip():
                following += 1
            row = table_cells(lines[following]) if following < len(lines) else None
            if not row or row[0] != header[0] or len(row[1]) != len(header[1]):
                break
            next_row = (
                table_cells(lines[following + 1])
                if following + 1 < len(lines)
                else None
            )
            if following > index and is_delimiter(next_row):
                # This is a separate complete table, not continuation data.
                break
            output.append(lines[following])
            index = following + 1
    return "".join(output)

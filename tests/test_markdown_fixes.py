"""Regressions for literal table rows caused by filtered channel blocks."""

import unittest

import markdown

from scripts.build_docs import filter_content
from scripts.markdown_fixes import repair_table_continuations, table_cells


class MarkdownTableTests(unittest.TestCase):
    def render(self, text):
        return markdown.markdown(text, extensions=["tables", "fenced_code"])

    def test_channel_rows_remain_in_one_table_in_both_channels(self):
        source = (
            "| Service | Role |\n|---|---|\n| Plex | Video |\n"
            "<!-- dev:start -->\n| Audiobookshelf | Books |\n<!-- dev:end -->\n"
            "| Seerr | Requests |\n"
        )
        for development in (False, True):
            with self.subTest(development=development):
                filtered = filter_content(source, development)
                self.assertIn("<p>|", self.render(filtered))
                fixed = self.render(repair_table_continuations(filtered))
                self.assertNotIn("<p>|", fixed)
                self.assertEqual(fixed.count("<table>"), 1)
                self.assertEqual(fixed.count("<tr>"), 4 if development else 3)
                self.assertEqual("Audiobookshelf" in fixed, development)

    def test_alternative_first_rows_and_blank_after_blocks(self):
        source = (
            "| Dependency | Startup |\n|---|---|\n"
            "<!-- dev:start -->\n| Battery | Detect layout |\n<!-- dev:end -->\n"
            "<!-- release:start -->\n| Battery | Start standalone |\n<!-- release:end -->\n\n"
            "| PostgreSQL | Start first |\n"
        )
        for development in (False, True):
            result = repair_table_continuations(filter_content(source, development))
            self.assertNotIn("<p>|", self.render(result))
            self.assertEqual(self.render(result).count("<tr>"), 3)

    def test_separate_complete_tables_stay_separate(self):
        source = "| First | Role |\n|---|---|\n| A | One |\n\n| Second | Port |\n|---|---|\n| B | Two |\n"
        self.assertEqual(repair_table_continuations(source), source)
        self.assertEqual(self.render(source).count("<table>"), 2)

    def test_fenced_examples_and_pipelines_are_preserved(self):
        for fence in ("```markdown", "~~~markdown", "    ```markdown"):
            closing = fence.replace("markdown", "")
            source = f"{fence}\n| Example | Value |\n|---|---|\n\n| A | B |\n{closing}\n\nUse `fresh | migrate` or `rclone | fuse`.\n"
            self.assertEqual(repair_table_continuations(source), source)

    def test_indented_table_context_and_prose_boundaries_are_preserved(self):
        source = "    | Item | Value |\n    |---|---|\n    | A | One |\n\n    | B | Two |\n\nNext paragraph.\n\n| C | Three |\n"
        result = repair_table_continuations(source)
        self.assertIn("    | A | One |\n    | B | Two |", result)
        self.assertTrue(result.endswith("\nNext paragraph.\n\n| C | Three |\n"))

    def test_escaped_pipe_is_a_cell_value(self):
        self.assertEqual(
            table_cells(r"| `a\|b` | Another |"), ("", [r"`a\|b`", "Another"])
        )
        source = "| Choice | Value |\n|---|---|\n| One | `a\\|b` |\n\n| Two | Other |\n"
        result = self.render(repair_table_continuations(source))
        self.assertNotIn("<p>|", result)
        self.assertIn("<code>a\\|b</code>", result)

    def test_inline_channel_badges_do_not_break_continuation_rows(self):
        source = (
            "| Service | Role |\n|---|---|\n| Plex | Video |\n\n"
            '| <span class="docs-channel-badge" data-channel="dev">Dev</span> Audiobookshelf | Books |\n\n'
            "| Seerr | Requests |\n"
        )
        rendered = self.render(repair_table_continuations(source))
        self.assertNotIn("<p>|", rendered)
        self.assertEqual(rendered.count("<tr>"), 4)
        self.assertIn('data-channel="dev">Dev</span>', rendered)

    def test_code_span_pipes_are_content_when_joining_rows(self):
        source = "| Goal | Regex |\n|---|---|\n| HD | `1080|720|480` |\n\n| UHD | ``4k|uhd|2160`` |\n"
        result = repair_table_continuations(source)
        self.assertNotIn("\n\n| UHD", result)
        self.assertEqual(
            table_cells("| HD | `1080|720|480` |"), ("", ["HD", "`1080|720|480`"])
        )


if __name__ == "__main__":
    unittest.main()

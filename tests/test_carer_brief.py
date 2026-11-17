# -*- coding: utf-8 -*-
"""Tests for scripts/carer_brief.py.

The point of this script is the guarantee, not the formatting: a sheet that
goes to Nan and Pop must never be built from something said in confidence.
These tests exist so that guarantee survives future edits.

Run with:
    python -m unittest tests/test_carer_brief.py -v
"""
import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import carer_brief  # noqa: E402

SUMMARY = """# Child Summary

## Leo

- Age: 9
- Diagnoses / differences: autism and ADHD, suspected PDA profile
- Strengths (lead with these): dinosaurs, building, remembers every fact
- Challenges right now: mornings, transitions off screens
- Communication: speaks, needs processing time, goes quiet when overwhelmed
- Sensory profile (brief): avoids loud rooms, seeks deep pressure, dysregulated by noise
- School / setting: Reservoir Primary, aide two days
- Supports in place: OT fortnightly, speech monthly
- Triggers: hand dryers, unexpected touch
- What helps most: warnings before change, headphones, a quiet corner
- What to avoid: surprise group activities, being rushed

## Mia

- Age: 6
- Diagnoses / differences: [not filled in]
- Strengths (lead with these): drawing, jokes
- Communication: very chatty
- What helps most: being included
"""


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        (self.root / "child-summary.md").write_text(SUMMARY, encoding="utf-8")
        (self.root / "family-profile.md").write_text("# Profile\n", encoding="utf-8")
        for part in ("private-parent", "private-yp"):
            d = self.root / part
            d.mkdir()
            (d / "child-summary.md").write_text(SUMMARY, encoding="utf-8")

    def run_cli(self, *args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = carer_brief.main(["--family", str(self.root)] + list(args))
        return code, buf.getvalue()


class TestGuard(Base):
    """The whole reason this script exists."""

    def test_refuses_private_parent(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            with self.assertRaises(SystemExit) as cm:
                carer_brief.guard(self.root / "private-parent" / "child-summary.md", self.root)
        self.assertIn("private partition", str(cm.exception))

    def test_refuses_private_yp(self):
        with self.assertRaises(SystemExit) as cm:
            carer_brief.guard(self.root / "private-yp" / "child-summary.md", self.root)
        self.assertIn("private partition", str(cm.exception))

    def test_refuses_file_outside_the_allowlist(self):
        other = self.root / "shared-notes.md"
        other.write_text("private thoughts\n", encoding="utf-8")
        with self.assertRaises(SystemExit) as cm:
            carer_brief.guard(other, self.root)
        self.assertIn("allowlist", str(cm.exception).replace("allow list", "allowlist"))

    def test_refuses_path_outside_the_family_folder(self):
        outside = pathlib.Path(self.tmp.name).parent / "child-summary.md"
        with self.assertRaises(SystemExit) as cm:
            carer_brief.guard(outside, self.root)
        self.assertIn("outside the family folder", str(cm.exception))

    def test_allows_the_shared_summary(self):
        ok = carer_brief.guard(self.root / "child-summary.md", self.root)
        self.assertEqual(ok.name, "child-summary.md")


class TestBriefContents(Base):
    def test_picks_the_requested_child(self):
        code, out = self.run_cli("--child", "Leo", "--for", "Nan and Pop")
        self.assertEqual(code, 0)
        self.assertIn("Leo", out)
        self.assertIn("dinosaurs", out)
        self.assertNotIn("drawing", out)

    def test_case_insensitive_child_match(self):
        code, out = self.run_cli("--child", "leo")
        self.assertIn("dinosaurs", out)

    def test_single_child_is_selected_automatically(self):
        (self.root / "child-summary.md").write_text(
            "# Child Summary\n\n## Leo\n\n- Age: 9\n- What helps most: warnings\n",
            encoding="utf-8")
        code, out = self.run_cli()
        self.assertEqual(code, 0)
        self.assertIn("Leo", out)

    def test_unknown_child_is_a_clean_error(self):
        with self.assertRaises(SystemExit) as cm:
            self.run_cli("--child", "Nobody")
        self.assertIn("no section found", str(cm.exception))

    def test_clinical_fields_are_withheld(self):
        data = carer_brief.build(self.root, "Leo", "Nan")
        joined = json.dumps(data["brief"]).lower()
        self.assertNotIn("autism", joined)
        self.assertNotIn("medication", joined)
        self.assertNotIn("fortnightly", joined)
        self.assertEqual(data["withheld"], sorted(data["withheld"],
                                                  key=data["withheld"].index))

    def test_withheld_list_names_what_was_dropped(self):
        data = carer_brief.build(self.root, "Leo", "Nan")
        self.assertIn("diagnoses / differences", data["withheld"])
        self.assertIn("supports in place", data["withheld"])

    def test_unfilled_template_fields_are_ignored(self):
        data = carer_brief.build(self.root, "Mia", "sitter")
        for value in data["brief"].values():
            self.assertNotIn("[not filled in]", value)

    def test_jargon_is_reported_as_counts(self):
        data = carer_brief.build(self.root, "Leo", "Nan")
        self.assertIn("dysregulat", data["jargon"])
        self.assertIsInstance(data["jargon"]["dysregulat"], int)

    def test_clean_source_reports_no_jargon(self):
        data = carer_brief.build(self.root, "Mia", "sitter")
        self.assertEqual(data["jargon"], {})

    def test_json_output_is_valid(self):
        code, out = self.run_cli("--child", "Leo", "--for", "Nan", "--json")
        data = json.loads(out)
        self.assertEqual(data["child"], "Leo")
        self.assertEqual(data["for"], "Nan")


class TestNeverLeaksPrivate(Base):
    def test_private_content_never_reaches_the_brief(self):
        # Give the private copy something unique and check it cannot appear.
        (self.root / "private-parent" / "child-summary.md").write_text(
            "# Child Summary\n\n## Leo\n\n- What helps most: mum said she regrets the move\n",
            encoding="utf-8")
        data = carer_brief.build(self.root, "Leo", "Nan")
        self.assertNotIn("regrets the move", json.dumps(data))

    def test_private_partitions_are_not_even_opened(self):
        opened = []
        real_read = pathlib.Path.read_text

        def spy(self, *a, **k):
            opened.append(str(self))
            return real_read(self, *a, **k)

        pathlib.Path.read_text = spy
        try:
            carer_brief.build(self.root, "Leo", "Nan")
        finally:
            pathlib.Path.read_text = real_read

        self.assertTrue(opened)
        for path in opened:
            self.assertNotIn("private-", path.replace("\\", "/"))


if __name__ == "__main__":
    unittest.main()

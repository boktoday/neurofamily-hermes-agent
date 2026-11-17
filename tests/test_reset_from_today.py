# -*- coding: utf-8 -*-
"""Tests for scripts/reset_from_today.py.

The contract is narrow on purpose: move the accumulated notes aside, leave the
picture of the family alone, and never print anything that reads as a list of
what was missed.

Run with:
    python -m unittest tests/test_reset_from_today.py -v
"""
import contextlib
import datetime as dt
import io
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import reset_from_today  # noqa: E402


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)

        (self.root / "shared-notes.md").write_text(
            "# Shared notes\n\n- 3 November: tried the new morning card\n"
            "- 5 November: OT said to drop the evening chart\n", encoding="utf-8")
        (self.root / "active-concerns.md").write_text(
            "# Active concerns\n\n- school refusal building again\n", encoding="utf-8")
        (self.root / "family-profile.md").write_text(
            "# Family profile\n\nstanding context, not backlog\n", encoding="utf-8")
        (self.root / "child-summary.md").write_text(
            "# Child summary\n\nstanding context\n", encoding="utf-8")
        for part in ("private-parent", "private-yp"):
            d = self.root / part
            d.mkdir()
            (d / "carer-notes.md").write_text("private and not to be tidied\n",
                                              encoding="utf-8")

    def run_cli(self, *args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = reset_from_today.main(["--root", str(self.root)] + list(args))
        return code, buf.getvalue()

    def month(self):
        return dt.date.today().strftime("%Y-%m")


class TestArchive(Base):
    def test_archives_rolling_notes_into_this_month(self):
        code, out = self.run_cli()
        self.assertEqual(code, 0)
        archived = list((self.root / "archive" / self.month()).iterdir())
        names = sorted(p.name for p in archived)
        self.assertEqual(len(names), 2)
        self.assertTrue(all(n.startswith(("shared-notes-", "active-concerns-"))
                            for n in names))

    def test_archive_keeps_the_original_text(self):
        self.run_cli()
        archived = list((self.root / "archive" / self.month()).iterdir())
        text = " ".join(p.read_text(encoding="utf-8") for p in archived)
        self.assertIn("tried the new morning card", text)
        self.assertIn("school refusal", text)

    def test_live_files_are_replaced_with_a_fresh_page(self):
        self.run_cli()
        notes = (self.root / "shared-notes.md").read_text(encoding="utf-8")
        self.assertIn("Fresh start", notes)
        self.assertNotIn("tried the new morning card", notes)
        concerns = (self.root / "active-concerns.md").read_text(encoding="utf-8")
        self.assertIn("Nothing carried forward", concerns)

    def test_second_run_is_harmless(self):
        self.run_cli()
        code, out = self.run_cli()
        self.assertEqual(code, 0)
        self.assertIn("already clean", out)


class TestNothingElseMoves(Base):
    def test_profile_and_summary_are_untouched(self):
        before = (self.root / "family-profile.md").read_text(encoding="utf-8")
        self.run_cli()
        self.assertEqual(
            (self.root / "family-profile.md").read_text(encoding="utf-8"), before)
        self.assertTrue((self.root / "child-summary.md").exists())

    def test_private_partitions_are_never_archived(self):
        self.run_cli()
        for part in ("private-parent", "private-yp"):
            self.assertTrue((self.root / part / "carer-notes.md").exists())
        archived = " ".join(
            p.name for p in (self.root / "archive" / self.month()).iterdir())
        self.assertNotIn("carer-notes", archived)

    def test_private_helper_guard_rejects_private_paths(self):
        target = self.root / "private-parent" / "carer-notes.md"
        self.assertTrue(reset_from_today.inside_private(target, self.root))
        self.assertFalse(
            reset_from_today.inside_private(self.root / "shared-notes.md", self.root))


class TestNoGuilt(Base):
    def test_output_never_mentions_missing_or_days(self):
        code, out = self.run_cli()
        low = out.lower()
        for banned in ("you missed", "overdue", "behind", "haven't", "days since"):
            self.assertNotIn(banned, low)

    def test_output_says_nothing_is_owed(self):
        code, out = self.run_cli()
        self.assertIn("Nothing is owed", out)

    def test_missing_folder_is_a_clean_error(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            with self.assertRaises(SystemExit):
                reset_from_today.main(["--root", str(self.root / "nope")])


class TestDryRun(Base):
    def test_dry_run_changes_nothing(self):
        before_notes = (self.root / "shared-notes.md").read_text(encoding="utf-8")
        code, out = self.run_cli("--dry-run")
        self.assertEqual(code, 0)
        self.assertIn("dry run", out)
        self.assertEqual(
            (self.root / "shared-notes.md").read_text(encoding="utf-8"), before_notes)
        self.assertFalse((self.root / "archive").exists())


if __name__ == "__main__":
    unittest.main()

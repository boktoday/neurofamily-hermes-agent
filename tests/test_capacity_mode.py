# -*- coding: utf-8 -*-
"""Tests for scripts/capacity_mode.py.

The whole point of this file is that the agreement is enforced by a file rather
than by good intentions, so the tests pin the two behaviours that matter: red
relaxes on its own, and red never changes which safety rules apply.

Run with:
    python -m unittest tests/test_capacity_mode.py -v
"""
import contextlib
import datetime as dt
import io
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import capacity_mode  # noqa: E402


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = pathlib.Path(self.tmp.name) / "shared" / "capacity-state.json"

    def run_cli(self, *args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = capacity_mode.main(list(args) + ["--state", str(self.path)])
        return code, buf.getvalue()

    def state(self):
        return json.loads(self.path.read_text(encoding="utf-8"))


class TestDefaults(Base):
    def test_missing_file_reads_as_green(self):
        self.assertEqual(capacity_mode.load(self.path)["mode"], "green")

    def test_corrupt_file_reads_as_green(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("{not json", encoding="utf-8")
        self.assertEqual(capacity_mode.load(self.path)["mode"], "green")

    def test_unknown_mode_reads_as_green(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text('{"mode": "purple"}', encoding="utf-8")
        self.assertEqual(capacity_mode.load(self.path)["mode"], "green")


class TestSetRed(Base):
    def test_set_red_writes_expiry(self):
        code, out = self.run_cli("set", "red")
        self.assertEqual(code, 0)
        self.assertIn("RED", out)
        state = self.state()
        self.assertEqual(state["mode"], "red")
        self.assertIsNotNone(state["expires_at"])

    def test_set_red_expires_in_about_24_hours(self):
        self.run_cli("set", "red")
        expires = capacity_mode._parse(self.state()["expires_at"])
        hours = (expires - capacity_mode._now()).total_seconds() / 3600
        self.assertAlmostEqual(hours, 24, delta=0.2)

    def test_extend_shortens_or_lengthens_the_timer(self):
        self.run_cli("set", "red", "--extend", "12")
        expires = capacity_mode._parse(self.state()["expires_at"])
        hours = (expires - capacity_mode._now()).total_seconds() / 3600
        self.assertAlmostEqual(hours, 12, delta=0.2)

    def test_set_red_pauses_nudges_by_default(self):
        self.run_cli("set", "red")
        self.assertIsNotNone(self.state()["paused_until"])


class TestSoftening(Base):
    def test_red_past_expiry_softens_to_yellow(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        past = capacity_mode._iso(capacity_mode._now() - dt.timedelta(hours=1))
        self.path.write_text(json.dumps(
            {"mode": "red", "since": past, "expires_at": past,
             "paused_until": None}), encoding="utf-8")

        code, out = self.run_cli("get")
        self.assertEqual(code, 0)
        self.assertIn("YELLOW", out)

    def test_softening_is_written_back(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        past = capacity_mode._iso(capacity_mode._now() - dt.timedelta(hours=1))
        self.path.write_text(json.dumps(
            {"mode": "red", "since": past, "expires_at": past,
             "paused_until": None}), encoding="utf-8")

        self.run_cli("get")
        state = self.state()
        self.assertEqual(state["mode"], "yellow")
        self.assertEqual(state.get("softened_from"), "red")

    def test_red_still_live_does_not_soften(self):
        self.run_cli("set", "red")
        code, out = self.run_cli("get")
        self.assertIn("RED", out)

    def test_yellow_does_not_expire_on_its_own(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        old = capacity_mode._iso(capacity_mode._now() - dt.timedelta(days=30))
        self.path.write_text(json.dumps(
            {"mode": "yellow", "since": old, "expires_at": None,
             "paused_until": None}), encoding="utf-8")
        code, out = self.run_cli("get")
        self.assertIn("YELLOW", out)


class TestClearAndPause(Base):
    def test_clear_returns_to_green(self):
        self.run_cli("set", "red")
        self.run_cli("clear")
        self.assertEqual(self.state()["mode"], "green")

    def test_pause_sets_a_future_timestamp(self):
        self.run_cli("pause", "48")
        until = capacity_mode._parse(self.state()["paused_until"])
        hours = (until - capacity_mode._now()).total_seconds() / 3600
        self.assertAlmostEqual(hours, 48, delta=0.2)

    def test_expired_pause_reads_as_not_paused(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        past = capacity_mode._iso(capacity_mode._now() - dt.timedelta(days=2))
        self.path.write_text(json.dumps(
            {"mode": "green", "since": None, "expires_at": None,
             "paused_until": past}), encoding="utf-8")
        code, out = self.run_cli("get")
        self.assertNotIn("paused until", out)


class TestSafetyIsNeverShortened(unittest.TestCase):
    """Red lowers verbosity. It must never lower the safety floor."""

    def test_every_mode_carries_the_safety_rules(self):
        for mode in capacity_mode.MODES:
            info = capacity_mode.summarise({"mode": mode})
            joined = " ".join(info["always"]).lower()
            self.assertIn("crisis", joined)
            self.assertIn("never shortens", joined)

    def test_red_rules_forbid_questions(self):
        rules = " ".join(capacity_mode.RULES["red"]).lower()
        self.assertIn("no follow-up questions", rules)

    def test_red_rule_states_the_word_limit(self):
        rules = " ".join(capacity_mode.RULES["red"]).lower()
        self.assertIn("60 words", rules)

    def test_safety_rules_are_not_mode_specific(self):
        first = capacity_mode.summarise({"mode": "red"})["always"]
        for mode in capacity_mode.MODES:
            self.assertEqual(capacity_mode.summarise({"mode": mode})["always"], first)


if __name__ == "__main__":
    unittest.main()

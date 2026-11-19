# -*- coding: utf-8 -*-
"""Tests for the slash-command surface (scripts/setup_commands.py).

The point of this file is the same as the capacity tests: the rule is enforced
by something that runs, not by a note somebody may read. Adding a skill without
its command is the likeliest way this repo drifts, because nothing breaks at
the time and only the person in overload notices later.

Run with:
    python -m unittest tests/test_commands.py -v
"""
import pathlib
import sys
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import check_commands  # noqa: E402
import setup_commands  # noqa: E402


class CommandSurfaceTests(unittest.TestCase):
    def test_every_skill_has_a_slash_command(self):
        on_disk = set(check_commands.skills_on_disk())
        mapped = set(setup_commands.SKILL_COMMANDS)
        self.assertEqual(
            set(), on_disk - mapped,
            "These skills have no slash command, so they cannot be started "
            "directly on a bad day: %s" % sorted(on_disk - mapped),
        )

    def test_no_command_names_a_missing_skill(self):
        on_disk = set(check_commands.skills_on_disk())
        mapped = set(setup_commands.SKILL_COMMANDS)
        self.assertEqual(
            set(), mapped - on_disk,
            "SKILL_COMMANDS points at skills that do not exist: %s" % sorted(mapped - on_disk),
        )

    def test_every_bundle_loads_at_least_one_skill(self):
        for name, skills, _description, _instruction in setup_commands.all_commands():
            self.assertTrue(skills, "/%s loads no skills, so invoking it does nothing" % name)

    def test_no_command_collides_with_a_hermes_builtin(self):
        names = {name for name, _skills, _desc in check_commands.command_surface()}
        collisions = sorted(names & check_commands.HERMES_BUILTINS)
        self.assertEqual(
            [], collisions,
            "These names are already Hermes commands and would silently win: %s"
            % ["/" + name for name in collisions],
        )

    def test_no_duplicate_command_names(self):
        names = [name for name, _skills, _desc in check_commands.command_surface()]
        duplicates = sorted({name for name in names if names.count(name) > 1})
        self.assertEqual([], duplicates, "installed twice: %s" % duplicates)

    def test_command_names_are_lowercase_kebab(self):
        for name, _skills, _desc in check_commands.command_surface():
            self.assertEqual(name, name.lower(), "%r is not lowercase" % name)
            self.assertNotIn(" ", name)
            self.assertNotIn("/", name)

    def test_the_check_reports_no_problems(self):
        self.assertEqual([], check_commands.check())


class BundleFileTests(unittest.TestCase):
    """The written YAML must have the shape Hermes reads back."""

    def setUp(self):
        self.rendered = {
            name: setup_commands.render_yaml(name, skills, description, instruction)
            for name, skills, description, instruction in setup_commands.all_commands()
        }

    def test_every_bundle_declares_its_name_and_skills(self):
        for name, text in self.rendered.items():
            self.assertTrue(text.startswith("name: %s\n" % name),
                            "/%s does not declare its name first" % name)
            self.assertIn("skills:", text, "/%s has no skills key" % name)

    def test_capacity_commands_run_the_script_first(self):
        """The brake must set the state, not just talk about it."""
        for name, text in self.rendered.items():
            if name not in setup_commands.CAPACITY_COMMANDS:
                continue
            self.assertIn("capacity_mode.py", text,
                          "/%s does not tell the agent to set capacity mode" % name)
            self.assertIn("set %s" % name, text,
                          "/%s does not set the %s mode specifically" % (name, name))

    def test_quotes_in_instructions_are_escaped(self):
        text = setup_commands.render_yaml("x", ["s"], 'a "quoted" description', "an instruction")
        self.assertIn('\\"quoted\\"', text)

    def test_yaml_round_trips_when_pyyaml_is_available(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed; structural checks cover the shape")
        for name, text in self.rendered.items():
            data = yaml.safe_load(text)
            self.assertEqual(name, data["name"])
            self.assertIsInstance(data["skills"], list)
            self.assertTrue(data["skills"])


class WriteTests(unittest.TestCase):
    def test_dry_run_writes_nothing(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            target = pathlib.Path(tmp) / "profile"
            setup_commands.main(["--profile-dir", str(target), "--dry-run"])
            self.assertFalse((target / "skill-bundles").exists(),
                             "dry run created bundle files")

    def test_real_run_writes_every_bundle_and_is_idempotent(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            target = pathlib.Path(tmp) / "profile"
            setup_commands.main(["--profile-dir", str(target)])
            written = sorted(p.stem for p in (target / "skill-bundles").glob("*.yaml"))
            expected = sorted(name for name, _s, _d, _i in setup_commands.all_commands())
            self.assertEqual(expected, written)

            marker = target / "skill-bundles" / "red.yaml"
            marker.write_text("name: red\nskills:\n  - family-navigator\nedited: true\n",
                              encoding="utf-8")
            setup_commands.main(["--profile-dir", str(target)])
            self.assertIn("edited: true", marker.read_text(encoding="utf-8"),
                          "a re-run overwrote an existing bundle without --force")


if __name__ == "__main__":
    unittest.main(verbosity=2)

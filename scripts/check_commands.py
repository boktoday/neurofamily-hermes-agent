# -*- coding: utf-8 -*-
"""Check that the slash-command surface matches the skills that exist.

Three failure modes this catches, and all three are silent at runtime:

1. **A skill with no command.** The skill still works through routing, so
   nothing looks broken at the time, and the person who added it never notices
   they did not make it reachable on a bad day. This is the drift the check
   exists for.
2. **A command naming a skill that does not exist.** The bundle installs fine,
   then loads nothing when it is invoked.
3. **A name that collides with a Hermes built-in.** The built-in wins, so the
   command silently does the wrong thing - worse than not existing at all.

Run it directly, or let tests/test_commands.py run it:

    python scripts/check_commands.py
    python -m unittest tests/test_commands.py -v
"""
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"
sys.path.insert(0, str(REPO / "scripts"))

import setup_commands  # noqa: E402

# A pinned snapshot of the commands Hermes itself registers, taken from
# hermes_cli/commands.py (CommandDef names plus their aliases).
#
# Pinned rather than imported so this repo stays standalone: it must not need a
# Hermes source checkout to check itself. Refresh it when a Hermes release adds
# commands, with:
#     python - <<'PY'
#     import re, pathlib
#     src = pathlib.Path("<hermes-agent>/hermes_cli/commands.py").read_text(encoding="utf-8")
#     names = set(re.findall(r'CommandDef\(\s*"([a-z0-9_-]+)"', src))
#     for m in re.finditer(r'aliases=\(([^)]*)\)', src):
#         names |= set(re.findall(r'"([a-z0-9_-]+)"', m.group(1)))
#     print(sorted(names))
#     PY
HERMES_BUILTINS = frozenset("""
agents approvals approve autoprune battery bg blueprint bp branch browser btw
bundles busy clear codex-runtime codex_runtime commands compact compose compress
config context copy cron ctx curator debug deny diff discard egress exit export
fast focus footer fork gateway generate-pet goal handoff hatch hb heartbeat help
history image import indicator init insights journey kanban learn learning login
loop memory memory-graph moa model new palette paste pause personality pet plan
platform platforms plugins proactive profile prompt q queue quit reasoning redraw
refine reload reload-mcp reload-skills reload_mcp reload_skills reset restart
resume retry review rewind rollback s save sb sessions set-home sethome short
skills skin snap snapshot start status statusbar steer stop subgoal subscription
suggest suggestions tasks timestamps title tools toolsets topic topup ts undo
update upgrade usage v verbose version voice wake whoami worktree yolo
""".split())


def skills_on_disk():
    return sorted(p.name for p in SKILLS.iterdir() if p.is_dir())


def command_surface():
    """(name, skills, description) for everything setup_commands installs."""
    return [(name, skills, description)
            for name, skills, description, _instruction in setup_commands.all_commands()]


def check():
    """Return a list of human-readable problems. Empty means good."""
    problems = []
    on_disk = skills_on_disk()
    surface = command_surface()

    mapped = set(setup_commands.SKILL_COMMANDS)
    missing = [slug for slug in on_disk if slug not in mapped]
    if missing:
        problems.append(
            "skills with no slash command (add them to SKILL_COMMANDS in "
            "scripts/setup_commands.py): %s" % ", ".join(missing)
        )

    unknown = sorted(slug for slug in mapped if slug not in on_disk)
    if unknown:
        problems.append(
            "SKILL_COMMANDS names skills that do not exist in skills/: %s" % ", ".join(unknown)
        )

    referenced = {skill for _name, skills, _desc in surface for skill in skills}
    ghost = sorted(skill for skill in referenced if skill not in on_disk)
    if ghost:
        problems.append("bundles reference skills that do not exist: %s" % ", ".join(ghost))

    names = [name for name, _skills, _desc in surface]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        problems.append("the same command is installed twice: %s" % ", ".join(duplicates))

    collisions = sorted(set(names) & HERMES_BUILTINS)
    if collisions:
        problems.append(
            "command names already owned by Hermes, which would silently win: %s"
            % ", ".join("/" + name for name in collisions)
        )

    for name in names:
        if name != name.lower() or " " in name or "/" in name:
            problems.append("command name is not lowercase-kebab: %r" % name)

    return problems


def main():
    surface = command_surface()
    print("%d skills, %d commands" % (len(skills_on_disk()), len(surface)))
    problems = check()
    if problems:
        print()
        for problem in problems:
            print("  FAIL  %s" % problem)
        print()
        print("The command surface does not match the skills. Fix scripts/setup_commands.py first.")
        return 1
    print("PASS  every skill has a command, and no name collides with Hermes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

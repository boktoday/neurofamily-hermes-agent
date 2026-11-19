# -*- coding: utf-8 -*-
"""Install one slash command per feature, as native Hermes skill bundles.

Every skill in this repo is otherwise reachable only by describing a problem
well enough that the router in AGENTS.md picks the right one of eighteen. That is
fine on a good day. On a bad day it is the barrier: a parent in sensory overload
cannot compose the paragraph that reliably routes to the skill they need.

Hermes already has the right mechanism for this. A *skill bundle* is a small
YAML file in the profile's ``skill-bundles/`` directory that loads named skills
and is invoked as ``/<name>``. No plugin, no custom code, nothing to rot.

What a bundle can and cannot do, since the difference matters here:

- It **loads skills**, so ``/hard`` puts the hard-moments skill in front of the
  agent and the agent answers. Verified end to end.
- It can carry an ``instruction`` that is prepended to the loaded skill, which is
  how the capacity commands tell the agent to run ``capacity_mode.py`` first.
- It **cannot reply without a model turn.** So ``/red`` is one word and a very
  small turn, not a zero-cost one. That is still the difference between four
  keystrokes and composing a sentence at the worst moment of the week.

Usage:
    python scripts/setup_commands.py                  # the profile called "me"
    python scripts/setup_commands.py --profile sarah
    python scripts/setup_commands.py --dry-run
    python scripts/setup_commands.py --force          # overwrite existing bundles

Then run ``python scripts/check_commands.py`` to prove every skill is covered.
"""
import argparse
import pathlib
import sys

# ---------------------------------------------------------------------------
# The command surface. One entry per skill, plus the capacity and artifact
# shortcuts. check_commands.py fails if a skill in skills/ has no entry here.
#
# Prompts are the person's request, not instructions about the person, and they
# never restate the skill's rules: those live in the skill.
# ---------------------------------------------------------------------------

CAPACITY_INSTRUCTION = (
    "Set capacity mode first, before anything else: run "
    "`python scripts/capacity_mode.py set {mode}`. Then reply in at most three "
    "short lines, with no questions and no lists. If this message also mentions "
    "a crisis or danger, the hard-moments rules win and brevity is suspended."
)

SKILL_COMMANDS = {
    "family-navigator": (
        "begin",
        "Start here: your profile, routing, the weekly check-in",
        "Start with the family profile. If it is empty, build it a few questions at "
        "a time. If it is not, name the two or three things that matter this week.",
    ),
    "hard-moments": (
        "hard",
        "A crisis or a very bad moment, right now",
        "This is a hard moment right now. Safety first, and keep it short.",
    ),
    "emotional-coach": (
        "feelings",
        "Big feelings, a meltdown, shutdown, or a spiral",
        "Help with a big feeling. Do not rush toward a solution.",
    ),
    "behaviour-advisor": (
        "behaviour",
        "A behaviour you do not understand, and what it might be saying",
        "Help me understand a behaviour. Assume it is communication, not defiance.",
    ),
    "communication-specialist": (
        "talk",
        "Communication support: AAC, semi-speaking, scripts",
        "Help with communication.",
    ),
    "sensory-guide": (
        "sensory",
        "Sensory needs, overload, and what helps",
        "Help with sensory needs.",
    ),
    "routine-architect": (
        "routine",
        "Routines, anchors, mornings and evenings",
        "Help with routines. Something that survives a bad day.",
    ),
    "education-advocate": (
        "school",
        "School: IEP or EHCP, meetings, emails, reviews",
        "Help with school.",
    ),
    "healthcare-passport": (
        "gp",
        "GP, dentist, blood test, hospital, haircut prep",
        "Help me prepare for an appointment.",
    ),
    "ndis-guide": (
        "ndis",
        "NDIS access, plans, budgets, reviews (Australia)",
        "Answer from the shipped NDIS documents and name the source.",
    ),
    "village-aligner": (
        "village",
        "Grandparents, co-parents, coaches, babysitters",
        "Help with a relative or another carer.",
    ),
    "parent-companion": (
        "carer",
        "The adult's own load: burnout, guilt, being a person too",
        "This is about me, not the child.",
    ),
    "sibling-support": (
        "sibling",
        "Brothers and sisters: their needs, their resentment, their turn",
        "Help with a sibling.",
    ),
    "food-support": (
        "food",
        "Eating, ARFID, safe foods, mealtime pressure",
        "Help with food and eating. No pressure and no forcing.",
    ),
    "local-support": (
        "support",
        "Helplines, services, and who to call (Australia)",
        "Find me support.",
    ),
    "young-person-coach": (
        "young",
        "Talk to the young person directly, in their own words",
        "Talk to the young person directly, please.",
    ),
    "morning-edition": (
        "morning",
        "Today's Morning Edition, as a printable page",
        "Run today's Morning Edition now, following its schedule file.",
    ),
    "artifacts-generator": (
        "make",
        "A printable or local tool: the IEP companion, food diary, passport, sensory map, lesson chunks",
        "Make me one of the local tools.",
    ),
}

# The brake. One word, no composing.
CAPACITY_COMMANDS = {
    "red": ("red", "Overwhelmed, low spoons: shortest replies, no questions"),
    "yellow": ("yellow", "Stretched: concise, one choice at most"),
    "green": ("green", "Steady: normal depth"),
}

# Starting over, and a status readout.
OPERATIONAL_COMMANDS = {
    "fresh": (
        "Start from today: archive the pile, zero backlog, no shame",
        "Run `python scripts/reset_from_today.py`, then one warm line. Do not list "
        "what was missed and do not ask what happened.",
    ),
    "state": (
        "Your capacity, and where the folder is",
        "Run `python scripts/capacity_mode.py get --json` and report the mode in one "
        "line, plus whether the family folder exists. Nothing else.",
    ),
}

# Artifact shortcuts: same generator skill, so the person does not have to
# remember a filename to ask for the thing.
ARTIFACT_COMMANDS = {
    "passport": ("communication-passport", "The communication passport: phone card and A4 sheet"),
    "iep": ("iep-companion", "The IEP or EHCP companion, in the child's own words"),
    "lesson": ("lesson-chunks", "Break a lesson or task into small steps"),
}


def all_commands():
    """Every (name, skills, description, instruction) the repo installs."""
    out = []
    for slug, (name, description, instruction) in sorted(SKILL_COMMANDS.items()):
        out.append((name, [slug], description, instruction))
    for name, (mode, description) in sorted(CAPACITY_COMMANDS.items()):
        out.append((name, ["family-navigator"], description,
                    CAPACITY_INSTRUCTION.format(mode=mode)))
    for name, (description, instruction) in sorted(OPERATIONAL_COMMANDS.items()):
        out.append((name, ["family-navigator"], description, instruction))
    generator = SKILL_COMMANDS["artifacts-generator"][2]
    for name, (slug, description) in sorted(ARTIFACT_COMMANDS.items()):
        out.append((name, ["artifacts-generator"], description,
                    "%s Deliver %s specifically, personalised for this family." % (generator, slug)))
    return out


def render_yaml(name, skills, description, instruction):
    """The same shape agent/skill_bundles.save_bundle writes."""
    lines = ["name: %s" % name, "skills:"]
    lines += ["  - %s" % skill for skill in skills]
    if description:
        lines.append("description: %s" % _quote(description))
    if instruction:
        lines.append("instruction: %s" % _quote(instruction))
    return "\n".join(lines) + "\n"


def _quote(text):
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return '"%s"' % escaped.replace("\n", "\\n")


def default_profile_dir(profile):
    """Mirror install.py: %LOCALAPPDATA% on Windows, XDG-ish elsewhere."""
    import os

    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA")
        root = pathlib.Path(base) if base else pathlib.Path.home() / "AppData" / "Local"
        return root / "hermes" / "profiles" / profile
    for candidate in (pathlib.Path.home() / ".local" / "share" / "hermes" / "profiles",
                      pathlib.Path.home() / ".hermes" / "profiles"):
        if candidate.is_dir():
            return candidate / profile
    return pathlib.Path.home() / ".local" / "share" / "hermes" / "profiles" / profile


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Install one slash command per feature as native Hermes skill bundles.")
    parser.add_argument("--profile", default="me", help="Hermes profile name (default: me)")
    parser.add_argument("--profile-dir", default=None, help="profile directory (default: auto-detected)")
    parser.add_argument("--force", action="store_true", help="overwrite bundles that already exist")
    parser.add_argument("--dry-run", action="store_true", help="show the plan, change nothing")
    args = parser.parse_args(argv)

    profile_dir = (pathlib.Path(args.profile_dir).expanduser() if args.profile_dir
                   else default_profile_dir(args.profile))
    target = profile_dir / "skill-bundles"

    commands = all_commands()
    print("Slash commands for profile: %s" % profile_dir)
    print("Writing %d bundles to %s" % (len(commands), target))
    if args.dry_run:
        print("(dry run: nothing will be written)\n")

    written = skipped = 0
    for name, skills, description, instruction in commands:
        path = target / ("%s.yaml" % name)
        if path.exists() and not args.force:
            skipped += 1
            continue
        if args.dry_run:
            print("  would write /%-10s -> %s" % (name, ", ".join(skills)))
            written += 1
            continue
        target.mkdir(parents=True, exist_ok=True)
        path.write_text(render_yaml(name, skills, description, instruction), encoding="utf-8")
        written += 1

    if args.dry_run:
        print("\n%d would be written, %d already exist." % (written, skipped))
        return 0

    print("\n%d written, %d left alone." % (written, skipped))
    print("Start a session on that profile and type /state to check, or /help to see them all.")
    if skipped and not args.force:
        print("Use --force to overwrite the ones that already exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

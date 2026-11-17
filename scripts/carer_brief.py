#!/usr/bin/env python3
"""Build the safe briefing behind a carer cheat sheet.

A cheat sheet for Nan and Pop, or for a soccer coach, leaves the house. It gets
photographed, forwarded and stuck on a fridge. So what goes into it is decided
here, by a script, rather than by a model being careful on the day:

- Only `child-summary.md` is read. The private partitions are refused outright,
  the same way `build_paper.py` refuses them for the Morning Edition.
- The clinical fields are dropped, not summarised. A grandparent does not need
  the diagnosis line to have a good Saturday afternoon, and handing one out is
  the family's decision, not ours.
- Anything that still reads like clinical shorthand is reported as a count, so
  the skill knows to translate it into ordinary words before writing.

Usage:
    python scripts/carer_brief.py --child Leo --for "Nan and Pop"
    python scripts/carer_brief.py --child Leo --for "soccer coach" --json
"""

import argparse
import json
import pathlib
import re
import sys

HOME = pathlib.Path.home()
DEFAULT_ROOT = HOME / "neurofamily"

PRIVATE_PARTITIONS = {"private-parent", "private-yp"}

# The only file this script will ever open, plus the guard for anything else.
ALLOWED_FILES = {"child-summary.md", "family-profile.md"}

# Fields worth handing to a person who looks after the child for an afternoon.
# The rest are for clinicians, schools and the family's own record.
CARER_FIELDS = {
    "strengths": "What they are great at",
    "communication": "How to understand them",
    "sensory profile": "What helps, and what gets too much",
    "triggers": "Things that can go wrong",
    "what helps most": "The reliable moves",
    "what to avoid": "Please don't",
}

# Dropped on purpose. Reported by name so nobody wonders where they went.
DROPPED_FIELDS = (
    "diagnoses / differences",
    "challenges right now",
    "school / setting",
    "supports in place",
)

# Clinical shorthand that does not belong in a note for a grandparent. Reported
# as counts only; the skill's job is to rewrite these in ordinary words.
JARGON = (
    "dysregulat", "co-regulat", "propriocept", "interocept", "vestibular",
    "executive function", "sensory diet", "sensory integration", "arfid",
    "pda", "spd", "alexithymia", "praxis", "modulation", "hyperacusis",
    "stimming", "neurotype", "low arousal", "demand avoidan",
)


def guard(path, root):
    """Refuse the private partitions, and anything that is not on the allowlist."""
    resolved = pathlib.Path(path).resolve()
    for part in resolved.parts:
        if part.lower() in PRIVATE_PARTITIONS:
            sys.exit("refusing to read %s: %s is a private partition, and a carer "
                     "sheet leaves the house" % (resolved, part))
    if resolved.name.lower() not in ALLOWED_FILES:
        sys.exit("refusing to read %s: %s is not on the allowlist for a carer sheet"
                 % (resolved.name, resolved.name))
    try:
        resolved.relative_to(pathlib.Path(root).resolve())
    except ValueError:
        sys.exit("refusing to read %s: outside the family folder" % resolved)
    return resolved


def split_children(text):
    """Return {name: body} for each '## Name' section."""
    out, name, buf = {}, None, []
    for line in text.splitlines():
        if line.startswith("## "):
            if name:
                out[name] = "\n".join(buf).strip()
            name = line[3:].strip()
            buf = []
        elif name:
            buf.append(line)
    if name:
        out[name] = "\n".join(buf).strip()
    return out


def parse_fields(body):
    """Turn '- Age: 9' bullets into {age: '9'}.

    Template labels carry parenthetical asides ("Strengths (lead with these)"),
    so the key is normalised before it is stored. Without this, the single most
    useful field on the sheet silently disappears.
    """
    fields = {}
    for line in body.splitlines():
        m = re.match(r"^\s*[-*]\s*([^:]+):\s*(.*)$", line)
        if m:
            label = re.sub(r"\s*\([^)]*\)\s*", " ", m.group(1)).strip().lower()
            label = re.sub(r"\s+", " ", label)
            fields[label] = m.group(2).strip()
    return fields


def strip_placeholders(value):
    """A template that was never filled in is not information."""
    if not value:
        return ""
    if value.startswith("[") and value.endswith("]"):
        return ""
    if value.strip() in ("", "-"):
        return ""
    return value


def find_child(children, wanted):
    if not wanted:
        if len(children) == 1:
            return next(iter(children.items()))
        return None, None
    low = wanted.strip().lower()
    for name, body in children.items():
        if name.lower() == low or low in name.lower():
            return name, body
    return None, None


def jargon_hits(fields):
    hits = {}
    blob = " ".join(fields.values()).lower()
    for term in JARGON:
        n = blob.count(term)
        if n:
            hits[term] = n
    return hits


def build(root, child, for_whom):
    root = pathlib.Path(root).expanduser()
    summary = guard(root / "child-summary.md", root)
    text = summary.read_text(encoding="utf-8")

    children = split_children(text)
    name, body = find_child(children, child)
    if name is None:
        available = ", ".join(children) or "none"
        sys.exit("no section found for %r in child-summary.md. Sections present: %s"
                 % (child or "(no --child given, and more than one child)", available))

    fields = parse_fields(body)
    brief, dropped = {}, []
    for key, label in CARER_FIELDS.items():
        value = strip_placeholders(fields.get(key, ""))
        if value:
            brief[label] = value
    for key in DROPPED_FIELDS:
        if strip_placeholders(fields.get(key, "")):
            dropped.append(key)

    return {
        "child": name,
        "for": for_whom or "a carer",
        "source": str(summary),
        "brief": brief,
        "withheld": dropped,
        "jargon": jargon_hits(fields),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Safe briefing for an external carer sheet.")
    ap.add_argument("--family", default=str(DEFAULT_ROOT), help="family folder")
    ap.add_argument("--child", default=None, help="child's name, as in child-summary.md")
    ap.add_argument("--for", dest="for_whom", default=None,
                    help='who the sheet is for, e.g. "Nan and Pop"')
    ap.add_argument("--json", action="store_true", dest="as_json")
    args = ap.parse_args(argv)

    data = build(args.family, args.child, args.for_whom)

    if args.as_json:
        print(json.dumps(data, indent=2))
        return 0

    print("Carer briefing for %s, for %s" % (data["child"], data["for"]))
    print("Source: %s (shared layer only)\n" % pathlib.Path(data["source"]).name)
    for label, value in data["brief"].items():
        print("%s\n  %s\n" % (label, value))
    if data["withheld"]:
        print("Held back from this sheet: %s" % ", ".join(data["withheld"]))
    if data["jargon"]:
        print("Rewrite before sending: %s"
              % ", ".join("%s x%d" % (k, v) for k, v in sorted(data["jargon"].items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())

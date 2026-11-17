#!/usr/bin/env python3
"""Traffic-light capacity mode: one word instead of a paragraph.

The family says "red" and the whole team gets quieter. This script owns the
state so the rule is enforced by a file rather than by good intentions: every
skill reads it before answering, and a red state softens back to yellow by
itself once 24 hours have passed, so a bad evening does not silence the team
for a week.

Usage:
    python scripts/capacity_mode.py get
    python scripts/capacity_mode.py set red
    python scripts/capacity_mode.py set red --extend 12
    python scripts/capacity_mode.py pause 48
    python scripts/capacity_mode.py clear

State lives in ~/neurofamily/shared/capacity-state.json so it is available to
the whole family view, and it holds no personal detail: a colour and two times.
"""

import argparse
import datetime as dt
import json
import pathlib
import sys

HOME = pathlib.Path.home()
DEFAULT_STATE = HOME / "neurofamily" / "shared" / "capacity-state.json"

MODES = ("red", "yellow", "green")

# Red is a brake, not a setting. After this many hours it relaxes to yellow on
# its own unless the family extends it.
RED_SOFTEN_HOURS = 24

RULES = {
    "red": [
        "At most 3 short bullets, under 60 words in total.",
        "Plain, concrete words. No preamble, no reflection.",
        "No follow-up questions. Offer one gentle default instead of a choice.",
        "Treat non-essential scheduled nudges as paused.",
    ],
    "yellow": [
        "Short and structured. Under about 150 words.",
        "At most one simple question, at the end, and it is optional.",
        "No new tasks unless the family asked for one.",
    ],
    "green": [
        "Normal collaborative depth, planning and artifacts.",
    ],
}

# These never bend, in any mode. Red lowers verbosity, never safety.
ALWAYS = [
    "Crisis, abuse, harm and medical emergencies are answered in full, with the "
    "real local crisis line and emergency number. Red mode never shortens that.",
    "Consent gates and privacy rules are unchanged.",
    "A human referral is never withheld to keep a reply brief.",
]


def _now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def _iso(when):
    return when.isoformat().replace("+00:00", "Z")


def _parse(value):
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def blank():
    return {"mode": "green", "since": None, "expires_at": None, "paused_until": None}


def load(path):
    """Missing or broken state is not an error. It means green."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return blank()
    if not isinstance(data, dict) or data.get("mode") not in MODES:
        return blank()
    return data


def save(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def soften(state, now=None):
    """Apply the clock. Red that has run out becomes yellow.

    Returns (state, changed) so callers can tell whether the file needs writing.
    """
    now = now or _now()
    if state.get("mode") != "red":
        return state, False
    expires = _parse(state.get("expires_at"))
    if expires is None or expires > now:
        return state, False
    state = dict(state)
    state["mode"] = "yellow"
    state["since"] = _iso(now)
    state["softened_from"] = "red"
    state["expires_at"] = None
    return state, True


def summarise(state, now=None):
    now = now or _now()
    mode = state["mode"]
    out = {"mode": mode, "rules": RULES[mode], "always": ALWAYS,
           "paused": False, "paused_until": None, "expires_at": state.get("expires_at")}

    paused_until = _parse(state.get("paused_until"))
    if paused_until and paused_until > now:
        out["paused"] = True
        out["paused_until"] = state["paused_until"]
    return out


def human(state, now=None):
    info = summarise(state, now)
    mode = info["mode"].upper()
    lines = ["Capacity: %s" % mode]

    if info["paused"]:
        lines.append("Non-essential nudges paused until %s" % info["paused_until"])
    if info["expires_at"]:
        lines.append("Red relaxes to yellow at %s unless extended" % info["expires_at"])

    lines.append("")
    lines.append("How to answer right now:")
    for rule in info["rules"]:
        lines.append("  - " + rule)

    lines.append("")
    lines.append("These do not bend, whatever the mode:")
    for rule in info["always"]:
        lines.append("  - " + rule)

    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Traffic-light capacity mode.")
    ap.add_argument("action", choices=["get", "set", "pause", "clear", "init"])
    ap.add_argument("mode", nargs="?", help="red, yellow or green (for 'set')")
    ap.add_argument("--hours", type=int, default=None,
                    help="for 'pause': how long to hold nudges (default 24)")
    ap.add_argument("--extend", type=int, default=None,
                    help="for 'set red': hours until it relaxes (default 24)")
    ap.add_argument("--state", default=str(DEFAULT_STATE), help="state file path")
    ap.add_argument("--json", action="store_true", dest="as_json",
                    help="machine-readable output")
    args = ap.parse_args(argv)

    path = pathlib.Path(args.state).expanduser()
    now = _now()
    state = load(path)
    state, changed = soften(state, now)

    if args.action == "init":
        save(path, state)
        print("capacity state ready at %s (mode: %s)" % (path, state["mode"]))
        return 0

    if args.action == "set":
        if not args.mode or args.mode.lower() not in MODES:
            ap.error("set needs one of: %s" % ", ".join(MODES))
        mode = args.mode.lower()
        state = dict(state)
        state["mode"] = mode
        state["since"] = _iso(now)
        state.pop("softened_from", None)

        if mode == "red":
            hours = args.extend if args.extend is not None else RED_SOFTEN_HOURS
            state["expires_at"] = _iso(now + dt.timedelta(hours=hours))
            # Red offers a pause, so apply a default one rather than asking.
            state["paused_until"] = _iso(now + dt.timedelta(hours=48))
        else:
            state["expires_at"] = None
            state["paused_until"] = None
        changed = True   # deliberate: the caller asked for a write

    elif args.action == "pause":
        hours = args.hours
        # `pause 168` is documented in schedules/README.md, so accept the count
        # positionally as well as through --hours.
        if hours is None and args.mode and str(args.mode).isdigit():
            hours = int(args.mode)
        if hours is None:
            hours = 24
        state = dict(state)
        state["paused_until"] = _iso(now + dt.timedelta(hours=hours))
        changed = True

    elif args.action == "clear":
        state = blank()
        changed = True

    if changed:
        save(path, state)

    if args.as_json:
        print(json.dumps(summarise(state, now), indent=2))
    else:
        print(human(state, now))
    return 0


if __name__ == "__main__":
    sys.exit(main())

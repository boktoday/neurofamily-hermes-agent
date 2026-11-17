#!/usr/bin/env python3
"""Start fresh from today, without a backlog and without a telling-off.

Families drop routines during hard weeks. The thing that keeps them away is not
the gap, it is opening the tool and being shown the gap. This script moves the
accumulated notes aside so the folder reads clean, and prints counts only: it
never lists what was missed and never asks what happened.

Usage:
    python scripts/reset_from_today.py
    python scripts/reset_from_today.py --dry-run

What moves: `shared-notes.md` and `active-concerns.md`, copied into
`~/neurofamily/archive/YYYY-MM/` with today's date in the filename, then
replaced with a clean page that points at the archive.

What never moves: the family profile, the child summary, the calendar, and
anything in `private-parent/` or `private-yp/`. Those are not backlog; they are
the picture of the family, and the private partitions are nobody else's to tidy.
"""

import argparse
import datetime as dt
import pathlib
import shutil
import sys

HOME = pathlib.Path.home()
DEFAULT_ROOT = HOME / "neurofamily"

# Only these accumulate. Everything else is standing context.
ROLLING = ("shared-notes.md", "active-concerns.md")

PRIVATE = ("private-parent", "private-yp")

# Text that marks a page as one this script wrote, so a re-run does not archive
# its own fresh stub.
STUB_MARKERS = ("Fresh start:", "Nothing carried forward")

FRESH_NOTES = """# Shared notes

Fresh start: {today}.

Nothing from before today is waiting for you. This page begins here.

If you ever want the earlier notes back, they are in `archive/{month}/`.
"""

FRESH_CONCERNS = """# Active concerns

Fresh start: {today}.

Nothing carried forward. Add a concern here only when it is live right now.

Earlier concerns are in `archive/{month}/` if you need to look.
"""


def inside_private(path, root):
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return False
    return bool(parts) and parts[0] in PRIVATE


def main(argv=None):
    ap = argparse.ArgumentParser(description="Archive the backlog and start from today.")
    ap.add_argument("--root", default=str(DEFAULT_ROOT), help="family folder")
    ap.add_argument("--dry-run", action="store_true", help="show what would move")
    args = ap.parse_args(argv)

    root = pathlib.Path(args.root).expanduser().resolve()
    if not root.is_dir():
        sys.exit("no family folder at %s. Run scripts/setup-family-folder.py first." % root)

    today = dt.date.today()
    month = today.strftime("%Y-%m")
    stamp = today.isoformat()
    archive = root / "archive" / month

    moved = []
    for name in ROLLING:
        src = root / name
        if not src.is_file():
            continue
        if inside_private(src, root):
            # Defensive: the list above cannot reach these, and that is the point.
            continue
        text = src.read_text(encoding="utf-8", errors="ignore")
        if not text.strip():
            continue
        # A page this script already wrote is not backlog. Without this, a
        # second run archives its own fresh stub and the archive fills with
        # nothing, which is exactly the pile-up it exists to prevent.
        if any(marker in text for marker in STUB_MARKERS):
            continue

        dest = archive / ("%s-%s.md" % (src.stem, stamp))
        if args.dry_run:
            print("would archive:", src.name, "->", dest.relative_to(root))
            moved.append(name)
            continue

        archive.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        fresh = FRESH_NOTES if name == "shared-notes.md" else FRESH_CONCERNS
        src.write_text(fresh.format(today=stamp, month=month), encoding="utf-8")
        moved.append(name)

    if args.dry_run:
        print("dry run: %d file(s) would move. Nothing changed." % len(moved))
        return 0

    if moved:
        print("Archived %d file(s) into archive/%s." % (len(moved), month))
    else:
        print("Nothing to archive. The folder was already clean.")
    print("Starting from today. Nothing is owed and nothing is late.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

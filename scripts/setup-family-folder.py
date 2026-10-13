#!/usr/bin/env python3
"""Create the family folder and copy every template into it.

Usage:
    python scripts/setup-family-folder.py
    python scripts/setup-family-folder.py --target /path/to/folder

Idempotent: existing files are never overwritten.
"""
import argparse
import pathlib
import shutil

REPO = pathlib.Path(__file__).resolve().parent.parent
SHARED = REPO / "shared"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default=str(pathlib.Path.home() / "neurofamily"),
                    help="where the family folder lives (default: ~/neurofamily)")
    args = ap.parse_args()
    target = pathlib.Path(args.target).expanduser()
    target.mkdir(parents=True, exist_ok=True)
    copied, skipped = 0, 0
    for src in sorted(SHARED.glob("*.template.md")):
        dest = target / src.name.replace(".template.md", ".md")
        if dest.exists():
            print("exists, left alone:", dest.name)
            skipped += 1
            continue
        shutil.copyfile(src, dest)
        print("wrote:", dest.name)
        copied += 1
    print()
    print("Family folder ready at: %s" % target)
    print("%d files written, %d left alone." % (copied, skipped))
    print("Next: start a conversation with the Family Navigator and say: Let's build our family profile.")


if __name__ == "__main__":
    main()

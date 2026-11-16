#!/usr/bin/env python3
"""Create the family folder, copy every template into it, and lay down the
privacy partitions.

Usage:
    python scripts/setup-family-folder.py
    python scripts/setup-family-folder.py --target /path/to/folder

Idempotent: existing files and folders are never overwritten.

What it creates inside the target folder:

    <target>/                 the shared family schema (family-profile.md and friends)
    <target>/paper.json       from shared/paper.template.json, needed by build_paper.py
    <target>/shared/          anything safe for the whole-family view and the printed paper
    <target>/private-parent/  carer reflections, finances, NDIS drafts. Owner-only.
    <target>/private-yp/      young-person and sibling notes. Owner-only.

The two private partitions are mode 0o700 on POSIX. The Morning Edition refuses
to read them (see scripts/build_paper.py).
"""
import argparse
import os
import pathlib
import shutil

REPO = pathlib.Path(__file__).resolve().parent.parent
SHARED = REPO / "shared"

PARTITIONS = {
    "shared": (
        "Shared by design",
        "Everything in this folder is safe for the whole family to see: it may be "
        "summarised into the family chat and printed on the Morning Edition.\n",
    ),
    "private-parent": (
        "Private: parent and carer only",
        "This folder holds carer reflections, burnout notes, financial detail and NDIS "
        "drafts. It is never summarised into shared-notes.md, never read by the Morning "
        "Edition, and never printed.\n\n"
        "The agent may write here. It must not quote this folder back to the young "
        "people, to siblings, or into a family group chat.\n",
    ),
    "private-yp": (
        "Private: the young person, and their siblings",
        "This folder holds what a young person or sibling said in confidence. The agent "
        "must not summarise it for parents, and must not copy it into shared-notes.md, "
        "without their explicit consent.\n\n"
        "The one exception is immediate safety: if someone is at risk of harm, the "
        "escalation rails in the hard-moments skill apply, and a real human is told. "
        "That is a safety boundary, not a confidentiality leak.\n",
    ),
}


def restrict(path: pathlib.Path) -> None:
    """Owner-only on POSIX. Windows ACLs are not expressible through chmod, so skip."""
    if os.name == "nt":
        return
    try:
        path.chmod(0o700)
    except OSError as exc:
        print("warning: could not restrict permissions on %s (%s)" % (path, exc))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default=str(pathlib.Path.home() / "neurofamily"),
                    help="where the family folder lives (default: ~/neurofamily)")
    args = ap.parse_args()
    target = pathlib.Path(args.target).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)

    copied, skipped = 0, 0

    # Templates: family-profile.template.md -> family-profile.md, and
    # paper.template.json -> paper.json (the Morning Edition needs the latter).
    for src in sorted(SHARED.glob("*.template.*")):
        marker = src.name.find(".template.")
        if marker < 0:
            continue
        stem = src.name[:marker]
        suffix = src.name[marker + len(".template."):]
        dest = target / ("%s.%s" % (stem, suffix))
        if dest.exists():
            print("exists, left alone:", dest.name)
            skipped += 1
            continue
        shutil.copyfile(src, dest)
        print("wrote:", dest.name)
        copied += 1

    # Privacy partitions.
    for name, (title, body) in PARTITIONS.items():
        folder = target / name
        if folder.exists():
            print("exists, left alone: %s/" % name)
        else:
            folder.mkdir(parents=True, exist_ok=True)
            print("created:", name + "/")
        restrict(folder)
        guard = folder / "README.md"
        if guard.exists():
            continue
        guard.write_text(
            "# %s\n\n%s\n"
            "Created by `scripts/setup-family-folder.py`. Edit it, but keep the rule.\n"
            % (title, body),
            encoding="utf-8",
        )
        print("wrote:", name + "/README.md")

    print()
    print("Family folder ready at: %s" % target)
    print("%d files written, %d left alone." % (copied, skipped))
    print("Partitions: shared/ (whole family), private-parent/ and private-yp/ (owner only).")
    print("Next: start a conversation with the Family Navigator and say: "
          "Let's build our family profile.")


if __name__ == "__main__":
    main()

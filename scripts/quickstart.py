#!/usr/bin/env python3
"""One command to get the family agent running.

Written for a tired parent, not for a developer. Every prompt is one line, the
choices are two, and nothing here needs a terminal command you have to remember.

    python scripts/quickstart.py             # the normal path
    python scripts/quickstart.py --update    # refresh an existing install
    python scripts/quickstart.py --dry-run   # show what it would do, change nothing

`--dry-run` never prompts, never writes and never calls the network, so it is
safe to run anywhere and is the fastest way to see how the paths resolve on a
particular machine.

Standard library only. Python 3.10 or newer.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROFILE_NAME = "neurofamily"
MIN_PY = (3, 10)
DOCS_URL = "https://hermes-agent.nousresearch.com/docs"

# Things copied from the repo into the profile.
TOP_FILES = ["SOUL.md", "AGENTS.md", "config.yaml", "profile.yaml", "PROFILE_BUILDER.md"]
TOP_DIRS = ["skills", "shared", "templates"]

WIDTH = 74

# Set once in main(). Prompts consult it so a dry run never touches stdin.
DRY = False


# --------------------------------------------------------------------------
# talking to a person
# --------------------------------------------------------------------------

def say(text=""):
    print(text)


def wrap(text, indent="  "):
    words = text.split()
    line = indent
    for w in words:
        if len(line) + len(w) + 1 > WIDTH:
            print(line)
            line = indent + w
        else:
            line = line + (" " if line.strip() else "") + w
    if line.strip():
        print(line)


def step(n, title):
    say()
    say("-" * WIDTH)
    say("STEP %s  %s" % (n, title))
    say("-" * WIDTH)


def ok(text):
    say("  [done] " + text)


def info(text):
    wrap(text, "         ")


def warn(text):
    say("  [note] " + text)


def bad(text):
    say("  [stop] " + text)


def ask(prompt, default=""):
    """One-line prompt. Returns default on EOF so a closed stdin never hangs."""
    suffix = " [%s]" % default if default else ""
    if DRY:
        say("  %s%s: %s   (dry run - not asking)"
            % (prompt, suffix, default or "-"))
        return default
    try:
        answer = input("  %s%s: " % (prompt, suffix)).strip()
    except (EOFError, KeyboardInterrupt):
        say()
        return default
    return answer or default


def choose(prompt, options, default="1"):
    """Numbered choice. options is a list of (label, detail)."""
    say("  " + prompt)
    for i, (label, detail) in enumerate(options, 1):
        say("    %d. %s" % (i, label))
        if detail:
            wrap(detail, "       ")
    while True:
        raw = ask("Pick a number", default)
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return int(raw) - 1
        if raw == "":
            return int(default) - 1
        bad("Please type a number from 1 to %d." % len(options))


# --------------------------------------------------------------------------
# where things live
# --------------------------------------------------------------------------

def hermes_home() -> Path:
    """Replicate Hermes' own resolution.

    hermes_constants._platform_default_hermes_home: on Windows LOCALAPPDATA/hermes,
    everywhere else ~/.hermes, with an optional HERMES_DATA_DIR_SUFFIX. HERMES_HOME
    overrides it, and may itself point AT a profile, in which case the root is two
    levels up.
    """
    suffix = os.environ.get("HERMES_DATA_DIR_SUFFIX", "").strip()
    env = os.environ.get("HERMES_HOME", "").strip()
    if env:
        p = Path(os.path.expanduser(env))
        if p.parent.name == "profiles":
            return p.parent.parent
        return p
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", "").strip()
        root = Path(base) if base else Path.home() / "AppData" / "Local"
        return root / ("hermes" + suffix)
    return Path.home() / (".hermes" + suffix)


def profiles_root(override: str = "") -> Path:
    if override:
        return Path(os.path.expanduser(override))
    return hermes_home() / "profiles"


def profile_dir(root: Path) -> Path:
    return root / PROFILE_NAME


def family_folder(override: str = "") -> Path:
    if override:
        return Path(os.path.expanduser(override))
    return Path.home() / "neurofamily"


# --------------------------------------------------------------------------
# step 1
# --------------------------------------------------------------------------

def check_python() -> bool:
    v = sys.version_info
    if v[:2] >= MIN_PY:
        ok("Python %d.%d.%d - new enough." % (v[0], v[1], v[2]))
        return True
    bad("Python %d.%d is too old. This needs 3.10 or newer." % (v[0], v[1]))
    info("On Windows, install the current version from python.org/downloads and tick "
         "\"Add python.exe to PATH\" on the first screen. On a Mac, run: "
         "brew install python@3.12")
    return False


def check_hermes() -> bool:
    found = shutil.which("hermes")
    if found:
        ok("Hermes Agent is installed.")
        return True
    bad("Hermes Agent is not installed yet, and the family team runs inside it.")
    info("Get it from %s - there is a one-click desktop installer for Windows and "
         "Mac, and a one-line command for the terminal shown on that page." % DOCS_URL)
    info("Then run this quickstart again.")
    return False


# --------------------------------------------------------------------------
# step 2
# --------------------------------------------------------------------------

def _same(a: Path, b: Path) -> bool:
    try:
        return a.read_bytes() == b.read_bytes()
    except OSError:
        return False


def plan_copy(src: Path, dest: Path, update: bool):
    """Decide what to do with one file. Returns (action, detail).

    Actions: 'new' (copy), 'same' (identical), 'keep' (differ, leave alone),
    'keep+new' (differ, write a .new beside it and leave the original).
    """
    if not dest.exists():
        return "new", ""
    if _same(src, dest):
        return "same", ""
    if update:
        return "keep+new", ""
    return "keep", ""


def copy_file(src: Path, dest: Path, action: str, dry: bool):
    if action == "new":
        if not dry:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
    elif action == "keep+new":
        if not dry:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest.with_name(dest.name + ".new"))


def do_profile(profiles: Path, update: bool, dry: bool) -> bool:
    pdir = profile_dir(profiles)
    exists = pdir.is_dir()

    say()
    say("  Family team goes here:")
    say("    %s" % pdir)
    if not exists:
        say("    (it does not exist yet)")

    if exists and not update and not dry:
        # Findings from a previous run: never silently overwrite a family's edits.
        clashes = [f for f in TOP_FILES if (pdir / f).exists()]
        if clashes:
            warn("A neurofamily profile is already here.")
            info("Run this with --update to refresh it safely. Your own files are kept "
                 "and anything the repo has changed is saved beside it with .new on the end.")
            return False

    counts = {"new": 0, "same": 0, "keep": 0, "keep+new": 0}
    details = []

    def handle(src: Path, dest: Path):
        action, _ = plan_copy(src, dest, update)
        counts[action] += 1
        details.append((src, dest, action))
        copy_file(src, dest, action, dry)

    for name in TOP_FILES:
        src = REPO / name
        if not src.exists():
            warn("%s is missing from this folder - skipping." % name)
            continue
        handle(src, pdir / name)

    for name in TOP_DIRS:
        src_dir = REPO / name
        if not src_dir.exists():
            warn("%s/ is missing from this folder - skipping." % name)
            continue
        for src in sorted(src_dir.rglob("*")):
            if not src.is_file():
                continue
            if "__pycache__" in src.parts or src.suffix == ".pyc":
                continue
            handle(src, pdir / src.relative_to(REPO))

    say()
    ok("%d files copied." % counts["new"])
    if counts["same"]:
        say("        %d already identical." % counts["same"])
    if counts["keep"]:
        say("        %d kept as they were (run --update to save new versions beside them)."
            % counts["keep"])
    if counts["keep+new"]:
        say("        %d kept, with the new version saved as <name>.new beside each."
            % counts["keep+new"])

    if dry:
        say()
        say("  Every file and where it goes:")
        for src, dest, action in details:
            say("    %-46s -> %s" % (src.relative_to(REPO).as_posix()[:46], action))
    return True


# --------------------------------------------------------------------------
# step 3
# --------------------------------------------------------------------------

def do_commands(pdir: Path, dry: bool) -> None:
    """Install one slash command per skill, as native Hermes skill bundles.

    Without this a person can only reach a skill by describing their problem
    well enough for routing to pick it, which is exactly what someone in sensory
    overload cannot do. Bundles give them /hard, /red, /state and one per skill.
    """
    import setup_commands

    commands = setup_commands.all_commands()
    target = pdir / "skill-bundles"
    if dry:
        info("%d slash commands would be installed, one per skill, e.g. /hard, /red, /state"
             % len(commands))
        return
    target.mkdir(parents=True, exist_ok=True)
    written = 0
    for name, skills, description, instruction in commands:
        path = target / ("%s.yaml" % name)
        if path.exists():
            continue
        path.write_text(setup_commands.render_yaml(name, skills, description, instruction),
                        encoding="utf-8")
        written += 1
    ok("%d slash commands in place: /red, /hard, /state, and one per skill" % written)


def do_family_folder(dry: bool, override: str = "") -> bool:
    script = REPO / "scripts" / "setup-family-folder.py"
    target = family_folder(override)
    say()
    say("  Your family's own folder:")
    say("    %s" % target)

    if not script.exists():
        warn("setup-family-folder.py is missing from this folder - skipping.")
        return False

    if dry:
        ok("Would build it with scripts/setup-family-folder.py")
        return True

    result = subprocess.run([sys.executable, str(script), "--target", str(target)],
                            capture_output=True, text=True)
    if result.returncode != 0:
        bad("The family folder could not be created.")
        info((result.stderr or result.stdout).strip()[:400])
        return False

    for line in result.stdout.strip().splitlines():
        if line.strip():
            say("        " + line.strip())
    ok("Family folder ready, with private rooms for the carer and each young person.")
    return True


# --------------------------------------------------------------------------
# step 4 - two choices, not three
# --------------------------------------------------------------------------

def port_open(port: int, host: str = "127.0.0.1", timeout: float = 1.2) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def detect_local_engine(dry: bool):
    """Returns (label, base_url) for a running local engine, or None."""
    if dry:
        return None
    for label, port in (("Ollama", 11434), ("LM Studio", 1234)):
        if port_open(port):
            return label, "http://localhost:%d/v1" % port
    return None


def write_env(pdir: Path, values: dict, dry: bool):
    """Set keys in <profile>/.env, create it 0600, keep everything already there."""
    env_path = pdir / ".env"
    existing = {}
    order = []
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"^\s*([A-Z0-9_]+)\s*=\s*(.*)$", line)
            if m:
                existing[m.group(1)] = m.group(2)
                order.append(m.group(1))

    for k, v in values.items():
        if k not in existing:
            order.append(k)
        existing[k] = v

    body = ["# Written by scripts/quickstart.py. Keep this file private.",
            "# It holds your key. Never commit it, never paste it into a chat.", ""]
    for k in order:
        body.append("%s=%s" % (k, existing[k]))
    body.append("")

    say()
    say("  Key file:")
    say("    %s" % env_path)
    for k, v in values.items():
        shown = v[:6] + "..." if len(v) > 8 else "(short key)"
        say("    %s = %s" % (k, shown))
    if dry:
        ok("Would write it, readable only by you.")
        return
    pdir.mkdir(parents=True, exist_ok=True)
    if env_path.exists():
        # Path(".env").suffix is ".env", so with_suffix() would give
        # ".env.env.bak". Name the backup explicitly instead.
        backup = env_path.with_name(".env.bak")
        shutil.copy2(env_path, backup)
        say("    (previous file saved as %s)" % backup.name)

    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    fd = os.open(str(env_path), flags, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write("\n".join(body))
    try:
        os.chmod(env_path, 0o600)
    except OSError:
        pass
    if os.name == "nt":
        ok("Written. It sits inside your own Windows user folder.")
        warn("Windows has no simple owner-only file mode. The profile folder is already "
             "readable only by your account. Do not copy this file anywhere else.")
    else:
        ok("Written, readable only by you.")


def set_model_in_config(pdir: Path, provider: str, model: str,
                        base_url: str = "", dry: bool = False):
    """Point config.yaml at a provider without disturbing the comments."""
    cfg = pdir / "config.yaml"
    if not cfg.exists():
        warn("No config.yaml in the profile yet - skipping the model setting.")
        return
    text = cfg.read_text(encoding="utf-8")

    def set_key(block_key, value):
        nonlocal text
        # replace within the model: block only
        m = re.search(r"(?m)^model:\s*$", text)
        if not m:
            return False
        start = m.end()
        nxt = re.search(r"(?m)^\S", text[start:])
        end = start + (nxt.start() if nxt else len(text[start:]))
        block = text[start:end]
        if re.search(r"(?m)^\s+%s:" % block_key, block):
            block = re.sub(r"(?m)^(\s+)%s:.*$" % block_key,
                           lambda mm: "%s%s: %s" % (mm.group(1), block_key, value), block)
        else:
            block = block.rstrip("\n") + "\n  %s: %s\n" % (block_key, value)
        text = text[:start] + block + text[end:]
        return True

    set_key("provider", provider)
    set_key("default", model)

    if base_url and "custom_providers:" not in text:
        text = text.rstrip("\n") + (
            "\n\n# Added by quickstart.py: a model running on this computer.\n"
            "custom_providers:\n"
            "  - name: %s\n"
            "    base_url: %s\n"
            "    api_key: local\n"
            "    model: %s\n" % (provider, base_url, model)
        )
    elif base_url and "custom_providers:" in text:
        warn("config.yaml already lists custom providers - leaving that section alone.")

    say()
    say("  Model setting:")
    say("    provider: %s" % provider)
    say("    model:    %s" % model)
    if base_url:
        say("    address:  %s" % base_url)

    if dry:
        ok("Would write these into config.yaml.")
        return
    cfg.write_text(text, encoding="utf-8")
    ok("config.yaml updated.")


def do_model(pdir: Path, dry: bool) -> bool:
    step(4, "Choose the brain")
    say()
    wrap("Two options. Both work. You can change your mind later without starting over.")

    engine = detect_local_engine(dry)

    options = [
        ("Easiest - use a cloud model (OpenRouter)",
         "One key, many models, free options that change monthly. Costs nothing to "
         "start. Your messages do go to that company, so the family folder keeps "
         "real names out of them."),
        ("100% local and offline (Ollama or LM Studio)",
         "Nothing ever leaves this computer. Needs a reasonably modern machine and a "
         "few GB of disk. Slower, and simpler answers."),
    ]
    if engine:
        say()
        ok("Found %s already running on this computer." % engine[0])
        say("       That is why the local option is the suggested default below.")

    pick = choose("Which sounds right?", options, "1" if not engine else "2")

    if pick == 0:
        if dry:
            say()
            ok("Would ask for an OpenRouter key and write it to .env (readable by you only).")
            info("Quickstart also recommends switching on the Zero Data Retention toggle in "
                 "the OpenRouter dashboard before the first conversation.")
            return True
        say()
        wrap("Go to openrouter.ai/keys, sign in, and make a key. It looks like sk-or-v1-...")
        key = ask("Paste the key here", "")
        if not key:
            warn("No key entered. You can run this again, or set it by hand in .env.")
            return False
        write_env(pdir, {"OPENROUTER_API_KEY": key}, dry)
        set_model_in_config(pdir, "openrouter", "deepseek/deepseek-v4-flash", "", dry)
        say()
        say("  One thing worth doing now, before your first conversation.")
        wrap("OpenRouter keeps prompts unless you tell it not to. Open your privacy settings "
             "at openrouter.ai/settings/privacy and switch zero data retention on for the "
             "model groups you will use. \"All other models\" covers most of them; if you "
             "pick an Anthropic, OpenAI or Google model, switch that group on too.")
        wrap("It is not on by default, and there is no single switch that covers everything, "
             "so give it a minute. Smaller choice of models afterwards, same idea as the "
             "workbook's page 12.", "  ")
        return True

    # ---- local
    if dry:
        say()
        ok("Would look for Ollama on port 11434, then LM Studio on port 1234.")
        info("If one is running, quickstart points the profile at it and writes no key at all.")
        return True

    if engine is None:
        say()
        bad("Neither Ollama nor LM Studio answered on this computer yet.")
        say("  Install one of these, start it, then run this quickstart again:")
        say("    Ollama      https://ollama.com      then:  ollama pull llama3.1")
        say("    LM Studio   https://lmstudio.ai     start the local server")
        return False

    label, base_url = engine
    say()
    ok("%s is running at %s" % (label, base_url))
    default_model = ask("Model name it is serving", "llama3.1")
    # A local engine needs no key, so there is nothing to put in .env.
    set_model_in_config(pdir, "local-" + label.lower().replace(" ", "-"),
                        default_model, base_url, dry)
    return True


# --------------------------------------------------------------------------
# step 5 - messaging
# --------------------------------------------------------------------------

def do_channel(pdir: Path, dry: bool) -> bool:
    step(5, "How you talk to it")
    say()
    wrap("Start with the one that takes no time at all. You can add another later.")

    options = [
        ("Just this computer for now (0 minutes)",
         "Type into the Hermes window. Nothing to set up, nothing to install."),
        ("Telegram on your phone (2 minutes, free)",
         "Message the team from anywhere, including at 2am in a hallway. No extra "
         "phone number needed."),
    ]
    pick = choose("Which do you want?", options, "1")

    if pick == 0:
        ok("Nothing to set up. Finish here and say hello in the Hermes window.")
        return True

    # ---- telegram
    say()
    wrap("In Telegram, search for @BotFather. Send /newbot, give it any name ending in "
         "\"bot\", and it replies with a token. Paste that token here.")
    if dry:
        ok("Would ask for the Telegram bot token and save it to .env.")
        info("Quickstart also turns platforms.telegram.enabled on in config.yaml.")
        return True

    token = ask("Paste the bot token", "")
    if not token:
        warn("No token entered. Telegram can be set up later with: hermes -p %s setup"
             % PROFILE_NAME)
        return False
    write_env(pdir, {"TELEGRAM_BOT_TOKEN": token}, dry)

    cfg = pdir / "config.yaml"
    if cfg.exists():
        text = cfg.read_text(encoding="utf-8")
        new = re.sub(r"(?m)^(\s*)telegram:\s*$\n(\s*)enabled:\s*false",
                     lambda m: "%stelegram:\n%senabled: true" % (m.group(1), m.group(2)),
                     text, count=1)
        if new != text:
            cfg.write_text(new, encoding="utf-8")
            ok("Telegram switched on in config.yaml.")
        else:
            warn("Could not switch Telegram on automatically - run: hermes -p %s setup"
                 % PROFILE_NAME)

    say()
    wrap("One honest note about WhatsApp. The repo can run on WhatsApp too, and it is the "
         "best choice for a whole-family group where several people reply. But it needs a "
         "separate phone number for the bot, because a WhatsApp account is tied to one SIM "
         "card. That is a real cost and a real afternoon. Telegram gets you the same "
         "conversation today, free, and WhatsApp can be added later without starting again.")
    return True


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Set up the NeuroFamily support team in one command.")
    ap.add_argument("--dry-run", action="store_true",
                    help="show what would happen and change nothing (never prompts)")
    ap.add_argument("--update", action="store_true",
                    help="refresh an existing profile, keeping your own files")
    ap.add_argument("--profiles-dir", default="",
                    help="where Hermes keeps profiles (rarely needed)")
    ap.add_argument("--family-folder", default="",
                    help="where to put the family folder (default: ~/neurofamily)")
    args = ap.parse_args(argv)

    global DRY
    DRY = args.dry_run
    dry = args.dry_run

    say()
    say("=" * WIDTH)
    say("  NeuroFamily setup")
    say("  A family support team that runs on your own computer.")
    say("=" * WIDTH)
    if dry:
        say()
        wrap("DRY RUN. Nothing will be written, no key will be asked for, and no network "
             "connection will be made. This only checks that the paths make sense.")

    # ---- step 1
    step(1, "Check the basics")
    py_ok = check_python()
    hermes_ok = check_hermes()
    if not (py_ok and hermes_ok) and not dry:
        say()
        bad("Sort that out first, then run this again. Nothing has been changed.")
        return 1

    profiles = profiles_root(args.profiles_dir)
    pdir = profile_dir(profiles)
    say()
    say("  System:  %s %s" % (platform.system(), platform.release()))
    say("  Profiles folder:")
    say("    %s" % profiles)
    if not profiles.exists() and not dry:
        warn("That folder does not exist yet, which usually means Hermes has never been "
             "run. Start Hermes once, close it, then run this again.")

    # ---- step 2
    step(2, "Copy the family team into place")
    if not do_profile(profiles, args.update, dry):
        return 1
    do_commands(pdir, dry)

    # ---- step 3
    step(3, "Make the family folder")
    do_family_folder(dry, args.family_folder)

    # ---- step 4
    do_model(pdir, dry)

    # ---- step 5
    do_channel(pdir, dry)

    # ---- finish
    say()
    say("=" * WIDTH)
    if dry:
        say("  Dry run finished. No changes were made.")
        say()
        wrap("Run the same command without --dry-run to do it for real.")
    else:
        say("  That is the setup finished.")
        say()
        say("  Start it with:")
        say("    hermes -p %s" % PROFILE_NAME)
        say()
        wrap("Then say: \"Hello, we are setting up the NeuroFamily support team. Let's "
             "build our family profile.\"")
        say()
        wrap("Before you attach a school letter or an NDIS plan, scrub it first: python "
             "scripts/redact_doc.py <file> --names \"<names>\". See page 12 of the workbook.")
    say("=" * WIDTH)
    say()
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""Morning Edition, the NeuroFamily family newspaper.

Reads the family folder and prints a calm, black-and-white A4 page:
one daily section (Today: calendar, anchors, one prompt) plus one
rotating feature per weekday, set in paper.json.

    python scripts/build_paper.py --family ~/neurofamily
    python scripts/build_paper.py --family ~/neurofamily --no-print
    python scripts/build_paper.py --family .demo-family --date 2026-11-04 --no-print

Writes <family>/paper/editions/YYYY-MM-DD.pdf and last-run.json, then
sends the PDF to the printer when paper.json print is true.

Only the standard library is required to build the HTML. The PDF step
uses Playwright, and printing uses SumatraPDF on Windows; both are
skipped with a clear message when missing, and the HTML is still written.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

PARENT_PROMPTS = [
    "What is one thing that went right this week that you have not said out loud?",
    "Which of today's jobs could be dropped without anyone noticing?",
    "What does your child do when they are at their best, and when did you last see it?",
    "What did you say yes to this week that you could have said no to?",
    "Where did you hold a boundary this week and stay kind about it?",
    "What is one small thing you did for yourself this week, and was it enough?",
    "What behaviour this week was communication, not defiance?",
    "Who is one person you could ask for help this week, in one sentence?",
    "What would make tomorrow morning ten minutes easier?",
    "What have you learned about your child this month that no report has captured?",
    "Where are you carrying guilt that belongs to a system, not to you?",
    "What is the smallest thing that made your child light up recently?",
    "If this week had one word, what would it be, and what would you like next week's word to be?",
    "What is one thing you would tell a parent starting where you started?",
]

FAMILY_PROMPTS = [
    "What was the funniest moment this week, for anyone in the house?",
    "What is one thing each person is looking forward to?",
    "What is something someone in this family did well that we have not mentioned?",
    "What would a perfect slow morning look like for you, in three things?",
    "What is one thing you would like more of together, and when could it happen?",
    "Who has been kind to you this week, and how would we thank them?",
    "What is one thing we could make easier for each other next week?",
]

LEARN_BANK = [
    ("First, then", "Say the demand as a two-part sentence: first the non-negotiable, then the thing they want. \"First shoes, then iPad.\" Routine Architect."),
    ("Show, do not tell", "One instruction, in their words, with the object in your hand. Two instructions in one sentence is two instructions too many. Communication Specialist."),
    ("Co-regulate before you correct", "Your calm is the intervention. Lower your voice and slow your pace before naming the behaviour. Emotional Coach."),
    ("Count the sensory load", "Uncomfortable clothes, a loud room, hunger and a bad night of sleep stack up. One loud event can be the last straw, not the cause. Sensory Guide."),
    ("Safe food is not a failure", "At meals, keep one safe food on the plate and no pressure to touch the rest. Repeated exposure without a demand does the work. Food Support."),
    ("Name the feeling, not the lesson", "\"That was really frustrating\" lands where \"you need to calm down\" does not. Emotional Coach."),
    ("Two choices, both fine", "Choice gives control back without opening the whole day to negotiation. Offer two options you can live with. Behaviour Advisor."),
    ("Transitions need a warning", "Five minutes, then two, then now. A surprise change is a demand in disguise. Routine Architect."),
    ("Write it so it can be read twice", "A visual schedule or a one-page social story removes the need to remember instructions under stress. Routine Architect."),
    ("The passport does the introducing", "Hand the communication passport to a new teacher, coach or clinician before they meet your child. Communication Specialist."),
    ("Ask for the record, not the rumour", "After a school meeting, ask for the decision in writing, with who, what and by when. Education Advocate."),
    ("One form, one sitting", "Paperwork expands to fill the time allowed. Pick the single most consequential form and finish only that. Family Navigator."),
    ("Review the plan on a date", "Appointments, reviews and deadlines belong on a calendar with a reminder, not in your head. Family Navigator."),
    ("Notice the sibling", "Ten minutes of undivided attention beats an hour of shared attention. Sibling Support."),
    ("Prepare the exit before you enter", "Before any outing, agree the leaving signal and the place you will meet. Hard Moments."),
    ("Keep the crisis card current", "Contacts, medications, what helps, what does not, on one page, in the bag and on the fridge. Local Support."),
    ("Say what you will do, then do it", "Predictability is a form of care. Small promises kept build the trust that hard days need. Family Navigator."),
    ("Ask the young person first", "Before deciding what support looks like, ask what they want help with and what they want left alone. Young Person Coach."),
    ("Funding follows evidence", "Keep dated notes of goals, supports and outcomes. The plan review reads what is written down. NDIS Guide."),
    ("Rest is part of the plan", "A recovery day after a big day is not a lost day. Build it in before the crash. Parent Companion."),
]

LOCAL_COUNTRY_NAMES = {"AU": "Australia", "UK": "United Kingdom", "US": "United States"}


PRIVATE_PARTITIONS = ("private-parent", "private-yp")


def guard_shared(path: pathlib.Path) -> pathlib.Path:
    """The Morning Edition is a shared, printable artefact.

    The private partitions hold what was said in confidence: a carer's burnout
    note, a young person's own words. Refuse to read them at all, so that no
    future call site can quietly start printing one onto the kitchen table.
    """
    resolved = pathlib.Path(path).resolve()
    for part in resolved.parts:
        if part.lower() in PRIVATE_PARTITIONS:
            raise SystemExit(
                "refusing to read %s: %s is a private partition, and the Morning "
                "Edition is shared" % (resolved, part))
    return resolved


def load_json(path: pathlib.Path, default: dict) -> dict:
    path = guard_shared(path)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print("warning: %s is not valid JSON (%s), using defaults" % (path.name, exc))
    return default


def parse_calendar(path: pathlib.Path) -> list[dict]:
    """Rows of the family calendar table for today onwards."""
    path = guard_shared(path)
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip().startswith("|") or set(line.strip()) <= set("|- "):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[0].lower().startswith("date"):
            continue
        rows.append({"date": cells[0], "time": cells[1], "what": cells[2],
                     "who": cells[3] if len(cells) > 3 else "", "notes": cells[4] if len(cells) > 4 else ""})
    return rows


def upcoming(rows: list[dict], today: dt.date, days: int = 3) -> list[dict]:
    out = []
    for r in rows:
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})", r["date"])
        if not m:
            continue
        try:
            d = dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            continue
        if 0 <= (d - today).days <= days:
            r["when"] = "Today" if d == today else ("Tomorrow" if d == today + dt.timedelta(days=1)
                                                   else DAY_NAMES[d.weekday()])
            r["sort"] = (d - today).days
            out.append(r)
    return sorted(out, key=lambda x: (x["sort"], x["time"]))


def newest_news(folder: pathlib.Path, today: dt.date) -> tuple[str, str]:
    """Newest news brief filed on or before today, with its date label."""
    folder = guard_shared(folder)
    if not folder.exists():
        return "", ""
    files = []
    for f in sorted(folder.glob("*.md")):
        m = re.search(r"(\d{4}-\d{2}-\d{2})", f.name)
        if not m:
            continue
        try:
            d = dt.date.fromisoformat(m.group(1))
        except ValueError:
            continue
        if d <= today:
            files.append((d, f))
    if not files:
        return "", ""
    files.sort()
    d, f = files[-1]
    text = f.read_text(encoding="utf-8", errors="replace")
    return text.strip(), "%d %s" % (d.day, MONTHS[d.month - 1])


def md_to_paras(text: str, limit: int = 4000) -> list[tuple[str, str]]:
    """Small markdown reader: (kind, text) where kind is h2, h3, bullet, para."""
    out = []
    for raw in text[:limit].splitlines():
        line = raw.rstrip()
        s = line.strip()
        if not s:
            continue
        if s.startswith("### "):
            out.append(("h3", s[4:]))
        elif s.startswith("## "):
            out.append(("h2", s[3:]))
        elif s.startswith("# "):
            out.append(("h2", s[2:]))
        elif s.startswith(("- ", "* ")):
            out.append(("bullet", s[2:]))
        elif re.match(r"^\d+\.\s", s):
            out.append(("bullet", re.sub(r"^\d+\.\s", "", s)))
        elif s.startswith("|"):
            continue
        else:
            out.append(("para", s))
    return out


def clean_md(s: str) -> str:
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
    s = re.sub(r"[*_`]", "", s)
    return s.strip()


def build_html(cfg: dict, today: dt.date, family: pathlib.Path, feature: str) -> tuple[str, dict]:
    weekday = DAY_NAMES[today.weekday()]
    weekend = today.weekday() >= 5
    edition = "Family edition" if weekend else "Parent edition"
    cal = upcoming(parse_calendar(family / "family-calendar.md"), today, days=7)
    prompt_bank = FAMILY_PROMPTS if weekend else PARENT_PROMPTS
    prompt = prompt_bank[today.toordinal() % len(prompt_bank)]

    sections = []
    used = {"today": True, "feature": "none"}

    anchors = [v for v in (cfg.get("anchors") or {}).values() if v]
    anchor_html = ""
    if anchors:
        anchor_html = "<ul class=\"anchors\">%s</ul>" % "".join("<li>%s</li>" % a for a in anchors)

    cal_html = "<p class=\"quiet\">Nothing in the calendar for the next seven days.</p>"
    if cal:
        cal_html = "<ul class=\"cal\">%s</ul>" % "".join(
            "<li><b>%s</b> %s%s <span class=\"who\">%s</span></li>" % (
                c["when"], (c["time"] + " · ") if c["time"] else "", c["what"],
                (" · " + c["who"]) if c["who"] else "")
            for c in cal)

    sections.append("""
      <section class="block">
        <h2>Today</h2>
        <p class="dayline">%s</p>
        %s
        %s
        <div class="prompt">
          <p class="label">One question for today</p>
          <p class="q">%s</p>
        </div>
      </section>""" % (edition,
                       ("<p class=\"label\">Routine anchors</p>" + anchor_html) if anchors else "",
                       ("<p class=\"label\">Appointments and deadlines</p>" + cal_html) if cal else "",
                       prompt))

    if feature == "news":
        text, filed = newest_news(family / "news", today)
        if text:
            body = []
            dropped_title = False
            for kind, t in md_to_paras(text, limit=5200):
                t = clean_md(t)
                if kind == "h2":
                    if not dropped_title and "neurodivergent families" in t.lower():
                        dropped_title = True
                        continue
                    body.append("<h3>%s</h3>" % t)
                elif kind == "h3":
                    body.append("<h4>%s</h4>" % t)
                elif kind == "bullet":
                    body.append("<li>%s</li>" % t)
                else:
                    body.append("<p>%s</p>" % t)
            html = "".join(body)
            html = re.sub(r"(<li>.*?</li>)", r"<ul>\1</ul>", html)
            sections.append("""
      <section class="block">
        <h2>News for neurodivergent families</h2>
        <p class="kicker">Filed %s</p>
        %s
      </section>""" % (filed, html))
            used["feature"] = "news (%s)" % filed
        else:
            sections.append("""
      <section class="block">
        <h2>News for neurodivergent families</h2>
        <p class="quiet">No news was filed for today. The NDIS watch and the news brief write into
        the family folder's news folder; when a brief lands, it prints here.</p>
      </section>""")
            used["feature"] = "news (none filed)"

    elif feature == "learn":
        title, text = LEARN_BANK[today.toordinal() % len(LEARN_BANK)]
        sections.append("""
      <section class="block">
        <h2>One thing to learn</h2>
        <h3>%s</h3>
        <p>%s</p>
      </section>""" % (title, text))
        used["feature"] = "learn: %s" % title

    elif feature == "local":
        cc = (cfg.get("country") or "AU").upper()
        p = REPO / "shared" / "local-support" / (cc.lower() + ".md")
        if p.exists():
            first = p.read_text(encoding="utf-8", errors="replace").splitlines()
            keep = []
            for line in first:
                if line.startswith("## ") and keep:
                    break
                keep.append(line)
            body = "".join("<li>%s</li>" % clean_md(l.lstrip("- ").strip())
                           for l in keep if l.strip().startswith("- "))
            region = cfg.get("region") or "your suburb or postcode, set in paper.json"
            sections.append("""
      <section class="block">
        <h2>Local services</h2>
        <p class="kicker">%s · %s</p>
        <ul>%s</ul>
        <p class="quiet">Local services for %s are listed in the family folder's local-support file.
        Update it when something changes, and check the numbers are still live.</p>
      </section>""" % (LOCAL_COUNTRY_NAMES.get(cc, cc), region, body, region))
            used["feature"] = "local (%s)" % LOCAL_COUNTRY_NAMES.get(cc, cc)
        else:
            sections.append("""
      <section class="block">
        <h2>Local services</h2>
        <p class="quiet">No local support file for %s yet. Ask the agent to build one.</p>
      </section>""" % cc)
            used["feature"] = "local (missing file)"

    elif feature == "family":
        prompt2 = FAMILY_PROMPTS[(today.toordinal() + 3) % len(FAMILY_PROMPTS)]
        sections.append("""
      <section class="block">
        <h2>For the whole family</h2>
        <h3>One thing to do together</h3>
        <p>Pick something that needs no preparation and no money: a walk to the same corner and back,
        ten minutes of drawing at the kitchen table, or one chapter read out loud. The point is that
        it is the same each week, so nobody has to negotiate it.</p>
        <h3>One question for the table</h3>
        <p class="q">%s</p>
        <h3>For the sibling who is not the focus</h3>
        <p>Ten minutes, their choice, no agenda. Ask what they would like to do, then do only that.</p>
      </section>""" % prompt2)
        used["feature"] = "family"

    css = """
    @page { size: A4; margin: 15mm 14mm 16mm; }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: Georgia, "Times New Roman", serif; color: #16130f; font-size: 11.4pt; line-height: 1.52; }
    .masthead { border-bottom: 2px solid #16130f; padding-bottom: 8px; margin-bottom: 14px; }
    .masthead h1 { font-family: Georgia, serif; font-weight: normal; font-size: 30pt; letter-spacing: -0.5px; margin: 0; }
    .masthead .family { display: flex; justify-content: space-between; align-items: baseline;
      border-top: 1px solid #16130f; margin-top: 6px; padding-top: 5px; font-size: 8.6pt;
      letter-spacing: 0.14em; text-transform: uppercase; color: #3a342c; }
    .kicker { font-size: 8.4pt; letter-spacing: 0.16em; text-transform: uppercase; color: #4a443a; margin: 0 0 4px; }
    h2 { font-family: Georgia, serif; font-weight: bold; font-size: 15pt; margin: 18px 0 6px;
      padding-top: 8px; border-top: 1px solid #16130f; text-transform: none; }
    h3 { font-size: 11.6pt; margin: 12px 0 3px; }
    h4 { font-size: 11pt; margin: 11px 0 2px; font-style: normal; font-weight: bold; }
    p { margin: 0 0 7px; }
    ul { margin: 2px 0 8px 16px; padding: 0; }
    li { margin: 0 0 3px; }
    .block { break-inside: auto; }
    section.block > h2 { break-after: avoid; }
    .dayline { font-size: 9.6pt; letter-spacing: 0.06em; text-transform: uppercase; color: #3a342c; margin-bottom: 10px; }
    .label { font-size: 8.2pt; letter-spacing: 0.16em; text-transform: uppercase; color: #4a443a; margin: 12px 0 3px; }
    .quiet { color: #4a443a; font-style: italic; }
    .who { color: #4a443a; }
    .cal li { margin-bottom: 4px; }
    .prompt { border: 1px solid #16130f; padding: 10px 12px; margin-top: 14px; break-inside: avoid; }
    .prompt .q { font-size: 13.4pt; margin: 0; line-height: 1.4; }
    .prompt .label { margin-top: 0; }
    .q { font-size: 12pt; }
    footer { margin-top: 16px; border-top: 1px solid #16130f; padding-top: 7px; font-size: 8.2pt;
      color: #3a342c; display: flex; justify-content: space-between; gap: 12px; }
    """

    name = cfg.get("family_name") or "The family"
    title = cfg.get("edition_title") or "Morning Edition"
    html = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>%s, %d %s %d</title><style>%s</style></head>
<body>
  <header class="masthead">
    <h1>%s</h1>
    <div class="family"><span>%s</span><span>%s %d %s %d</span></div>
  </header>
  %s
  <footer>
    <span>Not medical advice. In an emergency call your local emergency number. Support lines are in the family folder's local-support file.</span>
    <span>Prepared by your NeuroFamily agent</span>
  </footer>
</body></html>""" % (title, today.day, MONTHS[today.month - 1], today.year, css,
                     title, name, weekday, today.day, MONTHS[today.month - 1], today.year,
                     "".join(sections))
    meta = {"date": today.isoformat(), "weekday": weekday, "edition": edition,
            "feature": used["feature"], "calendar_items": len(cal), "anchors": len(anchors)}
    return html, meta


def html_to_pdf(html_path: pathlib.Path, pdf_path: pathlib.Path) -> tuple[bool, str]:
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return False, "playwright not installed, HTML only"
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page()
            page.goto(html_path.as_uri() if hasattr(html_path, "as_uri") else html_path.resolve().as_uri())
            page.pdf(path=str(pdf_path), format="A4", print_background=True,
                     margin={"top": "15mm", "bottom": "18mm", "left": "14mm", "right": "14mm"},
                     display_header_footer=True,
                     header_template="<div></div>",
                     footer_template="<div style=\"width:100%;font-size:7pt;color:#3a342c;font-family:Georgia,serif;"
                                     "padding:0 14mm;display:flex;justify-content:space-between;\">"
                                     "<span>" + html_path.stem.replace('%', '') +
                                     "</span><span class=\"pageNumber\"></span></div>")
            browser.close()
        return True, "pdf written"
    except Exception as exc:
        return False, "pdf failed: %s" % exc


def pdf_pages(pdf_path: pathlib.Path) -> int:
    try:
        import pymupdf as pdf
    except ImportError:
        try:
            import fitz as pdf
        except ImportError:
            return 0
    try:
        with pdf.open(str(pdf_path)) as doc:
            return doc.page_count
    except Exception:
        return 0


def print_pdf(pdf_path: pathlib.Path, printer: str) -> tuple[bool, str]:
    if os.name != "nt":
        return False, "printing is Windows only"
    candidates = [pathlib.Path(r"C:/Users/insig/AppData/Local/SumatraPDF/SumatraPDF-3.6.1-64.exe"),
                  pathlib.Path(shutil.which("SumatraPDF") or "")] if shutil.which("SumatraPDF") else \
                 [pathlib.Path(r"C:/Users/insig/AppData/Local/SumatraPDF/SumatraPDF-3.6.1-64.exe")]
    exe = next((c for c in candidates if c and c.exists()), None)
    if exe is None:
        return False, "SumatraPDF not found"
    try:
        subprocess.run([str(exe), "-print-to", printer, "-silent", "-exit-when-done", str(pdf_path)],
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       creationflags=0x08000000, check=False, timeout=120)
        return True, "sent to %s" % printer
    except Exception as exc:
        return False, "print failed: %s" % exc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True, help="path to the family folder")
    ap.add_argument("--date", help="YYYY-MM-DD, defaults to today")
    ap.add_argument("--no-print", action="store_true")
    ap.add_argument("--printer", default="Canon TS3400 series")
    args = ap.parse_args()

    family = pathlib.Path(os.path.expanduser(args.family)).resolve()
    if not family.exists():
        print("family folder not found: %s" % family)
        return 2
    # The paper is shared. Say so out loud, so a family reading the log knows
    # the private partitions were deliberately left alone.
    for name in PRIVATE_PARTITIONS:
        if (family / name).exists():
            print("private partition present, not read: %s/" % name)
    today = dt.date.fromisoformat(args.date) if args.date else dt.date.today()

    defaults = load_json(REPO / "shared" / "paper.template.json", {})
    cfg = dict(defaults)
    cfg.update(load_json(family / "paper.json", {}))

    features = cfg.get("weekday_features") or {}
    feature = (features.get(DAYS[today.weekday()]) or "none").strip().lower()

    html, meta = build_html(cfg, today, family, feature)

    outdir = family / "paper"
    (outdir / "editions").mkdir(parents=True, exist_ok=True)
    html_path = outdir / ("%s.html" % today.isoformat())
    pdf_path = outdir / "editions" / ("%s.pdf" % today.isoformat())
    html_path.write_text(html, encoding="utf-8")

    ok, msg = html_to_pdf(html_path, pdf_path)
    meta["pdf"] = ok
    meta["pdf_note"] = msg
    pages = pdf_pages(pdf_path) if ok else 0
    meta["pages"] = pages

    printed = False
    if ok and cfg.get("print", True) and not args.no_print:
        printed, pmsg = print_pdf(pdf_path, args.printer)
        meta["print_note"] = pmsg
    meta["printed"] = printed

    (outdir / "last-run.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print("edition %s | %s | feature: %s | pages: %d | pdf: %s | printed: %s" % (
        meta["date"], meta["edition"], meta["feature"], pages, ok, printed))
    print("html: %s" % html_path)
    if ok:
        print("pdf:  %s" % pdf_path)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

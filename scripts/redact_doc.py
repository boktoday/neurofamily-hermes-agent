#!/usr/bin/env python3
"""Redact personal information from a document before it reaches a cloud model.

Attaching an NDIS plan or an IEP to a chat with a hosted provider sends the raw
file. This scrubs it locally first and writes a `.redacted.md` beside the
original, so what leaves the machine is the plan's substance without the
identifiers.

Usage:
    python scripts/redact_doc.py NDIS-plan.pdf
    python scripts/redact_doc.py letter.txt --names "Sarah Whitmore, Amelia, Reservoir High School"
    python scripts/redact_doc.py notes.md --names "Sam" --outdir ./clean

Standard library only. PDF input needs `pypdf` (or `PyPDF2`) or the `pdftotext`
binary; if neither is present the script says so and stops rather than pretending
it redacted something it never read.

Nothing is ever printed to stdout except counts. The raw values never appear in
the log, so the terminal scrollback is safe to screenshot.
"""
import argparse
import html
import logging
import pathlib
import re
import shutil
import subprocess
import sys

SUPPORTED_TEXT = {".txt", ".md", ".markdown", ".csv", ".html", ".htm", ".text"}
SUPPORTED_PDF = {".pdf"}

# Order is load-bearing. Phones before NDIS numbers, because a mobile is ten
# digits and an NDIS participant number is nine: run the nine-digit sweep first
# and it will chew the middle out of a phone number, leaving debris behind.
# Names run first of all, so a person called "May" is not half-eaten by a date
# or an address rule.

SCHOOL_WORDS = ("school", "college", "academy", "grammar", "institute",
                "high", "primary", "campus", "university", "kindergarten")
ADULT_TITLES = ("dr", "mr", "mrs", "ms", "miss", "prof", "professor", "sir", "rev")

STREET_TYPES = (
    "Street|St|Road|Rd|Avenue|Ave|Drive|Dr|Court|Ct|Place|Pl|Crescent|Cres|"
    "Parade|Pde|Lane|Ln|Terrace|Tce|Boulevard|Blvd|Bvd|Close|Cl|Grove|Gr|"
    "Highway|Hwy|Circuit|Cct|Way|Square|Sq|Esplanade|Esp|Rise|Glen|View"
)

MONTHS = ("January|February|March|April|May|June|July|August|September|"
          "October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|"
          "Sept|Oct|Nov|Dec")

# Keyword-anchored. A bare 9-digit number is ambiguous, so anything following
# "NDIS" or "CRN" or "Centrelink" is claimed by that label first.
RE_CRN = re.compile(
    r"(?i)\b(?:crn|centrelink(?:\s+(?:reference|ref|crn))?(?:\s+number)?)\b"
    r"[\s:#.\-]*(\d{3}\s?\d{3}\s?\d{3}\s?[A-Za-z]?)"
)
RE_NDIS_KEYED = re.compile(
    r"(?i)\b(?:ndis|participant)\b[^0-9\n]{0,28}?(\d{3}\s?\d{3}\s?\d{3})\b"
)
RE_MEDICARE = re.compile(r"\b[2-6]\d{3}\s?\d{5}\s?\d\b")
RE_EMAIL = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")
RE_PHONE_MOBILE = re.compile(
    r"(?:\+?61[\s\-]?|\(?0)4\d{2}[\s\-]?\d{3}[\s\-]?\d{3}\b"
)
RE_PHONE_LANDLINE = re.compile(
    r"\b\(?0[2-9]\)?[\s\-]?\d{4}[\s\-]?\d{4}\b"
)
RE_STREET = re.compile(
    r"(?i)\b(?:unit|flat|suite|level|shop|u)?[\s#]*\d{1,4}[a-z]?[/\s]+"
    r"(?:[A-Z][A-Za-z'\-]+\s+){1,4}"
    r"(?:" + STREET_TYPES + r")\b\.?"
)
RE_STATE_POSTCODE = re.compile(r"\b(?:NSW|VIC|QLD|WA|SA|TAS|ACT|NT)\b,?\s+\d{4}\b")
RE_POSTCODE_ONLY = re.compile(r"\b(?:NSW|VIC|QLD|WA|SA|TAS|ACT|NT)\b,?\s+\d{4}\b")
RE_DOB = re.compile(
    r"(?i)\b(?:d\.?o\.?b\.?|date\s+of\s+birth|born)\b[\s:.\-]*"
    r"(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}"
    r"|\d{1,2}(?:st|nd|rd|th)?\s+(?:" + MONTHS + r")\s+\d{4}"
    r"|\d{4}-\d{2}-\d{2})"
)
RE_NDIS_BARE_FORMATTED = re.compile(r"\b\d{3}\s\d{3}\s\d{3}\b")
RE_NDIS_BARE = re.compile(r"\b\d{9}\b")


class Redactor:
    """Applies the rules in order and remembers what it replaced."""

    def __init__(self, names=None):
        self.counts = {}
        self.name_map = {}
        self._build_names(names or [])

    # ---------- custom names ----------

    def _build_names(self, raw, text=""):
        """Map each supplied name to a stable pseudonym.

        Classification uses both the supplied string and the document, because
        a family types "Daniel Whitmore" and the letter says "Mr Daniel
        Whitmore": without the pre-scan, a father is labelled [CHILD_B] and the
        page reads as though a child's parent were another child.
        """
        names = [n.strip() for n in raw if n.strip()]
        self._raw = names

        schools, titled = set(), set()
        for name in names:
            low = name.lower()
            if any(w in low for w in SCHOOL_WORDS):
                schools.add(name)
            elif low.split() and low.split()[0].lower() in ADULT_TITLES:
                titled.add(name)

        if text:
            title_re = "|".join(ADULT_TITLES)
            for name in names:
                if name in schools or name in titled:
                    continue
                first = name.split()[0] if name.split() else ""
                if not first:
                    continue
                pat = (r"(?i)\b(?:" + title_re + r")\b\.?\s+"
                       + re.escape(first) + r"\b")
                if re.search(pat, text):
                    titled.add(name)

        # A surname shared by two people cannot honestly be attributed to
        # either, so it gets its own label rather than quietly meaning "the
        # first one we happened to process".
        token_counts = {}
        for name in names:
            if name in schools:
                continue
            for tok in set(name.split()):
                tok = tok.strip(".,").lower()
                if tok:
                    token_counts[tok] = token_counts.get(tok, 0) + 1
        shared = {t for t, c in token_counts.items() if c > 1}

        child_n = school_n = person_n = surname_n = 0
        self.name_map = {}
        surname_map = {}
        for name in sorted(names, key=len, reverse=True):
            if name in schools:
                school_n += 1
                label = "[SCHOOL_%s]" % _letters(school_n)
            elif name in titled:
                person_n += 1
                label = "[PERSON_%s]" % _letters(person_n)
            else:
                child_n += 1
                label = "[CHILD_%s]" % _letters(child_n)
            self.name_map[name] = label

        # Full names first and longest first, so "Sarah Whitmore" wins over
        # "Sarah". Then bare tokens: a plan introduces a name once and uses the
        # first name forty times.
        self._name_patterns = []
        for name in sorted(self.name_map, key=len, reverse=True):
            label = self.name_map[name]
            pat = re.compile(r"\b" + re.escape(name).replace(r"\ ", r"\s+") + r"\b",
                             re.IGNORECASE)
            self._name_patterns.append((pat, label))

        for name in sorted(self.name_map, key=len, reverse=True):
            # A school shares words with places: "Reservoir High School" plus a
            # bare-token rule turns the suburb Reservoir into [SCHOOL_A] and
            # mangles the address around it.
            if name in schools:
                continue
            for tok in name.split():
                tok = tok.strip(".,")
                if len(tok) < 4 or tok.lower() in ADULT_TITLES:
                    continue
                key = tok.lower()
                if key in shared:
                    if key not in surname_map:
                        surname_n += 1
                        surname_map[key] = "[SURNAME_%s]" % _letters(surname_n)
                    label = surname_map[key]
                else:
                    label = self.name_map[name]
                tpat = re.compile(r"\b" + re.escape(tok) + r"\b", re.IGNORECASE)
                if all(tpat.pattern != p.pattern for p, _ in self._name_patterns):
                    self._name_patterns.append((tpat, label))

    # ---------- helpers ----------

    def _sub(self, category, pattern, text, group=0):
        """Replace matches with [CATEGORY], counting them. Never logs the value."""
        def repl(m):
            self.counts[category] = self.counts.get(category, 0) + 1
            label = "[%s]" % category
            if group == 0:
                return label
            whole = m.group(0)
            value = m.group(group)
            start = m.start(group) - m.start(0)
            return whole[:start] + label + whole[start + len(value):]

        return pattern.sub(repl, text)

    def run(self, text):
        # Rebuild the name rules with the document in hand, so a title in the
        # document ("Mr Daniel Whitmore") can inform the classification.
        self._build_names(getattr(self, "_raw", []), text)

        # Structured identifiers run first and names run last. A name rule
        # applied first would chew the middle out of an email or a street and
        # leave debris like [CHILD_A].[CHILD_A]@example.com, which is both
        # useless to read and no safer than the original.

        # 1. Labelled identifiers before bare digit runs.
        text = self._sub("CRN", RE_CRN, text, group=1)
        text = self._sub("NDIS_NUMBER", RE_NDIS_KEYED, text, group=1)
        text = self._sub("MEDICARE_NUMBER", RE_MEDICARE, text)

        # 2. Contact detail.
        text = self._sub("EMAIL", RE_EMAIL, text)
        text = self._sub("PHONE", RE_PHONE_MOBILE, text)
        text = self._sub("PHONE", RE_PHONE_LANDLINE, text)

        # 3. Where they live.
        text = self._sub("ADDRESS", RE_STREET, text)
        text = self._sub("ADDRESS", RE_STATE_POSTCODE, text)

        # 4. Dates of birth, only when labelled. A plan is full of review dates
        #    and they matter; scrubbing every date would remove the substance.
        text = self._sub("DOB", RE_DOB, text, group=1)

        # 5. Whatever is left that looks like a participant number.
        text = self._sub("NDIS_NUMBER", RE_NDIS_BARE_FORMATTED, text)
        text = self._sub("NDIS_NUMBER", RE_NDIS_BARE, text)

        # 6. Named people and places, once nothing else can be damaged by them.
        for pat, label in self._name_patterns:
            def repl(_m, label=label):
                self.counts["NAME"] = self.counts.get("NAME", 0) + 1
                return label
            text = pat.sub(repl, text)
        return text

    def redact_filename(self, stem):
        """The output file must not put a name back in the clear.

        A document called `Sarah-Whitmore-NDIS-plan.pdf` would otherwise become
        `Sarah-Whitmore-NDIS-plan.redacted.md`, which leaks exactly what the
        redaction was for. Filenames travel into chat logs and screenshots.
        """
        out = stem
        for pat, label in self._name_patterns:
            out = pat.sub(label.strip("[]"), out)
        out = RE_NDIS_BARE.sub("ndis-doc", out)
        out = RE_MEDICARE.sub("medicare-doc", out)
        out = re.sub(r"[^A-Za-z0-9._-]+", "-", out)
        out = re.sub(r"-{2,}", "-", out).strip("-._")
        return out or "document"


def _letters(n):
    """1 -> A, 26 -> Z, 27 -> AA."""
    out = ""
    while n > 0:
        n, rem = divmod(n - 1, 26)
        out = chr(65 + rem) + out
    return out


# ---------- reading ----------

def read_document(path: pathlib.Path) -> str:
    suffix = path.suffix.lower()
    if suffix in SUPPORTED_TEXT:
        raw = path.read_text(encoding="utf-8", errors="replace")
        if suffix in {".html", ".htm"}:
            raw = html_to_text(raw)
        return raw
    if suffix in SUPPORTED_PDF:
        return read_pdf(path)
    raise SystemExit(
        "unsupported file type: %s\n"
        "Supported: %s and .pdf.\n"
        "Convert the document to .txt or .md and run it again."
        % (suffix or "(none)", ", ".join(sorted(SUPPORTED_TEXT - {".text"})))
    )


def html_to_text(raw: str) -> str:
    """Strip tags and leave readable text. Good enough for redaction."""
    raw = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", raw)
    raw = re.sub(r"(?i)<br\s*/?>", "\n", raw)
    raw = re.sub(r"(?i)</(p|div|li|tr|h[1-6])>", "\n", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    raw = html.unescape(raw)
    raw = re.sub(r"[ \t]+", " ", raw)
    raw = re.sub(r"\n\s*\n\s*\n+", "\n\n", raw)
    return raw.strip()


def read_pdf(path: pathlib.Path) -> str:
    """pypdf if installed, else the pdftotext binary, else say so and stop."""
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        try:
            from PyPDF2 import PdfReader  # type: ignore
        except ImportError:
            PdfReader = None

    # pypdf logs recovered-file warnings straight to the terminal. Silence them:
    # this script's stdout is meant to carry counts and nothing else.
    logging.getLogger("pypdf").setLevel(logging.CRITICAL)

    reader_failed = False
    if PdfReader is not None:
        try:
            reader = PdfReader(str(path))
            pages = [(page.extract_text() or "") for page in reader.pages]
            text = "\n\n".join(pages).strip()
            if text:
                return text
            reader_failed = True
        except Exception as exc:  # noqa: BLE001 - report type only, never content
            print("warning: pypdf could not read this file (%s)" % type(exc).__name__)
            reader_failed = True

    binary = shutil.which("pdftotext")
    if binary:
        try:
            out = subprocess.run([binary, "-layout", str(path), "-"],
                                 capture_output=True, text=True, timeout=120)
            if out.returncode == 0 and out.stdout.strip():
                return out.stdout
            reader_failed = True
        except (subprocess.SubprocessError, OSError):
            reader_failed = True

    if reader_failed:
        # Different problem, different advice. Telling someone to install pypdf
        # when pypdf is installed and the file is a scan only wastes their time.
        raise SystemExit(
            "this PDF opened but contained no text.\n"
            "That usually means it is a scan or a photo of a document rather "
            "than a digital PDF.\n"
            "Run it through OCR first (for example `ocrmypdf in.pdf out.pdf`), "
            "or open it, copy the text and paste it into a .txt file."
        )

    raise SystemExit(
        "cannot read PDFs on this machine.\n"
        "Install one of these and try again:\n"
        "    pip install pypdf          (or PyPDF2)\n"
        "    apt install poppler-utils  (gives you pdftotext)\n"
        "Or open the PDF, copy the text, paste it into a .txt file and run "
        "this script on that."
    )


# ---------- writing ----------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Redact personal information from a document before it is "
                    "sent to a cloud model.")
    ap.add_argument("document", help="path to the document to redact")
    ap.add_argument("--names", default="",
                    help='comma-separated real names to replace, e.g. '
                         '"Sarah Whitmore, Amelia, Reservoir High School"')
    ap.add_argument("--outdir", default="",
                    help="where to write the redacted file (default: beside the input)")
    ap.add_argument("--quiet", action="store_true", help="print nothing on success")
    args = ap.parse_args(argv)

    src = pathlib.Path(args.document).expanduser()
    if not src.exists():
        print("no such file: %s" % src)
        return 2

    names = [n for n in (x.strip() for x in args.names.split(",")) if n]

    text = read_document(src)
    if not text.strip():
        print("nothing to redact: the document had no extractable text.")
        return 2

    redactor = Redactor(names)
    cleaned = redactor.run(text)

    outdir = pathlib.Path(args.outdir).expanduser() if args.outdir else src.parent
    outdir.mkdir(parents=True, exist_ok=True)
    dest = outdir / (redactor.redact_filename(src.stem) + ".redacted.md")

    header = (
        "<!-- Redacted locally by scripts/redact_doc.py. "
        "Identifiers were replaced in place; the structure and substance of the "
        "document are unchanged. Source file name withheld. -->\n\n"
    )
    dest.write_text(header + cleaned, encoding="utf-8")

    if not args.quiet:
        total = sum(redactor.counts.values())
        # Print the sanitised name, not the source name: a file called
        # Sarah-Whitmore-plan.pdf must not put "Sarah Whitmore" in the terminal.
        print("redacted: %s" % dest.name)
        if total == 0:
            print("  0 items matched. Check this before sending it anywhere: "
                  "a clean run on a real plan usually means a pattern missed.")
        else:
            for key in sorted(redactor.counts):
                print("  %-16s %d" % (key, redactor.counts[key]))
            print("  %-16s %d" % ("total", total))
        if redactor.name_map:
            print("  names replaced: %d" % len(redactor.name_map))
        print("wrote: %s" % dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())

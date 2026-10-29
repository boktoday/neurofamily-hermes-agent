#!/usr/bin/env python3
"""Refresh the NDIS library (shared/ndis/docs) from official sources.

Documents and legislation download directly. The guideline web pages sit behind a bot
wall that refuses plain fetch tools; refresh those with a real browser (open the URL,
save the page text) or skip them - the documents are the substance.

Needs: requests, pymupdf  (pip install requests pymupdf)
Run from the repo root:   python scripts/fetch-ndis-docs.py
"""
import datetime, pathlib, re, zipfile

import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "shared" / "ndis" / "docs"
DOCS.mkdir(parents=True, exist_ok=True)
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"}
TODAY = datetime.date.today().strftime("%d %B %Y")

MEDIA = [
    [
        "applying-to-the-ndis",
        "Applying to the NDIS (eligibility)",
        "7752"
    ],
    [
        "community-connections",
        "Community connections",
        "7766"
    ],
    [
        "early-childhood-approach",
        "Early childhood approach",
        "7760"
    ],
    [
        "early-connections",
        "Early connections",
        "7762"
    ],
    [
        "principles-creating-your-plan",
        "Principles we follow to create your plan",
        "7770"
    ],
    [
        "reasonable-and-necessary-supports",
        "Reasonable and necessary supports",
        "7772"
    ],
    [
        "creating-your-plan",
        "Creating your plan",
        "7816"
    ],
    [
        "your-plan",
        "Your plan",
        "7818"
    ],
    [
        "plan-reassessments",
        "Plan reassessments",
        "8813"
    ],
    [
        "plan-variations",
        "Plan variations",
        "8815"
    ],
    [
        "reviewing-our-decisions",
        "Reviewing our decisions",
        "7822"
    ],
    [
        "appointing-a-nominee",
        "Appointing a nominee",
        "7756"
    ],
    [
        "child-representatives",
        "Child representatives",
        "7768"
    ],
    [
        "behaviour-support",
        "Behaviour support",
        "8508"
    ],
    [
        "therapy-supports",
        "Therapy supports",
        "8091"
    ],
    [
        "including-specific-supports-in-plans",
        "Including specific types of supports in plans",
        "8008"
    ],
    [
        "ndis-pricing-schedule-2026-27",
        "NDIS pricing schedule 2026-27 (maximum price limits)",
        "8841"
    ],
    [
        "leaving-the-ndis",
        "Leaving the NDIS",
        "7904"
    ],
    [
        "justice-system",
        "Justice system",
        "7774"
    ],
    [
        "mainstream-community-supports",
        "Mainstream and community supports",
        "7826"
    ],
    [
        "your-privacy-and-information",
        "Your privacy and information",
        "7779"
    ],
    [
        "compensation",
        "Compensation",
        "8006"
    ],
    [
        "specialist-disability-accommodation",
        "Specialist disability accommodation (SDA)",
        "7788"
    ],
    [
        "short-term-accommodation",
        "Short term accommodation (STA)",
        "8099"
    ],
    [
        "medium-term-accommodation",
        "Medium term accommodation (MTA)",
        "7790"
    ],
    [
        "supported-independent-living",
        "Supported independent living (SIL)",
        "7784"
    ],
    [
        "individualised-living-options",
        "Individualised living options (ILO)",
        "7786"
    ],
    [
        "younger-people-residential-aged-care",
        "Younger people in residential aged care",
        "7796"
    ],
    [
        "assistive-technology",
        "Assistive technology",
        "7776"
    ],
    [
        "social-and-recreation-supports",
        "Social and recreation supports",
        "7824"
    ],
    [
        "work-and-study-supports",
        "Work and study supports",
        "7798"
    ],
    [
        "assistance-animals",
        "Assistance animals including dog guides",
        "7780"
    ],
    [
        "vehicle-modifications",
        "Vehicle modifications and specialised driver training",
        "7782"
    ],
    [
        "home-modifications",
        "Home modifications",
        "7794"
    ],
    [
        "disability-related-health-supports",
        "Disability-related health supports",
        "7812"
    ],
    [
        "dysphagia-supports",
        "Dysphagia supports",
        "7800"
    ],
    [
        "nutrition-supports",
        "Nutrition supports including meal preparation",
        "7802"
    ],
    [
        "diabetes-management-supports",
        "Diabetes management supports",
        "7804"
    ],
    [
        "continence-supports",
        "Continence supports",
        "7806"
    ],
    [
        "wound-and-pressure-care-supports",
        "Wound and pressure care supports",
        "7808"
    ],
    [
        "podiatry-and-foot-care-supports",
        "Podiatry and foot care supports",
        "7810"
    ]
]
LEG = [
    [
        "ndis-act-2013",
        "National Disability Insurance Scheme Act 2013 (consolidated, as at 1 October 2026)",
        "https://www.legislation.gov.au/C2013A00020/2026-10-01/2026-10-01/text/original/pdf"
    ],
    [
        "ndis-supports-for-participants-rules",
        "NDIS (Supports for Participants) Rules 2013 (current compilation)",
        "https://www.legislation.gov.au/F2013L01063/latest/downloads"
    ]
]
PAGES = [
    [
        "ndis-our-guidelines",
        "NDIS guidelines index (all topics)",
        "https://www.ndis.gov.au/understanding-ndis/about-ndis/our-guidelines"
    ],
    [
        "ndis-what-is-the-ndis",
        "What is the NDIS",
        "https://www.ndis.gov.au/understanding-ndis/about-ndis/what-ndis"
    ],
    [
        "ndis-how-the-ndis-works",
        "How the NDIS works",
        "https://www.ndis.gov.au/understanding-ndis/about-ndis/how-ndis-works"
    ],
    [
        "ndis-guide-to-getting-started",
        "A guide to getting started",
        "https://www.ndis.gov.au/understanding-ndis/where-begin/guide-getting-started"
    ],
    [
        "ndis-what-is-a-nominee",
        "What is a nominee",
        "https://www.ndis.gov.au/understanding-ndis/people-help-you/what-nominee"
    ],
    [
        "ndis-pricing-arrangements",
        "Pricing arrangements (how pricing works)",
        "https://www.ndis.gov.au/providers/pricing-and-payments/pricing/pricing-arrangements"
    ],
    [
        "ndis-support-catalogue",
        "What is the support catalogue",
        "https://www.ndis.gov.au/providers/pricing-and-payments/pricing/what-support-catalogue"
    ],
    [
        "ndis-changes-overview",
        "Changes to the NDIS (overview)",
        "https://www.ndis.gov.au/changes-ndis"
    ],
    [
        "ndis-new-way-of-planning",
        "The new way of planning",
        "https://www.ndis.gov.au/changes-ndis/new-way-planning"
    ],
    [
        "ndis-laws",
        "NDIS laws hub",
        "https://www.ndis.gov.au/ndis-laws"
    ],
    [
        "ndis-changes-plan-management",
        "Changes to plan management",
        "https://www.ndis.gov.au/changes-ndis/changes-plan-management"
    ],
    [
        "ndis-law-getting-back-on-track",
        "NDIS laws: Getting the NDIS back on track (October 2024)",
        "https://www.ndis.gov.au/ndis-laws/getting-ndis-back-track"
    ],
    [
        "ndis-law-integrity-and-safeguarding",
        "NDIS laws: Integrity and safeguarding (2026)",
        "https://www.ndis.gov.au/ndis-laws/integrity-and-safeguarding"
    ],
    [
        "ndis-law-securing-the-future",
        "NDIS laws: Securing the NDIS for future generations (August 2026)",
        "https://www.ndis.gov.au/ndis-laws/securing-ndis-future-generations"
    ],
    [
        "ndis-review",
        "The NDIS Review",
        "https://www.ndis.gov.au/ndis-laws/ndis-review"
    ],
    [
        "ndis-supports-lists",
        "NDIS supports lists (what funding can and cannot cover)",
        "https://www.ndis.gov.au/oldsupports-funded-ndis"
    ]
]

ATTR = ("> Source: {url}  \n> Fetched {fetched} by the NeuroFamily NDIS library refresh. "
        "(c) National Disability Insurance Agency (NDIA), or the Commonwealth of Australia, as marked at the source. "
        "Reproduced for noncommercial family support use only. Always verify current rules at ndis.gov.au.")

def extract_pdf(data):
    import fitz
    doc = fitz.open(stream=data, filetype="pdf")
    t = "\n".join(doc[p].get_text("text") for p in range(len(doc)))
    doc.close()
    return t

def extract_docx(data):
    import io
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        xml = z.read("word/document.xml").decode("utf-8", errors="replace")
    xml = re.sub(r"<w:p[ >]", "\n<w:p ", xml)
    t = re.sub(r"<[^>]+>", "", xml)
    return t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")

def tidy(t):
    t = re.sub(r"[ \t]+\n", "\n", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()

def fetch(url, timeout=180):
    return requests.get(url, timeout=timeout, headers=H)

def save(slug, title, url, text):
    md = "# %s\n\n%s\n\n%s\n" % (title, ATTR.format(url=url, fetched=TODAY), tidy(text))
    (DOCS / (slug + ".md")).write_text(md, encoding="utf-8", newline="\n")
    print("%-42s %8d bytes" % (slug + ".md", len(md)))

def main():
    for slug, title, mid in MEDIA:
        url = "https://www.ndis.gov.au/media/%s/download?attachment" % mid
        try:
            r = fetch(url)
            if r.content[:4] == b"%PDF":
                save(slug, title, url, extract_pdf(r.content))
            elif r.content[:2] == b"PK":
                save(slug, title, url, extract_docx(r.content))
            else:
                print(slug, "-> unexpected content", r.status_code, r.headers.get("content-type"))
        except Exception as e:
            print(slug, "ERR", str(e)[:90])
    for slug, title, url in LEG:
        try:
            r = fetch(url, timeout=300)
            data = r.content
            if b"text/original/pdf" in url.encode() or data[:4] == b"%PDF":
                save(slug, title, url, extract_pdf(data))
            else:
                m = re.search(rb'href="([^"]*text/original/pdf[^"]*)"', data)
                if m:
                    u2 = m.group(1).decode()
                    if u2.startswith("/"):
                        u2 = "https://www.legislation.gov.au" + u2
                    r2 = fetch(u2, timeout=300)
                    save(slug, title, url, extract_pdf(r2.content))
                else:
                    print(slug, "-> no PDF link found")
        except Exception as e:
            print(slug, "ERR", str(e)[:90])
    print()
    print("The sixteen guideline pages are behind a bot wall. Run scripts/fetch-ndis-pages.py, which drives a real browser:
    python scripts/fetch-ndis-pages.py --write
To do it by hand instead, open each URL and save the article text over the matching file:")
    for slug, title, url in PAGES:
        print("  %s  <-  %s" % (slug + ".md", url))
    print()
    print("Done. Review the diffs, then commit.")

if __name__ == "__main__":
    main()

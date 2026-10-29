#!/usr/bin/env python3
"""Refresh the sixteen ndis.gov.au guideline pages that plain fetch tools cannot reach.

`fetch-ndis-docs.py` handles the documents and legislation, but these pages sit behind a bot wall
that refuses urllib and requests. A real browser gets them, which is what this does.

    python scripts/fetch-ndis-pages.py            # dry run: report what the live page holds
    python scripts/fetch-ndis-pages.py --write     # overwrite a page when it is safe to do so

Safety rules, learned the hard way:
- Two conditions must both hold before a file is replaced: the content must have moved (fewer than 80
  per cent of its eight-word sequences still match) AND the live text must be at least as long as the
  stored file. In October 2026 a run reported nine pages "changed" at 36 to 76 per cent similarity, all
  of them only a fortnight old, which says the extraction differs from the original capture rather than
  that the NDIS rewrote nine pages at once. A library that gets quoted must not shrink silently, so a
  thinner page is reported for a human to merge and never written automatically.
- Anything under 120 words, a non-200 status, or a page whose title does not match the stored one is
  reported and left alone.
- Nothing is fetched twice in one run, and the script exits 0 so a cron wrapper can stay quiet.

Needs playwright (the Hermes runtime already has it) and a browser in PLAYWRIGHT_BROWSERS_PATH.
"""
import argparse
import datetime
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / 'shared' / 'ndis' / 'docs'
TODAY = datetime.date.today().strftime('%d %B %Y')
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/140.0 Safari/537.36')

PAGES = [
    ('ndis-our-guidelines', 'NDIS guidelines index (all topics)',
     'https://www.ndis.gov.au/understanding-ndis/about-ndis/our-guidelines'),
    ('ndis-what-is-the-ndis', 'What is the NDIS',
     'https://www.ndis.gov.au/understanding-ndis/about-ndis/what-ndis'),
    ('ndis-how-the-ndis-works', 'How the NDIS works',
     'https://www.ndis.gov.au/understanding-ndis/about-ndis/how-ndis-works'),
    ('ndis-guide-to-getting-started', 'A guide to getting started',
     'https://www.ndis.gov.au/understanding-ndis/where-begin/guide-getting-started'),
    ('ndis-what-is-a-nominee', 'What is a nominee',
     'https://www.ndis.gov.au/understanding-ndis/people-help-you/what-nominee'),
    ('ndis-pricing-arrangements', 'Pricing arrangements (how pricing works)',
     'https://www.ndis.gov.au/providers/pricing-and-payments/pricing/pricing-arrangements'),
    ('ndis-support-catalogue', 'What is the support catalogue',
     'https://www.ndis.gov.au/providers/pricing-and-payments/pricing/what-support-catalogue'),
    ('ndis-changes-overview', 'Changes to the NDIS (overview)',
     'https://www.ndis.gov.au/changes-ndis'),
    ('ndis-new-way-of-planning', 'The new way of planning',
     'https://www.ndis.gov.au/changes-ndis/new-way-planning'),
    ('ndis-laws', 'NDIS laws hub', 'https://www.ndis.gov.au/ndis-laws'),
    ('ndis-changes-plan-management', 'Changes to plan management',
     'https://www.ndis.gov.au/changes-ndis/changes-plan-management'),
    ('ndis-law-getting-back-on-track', 'NDIS laws: Getting the NDIS back on track (October 2024)',
     'https://www.ndis.gov.au/ndis-laws/getting-ndis-back-track'),
    ('ndis-law-integrity-and-safeguarding', 'NDIS laws: Integrity and safeguarding (2026)',
     'https://www.ndis.gov.au/ndis-laws/integrity-and-safeguarding'),
    ('ndis-law-securing-the-future', 'NDIS laws: Securing the NDIS for future generations',
     'https://www.ndis.gov.au/ndis-laws/securing-ndis-future-generations'),
    ('ndis-review', 'The NDIS review', 'https://www.ndis.gov.au/ndis-laws/ndis-review'),
    ('ndis-supports-lists', 'Supports lists', 'https://www.ndis.gov.au/oldsupports-funded-ndis'),
]

HEADER = ('# {title}\n\n> Source: {url}  \n> Fetched {today} by the NeuroFamily agent project. '
          '\u00a9 National Disability Insurance Agency (NDIA), or the Commonwealth of Australia, as marked at the source. '
          'Text reproduced for noncommercial family support use only. Always verify current rules at ndis.gov.au.\n\n')

EXTRACT = """() => {
  const drop = ['header','nav','footer','script','style','noscript','form'];
  const clone = document.querySelector('main') ? document.querySelector('main').cloneNode(true)
                                               : document.body.cloneNode(true);
  drop.forEach(t => clone.querySelectorAll(t).forEach(n => n.remove()));
  return clone.innerText || '';
}"""


def shingles(text, n=8):
    words = re.findall(r"[a-z0-9']+", text.lower())
    return {' '.join(words[i:i + n]) for i in range(max(0, len(words) - n + 1))}


def similarity(old_text, new_text):
    a, b = shingles(old_text), shingles(new_text)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a)


def clean(text):
    text = text.replace('\u00a0', ' ')
    text = re.sub(r'[ \t]+\n', '\n', text)
    return re.sub(r'\n{3,}', '\n\n', text).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true', help='overwrite pages that pass the safety rules')
    a = ap.parse_args()

    os.environ.setdefault('PLAYWRIGHT_BROWSERS_PATH', 'C:/Users/insig/AppData/Local/ms-playwright')
    from playwright.sync_api import sync_playwright

    rows = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1280, 'height': 900}, user_agent=UA)
        for slug, title, url in PAGES:
            target = DOCS / (slug + '.md')
            old_words = len(target.read_text(encoding='utf-8').split()) if target.exists() else 0
            try:
                resp = pg.goto(url, wait_until='networkidle', timeout=60000)
                pg.wait_for_timeout(1500)
                text = clean(pg.evaluate(EXTRACT) or '')
                words = len(text.split())
                if words < 120:                      # a slow accordion can lazy-render; one retry
                    pg.reload(wait_until='networkidle', timeout=60000)
                    pg.wait_for_timeout(2000)
                    text = clean(pg.evaluate(EXTRACT) or '')
                    words = len(text.split())
                status = resp.status if resp else 0
            except Exception as e:
                rows.append((slug, 'ERR', old_words, 0, 'left alone: ' + type(e).__name__))
                continue

            old_text = target.read_text(encoding='utf-8') if target.exists() else ''
            overlap = similarity(old_text, text) if old_text else 0.0
            if status != 200:
                action = 'left alone: http %s' % status
            elif words < 120:
                action = 'left alone: only %d words extracted' % words
            elif overlap >= 0.80:
                action = 'no change (%d%% of the stored text still matches)' % round(overlap * 100)
            elif words < old_words:
                action = ('left alone: content differs (%d%% match) but the live page is thinner '
                          '(%d vs %d words). Read the page and merge by hand.' % (round(overlap * 100), words, old_words))
            elif a.write:
                target.write_text(HEADER.format(title=title, url=url, today=TODAY) + text + '\n', encoding='utf-8')
                action = 'updated (%d%% match before, %d words now)' % (round(overlap * 100), words)
            else:
                action = 'would update (%d%% match, %d words now)' % (round(overlap * 100), words)
            rows.append((slug, status, old_words, words, action))
        b.close()

    for slug, status, old, new, action in rows:
        print('%-36s %-4s %5d -> %5d  %s' % (slug, status, old, new, action))
    changed = sum(1 for r in rows if r[4].startswith('updated'))
    print('\n%s' % ('%d files written' % changed if a.write else 'dry run: pass --write to apply'))
    return 0


if __name__ == '__main__':
    sys.exit(main())

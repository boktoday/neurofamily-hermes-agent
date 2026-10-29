#!/usr/bin/env python3
"""Watch the official NDIS sources for change, and refresh the shipped library when they move.

The NDIS changes its rules, price limits and guidelines without announcing it in one place. This
script hashes ten official pages on a schedule; when one changes it says so, and with --refresh it
downloads the latest library first so the agent never quotes a superseded rule.

    python scripts/ndis_watch.py              # check, silent when nothing changed (cron default)
    python scripts/ndis_watch.py --refresh    # check, then run fetch-ndis-docs.py if anything moved
    python scripts/ndis_watch.py --json       # machine-readable result for a cron wrapper
    python scripts/ndis_watch.py --baseline   # record current hashes without reporting changes

Exit codes: 0 no change (or handled), 2 changed (so a shell can branch on it), 1 error.
Only the standard library is needed for --check; --refresh shells out to fetch-ndis-docs.py, which
needs requests and pymupdf.
"""
import argparse
import datetime as dt
import hashlib
import html as H
import json
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
STATE = ROOT / 'shared' / 'ndis' / 'state.json'
CHANGES = ROOT / 'shared' / 'ndis' / 'changes'
DOCS = ROOT / 'shared' / 'ndis' / 'docs'
FETCH = ROOT / 'scripts' / 'fetch-ndis-docs.py'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/140.0 Safari/537.36')

# What matters to a family using this agent: the law, the money, and the rules that decide a plan.
SOURCES = [
    ('ndis-act', 'NDIS Act 2013 (consolidated)', 'https://www.legislation.gov.au/C2013A00020/latest/text'),
    ('pricing-arrangements', 'Pricing arrangements and price limits', 'https://www.ndis.gov.au/providers/pricing-arrangements'),
    ('pricing', 'Pricing and payments', 'https://www.ndis.gov.au/providers/pricing'),
    ('eligibility', 'Eligibility requirements', 'https://www.ndis.gov.au/understanding/eligibility'),
    ('what-ndis', 'What the NDIS is', 'https://www.ndis.gov.au/understanding/what-ndis'),
    ('reasonable-and-necessary', 'What reasonable and necessary means',
     'https://www.ndis.gov.au/participants/creating-plan/understanding-plan-meeting/what-reasonable-and-necessary'),
    ('would-we-fund-it', 'Would we fund it', 'https://www.ndis.gov.au/participants/using-your-funding/understanding-your-ndis-funding/would-we-fund-it'),
    ('early-childhood-guide', 'Guide to the early childhood approach', 'https://www.ndis.gov.au/applying/children/guide-early-childhood-approach'),
    ('early-childhood-partner', 'What an early childhood partner does', 'https://www.ndis.gov.au/applying/children/what-early-childhood-partner'),
    ('news', 'NDIS news and announcements', 'https://www.ndis.gov.au/news'),
]

# a bot wall or an error page must never be mistaken for an edit to policy
BAD_MARKERS = ('access denied', 'page not found', '404 not found', 'request blocked', 'captcha')


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml',
                                               'Accept-Language': 'en-AU,en;q=0.9'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, r.read().decode('utf-8', 'replace')


def to_text(raw):
    raw = re.sub(r'<script.*?</script>|<style.*?</style>|<nav.*?</nav>|<footer.*?</footer>', ' ', raw,
                 flags=re.S | re.I)
    text = re.sub(r'<[^>]+>', ' ', raw)
    text = H.unescape(text).replace('\u00a0', ' ')
    return re.sub(r'[ \t]+', ' ', text).strip()


def digest(text):
    return hashlib.sha256(re.sub(r'\s+', ' ', text).encode('utf-8')).hexdigest()[:16]


def library_hashes():
    out = {}
    if DOCS.exists():
        for f in sorted(DOCS.glob('*.md')):
            out[f.name] = hashlib.sha256(f.read_bytes()).hexdigest()[:16]
    return out


def load_state():
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {'pages': {}, 'library': {}, 'checked': None}


def save_state(state):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=1, sort_keys=True) + '\n', encoding='utf-8')


def check(state):
    today = dt.date.today().isoformat()
    previous = state.get('pages', {})
    results, changed = [], False
    for slug, label, url in SOURCES:
        row = {'slug': slug, 'label': label, 'url': url, 'status': 'unchanged'}
        try:
            code, raw = fetch(url)
            text = to_text(raw)
            if code != 200:
                row['status'] = 'http %s' % code
            elif len(text) < 400 or any(m in text.lower()[:4000] for m in BAD_MARKERS):
                row['status'] = 'blocked'
            else:
                h = digest(text)
                old = previous.get(slug, {})
                if not old.get('sha'):
                    row['status'] = 'new'
                elif old['sha'] != h:
                    row['status'] = 'changed'
                    row['previous_sha'] = old['sha']
                row['sha'] = h
                row['chars'] = len(text)
                if row['status'] == 'changed':
                    changed = True
                    old_text = old.get('excerpt', '')
                    row['excerpt'] = text[:1500]
                    row['was'] = old_text[:1500]
                state.setdefault('pages', {})[slug] = {
                    'sha': h, 'chars': len(text), 'checked': today, 'excerpt': text[:1500]}
                previous[slug] = state['pages'][slug]
        except urllib.error.HTTPError as e:
            row['status'] = 'http %s' % e.code
        except Exception as e:
            row['status'] = type(e).__name__
        results.append(row)

    lib = library_hashes()
    lib_missing = [k for k in state.get('library', {}) if k not in lib]
    lib_new = [k for k in lib if k not in state.get('library', {})]
    lib_changed = [k for k in lib if k in state.get('library', {}) and state['library'][k] != lib[k]]
    state['library'] = lib
    state['checked'] = today
    changed = changed or bool(lib_changed)
    return results, {'new': lib_new, 'changed': lib_changed, 'missing': lib_missing}, changed


def write_change_note(results, lib, changed):
    CHANGES.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    path = CHANGES / ('%s.md' % today)
    lines = ['# NDIS watch, %s' % today, '']
    lines.append('## Official pages')
    for r in results:
        mark = {'unchanged': 'no change', 'changed': '**CHANGED**', 'new': 'first sighting'}.get(r['status'], r['status'])
        lines.append('- %s: %s' % (r['label'], mark))
        if r['status'] == 'changed':
            lines.append('  - now: %s' % r.get('excerpt', '')[:600].replace('\n', ' '))
    if lib['changed'] or lib['new'] or lib['missing']:
        lines += ['', '## Library files']
        for name in lib['changed']:
            lines.append('- changed: %s' % name)
        for name in lib['new']:
            lines.append('- added: %s' % name)
        for name in lib['missing']:
            lines.append('- removed: %s' % name)
    lines += ['', 'Next step: run `python scripts/fetch-ndis-docs.py` to pull the latest, then read the',
              'changed pages and update `skills/ndis-guide/SKILL.md` where it quotes a rule that moved.', '']
    path.write_text('\n'.join(lines), encoding='utf-8')
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--refresh', action='store_true', help='run fetch-ndis-docs.py when something changed')
    ap.add_argument('--baseline', action='store_true', help='record hashes, report nothing')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--verbose', action='store_true')
    a = ap.parse_args()

    state = load_state()
    results, lib, changed = check(state)

    if a.baseline:
        save_state(state)
        print('baseline recorded: %d pages, %d library files' % (len(state['pages']), len(state['library'])))
        return 0

    if not changed:
        save_state(state)
        if a.json:
            print(json.dumps({'changed': False, 'checked': state['checked']}))
        elif a.verbose:
            print('no change across %d pages and %d library files (%s)'
                  % (len(results), len(lib and state['library'] or {}), state['checked']))
        return 0

    note = write_change_note(results, lib, changed)
    refreshed = None
    if a.refresh:
        refreshed = subprocess.run([sys.executable, str(FETCH)], cwd=str(ROOT), capture_output=True, text=True,
                                   env={'PATH': '/usr/bin:/bin', 'PYTHONPATH': '', 'PYTHONHOME': '',
                                        'USERPROFILE': str(pathlib.Path.home()), 'HOME': str(pathlib.Path.home())})
        state['library'] = library_hashes()
        state['refreshed'] = dt.date.today().isoformat()
    save_state(state)

    if a.json:
        print(json.dumps({'changed': True, 'checked': state['checked'], 'note': str(note),
                          'pages': results, 'library': lib,
                          'refresh': (refreshed.returncode if refreshed else None)}))
    else:
        print('NDIS sources moved on %s' % state['checked'])
        for r in results:
            if r['status'] != 'unchanged':
                print('  %-26s %s' % (r['slug'], r['status']))
        for k in ('changed', 'new', 'missing'):
            for name in lib[k]:
                print('  library %-8s %s' % (k, name))
        print('  note: %s' % note)
        if refreshed is not None:
            print('  refresh exit: %s' % refreshed.returncode)
    return 2


if __name__ == '__main__':
    sys.exit(main())

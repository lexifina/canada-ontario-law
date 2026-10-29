"""Builds a git repository of Ontario statutes from e-Laws (www.ontario.ca/laws), in which every amending act is one
commit, dated the day it took effect.

    python -X utf8 scripts/canada-ontario-law/build.py --today 2026-10-28 [--repo ../canada-ontario-law] [--offline]
                                                       [--verify-rebuild]

The King's Printer for Ontario publishes each consolidated statute on e-Laws in its point-in-time versions (the
"Versions" tab): each version's full English text, with the days it applies from and to. The text carries, at the end
of each subsection, the citations of the provisions that enacted and amended it ("2009, c. 5, s. 8."), and since 2016
each section ends with a list "Section Amendments with date in force (d/m/y)" that gives the day each amending provision
took effect. We take every version of the acts below, compare consecutive versions section by section, and credit each
change to the amending act that this evidence names. A change nothing explains is never credited to an act: it gets its
own commit by the publisher, labelled.

Text the consolidation prints for amendments not yet in force (the shaded "Y" paragraphs and the "Note: On a day to be
named by proclamation ..." notes before them) is not law in force on the version's days, so it is left out of the files.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from lxml import html as lhtml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fetchlib import CACHE, REQUESTS, fetch, fetch_json, API  # noqa: E402

ROOT = HERE.parents[1]
SITE = 'https://www.ontario.ca/laws'
COMMITTER = ('Lexifina', 'canada-ontario-law@lexifina.com')
PUBLISHER = ("e-Laws (King's Printer for Ontario)", 'e-laws@ontario.invalid')

# The acts in the record: the e-Laws identifier (also the folder), a short name, and the act's own citations (cited
# in its own text as the enacting provision; never an amendment).
ACTS = [
    {'id': '90h08', 'short': 'Highway Traffic Act', 'own': ['R.S.O. 1990, c. H.8']},
    {'id': '06r17', 'short': 'Residential Tenancies Act, 2006', 'own': ['S.O. 2006, c. 17']},
    {'id': '00e41', 'short': 'Employment Standards Act, 2000', 'own': ['S.O. 2000, c. 41']},
    {'id': '06l21', 'short': 'Legislation Act, 2006', 'own': ['S.O. 2006, c. 21']},
]


def clean(s: str) -> str:
    """Soft hyphens and zero-width characters go; runs of white space (spaces, line breaks, tabs, no-break and other
    Unicode spaces) become one space. Nothing else changes."""
    return re.sub(r'\s+', ' ', re.sub('[­​‌‍﻿]', '', s)).strip()


def canon(s: str) -> str:
    """Letters and digits only, case-folded: two texts with the same canon differ only in layout, punctuation or case."""
    return ''.join(ch for ch in s.casefold() if ch.isalnum())


# ---------------------------------------------------------------- the act's versions

def local_day(stamp: str) -> str:
    """e-Laws gives each version's first and last day as midnight in Toronto, written in UTC ('2026-07-01T04:00:00.000Z'
    is 1 July 2026, 00:00 EDT)."""
    if stamp[10:] not in ('T04:00:00.000Z', 'T05:00:00.000Z'):
        raise SystemExit(f'unexpected version time {stamp}')
    return stamp[:10]


def version_list(act: dict, offline: bool) -> list[dict]:
    """The act's point-in-time versions, oldest first: number, first and last day, and the API path of its text.
    Records the API lists without dates (two in the Highway Traffic Act, repeating version numbers it also lists with
    dates) are left out."""
    d = fetch_json(f'en/act-versions/statute/{act["id"]}', offline)
    hits = d['aggregations']['all']['versions']['hits']['hits']['hits']
    out = []
    for h in hits:
        s = h['_source']
        if 'dateFrom' not in s:
            continue
        n = s['version']
        out.append({'n': n, 'from': local_day(s['dateFrom']['en']),
                    'to': local_day(s['dateTo']['en']) if s.get('dateTo') else None,
                    'api': f'en/doc-search/statute/{act["id"]}' + (f'/v{n}' if n else '')})
    out.sort(key=lambda v: v['from'])
    for a, b in zip(out, out[1:]):
        if a['to'] is None or (dt.date.fromisoformat(a['to']) + dt.timedelta(days=1)).isoformat() != b['from']:
            raise SystemExit(f'{act["id"]}: versions do not join: v{a["n"]} to {a["to"]}, v{b["n"]} from {b["from"]}')
    if out[-1]['to'] is not None or out[-1]['n'] != 0:
        raise SystemExit(f'{act["id"]}: the last version is not the current one')
    for v in out:
        v['url'] = f'{SITE}/statute/{act["id"]}' + (f'/v{v["n"]}' if v['n'] else '')
    return out


# ---------------------------------------------------------------- reading one version

def cls_of(e) -> str:
    """The paragraph class without the '-e' (English) suffix the older pages carry: 'subsection-e' -> 'subsection'."""
    c = clean(e.get('class') or '') if isinstance(e.tag, str) else ''
    return c[:-2] if c.endswith('-e') else c


def not_in_force(c: str) -> bool:
    """Shaded text of amendments not yet in force ('Ysection', 'Yheadnote', 'YprocPnote', 'YSsubsection', ...), and
    the notes announcing them ('Pnote')."""
    return c.startswith('Y') or c == 'Pnote'


HEADINGS = {'partnum': 2, 'heading1': 3, 'heading2': 3, 'heading3': 4, 'headingx': 4, 'headnote': 5,
            'headnoteitalic': 5}
# Skipped: the table-of-contents heading and skip link, the separator line, and the publisher's 'Caution' notice that
# a version is not an official copy (two versions of the Employment Standards Act, 2021, with retroactive provisions
# not incorporated; REPRODUCE.md lists them).
SKIP = {'toc tocExpandable', 'toc', 'line', 'Caution'}


def text_of(e) -> str:
    """An element's text as the page shows it, line breaks as spaces; images and scripts have none."""
    parts = []

    def walk(x):
        if not isinstance(x.tag, str):
            return
        if x.tag in ('script', 'style'):
            return
        if x.tag == 'br':
            parts.append(' ')
        parts.append(x.text or '')
        for c in x:
            walk(c)
            parts.append(c.tail or '')
        if x.tag in ('p', 'td', 'th', 'div', 'tr'):
            parts.append(' ')
    parts.append(e.text or '')
    for c in e:
        walk(c)
        parts.append(c.tail or '')
    return clean(''.join(parts))


def table_lines(t) -> list[str]:
    """A table as one line per row, the cells separated by ' | ' (empty cells dropped). Nested tables are read as part
    of their cell."""
    out = []
    for tr in t.iter('tr'):
        if tr.getparent() is not None and any(a.tag == 'tr' for a in tr.iterancestors()):
            continue
        cells = [text_of(td) for td in tr if isinstance(td.tag, str) and td.tag in ('td', 'th')]
        row = ' | '.join(c for c in cells if c)
        if row:
            out.append(row)
    return out


SECNUM = re.compile(r'(\d+(?:\.\d+)*)\.?(?: ?[-–] ?(\d+(?:\.\d+)*)\.?)?(?= |$)')


def section_number(p) -> tuple[str, str] | None:
    """The number a 'section' paragraph begins with, in bold ('38 ', '1.', '247.-260.'), as (first, last); None for a
    'section' paragraph that continues a section (words after its list of clauses)."""
    if (p.text or '').strip():
        return None
    first = None
    for c in p:
        if not isinstance(c.tag, str):
            continue
        if c.tag == 'a' and not clean(c.text_content()):
            if (c.tail or '').strip():
                return None
            continue
        first = c
        break
    if first is None or first.tag not in ('b', 'a'):     # the number is in bold, or (2014-2016 pages) a link
        return None
    m = SECNUM.match(text_of(p))
    if not m:
        return None
    return m.group(1), m.group(2) or ''


def section_key(first: str, last: str) -> str:
    """'4.01' -> 's-004.01': the section number, its whole part padded to three digits so files sort in order; a group
    printed as one ('247.-260. Omitted') -> 's-247-260'."""
    def one(n):
        head, _, rest = n.partition('.')
        return f'{int(head):03d}' + (f'.{rest}' if rest else '')
    return 's-' + one(first) + (f'-{one(last)}' if last else '')


def schedule_key(p) -> tuple[str, str]:
    """A schedule's file key and label from its heading: 'SCHEDULE <br> Certificate of Justice' -> ('schedule',
    'Schedule'); 'SCHEDULE 1 <br> ...' -> ('schedule-1', 'Schedule 1')."""
    label = clean((p.text or '') + ''.join(clean(c.text_content()) + ' ' + (c.tail or '') if c.tag != 'br' else '\n'
                                           for c in p if isinstance(c.tag, str)).split('\n')[0])
    m = re.fullmatch(r'(?i)schedule(?: ([0-9]+(?:\.[0-9]+)*[A-Z]?|[A-Z](?:\.[0-9]+)?))?(?: .*)?', label)
    if not m:
        raise SystemExit(f'unexpected schedule heading {label!r}')
    n = m.group(1)
    return ('schedule' + (f'-{n.lower()}' if n else '')), ('Schedule' + (f' {n}' if n else ''))


CITE = re.compile(r'(R\.S\.O\. |S\.O\. )?(\d{4}), c\. ?([0-9]+|[A-Z]\.?[0-9]+(?:\.[0-9]+)?)(?=[,.;: )]|$)')


def laws_in(text: str) -> list[str]:
    """The laws a citation names: '2009, c. 5, s. 8.' -> ['S.O. 2009, c. 5']; 'R.S.O. 1990, c. H.8, s. 39 (1).' ->
    ['R.S.O. 1990, c. H.8']; '2002, c. 17, Sched. F, Table; 2005, c. 31' -> both."""
    out = []
    for m in CITE.finditer(text.replace(' ', ' ')):
        series = 'R.S.O.' if (m.group(1) or '').startswith('R') else 'S.O.'
        k = f'{series} {m.group(2)}, c. {m.group(3)}'
        if k not in out:
            out.append(k)
    return out


AMEND = re.compile(r'((?:R\.S\.O\. )?\d{4}, c\. ?[0-9A-Z.]+[^;]*?) ?[-–] ?(\d{1,2}/\d{1,2}/\d{4}|not in force)')


def amendment_entries(text: str) -> list[tuple[str, str]]:
    """'2009, c. 5, s. 8 - 03/10/2009; 2021, c. 26, Sched. 1, s. 3 - not in force - see: ...' -> [('S.O. 2009, c. 5',
    '2009-10-03'), ('S.O. 2021, c. 26', '')]: each amending law in a section's amendment list, with the day (d/m/y on
    the page) it took effect there, or '' when not in force."""
    out = []
    for m in AMEND.finditer(clean(text).replace('see: ', '')):
        laws = laws_in(m.group(1))
        if not laws:
            continue
        day = ''
        if m.group(2) != 'not in force':
            d, mo, y = (int(x) for x in m.group(2).split('/'))
            day = dt.date(y, mo, d).isoformat()
        out.append((laws[0], day))
    return out


def read_version(d: dict) -> dict:
    """One version as units in document order: 'intro' (short title, chapter and anything before the first heading or
    section), each section with the headings that open it, and each schedule. Each unit keeps its lines, the laws its
    citations name, and the entries of its amendment list."""
    doc = lhtml.fromstring(d['content'])
    if doc.tag != 'div':
        raise SystemExit('page layout changed: no single top-level div')
    units: dict[str, dict] = {}
    order: list[str] = []

    def unit(key: str, label: str) -> dict:
        if key in units:
            raise SystemExit(f'duplicate unit {key}')
        u = {'key': key, 'label': label, 'lines': [], 'cites': [], 'amend': [], 'html': []}
        units[key] = u
        order.append(key)
        return u

    intro = unit('intro', 'Title')
    for f in ('shortTitle', 'chapter'):
        if d.get(f):
            t = text_of(lhtml.fromstring(d[f]))
            if t:
                intro['lines'].append(('# ' if f == 'shortTitle' else '') + t)
    cur = intro
    pending: list[str] = []
    old = 'e-suffix' if re.search(r'class="(?:headnote|section|subsection)-e"', d['content']) else 'new'
    toc_done = False
    def body(x):
        """The page's paragraphs in order. Some pages close the 'WordSection1' div early (unbalanced tags), so the
        parser nests part of the text in it and the rest after it: both are read, in order."""
        for e in x:
            if isinstance(e.tag, str) and e.tag == 'div' and 'WordSection' in (e.get('class') or ''):
                yield from body(e)
            else:
                yield e
    for e in body(doc):
        if not isinstance(e.tag, str):
            continue
        c = cls_of(e)
        if e.tag in ('div', 'center') and not toc_done and len(order) == 1:     # the table of contents
            if e.xpath('.//*[contains(@class, "TOC")]'):
                toc_done = True
                continue
        if e.tag in ('table', 'center', 'div'):
            if pending:
                cur['lines'].extend(pending)
                pending = []
            cur['lines'].extend(table_lines(e))
            cur['html'].append(e)
            continue
        if e.tag != 'p':
            raise SystemExit(f'unexpected element {e.tag}')
        if c in SKIP:
            continue
        if not_in_force(c):
            if old == 'e-suffix':      # the older pages print the headnote of a section not in force unshaded
                pending = [p for p in pending if not p.startswith('##### ')]
            continue
        if 'amendments' in c and c.startswith('footnoteLeft'):
            if 'amendments-heading' not in c:
                cur['amend'].extend(amendment_entries(e.text_content()))
            continue
        t = text_of(e)
        if not t:
            continue
        if c in HEADINGS:
            pending.append('#' * HEADINGS[c] + ' ' + t)
            continue
        if c == 'section':
            num = section_number(e)
            if num:
                k = section_key(*num)
                label = 's. ' + num[0] + (f'-{num[1]}' if num[1] else '')
                if k in units:      # the act numbers two sections the same (s. 206 of the Highway Traffic Act, 2020-21)
                    k, label = k + '-b', label + ' (second)'
                cur = unit(k, label)
        elif c == 'schedule':
            k, label = schedule_key(e)
            cur = unit(k, label)
            t = '## ' + t
        cur['lines'].extend(pending)
        pending = []
        cur['lines'].append(t)
        cur['html'].append(e)
    if pending:
        cur['lines'].extend(pending)
    for k in order:
        u = units[k]
        u['text'] = '\n\n'.join(u['lines']) + '\n'
        cites = []
        for e in u['html']:
            for s in e.xpath('.//span[@class="citation"][not(ancestor::span[@class="citation"])]'):
                cites += laws_in(clean(s.text_content()))
        u['cites'] = sorted(set(cites))
        del u['html']
    if not units['intro']['lines']:
        raise SystemExit('no title')
    return {'units': units, 'order': order, 'format': old}


# ---------------------------------------------------------------- laws

def law_order(k: str) -> tuple:
    """Laws in order: the Revised Statutes, then statutes by year and chapter."""
    m = re.fullmatch(r'(R\.S\.O\.|S\.O\.) (\d{4}), c\. ([0-9]*)(.*)', k)
    return (0 if m.group(1) == 'R.S.O.' else 1, int(m.group(2)), int(m.group(3) or 0), m.group(4))


def law_slug(k: str) -> str:
    """'S.O. 2009, c. 5' -> 'so-2009-c5'; 'R.S.O. 1990, c. H.8' -> 'rso-1990-ch-8'."""
    s = k.lower().replace('r.s.o.', 'rso').replace('s.o.', 'so').replace('c. ', 'c')
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def source_id(k: str) -> str | None:
    """The e-Laws identifier of an annual statute as enacted ('S.O. 2009, c. 5' -> 's09005'); None for a revised statute."""
    m = re.fullmatch(r'S\.O\. (\d{4}), c\. (\d+)', k)
    return f's{m.group(1)[2:]}{int(m.group(2)):03d}' if m else None


MONTHS = {m: i for i, m in enumerate(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
                                       'September', 'October', 'November', 'December'], 1)}


def law_meta(k: str, offline: bool) -> dict:
    """An amending act's title and day of Royal Assent, from its source text on e-Laws ('Road Safety Act, 2009, S.O.
    2009, c. 5 - Bill 126', 'Assented to April 23, 2009')."""
    meta = {'key': k, 'title': '', 'assented': '', 'url': '', 'kind': 'Act of the Legislative Assembly of Ontario'}
    sid = source_id(k)
    if not sid:
        return meta
    d = fetch_json(f'en/doc-search/statute/{sid.upper()}', offline)
    if not d or not d.get('title'):
        return meta
    title = clean(re.sub(r' - Bill \S+$', '', clean(d['title'])))
    title = re.sub(r',? S\.O\. \d{4}, c\. \d+$', '', title)
    meta['title'] = title
    m = re.search(r'Assented to (\w+) (\d{1,2}), (\d{4})', clean(d.get('description') or ''))
    if m and m.group(1) in MONTHS:
        meta['assented'] = dt.date(int(m.group(3)), MONTHS[m.group(1)], int(m.group(2))).isoformat()
    meta['url'] = f'{SITE}/statute/{sid}'
    return meta


# ---------------------------------------------------------------- one act: versions, changes, causes

def unit_order(key: str) -> tuple:
    if key == 'intro':
        return (0, 0, ())
    m = re.fullmatch(r's-(\d+)((?:\.\d+)*)(-.*)?', key)
    if m:
        return (1, int(m.group(1)), tuple(int(x) for x in m.group(2).split('.')[1:]), m.group(3) or '')
    if key.startswith('schedule'):
        rest = key[len('schedule'):].lstrip('-')
        n = re.match(r'\d+', rest)
        return (2, int(n.group(0)) if n else 0, (rest,))
    return (3, 0, (key,))


def file_name(key: str) -> str:
    return f'{key}.md'


def build_act(act: dict, offline: bool) -> dict:
    versions = version_list(act, offline)
    for v in versions:
        body = fetch(f'{API}/{v["api"]}', offline)
        v['sha256'] = hashlib.sha256(body).hexdigest()
        parsed = read_version(json.loads(body))
        if sorted(parsed['order'], key=unit_order) != parsed['order']:
            bad = [(a, b) for a, b in zip(parsed['order'], parsed['order'][1:]) if unit_order(a) > unit_order(b)]
            raise SystemExit(f'{act["id"]} {v["from"]}: the file order differs from the order on the page: {bad[:3]}')
        v['units'] = parsed['units']
        v['format'] = parsed['format']
    changes = []
    problems = []
    own = set(act['own'])
    seen: dict[str, set[str]] = {}
    for i, (prev, cur) in enumerate(zip(versions, versions[1:])):
        if i:
            for k, u in versions[i - 1]['units'].items():
                seen.setdefault(k, set()).add(u['text'])
        day = cur['from']
        allkeys = sorted(set(prev['units']) | set(cur['units']), key=unit_order)
        changed = [k for k in allkeys if (prev['units'].get(k) or {}).get('text') != (cur['units'].get(k) or {}).get('text')]
        new: dict[str, set[str]] = {}
        how: dict[str, str] = {}
        layout: dict[str, bool] = {}
        for k in changed:
            p, c = prev['units'].get(k), cur['units'].get(k)
            listed = {law for law, d in (c['amend'] if c else []) if d == day} - own
            cited_all = set(c['cites'] if c else []) - set(p['cites'] if p else [])
            cited = cited_all - own
            if listed:
                new[k], how[k] = listed, 'amendment list'
            elif cited:
                new[k], how[k] = cited, 'citation'
            else:   # only the act's own citation is new: its own provisions taking effect (commencement)
                new[k], how[k] = cited_all, 'citation of the act itself'
            layout[k] = bool(p and c and canon(p['text']) == canon(c['text']))
        L = sorted({law for k in changed for law in new[k]}, key=law_order)
        cause: dict[str, str] = {}
        why: dict[str, str] = {}
        for k in changed:
            c = cur['units'].get(k)
            if len(new[k]) == 1:
                cause[k], why[k] = next(iter(new[k])), how[k]
            elif len(new[k]) > 1:
                cause[k], why[k] = 'candidates', f'its {how[k]} names two or more laws new on this day'
            elif layout[k]:
                cause[k], why[k] = 'layout', 'same letters and digits; layout, punctuation or case only'
            elif len(L) == 1:
                cause[k], why[k] = L[0], 'date only'
            elif L:
                cause[k], why[k] = 'candidates', 'no new citation; two or more laws are new that day'
            else:
                cause[k], why[k] = 'unexplained', 'no new citation in it or anywhere in the version'
            if c and c['text'] in seen.get(k, ()) and why[k] not in ('amendment list', 'citation',
                                                                       'citation of the act itself'):
                why[k] += '; the text equals an earlier version of it'
        for k in changed:
            if cause[k] in ('unexplained', 'candidates'):
                problems.append(f'{day} {k} ({why[k]})')
        groups: dict[str, list[str]] = {}
        for k in changed:
            groups.setdefault(cause[k], []).append(k)
        cand = sorted({law for k in groups.get('candidates', []) for law in (new[k] or set(L))}, key=law_order)
        changes.append({'from': day, 'url': cur['url'], 'laws': L, 'groups': groups, 'why': why, 'new': new,
                        'candidates': cand, 'prev': prev, 'cur': cur})
    title = versions[-1]['units']['intro']['lines'][0].lstrip('# ').strip()
    return {'act': act, 'versions': versions, 'changes': changes, 'problems': problems, 'title': title}


# ---------------------------------------------------------------- the git repository

def git(repo: Path, *args: str, env: dict | None = None, input: bytes | None = None) -> str:
    out = subprocess.run(['git', *args], cwd=repo, capture_output=True, env=env, input=input)
    if out.returncode:
        raise SystemExit(f'git {" ".join(args)} failed: {out.stderr.decode("utf-8", "replace")}')
    return out.stdout.decode('utf-8')


def nth_sunday(year: int, month: int, n: int) -> dt.date:
    d = dt.date(year, month, 1)
    d += dt.timedelta(days=(6 - d.weekday()) % 7)
    return d + dt.timedelta(weeks=n - 1)


def last_sunday(year: int, month: int) -> dt.date:
    d = (dt.date(year, month + 1, 1) if month < 12 else dt.date(year + 1, 1, 1)) - dt.timedelta(days=1)
    return d - dt.timedelta(days=(d.weekday() + 1) % 7)


def toronto_offset(day: dt.date) -> int:
    """Hours from UTC at noon on a day in Toronto (written out, because this machine has no tz database). Eastern
    Standard Time, UTC-5; daylight time, UTC-4: from the second Sunday in March to the first Sunday in November since
    2007; from the first Sunday in April to the last Sunday in October from 1987 to 2006; from the last Sunday in April
    to the last Sunday in October from 1974 to 1986 (the record starts in 2002). Clocks change at 2:00, so noon on the
    first day is daylight time and noon on the last day is standard time."""
    y = day.year
    if y >= 2007:
        start, end = nth_sunday(y, 3, 2), nth_sunday(y, 11, 1)
    elif y >= 1987:
        start, end = nth_sunday(y, 4, 1), last_sunday(y, 10)
    else:
        start, end = last_sunday(y, 4), last_sunday(y, 10)
    return -4 if start <= day < end else -5


def commit_date(day: str) -> str:
    """Noon in Toronto on the day, as git's raw '<seconds> <zone>'."""
    d = dt.date.fromisoformat(day)
    off = toronto_offset(d)
    stamp = int(dt.datetime(d.year, d.month, d.day, 12, tzinfo=dt.timezone(dt.timedelta(hours=off))).timestamp())
    return f'{stamp} -0{-off}00'


def author_of(law: str) -> tuple[str, str]:
    return law, f'{law_slug(law)}@ontario.invalid'


def tag_of(law: str) -> str:
    """'S.O. 2009, c. 5' -> 'so/2009-c5'."""
    head, _, rest = law_slug(law).partition('-')
    return f'{head}/{rest}'


def change_kind(prev: dict | None, cur: dict | None) -> str:
    if prev is None:
        return 'Added'
    if cur is None:
        return 'Removed from the consolidation'
    rep = re.compile(r'\bRepealed\b')
    if rep.search(cur['text']) and len(cur['text']) < 400 and not (rep.search(prev['text']) and len(prev['text']) < 400):
        return 'Repealed'
    return 'Amended'


def plan_commits(built: list[dict]) -> list[dict]:
    """Every commit, in the order the changes took effect. On a day: the first version of each act; then one commit
    per amending law (laws in order of citation), covering every act of the record it changed that day; then changes
    with two candidate laws, changes nothing explains, and changes of layout only, per act."""
    items: dict[tuple, dict] = {}
    for ai, b in enumerate(built):
        day0 = b['versions'][0]['from']
        items[(day0, 0, (ai,), '')] = {'kind': 'start', 'day': day0, 'parts': [(b, None)]}
        for ch in b['changes']:
            laws = [l for l in ch['groups'] if l not in ('unexplained', 'candidates', 'layout')]
            for law in laws:
                key = (ch['from'], 1, law_order(law), law)
                items.setdefault(key, {'kind': 'law', 'day': ch['from'], 'law': law, 'parts': []})['parts'].append((b, ch))
            for rank, kind in ((2, 'candidates'), (3, 'unexplained'), (4, 'layout')):
                if kind in ch['groups']:
                    items[(ch['from'], rank, (ai,), '')] = {'kind': kind, 'day': ch['from'], 'parts': [(b, ch)]}
            if not ch['groups']:
                items[(ch['from'], 5, (ai,), '')] = {'kind': 'nochange', 'day': ch['from'], 'parts': [(b, ch)]}
    return [items[k] for k in sorted(items)]


def provision_label(b: dict, u: dict) -> str:
    return f'{b["act"]["id"]} {u["label"]}'


def short_list(names: list[str], limit: int = 6) -> str:
    return ', '.join(names) if len(names) <= limit else f'{", ".join(names[:limit])} and {len(names) - limit} more'


def subject_for(parts: list[tuple[dict, list[str]]], tail: str) -> str:
    """'90h08: s. 38, s. 39 (S.O. 2009, c. 5)', shortened to counts when longer than 72 characters."""
    def full():
        return '; '.join(f'{b["act"]["id"]}: {", ".join(labels)}' for b, labels in parts)

    def counts():
        return '; '.join(f'{b["act"]["id"]}: {len(labels)} provision{"s" if len(labels) != 1 else ""}' for b, labels in parts)
    s = f'{full()} ({tail})'
    if len(s) <= 72:
        return s
    s = f'{counts()} ({tail})'
    return s if len(s) <= 72 else counts()


def wrap(text: str, width: int = 100) -> list[str]:
    out, line = [], ''
    for w in text.split(' '):
        if line and len(line) + 1 + len(w) > width:
            out.append(line)
            line = w
        else:
            line = f'{line} {w}' if line else w
    return out + ([line] if line else [])


def change_message(item: dict, laws: dict):
    """The author, message lines, trailers and the (act, unit key, new unit) writes of one commit."""
    kind = item['kind']
    day = item['day']
    writes, listing, affecting, subject_parts, consolidated = [], [], [], [], []
    evidence: dict[str, list[str]] = {}
    for b, ch in item['parts']:
        group = item.get('law') if kind == 'law' else kind
        keys = sorted(ch['groups'].get(group, []), key=unit_order) if kind != 'nochange' else []
        consolidated.append(ch['url'])
        by_kind: dict[str, list[str]] = {}
        labels = []
        for k in keys:
            p, c = ch['prev']['units'].get(k), ch['cur']['units'].get(k)
            u = c or p
            labels.append(u['label'])
            by_kind.setdefault(change_kind(p, c), []).append(u['label'])
            affecting.append(provision_label(b, u))
            writes.append((b, k, c))
            evidence.setdefault(ch['why'][k], []).append(provision_label(b, u))
        subject_parts.append((b, labels))
        for name in ('Added', 'Amended', 'Repealed', 'Removed from the consolidation'):
            if name in by_kind:
                listing += wrap(f'{b["act"]["id"]} ({b["act"]["short"]}), {name.lower()}: {", ".join(by_kind[name])}')
    trailers = []
    if kind == 'law':
        law = item['law']
        lm = laws[law]
        author = author_of(law)
        msg = [subject_for(subject_parts, law), '']
        if lm['title']:
            msg += [lm['title'], '']
        msg += listing + ['']
        for w in sorted(evidence):
            if w.startswith('amendment list'):
                trailers.append('Evidence: the amendment list of the section gives this law with this day in force')
            elif w.startswith('citation'):
                trailers.append('Evidence: citation of this law new in the provision in the version from this day')
        for w, provs in sorted(evidence.items()):
            if w.startswith('date only'):
                msg += wrap('These provisions changed on this day, but neither their citations nor their amendment '
                            'lists name a new law. This law is the only one the version from this day newly names, so '
                            f'the change is credited to it by date only: {short_list(provs, 20)}.') + ['']
                for p in provs:
                    trailers.append(f'Evidence: date only for {p}')
            if 'equals an earlier version' in w:
                msg += wrap('The new text equals an earlier version of the provision (a reprint of older text): '
                            f'{short_list(provs, 20)}.') + ['']
        trailers.append(f'Kind: {lm["kind"]}')
        if lm['assented']:
            trailers.append(f'Enacted: {lm["assented"]}')
            if day < lm['assented']:
                msg += wrap(f'Note: the version with this change applies from {day}, before the law received Royal '
                            f'Assent ({lm["assented"]}). The law reaches back; the day is kept as the source gives it.') + ['']
                trailers.append('Date-note: in force before Royal Assent (retroactive)')
        trailers.append(f'In-force: {day}')
        if lm['url']:
            trailers.append(f'Source: {lm["url"]}')
    elif kind == 'candidates':
        author = PUBLISHER
        names = [c for b, ch in item['parts'] for c in ch['candidates']]
        msg = [subject_for(subject_parts, 'two or more laws, credited to none'), '']
        msg += wrap(f'These provisions changed on this day, and the laws that may have changed them are '
                    f'{", ".join(names)}. The consolidation does not say which law made which change, so the change is '
                    'credited to none of them.') + [''] + listing + ['']
        for w, provs in sorted(evidence.items()):
            for p in provs:
                trailers.append(f'Evidence: {w} ({p})')
        trailers.append(f'In-force: {day}')
        trailers += [f'Candidate: {n}' for n in names]
    elif kind == 'unexplained':
        author = PUBLISHER
        msg = [subject_for(subject_parts, 'no amending law named'), '']
        msg += wrap('The consolidated text of these provisions changed on this day, but nothing in the version from '
                    'this day names a new law for it. The change is credited to no law: it is the publisher\'s.') + ['']
        msg += listing + ['']
        for w, provs in sorted(evidence.items()):
            if 'equals an earlier version' in w:
                msg += wrap('The new text equals an earlier version of the provision (a reprint of older text): '
                            f'{short_list(provs, 20)}.') + ['']
        trailers.append(f'In-force: {day}')
        trailers.append('Kind: editorial (publisher)')
    elif kind == 'layout':
        author = PUBLISHER
        msg = [subject_for(subject_parts, 'layout only'), '']
        msg += wrap('The consolidation prints these provisions differently from this day (spacing, punctuation, case '
                    'or section-number style), with the same letters and digits, and no new law is named for them. '
                    'This is the publisher\'s change, not a law\'s.') + [''] + listing + ['']
        trailers.append(f'In-force: {day}')
        trailers.append('Kind: layout (publisher)')
    else:   # nochange
        author = PUBLISHER
        b = item['parts'][0][0]
        msg = [f'{b["act"]["id"]}: new version, no change in the English text in force', '']
        msg += wrap(f'e-Laws starts a new version of the {b["act"]["short"]} on this day, but its English text in force '
                    'is the same as in the version before. (The change may be in text not yet in force, in a note, or '
                    'in the French text.) This commit changes no file; it marks the day.') + ['']
        trailers.append(f'In-force: {day}')
        trailers.append('Kind: version without a change in the English text in force (publisher)')
    for a in affecting:
        trailers.append(f'Affecting: {a}')
    for u in consolidated:
        trailers.append(f'Consolidated: {u}')
    return author, msg, trailers, writes


def start_message(b: dict):
    v = b['versions'][0]
    day = v['from']
    msg = [f'{b["act"]["id"]}: {b["title"]}, as consolidated on {day}', '']
    msg += wrap(f'The text in force in the first point-in-time version e-Laws publishes, from {day}. It is the act as '
                'enacted and amended up to then; e-Laws has no earlier versions, so the lines of this commit are '
                'credited to the publisher, not to a law. The citations at the end of each subsection name the laws '
                'that made it.') + ['']
    trailers = [f'In-force: {day}', 'Kind: first published version (publisher)', f'Consolidated: {v["url"]}']
    return PUBLISHER, msg, trailers


def write_repo(repo: Path, built: list[dict], laws: dict, docs: Path, today: str):
    """Writes the history with one `git fast-import`, then the documentation commit in the working tree."""
    remote = None
    if (repo / '.git').exists():
        out = subprocess.run(['git', 'remote', 'get-url', 'origin'], cwd=repo, capture_output=True, text=True)
        remote = out.stdout.strip() or None
    elif repo.exists() and any(repo.iterdir()):
        raise SystemExit(f'{repo} is not empty and not a git repository; refusing to write into it')

    def force(fn, path, _exc):
        os.chmod(path, 0o700)
        fn(path)
    if repo.exists():
        for p in repo.iterdir():
            shutil.rmtree(p, onexc=force) if p.is_dir() else p.unlink()
    repo.mkdir(parents=True, exist_ok=True)
    git(repo, 'init', '-q', '-b', 'main')
    git(repo, 'config', 'core.autocrlf', 'false')
    if remote:
        git(repo, 'remote', 'add', 'origin', remote)

    tags: dict[str, int] = {}
    law_days: dict[str, list[tuple[str, int]]] = {}
    log = []
    stream = io.BytesIO()

    def data(b: bytes):
        stream.write(b'data %d\n' % len(b) + b + b'\n')

    for mark, item in enumerate(plan_commits(built), 1):
        day = item['day']
        if day > today:
            raise SystemExit(f'a version in force after the build day ({day}); the record has no "future" branch')
        if item['kind'] == 'start':
            b = item['parts'][0][0]
            writes = [(b, k, u) for k, u in b['versions'][0]['units'].items()]
            author, msg, trailers = start_message(b)
            slugs = [b['act']['id']]
        else:
            author, msg, trailers, writes = change_message(item, laws)
            slugs = [b['act']['id'] for b, _ in item['parts']]
        when = commit_date(day)
        text = '\n'.join(msg).rstrip('\n') + '\n\n' + '\n'.join(trailers) + '\n'
        stream.write(f'commit refs/heads/main\nmark :{mark}\n'
                     f'author {author[0]} <{author[1]}> {when}\n'
                     f'committer {COMMITTER[0]} <{COMMITTER[1]}> {when}\n'.encode('utf-8'))
        data(text.encode('utf-8'))
        for b, k, u in writes:
            path = f'{b["act"]["id"]}/{file_name(k)}'
            if u is None:
                stream.write(f'D {path}\n'.encode('utf-8'))
            else:
                stream.write(f'M 100644 inline {path}\n'.encode('utf-8'))
                data(u['text'].encode('utf-8'))
        stream.write(b'\n')
        for s_ in slugs:
            tags[f'{s_}/{day}'] = mark
        if item['kind'] == 'law':
            law_days.setdefault(item['law'], []).append((day, mark))
        log.append({'day': day, 'kind': item['kind'], 'law': item.get('law'), 'author': author[0],
                    'units': len(writes), 'slugs': slugs})
    for law, days in law_days.items():
        if len(days) == 1:
            tags[tag_of(law)] = days[0][1]
        else:
            for day, mark in days:
                tags[f'{tag_of(law)}/{day}'] = mark
    for name in sorted(tags):
        stream.write(f'reset refs/tags/{name}\nfrom :{tags[name]}\n\n'.encode('utf-8'))
    out = subprocess.run(['git', 'fast-import', '--quiet', '--date-format=raw', '--done'], cwd=repo,
                         input=stream.getvalue() + b'done\n', capture_output=True)
    if out.returncode:
        raise SystemExit(f'git fast-import failed: {out.stderr.decode(errors="replace")}')
    git(repo, 'checkout', '-q', '-f', 'main')
    for p in sorted(docs.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:
            dest = repo / p.relative_to(docs)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(p.read_bytes())
    for name in ('build.py', 'fetchlib.py', 'fetch_versions.py', 'reproduce.py', 'check_repo.py', 'test_repo.py'):
        if (HERE / name).exists():
            (repo / 'tools' / name).write_bytes((HERE / name).read_bytes())
    write_tables(repo, built, laws)
    if (HERE / 'reproduce.py').exists():
        from reproduce import write_manifest, write_reproduce
        write_manifest(repo, built, laws, today)
        write_reproduce(repo, built, laws, log, tags, REQUESTS, today)
    git(repo, 'add', '-A')
    when = commit_date(today)
    env = {**os.environ, 'GIT_AUTHOR_NAME': COMMITTER[0], 'GIT_AUTHOR_EMAIL': COMMITTER[1], 'GIT_AUTHOR_DATE': when,
           'GIT_COMMITTER_NAME': COMMITTER[0], 'GIT_COMMITTER_EMAIL': COMMITTER[1], 'GIT_COMMITTER_DATE': when}
    git(repo, 'commit', '-q', '--cleanup=verbatim', '-F', '-', env=env,
        input=(f'Documentation, tables, tools and REPRODUCE.md\n\nNo law text changes.\n\nIn-force: {today}\n'
               'Kind: documentation\n').encode('utf-8'))
    return log, tags


def write_tables(repo: Path, built: list[dict], laws: dict):
    out = []
    for b in built:
        for ch in b['changes']:
            for law in ch['laws']:
                lm = laws[law]
                n = len(ch['groups'].get(law, []))
                out.append({'act': b['act']['id'], 'law': law, 'title': lm['title'], 'kind': lm['kind'],
                            'assented': lm['assented'], 'in_force': ch['from'], 'provisions': n,
                            'note': '' if n else 'named only by provisions changed together with another law',
                            'source': lm['url']})
    out.sort(key=lambda r: (r['in_force'], r['act'], law_order(r['law'])))
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(out[0]), lineterminator='\n')
    w.writeheader()
    w.writerows(out)
    (repo / 'laws.csv').write_text(buf.getvalue(), encoding='utf-8', newline='\n')
    for b in built:
        act = b['act']
        last = b['versions'][-1]
        counts: dict[str, int] = {}
        lastday: dict[str, str] = {}
        for ch in b['changes']:
            for g, keys in ch['groups'].items():
                if g == 'layout':
                    continue
                for k in keys:
                    counts[k] = counts.get(k, 0) + 1
                    lastday[k] = ch['from']
        out2 = [f'# {b["title"]} ({act["id"]})', '', f'<{SITE}/statute/{act["id"]}>', '',
                f'{len(b["versions"])} point-in-time versions on e-Laws, from {b["versions"][0]["from"]} '
                f'(the latest from {last["from"]}). Changes counted without layout-only changes.', '',
                '| Provision | File | Changes | Last changed |', '| --- | --- | ---: | --- |']
        for k in sorted(last['units'], key=unit_order):
            u = last['units'][k]
            out2.append(f'| {u["label"]} | [{file_name(k)}]({file_name(k)}) | {counts.get(k, 0)} | {lastday.get(k, "")} |')
        (repo / act['id'] / 'README.md').write_text('\n'.join(out2) + '\n', encoding='utf-8', newline='\n')


# ---------------------------------------------------------------- main

def build_all(offline: bool):
    built = [build_act(a, offline) for a in ACTS]
    keys = sorted({l for b in built for ch in b['changes'] for l in ch['laws'] + ch['candidates']}, key=law_order)
    laws = {k: law_meta(k, offline) for k in keys}
    return built, laws


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=str(ROOT.parent / 'canada-ontario-law'))
    ap.add_argument('--offline', action='store_true', help='read only the cache; fail on anything not cached')
    ap.add_argument('--today', required=True, help='the build day (the documentation commit is dated on it)')
    ap.add_argument('--analyse', action='store_true', help='print the analysis and write nothing')
    ap.add_argument('--verify-rebuild', action='store_true',
                    help='build again into a temporary folder from the cache, compare every hash with --repo, and record the result')
    args = ap.parse_args()
    if args.verify_rebuild:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            out = subprocess.run([sys.executable, '-X', 'utf8', str(HERE / 'build.py'), '--offline', '--repo', tmp,
                                  '--today', args.today], capture_output=True, text=True)
            if out.returncode:
                raise SystemExit(out.stderr)

            def hashes(r):
                log = git(Path(r), 'log', '--format=%H', 'main').split()
                tags = dict(l.split(' ', 1)[::-1] for l in git(Path(r), 'show-ref', '--tags').split('\n') if l)
                return log, tags
            a, b = hashes(args.repo), hashes(tmp)
            same_history = a[0][1:] == b[0][1:]
            rec = {'identical': same_history and a[1] == b[1], 'history_tip': a[0][1], 'commits': len(a[0]) - 1,
                   'tags': len(a[1]), 'main_identical': a[0][0] == b[0][0], 'main': a[0][0], 'rebuilt_main': b[0][0]}
            print(json.dumps(rec, indent=1))
            p = HERE / 'verification.json'
            ver = json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
            ver['rebuild'] = {k: rec[k] for k in ('identical', 'history_tip', 'commits', 'tags')}
            p.write_text(json.dumps(ver, indent=1, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
            for f in Path(tmp).rglob('*'):
                os.chmod(f, 0o700)
            raise SystemExit(0 if rec['identical'] else 1)
    built, laws = build_all(args.offline)
    for b in built:
        n = sum(len(ks) for ch in b['changes'] for g, ks in ch['groups'].items() if g != 'layout')
        nl = sum(len(ch['groups'].get('layout', [])) for ch in b['changes'])
        print(f'{b["act"]["id"]}: {len(b["versions"])} versions {b["versions"][0]["from"]}..{b["versions"][-1]["from"]}, '
              f'{len(b["versions"][-1]["units"])} units, {n} unit changes (+{nl} layout only), '
              f'{len(b["problems"])} not credited to one law')
        for p in b['problems'][:40]:
            print('   ', p)
    if args.analyse:
        return
    log, tags = write_repo(Path(args.repo), built, laws, HERE / 'repo', args.today)
    print(f'repo: {len(log)} commits + 1 documentation commit, {len(tags)} tags -> {args.repo}')


if __name__ == '__main__':
    main()

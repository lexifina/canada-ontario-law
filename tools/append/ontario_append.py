"""Grows the published canada-ontario-law history append-only, with build.py's own parser, evidence rules, messages
and dates.

    python -X utf8 ontario_append.py --repo <bare clone> --today YYYY-MM-DD --acts 01m25,90c20 [--extend 90h08] [--dry-run]

The repository's main was first built by build.py for four acts (2026-10-29); since then it only grows by
fast-forward. Each run (a "batch") appends, after the published head:

- every act given with --acts that main does not hold yet, as one block: its first point-in-time version on e-Laws
  (credited to the enacting act when that version is the act as enacted, else a baseline by the publisher), then one
  commit per amending law per day, in the order the changes took effect (build.plan_commits over the batch's acts,
  so a law that changed several acts of the batch on one day is one commit);
- for each act given with --extend that main holds: the versions newer than the newest one main carries, as changes
  from that one. The act's files at main's head must equal that version exactly; otherwise nothing is appended for
  it (it would need a correction) and it is reported;
- one documentation commit (Lexifina): corpus.json, data/versions.json, laws.csv, data/uncertain.tsv,
  data/appended.json, the acts' README.md tables, and the appended-batches sections of README.md and REPRODUCE.md.

An act block is dated in its own order, so its dates run backwards from the commits above it: an "end block", which
the corpus standard allows (section 3.2, rule 6: an older act found later is appended as new commits, its files new
files). Readers date every version by its In-force trailer, never by commit order.

New commits carry the corpus standard's trailers (Kind: law / baseline / uncredited / printing / documentation,
Law-kind, Law, In-force, Enacted, Source, Text-source, Retroactive); the evidence trailers are build.py's.
Author dates: noon in Toronto on the in-force day (build.commit_date). Committer: Lexifina
<canada-ontario-law@lexifina.com>, at the published head's committer time plus one second per appended commit.
Tags: <act>/<in-force day> for each appended act-day, never moving one that exists; amending-law tags are not added
for appended commits (the law's existing tags stay where build.py put them).

Everything is read through build.py's cache; with --offline nothing is fetched.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _p in (HERE, HERE.parent):          # tools/append/build.py in the repository, or scripts/canada-ontario-law/build.py
    if (_p / 'build.py').exists():
        sys.path.insert(0, str(_p))
        break
import build as B  # noqa: E402

SITE = B.SITE
DOC_FILES = ('README.md', 'REPRODUCE.md', 'corpus.json', 'laws.csv', 'data/versions.json', 'data/uncertain.tsv',
             'data/appended.json')
MARK = '<!-- appended-batches -->'


def git(repo: Path, *args: str, input: bytes | None = None, check: bool = True) -> str:
    out = subprocess.run(['git', *args], cwd=repo, capture_output=True, input=input)
    if check and out.returncode:
        raise SystemExit(f'git {" ".join(args)} failed: {out.stderr.decode("utf-8", "replace")[-2000:]}')
    return out.stdout.decode('utf-8', 'replace')


def show(repo: Path, ref: str, path: str) -> str | None:
    out = subprocess.run(['git', 'show', f'{ref}:{path}'], cwd=repo, capture_output=True)
    return out.stdout.decode('utf-8') if out.returncode == 0 else None


def acts_in(repo: Path, ref: str = 'main') -> set[str]:
    """The acts main holds: the e-Laws ids data/versions.json lists (an act repealed in the record has no folder)."""
    v = json.loads(show(repo, ref, 'data/versions.json') or '{"acts": []}')
    return {a['id'] for a in v['acts']}


def last_day(repo: Path, act: str, ref: str = 'main') -> str:
    """The newest In-force day of the act's commits on main."""
    out = git(repo, 'log', '--format=%(trailers:key=In-force,valueonly,separator=)', ref, '--', f'{act}/')
    days = [l.strip() for l in out.splitlines() if l.strip()]
    return max(days) if days else ''


def files_at(repo: Path, ref: str, act: str) -> dict[str, str]:
    """The act's provision files (not its README.md) at ref."""
    out = git(repo, 'ls-tree', '-r', ref, f'{act}/')
    blobs = []
    for line in out.splitlines():
        info, f = line.split('\t', 1)
        if f.endswith('.md') and not f.endswith('/README.md'):
            blobs.append((f[len(act) + 1:], info.split()[2]))
    if not blobs:
        return {}
    data = subprocess.run(['git', 'cat-file', '--batch'], cwd=repo, capture_output=True,
                          input=''.join(f'{s}\n' for _, s in blobs).encode()).stdout
    res, pos = {}, 0
    for name, _ in blobs:
        nl = data.index(b'\n', pos)
        size = int(data[pos:nl].split()[2])
        res[name] = data[nl + 1:nl + 1 + size].decode('utf-8')
        pos = nl + 1 + size + 1
    return res


# ---------------------------------------------------------------- trailers (corpus standard v1)

def standard(item: dict, trailers: list[str], author: tuple[str, str]) -> list[str]:
    """build.py's trailers in the corpus standard's words: one Kind of the eight, Law-kind and Law for a law,
    Text-source for the version's page (was Consolidated), Retroactive for a change in force before Royal Assent."""
    kind = item['kind']
    out = []
    day = item['day']
    for t in trailers:
        key, _, val = t.partition(': ')
        if key == 'Kind':
            continue
        if key == 'Consolidated':
            out.append(f'Text-source: {val}')
        elif key == 'Date-note':
            out.append(f'Retroactive: yes; the e-Laws version with this change applies from {day}, before the law '
                       'received Royal Assent')
        else:
            out.append(t)
    if author != B.PUBLISHER:
        head = ['Kind: law', 'Law-kind: act', f'Law: {author[0]}']
    elif kind == 'start':
        head = ['Kind: baseline', 'In-force-basis: e-Laws gives this day as the start of the act\'s first point-in-time '
                'version; the text existed before it']
    elif kind in ('candidates', 'unexplained'):
        head = ['Kind: unexplained']    # the standard's 'uncredited'; global-law's law.py reads this word today
    else:       # layout only, or a new version with no change in the English text in force
        head = ['Kind: printing']
    srcs = [t for t in out if t.startswith('Source: ')]
    if not srcs:
        acts = [b['act']['id'] for b, _ in item['parts']]
        out.append(f'Source: {SITE}/statute/{acts[0]}')
    return head + out


# ---------------------------------------------------------------- one batch

def build_batch(new_acts: list[dict], extend: dict[str, str], offline: bool, today: str, log=print):
    """Builds the acts (new ones whole; extended ones from the day after `extend[id]`). Returns (built, laws,
    skipped, deferred, refused): built acts to append, the laws they name, acts repealed before their first version,
    acts whose first version is after `today`, and extended acts whose base does not read back from main."""
    built, skipped, deferred = [], [], []
    for a in new_acts + [a for a in B.ACTS if a['id'] in extend]:
        b = B.build_act(a, offline)
        if b.get('skipped'):
            skipped.append(b)
            continue
        if a['id'] in extend:
            b['since'] = extend[a['id']]
        elif b['versions'][0]['from'] > today:
            deferred.append(a['id'])
            continue
        built.append(b)
        log(f'built {a["id"]}: {len(b["versions"])} versions')
    keys = {l for b in built for ch in b['changes'] for l in ch['laws'] + ch['candidates']}
    keys |= {b['act']['own'][0] for b in built if b['act']['own'] and B.source_id(b['act']['own'][0])}
    laws = {k: B.law_meta(k, offline) for k in sorted(keys, key=B.law_order)}
    for b in built:
        own = b['act']['own'][0] if b['act']['own'] else None
        v0 = b['versions'][0]
        if own and laws.get(own, {}).get('assented') and v0['from'] >= laws[own]['assented'] and v0['units'] and \
                all(set(u['cites']) <= set(b['act']['own']) for u in v0['units'].values()):
            b['enacted_by'] = own
    return built, laws, skipped, deferred


def plan(built: list[dict], today: str) -> list[dict]:
    """build.plan_commits, without what main already holds (an extended act's start and its changes up to `since`)
    and without anything in force after `today` (main holds no future; those versions wait for a later batch)."""
    out = []
    for item in B.plan_commits(built):
        if item['day'] > today:
            continue
        if item['kind'] == 'start':
            if item['parts'][0][0].get('since'):
                continue
            out.append(item)
            continue
        parts = [(b, ch) for b, ch in item['parts'] if not b.get('since') or ch['from'] > b['since']]
        if parts:
            out.append({**item, 'parts': parts})
    return out


def base_ok(repo: Path, b: dict) -> str:
    """For an extended act: '' when its files at main equal the version in force on `since`; else what differs."""
    since = b['since']
    base = [v for v in b['versions'] if v['from'] <= since][-1]
    want = {B.file_name(k): u['text'] for k, u in base['units'].items()}
    got = files_at(repo, 'main', b['act']['id'])
    if got == want:
        return ''
    diff = sorted(set(got) ^ set(want)) or [k for k in want if got.get(k) != want[k]]
    return f'main differs from v{base["n"]} ({base["from"]}): {diff[:5]}'


def write_history(repo: Path, items: list[dict], laws: dict, head: str) -> tuple[list[dict], dict[str, int], str]:
    """The batch's commits on top of `head` with one git fast-import. Returns (log, tags {name: mark}, stream)."""
    base_time = int(git(repo, 'log', '-1', '--format=%ct', head).strip())
    existing = set(git(repo, 'for-each-ref', '--format=%(refname:short)', 'refs/tags').split())
    stream = io.BytesIO()

    def data(b: bytes):
        stream.write(b'data %d\n' % len(b) + b + b'\n')
    tags: dict[str, int] = {}
    log = []
    for mark, item in enumerate(items, 1):
        day = item['day']
        if item['kind'] == 'start':
            b = item['parts'][0][0]
            writes = [(b, k, u) for k, u in b['versions'][0]['units'].items()]
            author, msg, trailers = B.start_message(b, laws)
            slugs = [b['act']['id']]
        else:
            author, msg, trailers, writes = B.change_message(item, laws)
            slugs = [b['act']['id'] for b, _ in item['parts']]
        trailers = standard(item, trailers, author)
        text = '\n'.join(msg).rstrip('\n') + '\n\n' + '\n'.join(trailers) + '\n'
        when = B.commit_date(day)
        stream.write(f'commit refs/heads/main\nmark :{mark}\n'
                     f'author {author[0]} <{author[1]}> {when}\n'
                     f'committer {B.COMMITTER[0]} <{B.COMMITTER[1]}> {base_time + mark} +0000\n'.encode('utf-8'))
        data(text.encode('utf-8'))
        if mark == 1:
            stream.write(f'from {head}\n'.encode())
        for b, k, u in writes:
            path = f'{b["act"]["id"]}/{B.file_name(k)}'
            if u is None:
                stream.write(f'D {path}\n'.encode('utf-8'))
            else:
                stream.write(f'M 100644 inline {path}\n'.encode('utf-8'))
                data(u['text'].encode('utf-8'))
        stream.write(b'\n')
        for s_ in slugs:
            name = f'{s_}/{day}'
            if name not in existing:
                tags[name] = mark
        log.append({'day': day, 'kind': item['kind'], 'law': item.get('law'), 'author': author[0],
                    'units': len(writes), 'slugs': slugs})
    for name in sorted(tags):
        stream.write(f'reset refs/tags/{name}\nfrom :{tags[name]}\n\n'.encode('utf-8'))
    out = subprocess.run(['git', 'fast-import', '--quiet', '--date-format=raw', '--done'], cwd=repo,
                         input=stream.getvalue() + b'done\n', capture_output=True)
    if out.returncode:
        raise SystemExit(f'git fast-import failed: {out.stderr.decode(errors="replace")[-3000:]}')
    return log, tags


# ---------------------------------------------------------------- documentation

def act_entry(b: dict) -> dict:
    return {'id': b['act']['id'], 'title': b['title'], 'short': b['act']['short'], 'state': b['act']['state'],
            'enacted_by': b.get('enacted_by', ''),
            'versions': [{'n': v['n'], 'from': v['from'], 'to': v['to'], 'state': v['state'],
                          'laws': next((ch['laws'] for ch in b['changes'] if ch['from'] == v['from']), []),
                          'page': v['url'], 'api': v['api'], 'sha256': v['sha256'],
                          **({'repairs': v['repairs']} if v['repairs'] else {}),
                          **({'page_order': v['page_order']} if v.get('page_order') else {}),
                          **({'note': v['note']} if v.get('note') else {})} for v in b['versions']]}


def act_readme(b: dict) -> str:
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
    out = [f'# {b["title"]} ({act["id"]})', '', f'<{SITE}/statute/{act["id"]}>', '',
           f'{len(b["versions"])} point-in-time versions on e-Laws, from {b["versions"][0]["from"]} '
           f'(the latest from {last["from"]}). Changes counted without layout-only changes.', '']
    if last['repealed']:
        out += [f'Repealed from {last["from"]}: every file of the act was removed by that commit. The e-Laws note: '
                f'"{last.get("note", "")}"', '']
        units = [v for v in b['versions'] if not v['repealed']][-1]['units']
    else:
        units = last['units']
    out += ['| Provision | File | Changes | Last changed |', '| --- | --- | ---: | --- |']
    for k in sorted(units, key=B.unit_order):
        u = units[k]
        out.append(f'| {u["label"]} | [{B.file_name(k)}]({B.file_name(k)}) | {counts.get(k, 0)} | {lastday.get(k, "")} |')
    return '\n'.join(out) + '\n'


def law_rows(b: dict, laws: dict) -> list[dict]:
    out = []
    for ch in b['changes']:
        if b.get('since') and ch['from'] <= b['since']:
            continue
        for law in ch['laws']:
            lm = laws[law]
            n = len(ch['groups'].get(law, []))
            out.append({'act': b['act']['id'], 'law': law, 'title': lm['title'], 'kind': lm['kind'],
                        'assented': lm['assented'], 'in_force': ch['from'], 'provisions': n,
                        'note': '' if n else 'named only by provisions changed together with another law',
                        'source': lm['url']})
    return out


def docs(repo: Path, built: list[dict], laws: dict, skipped: list[dict], today: str, batch: dict) -> dict[str, bytes]:
    """The documentation files after this batch, read from main and updated."""
    files: dict[str, bytes] = {}
    ver = json.loads(show(repo, 'main', 'data/versions.json'))
    by_id = {a['id']: i for i, a in enumerate(ver['acts'])}
    for b in built:
        e = act_entry(b)
        if e['id'] in by_id:
            ver['acts'][by_id[e['id']]] = e
        else:
            by_id[e['id']] = len(ver['acts'])
            ver['acts'].append(e)
    nir = {x['id']: x for x in ver.get('not_in_record', [])}
    for s in skipped:
        nir[s['act']['id']] = {'id': s['act']['id'], 'title': s['act']['title'], 'reason': s['skipped'],
                               'repealed_on': s['repealed_on'], 'note': s['note']}
    ver['not_in_record'] = [nir[k] for k in sorted(nir)]
    known = {l['key']: l for l in ver.get('laws', [])}
    known.update(laws)
    ver['laws'] = [known[k] for k in sorted(known, key=B.law_order)]
    ver['updated'] = today
    files['data/versions.json'] = (json.dumps(ver, ensure_ascii=False, indent=1) + '\n').encode('utf-8')

    old = list(csv.DictReader(io.StringIO(show(repo, 'main', 'laws.csv') or '')))
    rows = old + [r for b in built for r in law_rows(b, laws)]
    rows.sort(key=lambda r: (r['in_force'], r['act'], B.law_order(r['law'])))
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=['act', 'law', 'title', 'kind', 'assented', 'in_force', 'provisions', 'note',
                                        'source'], lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
    files['laws.csv'] = buf.getvalue().encode('utf-8')

    unc = show(repo, 'main', 'data/uncertain.tsv') or 'kind\tchange\n'
    add = []
    for b in built:
        for p in b['problems']:
            day = p.split(' ', 1)[0]
            if not b.get('since') or day > b['since']:
                add.append(f'not credited to one law\t{b["act"]["id"]} {p}')
    files['data/uncertain.tsv'] = (unc + ''.join(f'{x}\n' for x in add)).encode('utf-8')

    for b in built:
        files[f'{b["act"]["id"]}/README.md'] = act_readme(b).encode('utf-8')

    app = json.loads(show(repo, 'main', 'data/appended.json') or '{"batches": []}')
    app['batches'].append(batch)
    files['data/appended.json'] = (json.dumps(app, ensure_ascii=False, indent=1) + '\n').encode('utf-8')

    cj = json.loads(show(repo, 'main', 'corpus.json'))
    acts = [a['id'] for a in ver['acts']]
    listed = len(B.ACTS)
    n_rep = sum(1 for a in ver['acts'] if a['versions'][-1].get('state') == 'rrs')
    cj['name'] = (f'Ontario statutes on e-Laws: {len(acts)} of the {listed} consolidated public statutes e-Laws lists '
                  f'(current and repealed), {n_rep} of them repealed within the record')
    cj['acts'] = acts
    cj['path'] = 'canada/ontario/acts'
    cj['publisher'] = "e-Laws (King's Printer for Ontario)"
    cj['history_from'] = min(a['versions'][0]['from'] for a in ver['acts'])
    cj['record_to'] = max(cj.get('record_to', ''), max(v['from'] for a in ver['acts'] for v in a['versions']
                                                       if v['from'] <= today))
    cj['checked_on'] = today
    cj['record_note'] = (
        f'Checked against the official source on {today}: every point-in-time version on e-Laws of each act in the '
        'record, file by file and by letters and digits against the raw text. English text in force only (text of '
        'amendments not yet in force is left out). Each act starts with its first point-in-time version on e-Laws '
        '(2000s for most older acts), so earlier history is not in the record. The first four acts were built in '
        'date order (2026-10-29); every other act was appended later as its own block of commits (an end block: '
        'its dates run back from the commits above it; date each version by In-force, never by commit order). '
        f'{len(ver["not_in_record"])} acts repealed before their first version are not in it. Regulations are not '
        'included.')
    files['corpus.json'] = (json.dumps(cj, ensure_ascii=False, indent=2) + '\n').encode('utf-8')

    batches = app['batches']
    n_new = len({a for x in batches for a in x['acts']})
    section = '\n'.join([
        MARK,
        '## Appended acts (from 2026-11-05)',
        '',
        f'Since 2026-11-05 the other statutes on e-Laws are appended to this history, a batch at a time, without '
        f'changing any commit before them: {len(acts)} acts are in the record now ({n_new} appended in '
        f'{len(batches)} batches), of the {listed} statutes e-Laws lists. Each appended act is one block of commits in '
        'its own date order, so its dates run backwards from the commits above it; `tools/in_force_on.py` and readers '
        'date every version by its `In-force:` trailer, not by commit order. `data/appended.json` lists every batch.',
        '',
    ])
    readme = show(repo, 'main', 'README.md')
    head_, _, _ = readme.partition(MARK)
    if MARK not in readme:
        a, sep, rest = readme.partition('\n## ')
        files['README.md'] = (a.rstrip('\n') + '\n\n' + section + '\n' + sep.lstrip('\n') + rest).encode('utf-8')
    else:
        # the section runs from the marker to the next '## ' heading after its own
        pre, _, post = readme.partition(MARK)
        nxt = post.find('\n## ', post.find('## Appended acts') + 3)
        files['README.md'] = (pre + section + '\n' + (post[nxt + 1:] if nxt >= 0 else '')).encode('utf-8')

    rep = show(repo, 'main', 'REPRODUCE.md')
    pre = rep.partition(MARK)[0].rstrip('\n')
    lines = [MARK, '## Appended batches', '',
             'Made by `tools/append/ontario_append.py` (with the parser, evidence rules and messages of `tools/build.py`, extended to every statute e-Laws lists in `tools/append/acts.json`: version-list repairs, repealed acts, acts enacted in their first version) on a clone '
             'of the published main, then checked before a plain push: every point-in-time version of each appended '
             'act read back from git on its day, file by file and by letters and digits against the raw source '
             '(`tools/check_repo.py`\'s checks); global-law\'s `tools/check_corpus.py` with the published head as the '
             'pin (append-only); and a privacy audit of everything the push adds. An act that fails is held out of the '
             'batch and listed here. New commits use the corpus standard\'s trailers (Kind: law, baseline, unexplained for the standard uncredited, '
             'printing; Text-source for the version page; Retroactive for a change in force before Royal Assent).',
             '', '| Batch | Day | Acts | Commits | Versions checked | Mismatches | Held |',
             '| ---: | --- | ---: | ---: | ---: | ---: | --- |']
    for x in batches:
        g = x.get('gate', {})
        lines.append(f'| {x["n"]} | {x["day"]} | {len(x["acts"])} | {x["commits"]} | {g.get("versions", "")} | '
                     f'{g.get("mismatches", "")} | {", ".join(x.get("held", [])) or "none"} |')
    repairs = [f'- {b["act"]["id"]} v{v["n"]} ({v["from"]}): {r}' for b in built for v in b['versions']
               for r in v['repairs']]
    if repairs:
        lines += ['', f'Version-list repairs in batch {batch["n"]} (build.version_list\'s rules):', ''] + repairs
    files['REPRODUCE.md'] = (pre + '\n\n' + '\n'.join(lines) + '\n').encode('utf-8')
    return files


def write_docs(repo: Path, files: dict[str, bytes], tools: dict[str, bytes], today: str, n: int) -> None:
    head = git(repo, 'rev-parse', 'main').strip()
    base_time = int(git(repo, 'log', '-1', '--format=%ct', head).strip())
    stream = io.BytesIO()
    msg = (f'Documentation: appended batch {n}\n\nNo law text changes: corpus.json, data/versions.json, laws.csv, '
           'data/uncertain.tsv, data/appended.json, README.md, REPRODUCE.md and the tables of the acts appended.\n\n'
           f'Kind: documentation\nIn-force: {today}\n').encode('utf-8')
    when = B.commit_date(today)
    stream.write(f'commit refs/heads/main\nauthor {B.COMMITTER[0]} <{B.COMMITTER[1]}> {when}\n'
                 f'committer {B.COMMITTER[0]} <{B.COMMITTER[1]}> {base_time + 1} +0000\n'.encode())
    stream.write(b'data %d\n' % len(msg) + msg + b'\n')
    stream.write(f'from {head}\n'.encode())
    for path, body in sorted({**files, **tools}.items()):
        stream.write(f'M 100644 inline {path}\n'.encode('utf-8'))
        stream.write(b'data %d\n' % len(body) + body + b'\n')
    stream.write(b'\n')
    out = subprocess.run(['git', 'fast-import', '--quiet', '--date-format=raw', '--done'], cwd=repo,
                         input=stream.getvalue() + b'done\n', capture_output=True)
    if out.returncode:
        raise SystemExit(f'git fast-import (docs) failed: {out.stderr.decode(errors="replace")[-3000:]}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True, help='a clone whose main is the published main')
    ap.add_argument('--today', required=True)
    ap.add_argument('--acts', default='')
    ap.add_argument('--extend', default='')
    ap.add_argument('--offline', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    repo = Path(a.repo)
    have = acts_in(repo)
    ids = [x for x in a.acts.split(',') if x and x not in have]
    new_acts = [x for x in B.ACTS if x['id'] in ids]
    extend = {x: last_day(repo, x) for x in a.extend.split(',') if x and x in have}
    built, laws, skipped, deferred = build_batch(new_acts, extend, a.offline, a.today)
    items = plan(built, a.today)
    print(f'{len(built)} acts, {len(items)} commits, skipped {len(skipped)}, deferred {deferred}')
    if a.dry_run:
        return
    head = git(repo, 'rev-parse', 'main').strip()
    write_history(repo, items, laws, head)


if __name__ == '__main__':
    main()

"""Checks the git repository against the official text: every point-in-time version of every act on e-Laws, read back
from git on the day it took effect (with tools/in_force_on.py's rule), must equal that version's text.

    python -X utf8 scripts/canada-ontario-law/check_repo.py [--repo ../canada-ontario-law] [--no-record]

Two checks per version, from the cached API answers (no network):
1. File by file: the act's files in git on that day are exactly the files the build's parser makes from that version
   (same set of files, same bytes).
2. Letters and digits, independently of the parser: the act's files in git on that day, concatenated in reading order,
   have the same letters and digits (case-folded; everything else removed) as the raw version, read by a separate
   minimal extractor: the short title and chapter, then every text node of the version's HTML, except the table of
   contents, the skip link, the publisher's "Caution" notice, the shaded text of amendments not yet in force (classes beginning with "Y"), the notes
   announcing them ("Pnote"), the "Section Amendments with date in force" lists, and, on the older pages that do not
   shade it, the headnote printed directly before a shaded section.
The result is written to verification.json next to this script (unless --no-record), for REPRODUCE.md.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from lxml import html as lhtml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build  # noqa: E402


def letters(s: str) -> str:
    return ''.join(ch for ch in s.casefold() if ch.isalnum())


def official_letters(d: dict) -> str:
    """The independent extractor: no use of build.py's parser or renderer."""
    out = []
    for f in ('shortTitle', 'chapter'):
        if d.get(f):
            out.append(lhtml.fromstring(d[f]).text_content())
    doc = lhtml.fromstring(d['content'])
    old = bool(re.search(r'class="(?:headnote|section|subsection)-e"', d['content']))
    paras = []

    def blocks(x):      # the top-level blocks, also inside a 'WordSection' div the page closes early
        for e in x:
            if not isinstance(e.tag, str):
                continue
            if e.tag == 'div' and 'WordSection' in (e.get('class') or ''):
                blocks(e)
            else:
                paras.append(e)
    blocks(doc)
    keep = []
    toc_seen = False
    for e in paras:
        cls = (e.get('class') or '').strip()
        if e.tag in ('div', 'center') and e.xpath('.//*[contains(@class, "TOC")]') and not toc_seen:
            toc_seen = True
            continue
        if cls.startswith('toc') or cls == 'Caution':
            continue
        if cls.startswith('Y') or cls.startswith('Pnote') or cls.startswith('footnoteLeft'):
            if old and cls.startswith('Y'):
                while keep and (keep[-1].get('class') or '').startswith('headnote'):
                    keep.pop()
            continue
        keep.append(e)
    for e in keep:
        out.append(e.text_content())
    return letters(' '.join(out))


def files_at(repo: str, commit: str, slug: str) -> dict[str, str]:
    out = subprocess.run(['git', 'ls-tree', '-r', commit, f'{slug}/'], cwd=repo, capture_output=True,
                         text=True, encoding='utf-8').stdout.split('\n')
    blobs = []
    for line in out:
        if not line:
            continue
        info, f = line.split('\t', 1)
        if f.endswith('.md') and not f.endswith('/README.md'):
            blobs.append((f[len(slug) + 1:], info.split()[2]))
    if not blobs:
        return {}
    data = subprocess.run(['git', 'cat-file', '--batch'], cwd=repo, input=''.join(f'{sha}\n' for _, sha in blobs).encode(),
                          capture_output=True).stdout
    res, pos = {}, 0
    for name, _ in blobs:
        nl = data.index(b'\n', pos)
        size = int(data[pos:nl].split()[2])
        res[name] = data[nl + 1:nl + 1 + size].decode('utf-8')
        pos = nl + 1 + size + 1
    return res


def commits_by_day(repo: str, slug: str) -> list[tuple[str, str]]:
    out = subprocess.run(['git', 'log', '--format=%H%x09%(trailers:key=In-force,valueonly,separator=)', 'main', '--', slug],
                         cwd=repo, capture_output=True, text=True, encoding='utf-8').stdout
    return [(d.strip(), h) for h, _, d in (l.partition('\t') for l in out.splitlines()) if d.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=str(build.ROOT.parent / 'canada-ontario-law'))
    ap.add_argument('--no-record', action='store_true')
    args = ap.parse_args()
    versions = files = bad = wbad = 0
    nletters = 0
    per_act = {}
    for act in build.ACTS:
        slug = act['id']
        log = commits_by_day(args.repo, slug)
        for v in build.version_list(act, offline=True):
            commit = next((h for d, h in log if d <= v['from']), '')
            d = json.loads(build.fetch(f'{build.API}/{v["api"]}', offline=True))
            parsed = build.read_version(d)
            expected = {build.file_name(k): u['text'] for k, u in parsed['units'].items()}
            got = files_at(args.repo, commit, slug) if commit else {}
            versions += 1
            per_act[slug] = per_act.get(slug, 0) + 1
            files += len(expected)
            if got != expected:
                bad += 1
                diff = sorted(set(got) ^ set(expected)) or [k for k in expected if got.get(k) != expected[k]]
                print(f'MISMATCH {slug} {v["from"]}: {diff[:5]}')
            order = sorted(got, key=lambda n: build.unit_order(n[:-3]))
            mine = letters(' '.join(got[n] for n in order))
            theirs = official_letters(d)
            nletters += len(theirs)
            if mine != theirs:
                wbad += 1
                i = next((i for i, (a, b) in enumerate(zip(theirs, mine)) if a != b), min(len(theirs), len(mine)))
                print(f'LETTERS {slug} v{v["n"]} {v["from"]}: official {len(theirs)} vs repo {len(mine)}; first '
                      f'difference at {i}: {theirs[max(0, i - 40):i + 40]!r} / {mine[max(0, i - 40):i + 40]!r}')
    print(f'{versions} versions checked ({files} files), {bad} mismatches; letters and digits of every version '
          f'({nletters} characters) against the raw source, {wbad} mismatches')
    print('per act:', per_act)
    if not args.no_record:
        p = HERE / 'verification.json'
        rec = json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
        rec['check'] = {'versions': versions, 'files': files, 'mismatches': bad, 'letters': nletters,
                        'letter_mismatches': wbad, 'per_act': per_act}
        p.write_text(json.dumps(rec, indent=1, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
    raise SystemExit(1 if bad or wbad else 0)


if __name__ == '__main__':
    main()

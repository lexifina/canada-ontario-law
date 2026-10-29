"""Lists every consolidated Ontario statute (or regulation) on e-Laws, current and repealed ("Repealed / Revoked /
Spent"), and writes acts.json (or regulations.json), the list the builder takes its acts from.

    python -X utf8 scripts/canada-ontario-law/list_all.py [--offline] [--kind statute|regulation]

The listing is the e-Laws browse search the www.ontario.ca/laws app calls:
`/en/browse-search?text=&selection=<current|rrs>&result=<statute|regulation>&page=<n>&pageSize=50&sort=Newest`.
Sorted by date it answers with plain pages of 50 records (alias, title, state, first day of the latest version), which
are read until every record the search counts has been seen. Sorted by name (`sort=AZ`) it answers instead with one
bucket per act name; that answer is read too, as a cross-check: every act it shows must be in the pages. (A bucket can
hide a second act of the same name, e.g. the two Ontario Loan Acts, 2009, which is why the pages are the list.)
Every request is cached like the others (fetchlib), one at a time, at least 1.1 seconds apart.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fetchlib import fetch_json  # noqa: E402

PAGE = 50


def listing(kind: str, selection: str, sort: str, page: int, offline: bool) -> dict:
    return fetch_json(f'en/browse-search?text=&selection={selection}&result={kind}&page={page}&pageSize={PAGE}'
                      f'&sort={sort}', offline)


def en(v):
    return v.get('en') if isinstance(v, dict) else v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--offline', action='store_true')
    ap.add_argument('--kind', default='statute', choices=['statute', 'regulation'])
    ap.add_argument('--out', default=None)
    args = ap.parse_args()
    out_path = Path(args.out) if args.out else HERE / ('acts.json' if args.kind == 'statute' else 'regulations.json')
    rows: dict[str, dict] = {}
    shared = []
    for selection in ('current', 'rrs'):
        recs: dict[str, dict] = {}
        page, total = 1, None
        while True:
            d = listing(args.kind, selection, 'Newest', page, args.offline)
            hits = d['hits']['hits']
            total = d['hits']['total']['value']
            if d['hits']['total']['relation'] != 'eq':
                raise SystemExit(f'{selection}: the search gives no exact count')
            for h in hits:
                s = h['_source']
                recs[en(s['alias'])] = s
            if not hits or page * PAGE >= total:
                break
            page += 1
        if len(recs) != total:
            raise SystemExit(f'{selection}: {len(recs)} different records in {page} pages, the search counts {total}')
        # cross-check against the answer by name
        d = listing(args.kind, selection, 'AZ', 1, args.offline)
        names: dict[str, int] = {}
        for b in d['aggregations']['act']['buckets']:
            for h in b[args.kind][f'{args.kind}_hits']['hits']['hits']:
                if en(h['_source']['alias']) not in recs:
                    raise SystemExit(f'{selection}: {en(h["_source"]["alias"])} is in the answer by name, not in the pages')
                names[en(h['_source']['act'])] = b['doc_count']
        for name, n in sorted(names.items()):
            if n > 1:
                shared.append({'name': name, 'selection': selection,
                               'aliases': sorted(a for a, s in recs.items() if en(s['act']) == name)})
        for alias, s in recs.items():
            kind, _, ident = alias.partition('/')
            if kind != args.kind or ident in rows:
                raise SystemExit(f'unexpected or repeated record {alias}')
            rows[ident] = {'id': ident, 'kind': args.kind, 'short': en(s['act']),
                           'title': re.sub(r'\s+', ' ', en(s['title'])).strip().replace(' ,', ','),
                           'state': en(s['state']), 'listed_as': selection}
    acts = [rows[k] for k in sorted(rows)]
    out_path.write_text(json.dumps({'acts': acts, 'shared_names': shared}, indent=1, ensure_ascii=False) + '\n',
                        encoding='utf-8', newline='\n')
    by: dict[str, int] = {}
    for a in acts:
        by[a['state']] = by.get(a['state'], 0) + 1
    print(f'{len(acts)} {args.kind}s {by}; names shared by two or more: {shared}')


if __name__ == '__main__':
    main()

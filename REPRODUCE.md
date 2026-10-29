# How this history was made, and how to make it again

This file records exactly how the repository was built: the sources, the commands, the software, the decisions made
by hand, and what an AI model did and did not do. The build writes it, so it describes the build that made this
commit.

## Short version

```sh
git clone https://github.com/lexifina/canada-ontario-law && cd canada-ontario-law
pip install lxml
python -X utf8 tools/build.py --repo ../rebuilt --today 2026-10-29
git -C ../rebuilt rev-parse main        # the same hash as this repository's main
python -X utf8 tools/check_repo.py --repo ../rebuilt --no-record
python -X utf8 tools/test_repo.py --repo ../rebuilt
```

`tools/build.py` needs Python 3.12 or later with `lxml`, and git. It reads e-Laws (or its own cache, `.cache/` next to
the script) and writes this repository into `--repo`, which must be empty or a git repository. With the same data and
the same `--today` it gives the same commits with the same hashes. `data/versions.json` lists every version it read
with the sha256 of the API answer, so a rebuild can show it read the same bytes; e-Laws may change its answers, and then
the hashes change too.

## Sources

All legal text and all information about versions and amending acts come from **e-Laws** (www.ontario.ca/laws), the
Government of Ontario's database of statutes and regulations, published by the King's Printer for Ontario. Nothing was
typed in, summarised or rewritten. The pages of e-Laws are drawn in the browser from a JSON interface at
`https://www.ontario.ca/laws/api/v2/legislation`; the build reads the same answers the pages read. It read
4 version lists, 293 versions and 121 amending acts as enacted:

| What | Where |
| --- | --- |
| Each act's point-in-time versions (the "Versions" tab), with the days each applies from and to | `/laws/api/v2/legislation/en/act-versions/statute/<id>` |
| The full text of each version (the same HTML the page shows), with the citations that end each subsection and, since 2016, each section's "Section Amendments with date in force (d/m/y)" | `/laws/api/v2/legislation/en/doc-search/statute/<id>/v<n>` (the current version without `/v<n>`), listed with sha256 in `data/versions.json` |
| Each amending act's title and day of Royal Assent (118 of 121 laws) | `/laws/api/v2/legislation/en/doc-search/statute/S<yy><chapter>` |

| Act | Title | Folder | Versions | In force from | Files today |
| --- | --- | --- | ---: | --- | ---: |
| 90h08 | Highway Traffic Act | `90h08/` | 141 | 2004-01-01 to 2026-07-01 | 395 |
| 06r17 | Residential Tenancies Act, 2006 | `06r17/` | 53 | 2006-06-22 to 2026-09-21 | 310 |
| 00e41 | Employment Standards Act, 2000 | `00e41/` | 84 | 2002-11-26 to 2026-01-01 | 260 |
| 06l21 | Legislation Act, 2006 | `06l21/` | 15 | 2006-10-19 to 2025-12-11 | 108 |

The data was retrieved on 2026-10-28: one request at a time, at least 1.1 seconds apart (robots.txt asks for
`Crawl-delay: 1` and names no AI agents; the paths read are not disallowed), with gzip, and the user agent
`lexifina-watch/1.0 (+https://lexifina.com/watch; corpus@lexifina.com)`. Fetch rate: one request per 1.1 seconds or
slower. No login, no challenge page. e-Laws offers no bulk download of past versions.

## The build, step by step

1. `python -X utf8 scripts/canada-ontario-law/fetch_versions.py`, then `build.py --today 2026-10-29` in Lexifina's own
   repository fetched the data into the cache and wrote this repository. `tools/build.py` here is the same file
   (git blob `ecaced27c12d0a25007d311cdd23b6303fd73b59`), with `tools/fetchlib.py` (the cached fetcher), `tools/fetch_versions.py`, `tools/reproduce.py`,
   which writes this file, `tools/check_repo.py` and `tools/test_repo.py`. Every later build ran with `--offline`.
2. `python -X utf8 scripts/canada-ontario-law/check_repo.py` read every version of each act back from this repository
   on the day it took effect and compared it file by file with the text parsed afresh from the cached answer; then it
   compared the letters and digits of the whole act with those of the raw version, read by a separate minimal
   extractor that does not use the build's parser. Result: `293 versions checked (82236 files), 0 mismatches; letters and digits of every version (118582957 characters) against the raw source, 0 mismatches`.
3. `python -X utf8 scripts/canada-ontario-law/test_repo.py --record` ran the functional smoke test (6 of 6 passed):
   - pass: blame names a law: 90h08/s-041.md lines by S.O. 2007, c. 13, S.O. 2009, c. 5, S.O. 2015, c. 14, S.O. 2019, c. 8, S.O. 2024, c. 21, S.O. 2024, c. 9, e-Laws (King's Printer for Ontario)
   - pass: text before and after an amendment: 90h08/s-041.md 2009-04-22 != 2009-04-23; 00e41/s-015.md 2021-12-01 != 2021-12-02; 06r17/s-053.md 2026-09-20 != 2026-09-21
   - pass: log --follow in date order: 90h08/s-041.md 10 commits; 00e41/s-015.md 20 commits; 06r17/s-053.md 3 commits
   - pass: tags resolve, In-force on every commit: 529 tags resolve; all 357 commits carry In-force
   - pass: only the documentation commit is by Lexifina: only the documentation commit 23e49a77da is by Lexifina; 120 distinct authors
   - pass: README commands run: 9 README commands ran and printed output
4. `python -X utf8 scripts/canada-ontario-law/build.py --offline --today 2026-10-29 --verify-rebuild` built the repository
   a second time from the same cache into a temporary folder and compared the hashes. A second build from the same cache into an empty folder gave the same history: the last law commit was `a6448b41e683e3524bf20db3b00ba6c8e65ff3c0` in both, and every one of the 356 law commits and 529 tags had the same hash.
5. The build was run once more to write these results into this file, and the final `main` was rebuilt again and
   compared hash for hash before it was pushed.
6. `git push origin main --tags` published it to the private GitHub repository `lexifina/canada-ontario-law`.

It ran with Python 3.12.10, lxml 6.1.3 and git version 2.46.0.windows.1 on Windows 11. No network service other than e-Laws is involved.

## How the text and the commits are derived

Everything below is done by `tools/build.py`, deterministically.

- **Text in force.** Each version's HTML is a flat run of paragraphs, each with a class: `section`, `subsection`,
  `clause`, `definition`, `headnote`, `partnum` and so on (older versions add `-e`). e-Laws prints the text of
  amendments not yet in force in the same consolidation, shaded: classes beginning with `Y` (`Ysection`,
  `Yheadnote`, ...), announced by a note (`Pnote`, "Note: On a day to be named by proclamation ..."). That text is not
  law in force on the version's days, so it is left out, with its notes; on the older pages, which do not shade the
  headnote of a section not yet in force, the headnote directly before a shaded section goes with it. The publisher's
  notice "Disclaimer: This consolidation is not an official copy ..." (two versions of the Employment Standards Act,
  2000, in 2021) and the table of contents are left out too.
- **Files.** Each act is a folder named by its e-Laws identifier (`90h08/`). Each section is one file, named by its
  number with the whole part padded to three digits: `90h08/s-041.0.1.md`; a group printed as one ("247.-260.
  Omitted") is `s-247-260.md`; where the act numbers two sections the same (the Highway Traffic Act's two sections 206
  in 2020-2021), the second is `s-206-b.md`. The headings that begin with a section are `##` (Part), `###`/`####`
  (headings) and `#####` (the headnote) lines; every other paragraph is one line, as printed, with the citations that
  end it. Tables are one line per row, cells separated by ` | `; images are left out. `intro.md` holds the short
  title, the chapter, and anything printed before the first heading; `schedule[-<n>].md` each schedule.
- **Normalised.** Only white space (runs of spaces, line breaks, tabs, no-break and other Unicode spaces become one
  space), soft hyphens and zero-width characters (removed).
- **Changes.** Consecutive versions are compared file by file. 2768 changes of a file were found.
- **Cause.** Tried in this order for each changed file:
  1. since 2016, the section's list "Section Amendments with date in force (d/m/y)" names a law with this day: that
     law (815 file changes);
  2. a citation new in the file names exactly one law other than the act itself: that law (483);
  3. only the act's own citation is new (its own provisions taking effect, such as the Legislation Act, 2006 on
     2007-07-25): the act itself (347);
  4. the list or the new citations name two or more laws: none; committed by the publisher naming them
     (29);
  5. the same letters and digits as before (spacing, punctuation, hyphens, case, section-number style such as `1.`
     becoming `1` in 2017): a layout commit by the publisher (981);
  6. no law named for the file, and exactly one law named for the act that day: that law, by date only, labelled
     `Evidence: date only` (60);
  7. no law named for the file, two or more for the act that day: none; publisher, `Candidate:` trailers
     (0);
  8. nothing named anywhere in the version: no law; committed by the publisher and labelled
     (15).
- **Date.** The day the version applies from on e-Laws ("Historical version for the period June 20, 2012 to December
  30, 2012"); the build checks that the versions follow each other without a gap. For the version a law produced, that
  is the day the law's provisions took effect.
- **Commits.** One commit per amending law per day (236 commits by 119 laws), covering every act of the
  record it changed that day; one for the first version of each act (4); 25 for
  changes with two or more candidate laws; 11 for changes nothing explains; 21 for
  layout only; 59 for versions with no change in the English text in force. They are in the order
  they took effect, then one for this documentation.
  - The author is the amending law, `S.O. 2009, c. 5` (Statutes of Ontario 2009, chapter 5), at an address ending
    `@ontario.invalid` (`so-2009-c5@ontario.invalid`), which cannot exist. Publisher commits are by
    `e-Laws (King's Printer for Ontario) <e-laws@ontario.invalid>`, labelled in the subject.
  - Author and committer dates are noon in Toronto on the day the change took effect: UTC-5, or UTC-4 in daylight
    time (from the second Sunday in March to the first Sunday in November since 2007; from the first Sunday in April
    to the last Sunday in October from 1987 to 2006), written into the code because the build machine has no
    time-zone database. The committer is `Lexifina <canada-ontario-law@lexifina.com>`.
  - Trailers: `Evidence:`, `Kind:`, `Enacted:` (Royal Assent), `Date-note:`, `In-force:`, `Source:` (the act as
    enacted), `Affecting:` (one line per provision, `90h08 s. 38`), `Candidate:` and `Consolidated:` (the version the
    text came from).
  - Tags: each act's days (`90h08/2009-10-03`) and each amending law (`so/2009-c5`; a law that took effect on several
    days has one tag per day, `so/2015-c14/2017-05-01`); 529 in all.
- **Documentation commit.** Dated 2026-10-29, the `--today` of the build, so a later rebuild of the same data with the same
  `--today` gives the same hash. It carries `In-force: 2026-10-29` and `Kind: documentation`.

Changes credited by date only:

- 90h08 2004-01-02: s. 127 -> S.O. 1994, c. 27
- 90h08 2004-01-02: s. 129 -> S.O. 1994, c. 27
- 90h08 2005-11-21: s. 129 -> S.O. 2005, c. 26
- 90h08 2006-02-15: s. 228 -> S.O. 2005, c. 26
- 90h08 2006-03-31: s. 140 -> S.O. 2005, c. 26
- 90h08 2007-09-30: s. 27 -> S.O. 2007, c. 13
- 90h08 2007-09-30: s. 62 -> S.O. 2007, c. 13
- 90h08 2007-09-30: s. 140 -> S.O. 2007, c. 13
- 90h08 2008-06-16: s. 32 -> S.O. 2002, c. 18
- 90h08 2009-10-03: s. 1 -> S.O. 2009, c. 5
- 90h08 2009-10-03: s. 104 -> S.O. 2009, c. 5
- 90h08 2010-08-01: s. 48 -> S.O. 2009, c. 5
- 90h08 2010-08-01: s. 48.1 -> S.O. 2009, c. 5
- 90h08 2011-01-01: s. 82.1 -> S.O. 2009, c. 5
- 90h08 2015-06-02: s. 147 -> S.O. 2015, c. 14
- 90h08 2015-09-01: s. 62 -> S.O. 2015, c. 14
- 90h08 2016-01-01: s. 175 -> S.O. 2015, c. 14
- 90h08 2020-01-01: s. 1 -> S.O. 2019, c. 8
- 90h08 2020-12-08: s. 4.1 -> S.O. 2002, c. 22
- 90h08 2020-12-08: s. 23.1 -> S.O. 2002, c. 22
- 90h08 2021-03-01: s. 206 (second) -> S.O. 2019, c. 15
- 90h08 2021-03-01: s. 207 -> S.O. 2019, c. 15
- 90h08 2021-11-01: s. 198.4 -> S.O. 2017, c. 34
- 90h08 2021-11-01: s. 198.5 -> S.O. 2017, c. 34
- 90h08 2021-11-28: s. 172 -> S.O. 2021, c. 26
- 90h08 2024-05-16: s. 110.5 -> S.O. 2024, c. 9
- 90h08 2024-07-01: s. 110.5 -> S.O. 2024, c. 9
- 90h08 2024-11-19: s. 1.2 -> S.O. 2024, c. 21
- 90h08 2024-11-19: s. 48.1 -> S.O. 2024, c. 21
- 90h08 2024-11-19: s. 48.2.1 -> S.O. 2024, c. 21
- 90h08 2024-11-25: s. 195 -> S.O. 2024, c. 25
- 90h08 2025-06-05: s. 195 -> S.O. 2025, c. 10
- 90h08 2025-11-14: s. 205.1 -> S.O. 2025, c. 11
- 90h08 2025-11-14: s. 205.2 -> S.O. 2025, c. 11
- 06r17 2014-06-01: s. 183 -> S.O. 2013, c. 3
- 06r17 2015-07-01: s. 215 -> S.O. 2011, c. 6
- 06r17 2017-01-01: s. 2 -> S.O. 2016, c. 23
- 06r17 2017-09-01: s. 47.1 -> S.O. 2017, c. 13
- 06r17 2017-09-01: s. 78 -> S.O. 2017, c. 13
- 06r17 2017-09-01: s. 126 -> S.O. 2017, c. 13
- 00e41 2004-06-29: s. 135 -> S.O. 2004, c. 15
- 00e41 2005-06-13: s. 52 -> S.O. 2004, c. 15
- 00e41 2006-06-30: s. 50 -> S.O. 2006, c. 13
- 00e41 2007-04-01: s. 3 -> S.O. 2006, c. 34
- 00e41 2007-07-25: s. 118 -> S.O. 2006, c. 21
- 00e41 2007-08-20: s. 50 -> S.O. 2006, c. 35
- 00e41 2008-10-08: s. 49.1 -> S.O. 2008, c. 15
- 00e41 2009-12-15: s. 74.11.1 -> S.O. 2009, c. 33
- 00e41 2015-02-20: s. 103 -> S.O. 2014, c. 10
- 00e41 2015-05-20: s. 2 -> S.O. 2014, c. 10
- 00e41 2015-11-20: s. 74.5 -> S.O. 2014, c. 10
- 00e41 2017-12-03: s. 74.14 -> S.O. 2017, c. 22
- 00e41 2022-05-01: s. 45 -> S.O. 2019, c. 5
- 00e41 2023-01-01: s. 91.1 -> S.O. 2022, c. 7
- 00e41 2023-07-01: s. 74.13 -> S.O. 2021, c. 35
- 00e41 2023-10-26: s. 54 -> S.O. 2023, c. 15
- 06l21 2009-12-15: s. 101-142 -> S.O. 2009, c. 33
- 06l21 2009-12-15: s. 143 -> S.O. 2009, c. 33
- 06l21 2024-03-06: s. 13 -> S.O. 2024, c. 2
- 06l21 2025-01-01: s. 89 -> S.O. 2024, c. 2

Changes whose amendment list or new citations name two or more laws (credited to none):

- 90h08 2006-01-01: s. 7 (candidates: S.O. 2002, c. 18, S.O. 2005, c. 26)
- 90h08 2006-01-01: s. 23.1 (candidates: S.O. 2002, c. 18, S.O. 2002, c. 22)
- 90h08 2006-06-22: s. 41 (candidates: S.O. 2006, c. 19, S.O. 2006, c. 20)
- 90h08 2006-06-22: s. 210 (candidates: S.O. 2006, c. 19, S.O. 2006, c. 20)
- 90h08 2007-01-01: s. 128 (candidates: S.O. 2006, c. 11, S.O. 2006, c. 32)
- 90h08 2009-05-01: s. 48.2 (candidates: S.O. 2007, c. 13, S.O. 2009, c. 5)
- 90h08 2010-01-01: s. 159 (candidates: S.O. 2009, c. 19, S.O. 2009, c. 5)
- 90h08 2010-07-01: s. 109 (candidates: S.O. 1994, c. 27, S.O. 2002, c. 18)
- 90h08 2010-12-01: s. 41.4 (candidates: S.O. 2009, c. 5, S.O. 2010, c. 16)
- 90h08 2017-03-22: s. 41 (candidates: S.O. 2000, c. 26, S.O. 2006, c. 19)
- 90h08 2017-03-22: s. 82 (candidates: S.O. 2016, c. 5, S.O. 2017, c. 2)
- 90h08 2018-10-17: s. 46 (candidates: S.O. 2017, c. 26, S.O. 2018, c. 12)
- 90h08 2019-12-01: s. 205.3 (candidates: S.O. 2017, c. 34, S.O. 2017, c. 9)
- 90h08 2019-12-01: s. 205.7 (candidates: S.O. 2017, c. 34, S.O. 2017, c. 9)
- 90h08 2019-12-01: s. 205.19 (candidates: S.O. 2017, c. 34, S.O. 2017, c. 9)
- 90h08 2019-12-01: s. 205.25 (candidates: S.O. 2017, c. 34, S.O. 2017, c. 9)
- 90h08 2022-04-01: s. 82 (candidates: S.O. 2015, c. 14, S.O. 2019, c. 14)
- 90h08 2022-04-01: s. 100.3 (candidates: S.O. 2015, c. 14, S.O. 2019, c. 7)
- 90h08 2022-04-01: s. 100.7 (candidates: S.O. 2015, c. 14, S.O. 2019, c. 14)
- 90h08 2022-04-01: s. 100.8 (candidates: S.O. 2015, c. 14, S.O. 2019, c. 14)
- 90h08 2022-07-01: s. 21.1 (candidates: S.O. 2014, c. 9, S.O. 2019, c. 8)
- 90h08 2025-04-01: s. 96 (candidates: S.O. 2015, c. 14, S.O. 2024, c. 28)
- 90h08 2026-05-19: s. 1.2 (candidates: S.O. 2024, c. 21, S.O. 2024, c. 25)
- 06r17 2011-01-01: s. 6 (candidates: S.O. 2008, c. 14, S.O. 2009, c. 33)
- 00e41 2019-01-01: s. 15 (candidates: S.O. 2017, c. 22, S.O. 2018, c. 14)
- 00e41 2019-01-01: s. 21.2 (candidates: S.O. 2017, c. 22, S.O. 2018, c. 14)
- 00e41 2019-01-01: s. 141 (candidates: S.O. 2017, c. 22, S.O. 2018, c. 14)
- 00e41 2026-01-01: s. 8.1 (candidates: S.O. 2024, c. 3, S.O. 2025, c. 13)
- 00e41 2026-01-01: s. 15 (candidates: S.O. 2024, c. 19, S.O. 2024, c. 3, S.O. 2025, c. 13)

Changes naming no law, on a day two or more laws are new (credited to none):

- none

Changes nothing explains (publisher):

- 90h08 2006-04-28: s. 170
- 90h08 2011-12-31: s. 144
- 90h08 2014-07-01: s. 205.17
- 90h08 2014-11-20: s. 127
- 90h08 2014-11-20: s. 129
- 90h08 2016-04-01: s. 1
- 90h08 2019-12-10: s. 128.0.1
- 90h08 2019-12-10: s. 225
- 90h08 2024-12-19: s. 41
- 06r17 2007-05-01: s. 185
- 06r17 2007-05-01: s. 204
- 06r17 2007-05-01: s. 208
- 06r17 2023-06-08: s. 215
- 00e41 2006-06-20: s. 141
- 00e41 2006-12-20: s. 142

Changes whose new text equals an earlier version of the same file (labelled as a reprint of older text):

- 90h08 2005-09-01: s. 127
- 90h08 2005-09-01: s. 196
- 90h08 2005-09-01: Schedule
- 90h08 2012-06-20: s. 127
- 90h08 2012-06-20: s. 196
- 90h08 2012-06-20: Schedule
- 90h08 2017-03-22: s. 210.1
- 90h08 2024-07-01: s. 110.5
- 90h08 2025-06-05: s. 195
- 00e41 2017-12-03: s. 74.14
- 00e41 2025-06-19: s. 1
- 00e41 2025-06-19: s. 2
- 00e41 2025-06-19: s. 3
- 00e41 2025-06-19: s. 6
- 00e41 2025-06-19: s. 8
- 00e41 2025-06-19: s. 9
- 00e41 2025-06-19: s. 10
- 00e41 2025-06-19: s. 11
- 00e41 2025-06-19: s. 12
- 00e41 2025-06-19: s. 13
- 00e41 2025-06-19: s. 14.1
- 00e41 2025-06-19: s. 14.2
- 00e41 2025-06-19: s. 14.3
- 00e41 2025-06-19: s. 14.4
- 00e41 2025-06-19: s. 14.5
- 00e41 2025-06-19: s. 15.1
- 00e41 2025-06-19: s. 17
- 00e41 2025-06-19: s. 19
- 00e41 2025-06-19: s. 21.1.1
- 00e41 2025-06-19: s. 21.1.2
- 00e41 2025-06-19: s. 21.2
- 00e41 2025-06-19: s. 22
- 00e41 2025-06-19: s. 23.1
- 00e41 2025-06-19: s. 24
- 00e41 2025-06-19: s. 25
- 00e41 2025-06-19: s. 27
- 00e41 2025-06-19: s. 28
- 00e41 2025-06-19: s. 30
- 00e41 2025-06-19: s. 33
- 00e41 2025-06-19: s. 34
- 00e41 2025-06-19: s. 35
- 00e41 2025-06-19: s. 35.2
- 00e41 2025-06-19: s. 38
- 00e41 2025-06-19: s. 41
- 00e41 2025-06-19: s. 41.1.1
- 00e41 2025-06-19: s. 41.2
- 00e41 2025-06-19: s. 43
- 00e41 2025-06-19: s. 45
- 00e41 2025-06-19: s. 46.1
- 00e41 2025-06-19: s. 47
- 00e41 2025-06-19: s. 48
- 00e41 2025-06-19: s. 49
- 00e41 2025-06-19: s. 49.1
- 00e41 2025-06-19: s. 49.2
- 00e41 2025-06-19: s. 49.3
- 00e41 2025-06-19: s. 49.4
- 00e41 2025-06-19: s. 49.5
- 00e41 2025-06-19: s. 49.6
- 00e41 2025-06-19: s. 49.7
- 00e41 2025-06-19: s. 50
- 00e41 2025-06-19: s. 50.0.1
- 00e41 2025-06-19: s. 50.0.2
- 00e41 2025-06-19: s. 50.1
- 00e41 2025-06-19: s. 50.1.1
- 00e41 2025-06-19: s. 50.2
- 00e41 2025-06-19: s. 51
- 00e41 2025-06-19: s. 51.1
- 00e41 2025-06-19: s. 52
- 00e41 2025-06-19: s. 52.1
- 00e41 2025-06-19: s. 53
- 00e41 2025-06-19: s. 53.2
- 00e41 2025-06-19: s. 56
- 00e41 2025-06-19: s. 57
- 00e41 2025-06-19: s. 58
- 00e41 2025-06-19: s. 59
- 00e41 2025-06-19: s. 60
- 00e41 2025-06-19: s. 63
- 00e41 2025-06-19: s. 64
- 00e41 2025-06-19: s. 65
- 00e41 2025-06-19: s. 67.1
- 00e41 2025-06-19: s. 67.2
- 00e41 2025-06-19: s. 68
- 00e41 2025-06-19: s. 74
- 00e41 2025-06-19: s. 74.1.3
- 00e41 2025-06-19: s. 74.1.4
- 00e41 2025-06-19: s. 74.1.10
- 00e41 2025-06-19: s. 74.1.12
- 00e41 2025-06-19: s. 74.1.13
- 00e41 2025-06-19: s. 74.1.15
- 00e41 2025-06-19: s. 74.2
- 00e41 2025-06-19: s. 74.3
- 00e41 2025-06-19: s. 74.4
- 00e41 2025-06-19: s. 74.8
- 00e41 2025-06-19: s. 74.9
- 00e41 2025-06-19: s. 74.10.1
- 00e41 2025-06-19: s. 74.11
- 00e41 2025-06-19: s. 74.12
- 00e41 2025-06-19: s. 74.18
- 00e41 2025-06-19: s. 75
- 00e41 2025-06-19: s. 76
- 00e41 2025-06-19: s. 78
- 00e41 2025-06-19: s. 79
- 00e41 2025-06-19: s. 81
- 00e41 2025-06-19: s. 85
- 00e41 2025-06-19: s. 87
- 00e41 2025-06-19: s. 88.2
- 00e41 2025-06-19: s. 91
- 00e41 2025-06-19: s. 93
- 00e41 2025-06-19: s. 95
- 00e41 2025-06-19: s. 100
- 00e41 2025-06-19: s. 102
- 00e41 2025-06-19: s. 102.1
- 00e41 2025-06-19: s. 103
- 00e41 2025-06-19: s. 105
- 00e41 2025-06-19: s. 106
- 00e41 2025-06-19: s. 111
- 00e41 2025-06-19: s. 112
- 00e41 2025-06-19: s. 113
- 00e41 2025-06-19: s. 114
- 00e41 2025-06-19: s. 115
- 00e41 2025-06-19: s. 116
- 00e41 2025-06-19: s. 117
- 00e41 2025-06-19: s. 118
- 00e41 2025-06-19: s. 119
- 00e41 2025-06-19: s. 120
- 00e41 2025-06-19: s. 122
- 00e41 2025-06-19: s. 125.3
- 00e41 2025-06-19: s. 127
- 00e41 2025-06-19: s. 128
- 00e41 2025-06-19: s. 129
- 00e41 2025-06-19: s. 130
- 00e41 2025-06-19: s. 136
- 00e41 2025-06-19: s. 137
- 00e41 2025-06-19: s. 138.1

## Decisions made by hand

1. **The acts.** Ontario has no constitution of its own in a statute; the record takes four public statutes with long,
   clean version histories: the Highway Traffic Act (amended more often than almost any other), the Residential
   Tenancies Act, 2006, the Employment Standards Act, 2000 and the Legislation Act, 2006 (which governs Ontario
   legislation itself). Regulations are on e-Laws in the same form and could be added the same way; they are not in
   this record yet.
2. **In force only.** Shaded text of amendments not yet in force is left out of every version, so each commit holds
   the law in force on its day. There is no `future` branch: e-Laws gives no day for unproclaimed amendments.
3. **The consolidation's own evidence.** A change is credited to a law only when the section's amendment list gives it
   this day, when its citation is new in the changed file, or by date only (labelled) when it is the only law named that
   day. The amending acts' commencement sections were not parsed.
4. **Two laws are not separated.** Where the evidence names two laws for one file on one day, the amending texts were
   not read to divide the change; it is the publisher's, naming both.
5. **Layout is not law.** A change that leaves every letter and digit in place (e-Laws re-typeset all its statutes in
   2017, dropping the period after section numbers) is the publisher's, labelled `layout only`.
6. **The record starts with the first point-in-time version** of each act on e-Laws (2002-11-26 at the earliest),
   credited to the publisher.
7. **English only.** The French version is equally authoritative; it is not recorded.

## What an AI model did

This repository was built on 2026-10-29 in **Claude Code**, Anthropic's coding tool, by the model **Claude Opus 5.5**
(model id `claude-opus-5-5`), working from a brief by the user at Lexifina: a private "git for law" repository for
Ontario to the same standard as Lexifina's other corpora.

The model researched the source (e-Laws' pages and the JSON interface behind them, the shape of their HTML, robots.txt
and the King's Printer's copyright policy), wrote all the code and text in this repository, ran the commands above and
checked the results. It did **not** write or edit any legal text: every word of every provision, every date and every
law's title is copied by the script from e-Laws. No AI model is called when the history is built or checked. The work
was not reviewed line by line by a lawyer. This is not an official version (see the README).

## Prior art

- e-Laws itself, whose "Versions" tab shows each point-in-time version; it has no change-by-change view.
- Lexifina's other corpora, whose rules this one follows, and `lexifina/canada-law` (federal Acts), whose builder this
  one adapts.

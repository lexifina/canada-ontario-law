# Ontario statutes, change by change

Every consolidated Ontario statute on e-Laws, current and repealed, as one git repository: the Highway Traffic Act,
the Residential Tenancies Act, 2006, the Employment Standards Act, 2000, the Legislation Act, 2006 and some 1,200
more. Each amending act is one commit, credited to that act and dated the day its change took effect, at noon in
Toronto; a repealed act's files are removed on the day of its repeal. The text is the English consolidated text in
force, published by the King's Printer for Ontario on [e-Laws](https://www.ontario.ca/laws), in each of its
point-in-time versions (from the early 2000s for older acts). [`data/acts.json`](data/acts.json) lists the acts.

This is not an official version (see [Licence](#licence)).

## The questions, as git commands

| Question | Command |
| --- | --- |
| What did s. 38 of the Highway Traffic Act say on 1 January 2008? | `python tools/in_force_on.py 2008-01-01 90h08 38` |
| The whole Residential Tenancies Act as it stood on 1 January 2020 | `python tools/in_force_on.py 2020-01-01 06r17` |
| Which law wrote each line of s. 41 of the Highway Traffic Act? | `git blame 90h08/s-041.md` |
| Every change to s. 15 of the Employment Standards Act, with the law and the day | `git log --follow 00e41/s-015.md` |
| Everything one law changed on one day | `git show --stat so/2009-c5/2009-10-03` |
| What changed in the Highway Traffic Act on one day | `git show --stat 90h08/2009-10-03` |
| The amending laws with all their dates | [`laws.csv`](laws.csv) |
| Changes where two or more laws were possible (credited to none) | `git log --grep="credited to none"` |
| Changes credited by date only | `git log --grep="Evidence: date only"` |
| Every act a law changed (an omnibus act across the statute book) | `git log --format="%s" --author="S.O. 2017, c. 34"` |
| Laws that changed the Residential Tenancies Act in 2017 | `git log --format="%an %s" --since=2017-01-01T00:00:00-05:00 --until=2017-12-31T23:59:59-05:00 -- 06r17` |

## The dates, and which one we use

An Ontario act has the day it received Royal Assent (`Enacted:`) and the day or days its provisions came into force
(`In-force:`), often named later by proclamation. **Commits are dated the day the change took effect**, at noon in
Toronto (Eastern time, UTC-5, or UTC-4 in daylight time): that is the day e-Laws gives as the start of the version the
change produced. `tools/in_force_on.py` reads the `In-force:` trailer, not the commit date, so it does not depend on
the reader's time zone; with raw git, give a full time, `--before="2009-10-03T23:59:59-04:00"`.

A law can take effect in steps: the Road Safety Act, 2009 (S.O. 2009, c. 5) changed the Highway Traffic Act on several
days. Each step is its own commit, with its own tag (`so/2009-c5/2009-10-03`).

In PowerShell, `git show $(...):path` is split into two arguments; use
`$r = git rev-list -1 90h08/2009-10-03; git show "$($r):90h08/s-038.md"`.

## What "author" means

The author of a commit is the law that made the change: `S.O. 2009, c. 5` (Statutes of Ontario 2009, chapter 5), with
an address ending `@ontario.invalid`, which cannot exist, so `git blame` names the law. The committer is always
`Lexifina`.

The evidence is the consolidation's own. Each subsection ends with the citations of the provisions that enacted and
amended it ("2009, c. 5, s. 8."), and since 2016 each section ends with "Section Amendments with date in force
(d/m/y)", which gives the day each amending provision took effect. A changed section is credited to the law that list
gives with this day, or else to the law whose citation is new in it. Further rules, each labelled in the commit:

- a section that changed with no law named for it, on a day when exactly one law is named for the act, is credited to
  that law by date only (`Evidence: date only`);
- where two or more laws are named for one change, it is committed by the publisher, `e-Laws (King's Printer for
  Ontario)`, labelled "credited to none", with each law in a `Candidate:` trailer;
- a change that keeps every letter and digit (spacing, hyphens, punctuation, and the 2017 re-typesetting that dropped
  the period after section numbers) is the publisher's, labelled "layout only";
- a change nothing explains (such as "Her Majesty the Queen" becoming "the Crown") is the publisher's, labelled "no
  amending law named".

The first version of each act is credited to the act that enacted it when it applies from on or after Royal Assent
and cites only that act; otherwise it is the act as amended up to then, credited to the publisher, and the citations
in each file still name the laws that made it. A repealed act's files are removed on the day e-Laws gives for the
repeal, by the law its note names ("This Act was repealed on ... See: 1996, c. 17, Sched. J"); the folder keeps its
`README.md`. Blame credits whole lines; use `git log -p --word-diff` to see each law's words.

## Text not yet in force

e-Laws prints amendments that have been enacted but are not yet in force inside the consolidation, shaded, after a note
("Note: On a day to be named by proclamation of the Lieutenant Governor, ..."). They are not law on the version's days,
so they are left out: every commit holds only the text in force. There is no `future` branch, because e-Laws gives no
day for them.

## How it is checked

`tools/check_repo.py` reads every version of each act back from git on the day it took effect and compares it with the
official text: file by file with the text parsed from e-Laws, and by letters and digits with the raw version, read by a
separate extractor that does not use the build's parser. `tools/test_repo.py` checks that the commands above work. The
results are in [`REPRODUCE.md`](REPRODUCE.md).

## Files

Each act is a folder named by its e-Laws identifier, e.g. `90h08/` (Highway Traffic Act), `06r17/` (Residential
Tenancies Act, 2006), `00e41/` (Employment Standards Act, 2000), `06l21/` (Legislation Act, 2006); `data/acts.json`
maps every identifier to its title. Each section is one file, named
by its number with the whole part padded to three digits: `90h08/s-038.md` is section 38, `90h08/s-041.0.1.md` section
41.0.1. Inside a file, the Part and headings that begin with the section are `##` to `####` lines, the headnote is a
`#####` line, and every other paragraph is one line as printed, with its citations. `intro.md` holds the short title
and the chapter; `schedule.md` or `schedule-<n>.md` each schedule (one line per row of a table). A repealed section
stays as e-Laws prints it ("Repealed: 2002, c. 24, Sched. B, s. 25."). Each folder's `README.md` lists its provisions
and how often each changed.

## What it does not show

- Versions e-Laws does not publish: nothing before its first point-in-time version of each act; acts repealed before
  e-Laws kept versions of them (listed in `REPRODUCE.md`) are not in the record at all.
- Amendments not yet in force (above), and editorial notes.
- The French text, which is equally authoritative.
- Which of two laws named for one change made it (above).
- Regulations (a separate record), private acts not consolidated on e-Laws, and source law as enacted.

## How it is built

`tools/build.py` reads e-Laws and writes this repository from scratch; the same data gives the same hashes. Every step,
the software, the decisions made by hand and what an AI model did are in [`REPRODUCE.md`](REPRODUCE.md).
[`corpus.json`](corpus.json) describes the corpus for tools that read several of Lexifina's law repositories.
`data/versions.json` lists every source version with its sha256. [`SOURCES.md`](SOURCES.md) gives the legal basis.

## Licence

The text of the statutes is reproduced under the King's Printer for Ontario's policy on copyright on legal materials:
"The King's Printer permits any person to reproduce the text and images contained in the statutes, regulations and
judicial decisions without seeking permission and without charge." © King's Printer for Ontario.

**This is not an official version.** Under section 35 of the Legislation Act, 2006, an official copy of Ontario law is
one printed by the King's Printer (or a prescribed entity), one accessed from e-Laws in a prescribed form or format, or
one prescribed as official; this repository is none of these. The history, commit
messages, tables and tools are released under [CC0 1.0](LICENSE).

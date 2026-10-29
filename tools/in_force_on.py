"""Prints an Ontario statute, or one provision of it, as it stood in force on a given day, from this repository's
history.

    python tools/in_force_on.py 2019-01-01 90h08 38          # section 38 of the Highway Traffic Act on 1 January 2019
    python tools/in_force_on.py 2019-01-01 90h08 41.0.1      # section 41.0.1
    python tools/in_force_on.py 2020-01-01 06r17             # the whole Residential Tenancies Act, 2006
    python tools/in_force_on.py 2010-01-01 90h08 schedule    # the Schedule

Each commit carries the day its change took effect in an `In-force:` trailer, which is the source of truth (not the
commit date, which is noon in Toronto on that day). The text in force on a day is the last commit on or before it.
Changes published but not yet in force would be on the branch "future"; a date after today reads from there.
Standard library only.
"""
import datetime as dt
import re
import subprocess
import sys


def git(*args: str) -> str:
    return subprocess.run(['git', *args], capture_output=True, text=True, encoding='utf-8', check=True).stdout


def order(path: str) -> tuple:
    """The order of the act's files: the title, the sections by number, the schedules."""
    name = path.split('/', 1)[1][:-3]
    if name == 'intro':
        return (0, 0, ())
    m = re.fullmatch(r's-(\d+)((?:\.\d+)*)(-.*)?', name)
    if m:
        return (1, int(m.group(1)), tuple(int(x) for x in m.group(2).split('.')[1:]), m.group(3) or '')
    if name.startswith('schedule'):
        rest = name[len('schedule'):].lstrip('-')
        n = re.match(r'\d+', rest)
        return (2, int(n.group(0)) if n else 0, (rest,))
    return (3, 0, (name,))


def file_for(key: str) -> str:
    """'38' -> s-038.md, '41.0.1' -> s-041.0.1.md; anything else is a file name ('schedule', 'intro')."""
    m = re.fullmatch(r'(\d+)((?:\.\d+)*)', key)
    if m:
        return f's-{int(m.group(1)):03d}{m.group(2)}.md'
    return key if key.endswith('.md') else f'{key}.md'


def commit_on(day: str, act: str) -> str:
    branch = 'future' if day > dt.date.today().isoformat() and git('branch', '--list', 'future').strip() else 'HEAD'
    out = git('log', '--format=%H%x09%(trailers:key=In-force,valueonly,separator=)', branch, '--', act)
    for line in out.splitlines():
        h, _, d = line.partition('\t')
        if d.strip() and d.strip() <= day:
            return h
    return ''


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    day, act = sys.argv[1], sys.argv[2]
    dt.date.fromisoformat(day)
    commit = commit_on(day, act)
    if not commit:
        sys.exit(f'{act} is not in the record on {day} (the record starts with its first point-in-time version).')
    if len(sys.argv) > 3:
        name = file_for(sys.argv[3])
        try:
            sys.stdout.write(git('show', f'{commit}:{act}/{name}'))
        except subprocess.CalledProcessError:
            sys.exit(f'{act}/{name} was not in the text in force on {day}.')
        return
    files = [f for f in git('ls-tree', '-r', '--name-only', commit, f'{act}/').split('\n')
             if f.endswith('.md') and not f.endswith('/README.md')]
    files = sorted(files, key=order)
    data = subprocess.run(['git', 'cat-file', '--batch'], input=''.join(f'{commit}:{f}\n' for f in files).encode('utf-8'),
                          capture_output=True, check=True).stdout
    pos = 0
    for _ in files:
        nl = data.index(b'\n', pos)
        size = int(data[pos:nl].split()[2])
        sys.stdout.write(data[nl + 1:nl + 1 + size].decode('utf-8') + '\n')
        pos = nl + 1 + size + 1


if __name__ == '__main__':
    main()

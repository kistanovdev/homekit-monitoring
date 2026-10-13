#!/usr/bin/env python3
"""Back up the home network monitor's data into this repo.

Downloads a consistent SQLite snapshot from the monitor's /api/backup endpoint,
keeps compressed copies under backups/db/ (git-ignored), and merges the history
into git-friendly text files:

    backups/events.jsonl            every event ever recorded (outages, reboots, re-pairs)
    backups/daily_availability.csv  per device per day: checks, successful checks, availability %
    backups/state.json              status of every device at backup time

The monitor deletes data older than 90 days, but these files keep everything
that was ever backed up.

Usage:
    python3 tools/backup.py                # back up into backups/
    python3 tools/backup.py --push         # ...then git commit and push backups/
    python3 tools/backup.py --from-file x.db   # use an existing snapshot instead of downloading
"""
import argparse
import csv
import gzip
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BACKUPS = REPO / "backups"
DEFAULT_URL = "http://192.168.0.52:8088/api/backup"


def download(url: str, dest: Path) -> None:
    # The monitor is on the home LAN: never route through HTTP(S)_PROXY from the environment.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(url, timeout=60) as resp, open(dest, "wb") as f:
            shutil.copyfileobj(resp, f)
    except urllib.error.URLError as e:
        sys.exit(f"could not download {url}: {e}\n"
                 "Are you on the home network, and is the monitor running "
                 "(http://192.168.0.52:8088)?")


def save_snapshot(snapshot: Path, keep: int) -> Path:
    db_dir = BACKUPS / "db"
    db_dir.mkdir(parents=True, exist_ok=True)
    out = db_dir / f"hkmon-{time.strftime('%Y%m%d-%H%M%S')}.db.gz"
    with open(snapshot, "rb") as src, gzip.open(out, "wb") as dst:
        shutil.copyfileobj(src, dst)
    for old in sorted(db_dir.glob("hkmon-*.db.gz"))[:-keep]:
        old.unlink()
    return out


def merge_events(con: sqlite3.Connection) -> tuple[int, int]:
    path = BACKUPS / "events.jsonl"
    events = {}
    if path.exists():
        for line in path.read_text().splitlines():
            if line.strip():
                e = json.loads(line)
                events[(e["ts"], e["name"], e["kind"], e["detail"])] = e
    before = len(events)
    for ts, name, kind, detail in con.execute("SELECT ts, name, kind, detail FROM events"):
        e = {"ts": ts, "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts)),
             "name": name, "kind": kind, "detail": detail}
        events.setdefault((ts, name, kind, detail), e)
    rows = sorted(events.values(), key=lambda e: (e["ts"], e["name"], e["kind"]))
    path.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in rows))
    return len(rows), len(rows) - before


def merge_availability(con: sqlite3.Connection) -> int:
    path = BACKUPS / "daily_availability.csv"
    rows: dict[tuple[str, str], tuple[int, int]] = {}
    if path.exists():
        with open(path, newline="") as f:
            for r in csv.DictReader(f):
                rows[(r["date"], r["name"])] = (int(r["checks"]), int(r["ok"]))
    # Days in the snapshot replace what was stored, so a partial day is
    # completed by the next backup.
    fresh = {}
    for day, name, checks, ok in con.execute(
        "SELECT date(ts, 'unixepoch', 'localtime') AS day, name, COUNT(*), SUM(ok) "
        "FROM samples GROUP BY day, name"
    ):
        fresh[(day, name)] = (checks, ok)
    rows.update(fresh)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "name", "checks", "ok", "availability_pct"])
        for (day, name), (checks, ok) in sorted(rows.items()):
            w.writerow([day, name, checks, ok, f"{100 * ok / checks:.2f}" if checks else ""])
    return len({d for d, _ in rows})


def write_state(con: sqlite3.Connection) -> int:
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute("SELECT * FROM state ORDER BY grp, name")]
    for r in rows:
        for k in ("since", "last_ok", "last_check"):
            if r.get(k):
                r[k + "_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(r[k]))
    (BACKUPS / "state.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
    return len(rows)


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)


def push() -> None:
    if git("rev-parse", "--is-inside-work-tree").returncode != 0:
        sys.exit("--push: this folder is not a git repository yet (run `git init` and add a remote).")
    if not git("remote").stdout.strip():
        sys.exit("--push: no git remote configured (git remote add origin <url>).")
    git("add", "backups")
    if git("diff", "--cached", "--quiet", "--", "backups").returncode == 0:
        print("git: no changes to commit")
        return
    msg = f"Monitor backup {time.strftime('%Y-%m-%d %H:%M')}"
    res = git("commit", "-m", msg, "--", "backups")
    if res.returncode != 0:
        sys.exit(f"git commit failed:\n{res.stderr}")
    res = git("push")
    if res.returncode != 0:
        sys.exit(f"git push failed:\n{res.stderr}")
    print(f"git: committed and pushed '{msg}'")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default=DEFAULT_URL, help=f"monitor backup URL (default {DEFAULT_URL})")
    ap.add_argument("--from-file", type=Path, help="use this SQLite snapshot instead of downloading")
    ap.add_argument("--keep", type=int, default=10, help="compressed DB snapshots to keep (default 10)")
    ap.add_argument("--push", action="store_true", help="git commit and push backups/ afterwards")
    args = ap.parse_args()

    BACKUPS.mkdir(exist_ok=True)
    gitignore = BACKUPS / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("# Full database snapshots stay local; the text exports are committed.\ndb/\n")

    with tempfile.TemporaryDirectory() as tmp:
        snapshot = Path(tmp) / "snapshot.db"
        if args.from_file:
            shutil.copyfile(args.from_file, snapshot)
        else:
            print(f"downloading {args.url} ...")
            download(args.url, snapshot)
        con = sqlite3.connect(snapshot)
        if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            sys.exit("snapshot failed SQLite integrity check; nothing was changed")
        total, new = merge_events(con)
        days = merge_availability(con)
        devices = write_state(con)
        con.close()
        saved = save_snapshot(snapshot, args.keep)

    print(f"events.jsonl: {total} events ({new} new)")
    print(f"daily_availability.csv: {days} days")
    print(f"state.json: {devices} devices")
    print(f"snapshot: {saved.relative_to(REPO)}")
    if args.push:
        push()


if __name__ == "__main__":
    main()

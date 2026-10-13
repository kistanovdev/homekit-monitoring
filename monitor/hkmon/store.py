"""SQLite persistence for device state, events and per-check samples."""
import sqlite3
import time
from dataclasses import dataclass

SCHEMA = """
CREATE TABLE IF NOT EXISTS state (
    name TEXT PRIMARY KEY, grp TEXT, status TEXT, since REAL,
    last_ok REAL, last_check REAL, fails INTEGER, detail TEXT
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, name TEXT, kind TEXT, detail TEXT
);
CREATE INDEX IF NOT EXISTS events_ts ON events(ts);
CREATE TABLE IF NOT EXISTS samples (ts REAL, name TEXT, ok INTEGER);
CREATE INDEX IF NOT EXISTS samples_ts_name ON samples(ts, name);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
"""


def connect(path: str) -> sqlite3.Connection:
    con = sqlite3.connect(path, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.executescript(SCHEMA)
    return con


@dataclass
class DeviceState:
    name: str
    group: str
    status: str = "unknown"  # unknown | up | down
    since: float = 0.0
    last_ok: float = 0.0
    last_check: float = 0.0
    fails: int = 0
    detail: str = ""


class Store:
    def __init__(self, path: str) -> None:
        self.con = connect(path)

    def load_states(self) -> dict[str, DeviceState]:
        rows = self.con.execute("SELECT * FROM state").fetchall()
        return {
            r["name"]: DeviceState(r["name"], r["grp"], r["status"], r["since"],
                                   r["last_ok"], r["last_check"], r["fails"], r["detail"])
            for r in rows
        }

    def save_states(self, states: list[DeviceState]) -> None:
        self.con.executemany(
            "INSERT OR REPLACE INTO state VALUES (?,?,?,?,?,?,?,?)",
            [(s.name, s.group, s.status, s.since, s.last_ok, s.last_check, s.fails, s.detail)
             for s in states],
        )
        self.con.commit()

    def drop_states_except(self, names: set[str]) -> None:
        for (name,) in self.con.execute("SELECT name FROM state").fetchall():
            if name not in names:
                self.con.execute("DELETE FROM state WHERE name=?", (name,))
        self.con.commit()

    def add_event(self, name: str, kind: str, detail: str, ts: float | None = None) -> None:
        self.con.execute(
            "INSERT INTO events (ts, name, kind, detail) VALUES (?,?,?,?)",
            (ts or time.time(), name, kind, detail),
        )
        self.con.commit()

    def add_samples(self, ts: float, results: list[tuple[str, bool]]) -> None:
        self.con.executemany(
            "INSERT INTO samples VALUES (?,?,?)", [(ts, n, int(ok)) for n, ok in results]
        )
        self.con.commit()

    def get_meta(self, key: str) -> str | None:
        row = self.con.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return row["value"] if row else None

    def set_meta(self, key: str, value: str) -> None:
        self.con.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", (key, value))
        self.con.commit()

    def prune(self, retention_days: int) -> None:
        cutoff = time.time() - retention_days * 86400
        self.con.execute("DELETE FROM samples WHERE ts < ?", (cutoff,))
        self.con.execute("DELETE FROM events WHERE ts < ?", (cutoff,))
        self.con.commit()

"""Read-only web dashboard and JSON API, served from a background thread."""
import html
import json
import os
import sqlite3
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .config import Device
from .store import connect

STYLE = """
body{font:14px -apple-system,system-ui,sans-serif;margin:24px;color:#222;background:#fafafa}
h1{font-size:20px;margin:0 0 4px} h2{font-size:16px;margin:24px 0 8px}
nav a{margin-right:16px} .muted{color:#777}
table{border-collapse:collapse;background:#fff;width:100%}
td,th{padding:4px 8px;border-bottom:1px solid #eee;text-align:left;vertical-align:top}
th{background:#f0f0f0;font-weight:600}
.up{color:#1a7f37;font-weight:600}.down{color:#cf222e;font-weight:600}.unknown{color:#777}
.ev-down,.ev-outage,.ev-unpaired,.ev-boot{color:#cf222e}.ev-up,.ev-paired{color:#1a7f37}
.tl{display:flex;gap:1px}.tl span{width:4px;height:14px;display:inline-block;background:#ddd}
.tl .g{background:#2da44e}.tl .p{background:#e3a008}.tl .r{background:#cf222e}
.tl-name{white-space:nowrap;padding-right:8px}
"""


def _t(ts: float | None) -> str:
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(ts)) if ts else "-"


def _ago(ts: float | None) -> str:
    if not ts:
        return "-"
    s = int(time.time() - ts)
    if s < 120:
        return f"{s}s ago"
    if s < 7200:
        return f"{s // 60}m ago"
    if s < 172800:
        return f"{s // 3600}h ago"
    return f"{s // 86400}d ago"


def _page(title: str, body: str) -> bytes:
    nav = '<nav><a href="/">Status</a><a href="/timeline">Timeline</a><a href="/events">Events</a></nav>'
    return (f"<!doctype html><html><head><meta charset=utf-8><title>{html.escape(title)}</title>"
            f'<meta name=viewport content="width=device-width"><style>{STYLE}</style></head>'
            f"<body><h1>{html.escape(title)}</h1>{nav}{body}</body></html>").encode()


class Dashboard:
    def __init__(self, db_path: str, devices: list[Device], port: int, notify_enabled: bool) -> None:
        self.db_path = db_path
        self.devices = devices
        self.port = port
        self.notify_enabled = notify_enabled

    def start(self) -> None:
        dash = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                url = urlparse(self.path)
                qs = parse_qs(url.query)
                routes = {
                    "/": dash.status_page,
                    "/timeline": dash.timeline_page,
                    "/events": dash.events_page,
                    "/api/status": dash.api_status,
                    "/api/events": dash.api_events,
                    "/api/backup": dash.api_backup,
                }
                fn = routes.get(url.path)
                if not fn:
                    self.send_error(404)
                    return
                ctype, body = fn(qs)
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("0.0.0.0", self.port), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()

    # -- pages -------------------------------------------------------------

    def status_page(self, qs):
        con = connect(self.db_path)
        now = time.time()
        states = {r["name"]: r for r in con.execute("SELECT * FROM state")}
        avail = dict(con.execute(
            "SELECT name, AVG(ok) FROM samples WHERE ts > ? GROUP BY name", (now - 86400,)))
        drops = dict(con.execute(
            "SELECT name, COUNT(*) FROM events WHERE kind='down' AND ts > ? GROUP BY name",
            (now - 7 * 86400,)))
        last_check = max((r["last_check"] or 0 for r in states.values()), default=0)
        con.close()

        counts = {"up": 0, "down": 0, "unknown": 0}
        for r in states.values():
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        notify = "on" if self.notify_enabled else "off (set NTFY_URL)"
        body = [f'<p class=muted>{counts["up"]} up, {counts["down"]} down, '
                f'{counts["unknown"]} unknown. Last check {_ago(last_check)}. '
                f"Phone alerts: {notify}.</p>"]

        down = [d for d in self.devices if states.get(d.name) and states[d.name]["status"] == "down"]
        if down:
            body.append("<h2>Down now</h2><table><tr><th>Device</th><th>Since</th><th>Detail</th></tr>")
            for d in down:
                r = states[d.name]
                body.append(f"<tr><td>{html.escape(d.name)}</td><td>{_t(r['since'])} "
                            f"({_ago(r['since'])})</td><td>{html.escape(r['detail'] or '')}</td></tr>")
            body.append("</table>")

        groups: dict[str, list[Device]] = {}
        for d in self.devices:
            groups.setdefault(d.group, []).append(d)
        for group, devs in groups.items():
            body.append(f"<h2>{html.escape(group)}</h2><table><tr><th>Device</th><th>Status</th>"
                        "<th>Since</th><th>24h avail.</th><th>Drops 7d</th><th>Detail</th></tr>")
            for d in devs:
                r = states.get(d.name)
                status = r["status"] if r else "unknown"
                a = avail.get(d.name)
                body.append(
                    f"<tr><td>{html.escape(d.name)}</td><td class={status}>{status}</td>"
                    f"<td>{_ago(r['since']) if r else '-'}</td>"
                    f"<td>{'-' if a is None else f'{a * 100:.1f}%'}</td>"
                    f"<td>{drops.get(d.name, 0)}</td>"
                    f"<td class=muted>{html.escape((r['detail'] or '') if r else '')}</td></tr>")
            body.append("</table>")
        return "text/html; charset=utf-8", _page("Home network monitor", "".join(body))

    def timeline_page(self, qs):
        days = min(max(int((qs.get("days") or ["7"])[0]), 1), 90)
        bucket = 900 if days <= 2 else 3600 if days <= 14 else 4 * 3600
        now = time.time()
        start = now - days * 86400
        nbuckets = int((now - start) // bucket) + 1
        con = connect(self.db_path)
        rows = con.execute(
            "SELECT name, CAST((ts - ?) / ? AS INTEGER) AS b, AVG(ok) FROM samples "
            "WHERE ts >= ? GROUP BY name, b", (start, bucket, start)).fetchall()
        con.close()
        grid: dict[str, dict[int, float]] = {}
        for name, b, ok in rows:
            grid.setdefault(name, {})[b] = ok

        links = " ".join(f'<a href="/timeline?days={n}">{n}d</a>' for n in (1, 3, 7, 14, 30, 90))
        width = f"{bucket // 60} min" if bucket < 3600 else f"{bucket // 3600} h"
        body = [f"<p class=muted>{links}. Each cell is {width}; green = always up, "
                "amber = partly down, red = down, grey = no data. "
                f"{_t(start)} &rarr; {_t(now)}</p><table>"]
        for d in self.devices:
            cells = []
            row = grid.get(d.name, {})
            for b in range(nbuckets):
                ok = row.get(b)
                cls = "" if ok is None else "g" if ok >= 0.999 else "r" if ok <= 0.001 else "p"
                tip = _t(start + b * bucket) + ("" if ok is None else f" {ok * 100:.0f}%")
                cells.append(f'<span class="{cls}" title="{tip}"></span>')
            body.append(f"<tr><td class=tl-name>{html.escape(d.name)}</td>"
                        f"<td><div class=tl>{''.join(cells)}</div></td></tr>")
        body.append("</table>")
        return "text/html; charset=utf-8", _page(f"Timeline: last {days} days", "".join(body))

    def events_page(self, qs):
        name = (qs.get("name") or [None])[0]
        rows = self._events(name, 500)
        body = ["<table><tr><th>Time</th><th>Device</th><th>Event</th><th>Detail</th></tr>"]
        for r in rows:
            link = f'<a href="/events?name={html.escape(r["name"])}">{html.escape(r["name"])}</a>'
            body.append(f"<tr><td>{_t(r['ts'])}</td><td>{link}</td>"
                        f"<td class=ev-{r['kind']}>{r['kind']}</td>"
                        f"<td>{html.escape(r['detail'] or '')}</td></tr>")
        body.append("</table>")
        title = f"Events: {name}" if name else "Events"
        return "text/html; charset=utf-8", _page(title, "".join(body))

    def api_status(self, qs):
        con = connect(self.db_path)
        rows = [dict(r) for r in con.execute("SELECT * FROM state ORDER BY grp, name")]
        con.close()
        return "application/json", json.dumps(rows).encode()

    def api_events(self, qs):
        since = float((qs.get("since") or ["0"])[0])
        con = connect(self.db_path)
        rows = [dict(r) for r in con.execute(
            "SELECT * FROM events WHERE ts > ? ORDER BY ts DESC LIMIT 2000", (since,))]
        con.close()
        return "application/json", json.dumps(rows).encode()

    def api_backup(self, qs):
        """Consistent snapshot of the whole database, safe to take while checks run."""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "snapshot.db")
            src = connect(self.db_path)
            dst = sqlite3.connect(path)
            src.backup(dst)
            dst.close()
            src.close()
            with open(path, "rb") as f:
                return "application/vnd.sqlite3", f.read()

    def _events(self, name: str | None, limit: int):
        con = connect(self.db_path)
        if name:
            rows = con.execute("SELECT * FROM events WHERE name=? ORDER BY ts DESC LIMIT ?",
                               (name, limit)).fetchall()
        else:
            rows = con.execute("SELECT * FROM events ORDER BY ts DESC LIMIT ?", (limit,)).fetchall()
        con.close()
        return rows

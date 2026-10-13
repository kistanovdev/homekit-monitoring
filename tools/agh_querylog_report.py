"""Summarise an AdGuard Home querylog.json (JSON lines) read from stdin.

Usage: sudo cat querylog.json | python3 agh_querylog_report.py
"""
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime

per_client = Counter()
blocked_by_client = defaultdict(Counter)
per_second = Counter()
first = last = None

for line in sys.stdin:
    try:
        q = json.loads(line)
    except ValueError:
        continue
    ip, t, host = q.get("IP", "?"), q.get("T", ""), q.get("QH", "")
    per_client[ip] += 1
    per_second[t[:19]] += 1
    first = first or t
    last = t
    if q.get("Result", {}).get("IsFiltered"):
        blocked_by_client[ip][host] += 1

print(f"range: {first} .. {last}")
print(f"total queries: {sum(per_client.values())}, clients: {len(per_client)}")
print("\n== top clients")
for ip, n in per_client.most_common(60):
    print(f"{ip:40} {n}")
print("\n== blocked domains by client (top 5 each)")
for ip, c in sorted(blocked_by_client.items(), key=lambda kv: -sum(kv[1].values())):
    print(f"{ip:40} {sum(c.values()):6}  " + ", ".join(f"{h}({n})" for h, n in c.most_common(5)))
print("\n== busiest seconds (all clients, shared ratelimit bucket)")
for sec, n in per_second.most_common(15):
    print(f"{sec}  {n}")
over = sum(1 for n in per_second.values() if n > 20)
print(f"\nseconds over 20 qps: {over}")

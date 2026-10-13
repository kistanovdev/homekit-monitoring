"""Main check loop: probe every device, track up/down state, record and alert."""
import asyncio
import logging
import time

from .config import Device, Settings
from .mdns import MdnsWatcher, Service
from .notify import Notifier
from .probe import dns_ok, ping_ok, tcp_ok
from .store import DeviceState, Store

log = logging.getLogger(__name__)

# Built-in checks that are not physical devices.
NETWORK_CHECKS = [
    Device(name="Internet", group="network", check="internet"),
    Device(name="DNS", group="network", check="dns"),
    Device(name="Thread network", group="network", check="thread"),
]

INTERNET_TARGETS = [("1.1.1.1", 443), ("8.8.8.8", 443), ("9.9.9.9", 443)]


def fmt_duration(seconds: float) -> str:
    s = int(seconds)
    d, s = divmod(s, 86400)
    h, s = divmod(s, 3600)
    m = s // 60
    if d:
        return f"{d}d {h}h"
    if h:
        return f"{h}h {m}m"
    return f"{m}m"


def fmt_time(ts: float) -> str:
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(ts))


def host_boot_time() -> int:
    with open("/proc/stat") as f:
        for line in f:
            if line.startswith("btime"):
                return int(line.split()[1])
    return 0


def _unpaired(sf: str) -> bool:
    """HAP status flag bit 0 set means the accessory is not paired with any controller."""
    try:
        return bool(int(sf) & 1)
    except ValueError:
        return False


class Monitor:
    def __init__(self, settings: Settings, devices: list[Device]) -> None:
        self.s = settings
        self.devices = NETWORK_CHECKS + devices
        self.store = Store(settings.db_path)
        self.mdns = MdnsWatcher()
        self.notifier = Notifier(settings.ntfy_url, settings.ntfy_token)
        saved = self.store.load_states()
        self.states: dict[str, DeviceState] = {}
        for d in self.devices:
            st = saved.get(d.name) or DeviceState(d.name, d.group)
            st.group = d.group
            self.states[d.name] = st
        self.store.drop_states_except(set(self.states))
        self._sem = asyncio.Semaphore(16)
        self._hap_flags: dict[str, tuple[str, str]] = {}
        self._last_prune = 0.0

    async def run(self) -> None:
        await self.mdns.start()
        self._record_start()
        await asyncio.sleep(10)  # let the first mDNS browse settle
        while True:
            started = time.monotonic()
            try:
                await self.cycle()
            except Exception:
                log.exception("check cycle failed")
            await asyncio.sleep(max(1.0, self.s.interval - (time.monotonic() - started)))

    def _record_start(self) -> None:
        boot = host_boot_time()
        prev = self.store.get_meta("host_boot")
        if prev and abs(int(prev) - boot) > 5:
            row = self.store.con.execute("SELECT MAX(ts) FROM samples").fetchone()
            last_seen = row[0]
            window = f" Monitor last ran at {fmt_time(last_seen)}." if last_seen else ""
            msg = (f"Pi booted at {fmt_time(boot)}.{window} "
                   "If nobody restarted it, this was probably a power cut.")
            self.store.add_event("Pi", "boot", msg, boot)
            self.notifier.send("Homebridge Pi rebooted", msg, "high", "electric_plug")
        self.store.set_meta("host_boot", str(boot))
        self.store.add_event("monitor", "monitor", "monitor started")

    async def cycle(self) -> None:
        now = time.time()
        await self.mdns.refresh()
        results = await asyncio.gather(*(self.check(d) for d in self.devices))
        downs: list[Device] = []
        ups: list[tuple[Device, float]] = []
        for d, (ok, detail) in zip(self.devices, results):
            st = self.states[d.name]
            prev_detail = st.detail
            st.last_check = now
            st.detail = detail
            if ok:
                st.fails = 0
                st.last_ok = now
                if st.status != "up":
                    if st.status == "down":
                        ups.append((d, now - st.since))
                    st.status = "up"
                    st.since = now
                if d.check == "thread" and prev_detail and detail != prev_detail:
                    self.store.add_event(d.name, "thread", f"{prev_detail} -> {detail}")
            else:
                st.fails += 1
                if st.status != "down" and st.fails >= self.s.down_after:
                    st.status = "down"
                    st.since = now - (st.fails - 1) * self.s.interval
                    downs.append(d)
        self._report(downs, ups)
        self._check_hap_flags()
        self.store.save_states(list(self.states.values()))
        self.store.add_samples(now, [(d.name, ok) for d, (ok, _) in zip(self.devices, results)])
        await self.notifier.flush()
        if now - self._last_prune > 3600:
            self.store.prune(self.s.retention_days)
            self._last_prune = now

    async def check(self, d: Device) -> tuple[bool, str]:
        async with self._sem:
            if d.check == "internet":
                for host, port in INTERNET_TARGETS:
                    if await tcp_ok(host, port):
                        return True, f"tcp {host}:{port}"
                return False, "no TCP connection to 1.1.1.1, 8.8.8.8 or 9.9.9.9"
            if d.check == "dns":
                ok = await dns_ok()
                return ok, "resolved www.apple.com" if ok else "lookup of www.apple.com failed"
            if d.check == "thread":
                return self._thread_status()

            matches = self.mdns.match(d.mdns)
            ipv4 = next((a for s in matches for a in s.ipv4), None) or d.ip
            if d.check == "presence" or not ipv4:
                if matches:
                    return True, "mDNS: " + ", ".join(sorted({s.name for s in matches}))
                return False, "not advertised in mDNS"

            if d.check != "service" and await ping_ok(ipv4):
                return True, f"ping {ipv4}"
            # Many low-power devices ignore ping; fall back to their service port.
            ports = [s.port for s in matches if s.type == "_hap._tcp.local." and s.port]
            if d.tcp_port:
                ports.append(d.tcp_port)
            for port in dict.fromkeys(ports):
                if await tcp_ok(ipv4, port):
                    return True, f"tcp {ipv4}:{port} (ignores ping)"
            cached = " (mDNS record still cached)" if matches else ""
            return False, f"no reply from {ipv4}{cached}"

    def _thread_status(self) -> tuple[bool, str]:
        brs = self.mdns.of_type("_meshcop._udp.local.")
        if not brs:
            return False, "no Thread border routers advertised"
        nets: dict[tuple[str, str], list[str]] = {}
        for s in brs:
            nets.setdefault((s.txt.get("nn", "?"), s.txt.get("xp", "")), []).append(s.name)
        if len(nets) > 1:
            parts = [f"{nn} ({', '.join(sorted(m))})" for (nn, _), m in nets.items()]
            return False, "Thread split into separate networks: " + "; ".join(parts)
        (nn, _), members = next(iter(nets.items()))
        return True, f"{nn}: {len(members)} border routers"

    def _device_name(self, svc: Service) -> str:
        for d in self.devices:
            if svc in self.mdns.match(d.mdns):
                return d.name
        return svc.name

    def _check_hap_flags(self) -> None:
        services = self.mdns.of_type("_hap._tcp.local.") + self.mdns.of_type("_hap._udp.local.")
        for svc in services:
            sf, cn = svc.txt.get("sf", ""), svc.txt.get("c#", "")
            prev = self._hap_flags.get(svc.name)
            self._hap_flags[svc.name] = (sf, cn)
            name = self._device_name(svc)
            if prev is None:
                if _unpaired(sf):
                    self.store.add_event(name, "unpaired", "not paired with HomeKit (seen at startup)")
                continue
            prev_sf, prev_cn = prev
            if _unpaired(sf) and not _unpaired(prev_sf):
                self.store.add_event(name, "unpaired", "accessory lost its HomeKit pairing")
                self.notifier.send(f"{name} lost its HomeKit pairing",
                                   "It will need to be re-added in the Home app.", "high", "warning")
            elif _unpaired(prev_sf) and not _unpaired(sf):
                self.store.add_event(name, "paired", "accessory paired with HomeKit")
            if prev_cn and cn and prev_cn != cn:
                self.store.add_event(name, "config",
                                     f"HomeKit config number {prev_cn} -> {cn} "
                                     "(firmware update, re-pair or accessory change)")

    def _report(self, downs: list[Device], ups: list[tuple[Device, float]]) -> None:
        for d in downs:
            self.store.add_event(d.name, "down", self.states[d.name].detail)
        for d, dur in ups:
            self.store.add_event(d.name, "up", f"back after {fmt_duration(dur)}")
        if len(downs) >= self.s.mass_outage:
            self.store.add_event("*", "outage", f"{len(downs)} devices went down together: "
                                 + ", ".join(d.name for d in downs))

        notify_downs = [d for d in downs if d.notify]
        notify_ups = [(d, dur) for d, dur in ups if d.notify]
        if len(notify_downs) >= self.s.mass_outage:
            self.notifier.send(f"{len(notify_downs)} devices went offline",
                               ", ".join(d.name for d in notify_downs), "high", "rotating_light")
        else:
            for d in notify_downs:
                priority = "high" if d.group in ("network", "infrastructure") else "default"
                self.notifier.send(f"{d.name} offline", self.states[d.name].detail, priority, "warning")
        if len(notify_ups) >= self.s.mass_outage:
            longest = max(dur for _, dur in notify_ups)
            self.notifier.send(f"{len(notify_ups)} devices back online",
                               f"Longest outage {fmt_duration(longest)}: "
                               + ", ".join(d.name for d, _ in notify_ups), "default", "white_check_mark")
        else:
            for d, dur in notify_ups:
                self.notifier.send(f"{d.name} back online", f"Was offline for {fmt_duration(dur)}",
                                   "low", "white_check_mark")

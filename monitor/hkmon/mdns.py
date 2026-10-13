"""Bonjour/mDNS watcher for HomeKit, Matter, Thread and AirPlay services."""
import asyncio
import logging
import time
from dataclasses import dataclass, field

from zeroconf import IPVersion, ServiceStateChange
from zeroconf.asyncio import AsyncServiceBrowser, AsyncServiceInfo, AsyncZeroconf

log = logging.getLogger(__name__)

SERVICE_TYPES = [
    "_hap._tcp.local.",
    "_hap._udp.local.",
    "_matter._tcp.local.",
    "_meshcop._udp.local.",
    "_airplay._tcp.local.",
]

# A service that has not answered a resolve for this long counts as gone.
STALE_AFTER = 600


@dataclass
class Service:
    type: str
    name: str
    server: str = ""
    port: int = 0
    ipv4: list[str] = field(default_factory=list)
    ipv6: list[str] = field(default_factory=list)
    txt: dict[str, str] = field(default_factory=dict)
    resolved_at: float = 0.0

    @property
    def fresh(self) -> bool:
        return time.time() - self.resolved_at < STALE_AFTER


def _decode_txt(props: dict) -> dict[str, str]:
    out = {}
    for k, v in props.items():
        key = k.decode("utf-8", "replace") if isinstance(k, bytes) else str(k)
        if v is None:
            out[key] = ""
            continue
        try:
            out[key] = v.decode("utf-8")
        except UnicodeDecodeError:
            # Binary values such as the Thread extended PAN ID.
            out[key] = v.hex()
    return out


class MdnsWatcher:
    def __init__(self) -> None:
        self.services: dict[tuple[str, str], Service] = {}
        self._tasks: set[asyncio.Task] = set()
        self._azc: AsyncZeroconf | None = None

    async def start(self) -> None:
        try:
            self._azc = AsyncZeroconf(ip_version=IPVersion.All)
        except OSError as e:
            log.warning("IPv6 mDNS unavailable (%s), using IPv4 only", e)
            self._azc = AsyncZeroconf(ip_version=IPVersion.V4Only)
        self._browser = AsyncServiceBrowser(
            self._azc.zeroconf, SERVICE_TYPES, handlers=[self._on_change]
        )

    async def stop(self) -> None:
        if self._azc:
            await self._browser.async_cancel()
            await self._azc.async_close()

    def _on_change(self, zeroconf, service_type: str, name: str,
                   state_change: ServiceStateChange) -> None:
        if state_change is ServiceStateChange.Removed:
            self.services.pop((service_type, name), None)
            return
        self._spawn(self._resolve(service_type, name))

    def _spawn(self, coro) -> None:
        task = asyncio.ensure_future(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def _resolve(self, service_type: str, name: str) -> None:
        info = AsyncServiceInfo(service_type, name)
        try:
            ok = await info.async_request(self._azc.zeroconf, 3000)
        except Exception as e:  # zeroconf raises a variety of errors on bad packets
            log.debug("resolve %s failed: %s", name, e)
            return
        if not ok:
            return
        svc = self.services.setdefault(
            (service_type, name),
            Service(type=service_type, name=name.removesuffix("." + service_type)),
        )
        svc.server = (info.server or "").rstrip(".")
        svc.port = info.port or 0
        svc.ipv4 = info.parsed_scoped_addresses(IPVersion.V4Only)
        svc.ipv6 = info.parsed_scoped_addresses(IPVersion.V6Only)
        svc.txt = _decode_txt(info.properties)
        svc.resolved_at = time.time()

    async def refresh(self) -> None:
        """Re-resolve every known service; answered from cache until TTLs expire."""
        await asyncio.gather(
            *(self._resolve(t, f"{s.name}.{t}") for (t, _), s in list(self.services.items())),
            return_exceptions=True,
        )

    def match(self, patterns: list[str]) -> list[Service]:
        """Fresh services whose instance name or hostname matches a pattern."""
        if not patterns:
            return []
        pats = [p.lower().removesuffix(".local") for p in patterns]
        out = []
        for s in self.services.values():
            if not s.fresh:
                continue
            name = s.name.lower()
            host = s.server.lower().removesuffix(".local")
            if any(p == name or p == host for p in pats):
                out.append(s)
        return out

    def of_type(self, service_type: str) -> list[Service]:
        return [s for s in self.services.values() if s.type == service_type and s.fresh]

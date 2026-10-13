"""Configuration: environment settings and the device inventory (devices.yaml)."""
import os
from dataclasses import dataclass, field

import yaml


@dataclass
class Settings:
    interval: int = int(os.environ.get("INTERVAL", "60"))
    # Consecutive failed checks before a device is marked down.
    down_after: int = int(os.environ.get("DOWN_AFTER", "3"))
    # This many devices going down in the same cycle is reported as one outage.
    mass_outage: int = int(os.environ.get("MASS_OUTAGE", "5"))
    http_port: int = int(os.environ.get("HTTP_PORT", "8088"))
    db_path: str = os.environ.get("DB_PATH", "/data/hkmon.db")
    devices_path: str = os.environ.get("DEVICES_PATH", "/config/devices.yaml")
    ntfy_url: str = os.environ.get("NTFY_URL", "")
    ntfy_token: str = os.environ.get("NTFY_TOKEN", "")
    retention_days: int = int(os.environ.get("RETENTION_DAYS", "90"))


@dataclass
class Device:
    name: str
    group: str
    ip: str | None = None
    mac: str | None = None
    # mDNS instance names or hostnames that identify this device.
    mdns: list[str] = field(default_factory=list)
    # auto: ping/TCP if an IPv4 address is known, else mDNS presence.
    # presence: mDNS presence only (Thread devices).
    # service: TCP to the HomeKit port only, no ping (services on this host).
    check: str = "auto"
    # Optional TCP port to try when ping fails (in addition to the HAP port).
    tcp_port: int | None = None
    notify: bool = True


def load_devices(path: str) -> list[Device]:
    with open(path) as f:
        raw = yaml.safe_load(f) or {}
    devices = []
    for group, entries in (raw.get("groups") or {}).items():
        for e in entries or []:
            mdns = e.get("mdns", [])
            devices.append(Device(
                name=e["name"],
                group=group,
                ip=e.get("ip"),
                mac=e.get("mac"),
                mdns=[mdns] if isinstance(mdns, str) else list(mdns),
                check=e.get("check", "auto"),
                tcp_port=e.get("tcp_port"),
                notify=e.get("notify", True),
            ))
    names = [d.name for d in devices]
    dupes = {n for n in names if names.count(n) > 1}
    if dupes:
        raise ValueError(f"duplicate device names in {path}: {sorted(dupes)}")
    return devices

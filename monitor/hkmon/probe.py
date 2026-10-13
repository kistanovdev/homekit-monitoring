"""Reachability probes."""
import asyncio
import socket


async def ping_ok(host: str, timeout: int = 2) -> bool:
    proc = await asyncio.create_subprocess_exec(
        "ping", "-c", "1", "-W", str(timeout), host,
        stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
    )
    return await proc.wait() == 0


async def arp_ok(host: str, timeout: int = 2) -> bool:
    """True if the host answers an ARP request (works for devices that drop ping)."""
    proc = await asyncio.create_subprocess_exec(
        "arping", "-c", "1", "-w", str(timeout), host,
        stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
    )
    return await proc.wait() == 0


async def tcp_ok(host: str, port: int, timeout: float = 3.0) -> bool:
    try:
        _, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout)
    except (OSError, asyncio.TimeoutError):
        return False
    writer.close()
    try:
        await writer.wait_closed()
    except OSError:
        pass
    return True


async def dns_ok(name: str = "www.apple.com", timeout: float = 5.0) -> bool:
    loop = asyncio.get_running_loop()
    try:
        await asyncio.wait_for(
            loop.getaddrinfo(name, 443, type=socket.SOCK_STREAM), timeout
        )
    except (OSError, asyncio.TimeoutError):
        return False
    return True

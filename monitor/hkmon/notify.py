"""Push notifications via ntfy, queued so alerts survive an internet outage."""
import asyncio
import logging
import urllib.request
from collections import deque

log = logging.getLogger(__name__)


class Notifier:
    def __init__(self, url: str, token: str = "") -> None:
        self.url = url
        self.token = token
        self.pending: deque[tuple[str, str, str, str]] = deque(maxlen=50)

    @property
    def enabled(self) -> bool:
        return bool(self.url)

    def send(self, title: str, message: str, priority: str = "default", tags: str = "") -> None:
        if self.enabled:
            self.pending.append((title, message, priority, tags))

    async def flush(self) -> None:
        """Deliver queued messages; stop at the first failure and retry next cycle."""
        while self.pending:
            msg = self.pending[0]
            try:
                await asyncio.to_thread(self._post, *msg)
            except OSError as e:
                log.info("ntfy delivery failed, will retry: %s", e)
                return
            self.pending.popleft()

    def _post(self, title: str, message: str, priority: str, tags: str) -> None:
        headers = {"Title": title, "Priority": priority}
        if tags:
            headers["Tags"] = tags
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = urllib.request.Request(self.url, data=message.encode(), headers=headers)
        with urllib.request.urlopen(req, timeout=10):
            pass

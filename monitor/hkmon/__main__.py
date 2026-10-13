import asyncio
import logging

from .config import Settings, load_devices
from .monitor import Monitor
from .web import Dashboard


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    settings = Settings()
    devices = load_devices(settings.devices_path)

    async def run() -> None:
        monitor = Monitor(settings, devices)
        Dashboard(settings.db_path, monitor.devices, settings.http_port,
                  monitor.notifier.enabled).start()
        logging.info("monitoring %d checks, dashboard on port %d",
                     len(monitor.devices), settings.http_port)
        await monitor.run()

    asyncio.run(run())


main()

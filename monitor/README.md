# hkmon: home network monitor

Runs on the Homebridge Pi (192.168.0.52) as the `hkmon` Docker container and
checks every device in `devices.yaml` once a minute.

- Wi-Fi/Ethernet devices: ping, falling back to the device's HomeKit TCP port.
- Thread devices: Bonjour (mDNS) presence, which goes through the border routers.
- Built-in checks: Internet, DNS, and Thread network health (detects a split network).
- Also records: Pi reboots (power cuts), HomeKit accessories losing their
  pairing, and HomeKit config-number changes (firmware updates and re-pairs).

A device is marked down after `DOWN_AFTER` consecutive failed checks (default 3).
If `MASS_OUTAGE` or more go down in the same cycle (default 5), it is recorded
as a single outage.

Dashboard: http://192.168.0.52:8088 (status, `/timeline?days=N`, `/events`,
`/api/status`, `/api/events`). Data lives in `~/homekit-monitor/data/hkmon.db`
and is kept for 90 days.

## Phone alerts (optional)

Install the ntfy app, subscribe to a hard-to-guess topic, then on the Pi:

    cd ~/homekit-monitor
    echo 'NTFY_URL=https://ntfy.sh/<your-topic>' > .env
    sudo docker compose up -d

Alerts are queued and retried, so an internet outage is reported once the
connection comes back.

## Deploy changes from this repo

    tar czf - --exclude data -C monitor . | ssh kistanov@192.168.0.52 'tar xzf - -C ~/homekit-monitor'
    ssh -t kistanov@192.168.0.52 'cd ~/homekit-monitor && sudo docker compose up -d --build'

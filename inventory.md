# Home device inventory

Last updated 2026-10-13. Live up/down status is on the monitor dashboard: http://192.168.0.52:8088

## Status summary

| Status | Meaning | Count |
|---|---|---|
| ✅ | Confirmed: device type and location known | 33 |
| 🏷️ | Device type known, **room name needed** | 19 |
| ❓ | **Not identified yet** | 4 |
| | **Total smart/network devices** | **56** |

### ❓ Still to identify

| # | What the scan shows | IP / MAC | Best guess | Needed |
|---|---|---|---|---|
| 47 | Matter over Wi-Fi, Google Home only | .193 / 3c:31:74:db:55:28 | Second Nest thermostat | Confirm in Google Home (MAC ends 55:28), plus room |
| 46 | Nanoleaf Matter over Wi-Fi, in Apple Home and a 2nd app | .139 / 80:8a:f7:23:c8:cf | Nanoleaf strip, Lines or Skylight | Which product, plus room |
| 53 | Matter Thread device, in Apple Home and a 2nd app | ID 3E8F27DE3E6647FC | ? | What it is |
| 54 | Matter Thread device, in Apple Home and a 2nd app | ID 7A42F12275292777 | ? | What it is |
| - | The "2nd app" sharing #46, #53, #54 | Matter fabric 8E7AB5CF23900107 | Alexa, SmartThings or Nanoleaf app (not Google) | Which app |

### 🏷️ Room names needed

- Meross switches (11): 6bee, 6d21, 6d9f, 6da3, 6da5, 6df5, 6e90, 6e9a, 705a, the new 74c2, and the laundry switch (photo label too blurry; most likely 6e1a). All 4 connected dimmers are named.
  The MAC is printed on a sticker on each switch (visible with the cover plate off), and the Meross app shows it too.
- Nanoleaf: 4 A19 bulbs (#49–52), 2 Shapes (#44–45)
- VOCOlinc bulb (#43)
- Schlage Encode Plus (#48): assumed front door

Tip: to find a device, switch it off for about 4 minutes and see which row turns red on the dashboard.

### 🔌 Installed but not connected to the network (from switch photos, 2026-10-13)

These Meross MSS560 dimmers are on the wall but have never joined Wi-Fi, so they are not monitored.

| Room | Position | MAC |
|---|---|---|
| Kids' Room (Детская) | left | c4:e7:ae:0c:7f:43 |
| Kids' Room (Детская) | right | c4:e7:ae:0c:7d:f1 |
| Unpainted Room (Некрашенная) | | c4:e7:ae:0c:7f:ea |
| Blue Room (Синяя) | | c4:e7:ae:0c:81:82 |
| Bedroom (Спальня) | right | c4:e7:ae:0c:7e:01 |

---

## Infrastructure

| # | Status | Name | Device | IP | MAC | Notes |
|---|---|---|---|---|---|---|
| 1 | ✅ | Router | TP-Link Archer BE9700 (Wi-Fi 7 tri-band) | 192.168.0.1 | 68:7f:f0:25:44:d0 | Gateway + DHCP |
| 2 | ✅ | Homebridge Pi | Raspberry Pi 4 (Ethernet), Ubuntu 25.04 | 192.168.0.52 | d8:3a:dd:3d:f2:f2 | Homebridge (Dyson only), AdGuard Home, Unbound, hkmon monitor |
| 3 | ✅ | Mac mini | Apple Mac mini ("exrector's Mac mini") | 192.168.0.105 | 14:98:77:5e:2d:d1 | SMB + SSH enabled. Not monitored |

## Apple home hubs / Thread border routers

| # | Status | Name | Device | IP | MAC | Thread BR | Notes |
|---|---|---|---|---|---|---|---|
| 4 | ✅ | Living Room Apple TV | Apple TV 4K 2nd gen (AppleTV11,1) | 192.168.0.215 | 1c:b3:c9:13:b3:2f | yes | Also a Matter node in Apple Home |
| 5 | ✅ | Living Room HomePod mini | HomePod mini | 192.168.0.71 | 04:99:b9:9d:72:b2 | yes | |
| 6 | ✅ | Master Bathroom HomePod mini | HomePod mini | 192.168.0.119 | 58:d3:49:0c:3e:f1 | yes | |
| 7 | ✅ | Playroom HomePod mini | HomePod mini | 192.168.0.86 | 94:ea:32:90:0d:0d | yes | |
| 8 | ✅ | Daniel's Office HomePod | HomePod 1st gen | 192.168.0.14 | d4:90:9c:df:d5:7a | no | Named "Daniel's Office (2)" in AirPlay |
| 9 | ✅ | Guest Room Apple TV | Apple TV 4K 3rd gen, Wi-Fi only (AppleTV14,1) | 192.168.0.96 | c4:f7:c1:15:da:fd | no | Wi-Fi only; shouldn't be the primary home hub |

## Hubs / bridges (their child devices are not visible on the network)

| # | Status | Name | Device | IP | MAC | Notes |
|---|---|---|---|---|---|---|
| 10 | ✅ | Aqara Hub M3 | Aqara M3 (HM-G01E) | 192.168.0.43 | 18:c2:3c:48:b1:48 | Zigbee hub + Thread BR + Matter bridge |
| 11 | ✅ | Aqara Camera Hub G2H | Aqara G2H (CH-H01) | 192.168.0.44 | 54:ef:44:ca:ec:51 | |
| 12 | ✅ | Aqara Camera Hub G3 | Aqara G3 (CH-H03) | 192.168.0.216 | 54:ef:44:89:58:26 | |
| 13 | ✅ | Aqara Doorbell Repeater | Aqara G4 chime/repeater (SVD-C02) | 192.168.0.166 | 54:ef:44:5d:5b:ff | |
| 14 | ✅ | eufy HomeBase 2 | eufy HomeBase 2 | 192.168.0.214 | 10:2c:b1:68:0b:97 | Cameras sometimes need re-syncing in the eufy app |
| 15 | ✅ | Lutron Caséta Bridge | Lutron Smart Bridge 2 | 192.168.0.186 | 88:0c:e0:0e:52:0c | |

## Meross Wi-Fi (2.4 GHz)

| # | Status | Name | Device | IP | MAC | Notes |
|---|---|---|---|---|---|---|
| 16 | ✅ | Garage Door | Meross MSG100 garage opener | 192.168.0.250 | c4:e7:ae:05:b1:47 | |
| 17 | ✅ | Bedroom Dimmer (left) | Meross MSS560 dimmer | 192.168.0.129 | c4:e7:ae:0c:7c:2a | |
| 18 | ✅ | Stairs Dimmer | Meross MSS560 dimmer | 192.168.0.242 | c4:e7:ae:0c:7d:4c | |
| 19 | ✅ | Guest Room Dimmer | Meross MSS560 dimmer | 192.168.0.157 | c4:e7:ae:0c:80:06 | |
| 20 | ✅ | Baby Bedroom Dimmer | Meross MSS560 dimmer | 192.168.0.145 | c4:e7:ae:0c:80:f6 | |
| 21 | ✅ | Upstairs Bathroom Switch (left) | Meross MSS510 switch | 192.168.0.132 | 48:e1:e9:ef:64:e7 | |
| 22 | ✅ | Master Bedroom Closet Light | Meross MSS510 switch | 192.168.0.126 | 48:e1:e9:ef:66:43 | |
| 23 | ✅ | Kitchen Switch 6691 | Meross MSS510 switch | 192.168.0.204 | 48:e1:e9:ef:66:91 | |
| 24 | ✅ | Half Bath Switch (left) | Meross MSS510 switch | 192.168.0.94 | 48:e1:e9:ef:68:81 | |
| 25 | ✅ | Bathroom Switch (middle) | Meross MSS510 switch | 192.168.0.134 | 48:e1:e9:ef:69:5a | |
| 26 | ✅ | Upstairs Bathroom Switch (middle) | Meross MSS510 switch | 192.168.0.203 | 48:e1:e9:ef:69:9f | |
| 27 | ✅ | Half Bath Switch (right) | Meross MSS510 switch | 192.168.0.234 | 48:e1:e9:ef:6a:6f | |
| 28 | ✅ | Bedroom Switch (middle) | Meross MSS510 switch | 192.168.0.140 | 48:e1:e9:ef:6b:be | |
| 29 | 🏷️ | Switch 6bee | Meross MSS510 switch | 192.168.0.188 | 48:e1:e9:ef:6b:ee | |
| 30 | ✅ | Bathroom Switch (right) | Meross MSS510 switch | 192.168.0.32 | 48:e1:e9:ef:6c:03 | |
| 31 | 🏷️ | Switch 6d21 | Meross MSS510 switch | 192.168.0.141 | 48:e1:e9:ef:6d:21 | |
| 32 | ✅ | Upstairs Bathroom Switch (right) | Meross MSS510 switch | 192.168.0.189 | 48:e1:e9:ef:6d:50 | |
| 33 | ✅ | Kitchen Switch 6d71 | Meross MSS510 switch | 192.168.0.221 | 48:e1:e9:ef:6d:71 | |
| 34 | 🏷️ | Switch 6d9f | Meross MSS510 switch | 192.168.0.15 | 48:e1:e9:ef:6d:9f | |
| 35 | 🏷️ | Switch 6da3 | Meross MSS510 switch | 192.168.0.19 | 48:e1:e9:ef:6d:a3 | |
| 36 | 🏷️ | Switch 6da5 | Meross MSS510 switch | 192.168.0.21 | 48:e1:e9:ef:6d:a5 | |
| 37 | 🏷️ | Switch 6df5 | Meross MSS510 switch | 192.168.0.101 | 48:e1:e9:ef:6d:f5 | |
| 38 | 🏷️ | Laundry Switch (unconfirmed) | Meross MSS510 switch | 192.168.0.213 | 48:e1:e9:ef:6e:1a | |
| 39 | 🏷️ | Switch 6e90 | Meross MSS510 switch | 192.168.0.79 | 48:e1:e9:ef:6e:90 | |
| 40 | 🏷️ | Switch 6e9a | Meross MSS510 switch | 192.168.0.89 | 48:e1:e9:ef:6e:9a | |
| 41 | ✅ | Bathroom Switch (left) | Meross MSS510 switch | 192.168.0.149 | 48:e1:e9:ef:6f:87 | |
| 42 | 🏷️ | Switch 705a | Meross MSS510 switch | 192.168.0.183 | 48:e1:e9:ef:70:5a | |
| 56 | 🏷️ | Switch 74c2 | Meross switch (no HomeKit advertised) | 192.168.0.147 | 28:af:42:22:74:c2 | Added 2026-10-13 |

## Other Wi-Fi smart devices

| # | Status | Name | Device | IP | MAC | Notes |
|---|---|---|---|---|---|---|
| 43 | 🏷️ | VOCOlinc Bulb | VOCOlinc L3 bulb | 192.168.0.90 | e4:23:54:17:ff:08 | |
| 44 | 🏷️ | Nanoleaf Shapes 66F8 | Nanoleaf Shapes (NL42) | 192.168.0.190 | 80:8a:f7:10:66:f8 | Wi-Fi + Thread BR |
| 45 | 🏷️ | Nanoleaf Shapes 6CA6 | Nanoleaf Shapes (NL42) | 192.168.0.75 | 80:8a:f7:10:6c:a6 | Wi-Fi + Thread BR |
| 46 | ❓ | Nanoleaf Matter device | Nanoleaf, Matter over Wi-Fi | 192.168.0.139 | 80:8a:f7:23:c8:cf | In Apple Home + 2nd app |
| 47 | ❓ | Second Thermostat (unconfirmed) | Probably Google Nest | 192.168.0.193 | 3c:31:74:db:55:28 | Matter, Google Home only |
| 55 | ✅ | Hallway Thermostat | Google Nest Thermostat (4th gen) | 192.168.0.2 | 3c:31:74:db:54:b4 | Matter, Google Home only. Can be shared to Apple Home via Google Home → Linked Matter apps |

## Thread devices (no IPv4/MAC on Wi-Fi; reached through border routers)

| # | Status | Name | Device | Thread/HAP ID | Notes |
|---|---|---|---|---|---|
| 48 | 🏷️ | Front Door Lock (assumed) | Schlage Encode Plus (BE499WB) | Encode-Plus.local | HomeKit over Thread |
| 49 | 🏷️ | Nanoleaf A19 1WWJ | Nanoleaf Essentials A19 (NL45) | 87:82:67:CD:57:A2 | HomeKit over Thread |
| 50 | 🏷️ | Nanoleaf A19 3R4X | Nanoleaf Essentials A19 (NL45) | 35:A5:82:C2:96:65 | HomeKit over Thread |
| 51 | 🏷️ | Nanoleaf A19 4565 | Nanoleaf Essentials A19 (NL45) | AE:03:68:3F:7E:B9 | HomeKit over Thread |
| 52 | 🏷️ | Nanoleaf A19 96M2 | Nanoleaf Essentials A19 (NL45) | 69:70:CD:68:74:27 | HomeKit over Thread |
| 53 | ❓ | Matter Thread device A | ? | 3E8F27DE3E6647FC | In Apple Home + 2nd app |
| 54 | ❓ | Matter Thread device B | ? | 7A42F12275292777 | In Apple Home + 2nd app |

## Not monitored (phones, consoles)

| IP | MAC | Guess |
|---|---|---|
| 192.168.0.211 | bc:33:29:b4:93:e2 | PlayStation 5 |
| .11, .13, .17, .98, .133, .187 | private (randomized) MACs | iPhones / iPads / Watches |

## Matter fabrics (ecosystems) seen

| Fabric ID | Owner | Members |
|---|---|---|
| 724CFE1FC19C2CA8 | Apple Home | Living Room Apple TV, #46, #53, #54 |
| 054897967B5FBD1E | Google Home (confirmed) | #47, #55 |
| 8E7AB5CF23900107 | ❓ 2nd app (not Google) | #46, #53, #54 |
| 19D71CB34A7D29AE | Aqara M3's own Matter bridge | #10 |

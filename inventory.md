# Home device inventory

Scanned 2026-10-12 from MacBook Pro (192.168.0.136 wired / .212 Wi-Fi) via Bonjour (`dns-sd`), ARP and ping.
MACs marked `*` were derived from the device's IPv6 link-local (EUI-64) address because the device did not answer ARP during the scan.
`?` = guess, needs confirmation. Battery-saving Wi-Fi devices often ignore ping/ARP, so a missed ping alone does not mean a device is offline.

## Infrastructure

| # | Proposed name | Device | IP | MAC | Notes |
|---|---|---|---|---|---|
| 1 | Router | TP-Link Archer BE9700 (Wi-Fi 7 tri-band) | 192.168.0.1 | 68:7f:f0:25:44:d0 | Gateway + DHCP |
| 2 | Homebridge Pi | Raspberry Pi running Homebridge (Ethernet) | 192.168.0.52 | d8:3a:dd:3d:f2:f2 | Only plugin: Dyson (child bridge) |
| 3 | Mac mini | Apple Mac mini ("exrector's Mac mini") | 192.168.0.105 | 14:98:77:5e:2d:d1 | SMB + SSH enabled |

## Apple home hubs / Thread border routers

| # | Proposed name | Device | IP | MAC | Thread BR | Notes |
|---|---|---|---|---|---|---|
| 4 | Living Room Apple TV | Apple TV 4K 2nd gen (AppleTV11,1) | 192.168.0.215 | 1c:b3:c9:13:b3:2f | yes | Also a Matter node (Apple fabric) |
| 5 | Living Room HomePod | HomePod mini (AudioAccessory5,1) | 192.168.0.71 | 04:99:b9:9d:72:b2 | yes | |
| 6 | Master Bathroom HomePod | HomePod mini (AudioAccessory5,1) | 192.168.0.119 | 58:d3:49:0c:3e:f1 | yes | |
| 7 | Playroom HomePod | HomePod mini (AudioAccessory5,1) | 192.168.0.86 | 94:ea:32:90:0d:0d | yes | |
| 8 | Daniel's Office (2) | HomePod 1st gen (AudioAccessory1,1) | 192.168.0.14 | d4:90:9c:df:d5:7a | no | No Thread, no sensor |
| 9 | Guest Room Apple TV | Apple TV 4K 3rd gen, Wi-Fi-only model (AppleTV14,1) | 192.168.0.96 | c4:f7:c1:15:da:fd | no | No Thread, no Ethernet. User thought it was a HomePod, to confirm |

## Hubs / bridges (each has child devices not visible on the network)

| # | Proposed name | Device | IP | MAC | Notes |
|---|---|---|---|---|---|
| 10 | Aqara Hub M3 | Aqara M3 (HM-G01E) | 192.168.0.43 | 18:c2:3c:48:b1:48 | Zigbee hub + Thread BR + Matter bridge |
| 11 | Aqara Camera Hub G2H | Aqara G2H (CH-H01) | 192.168.0.44 | 54:ef:44:ca:ec:51 * | ignored ping/ARP during scan (user says it works) |
| 12 | Aqara Camera Hub G3 | Aqara G3 (CH-H03) | 192.168.0.216 | 54:ef:44:89:58:26 * | ignored ping/ARP during scan (user says it works) |
| 13 | Aqara Doorbell Repeater | Aqara G4 doorbell chime/repeater (SVD-C02) | 192.168.0.166 | 54:ef:44:5d:5b:ff | |
| 14 | eufy HomeBase 2 | eufy HomeBase 2 | 192.168.0.214 | 10:2c:b1:68:0b:97 * | ignored ping/ARP during scan (user says it works) |
| 15 | Lutron Caséta Bridge | Lutron Smart Bridge 2 | 192.168.0.186 | 88:0c:e0:0e:52:0c | |

## Meross Wi-Fi (2.4 GHz)

| # | Proposed name | Device | IP | MAC | Notes |
|---|---|---|---|---|---|
| 16 | Garage Door | Meross MSG100 garage opener | 192.168.0.250 | c4:e7:ae:05:b1:47 * | ignored ping/ARP during scan (user says it works) |
| 17 | Dimmer 7c2a | Meross MSS560 dimmer | 192.168.0.129 | c4:e7:ae:0c:7c:2a | |
| 18 | Dimmer 7d4c | Meross MSS560 dimmer | 192.168.0.242 | c4:e7:ae:0c:7d:4c * | ignored ping/ARP during scan (user unsure which dimmers these are) |
| 19 | Dimmer 8006 | Meross MSS560 dimmer | 192.168.0.157 | c4:e7:ae:0c:80:06 * | ignored ping/ARP during scan (user unsure which dimmers these are) |
| 20 | Dimmer 80f6 | Meross MSS560 dimmer | 192.168.0.145 | c4:e7:ae:0c:80:f6 * | ignored ping/ARP during scan (user unsure which dimmers these are) |
| 21 | Switch 64e7 | Meross MSS510 switch | 192.168.0.132 | 48:e1:e9:ef:64:e7 | |
| 22 | Switch 6643 | Meross MSS510 switch | 192.168.0.126 | 48:e1:e9:ef:66:43 | |
| 23 | Switch 6691 | Meross MSS510 switch | 192.168.0.204 | 48:e1:e9:ef:66:91 | |
| 24 | Switch 6881 | Meross MSS510 switch | 192.168.0.94 | 48:e1:e9:ef:68:81 | |
| 25 | Switch 695a | Meross MSS510 switch | 192.168.0.134 | 48:e1:e9:ef:69:5a | |
| 26 | Switch 699f | Meross MSS510 switch | 192.168.0.203 | 48:e1:e9:ef:69:9f | |
| 27 | Switch 6a6f | Meross MSS510 switch | 192.168.0.234 | 48:e1:e9:ef:6a:6f | |
| 28 | Switch 6bbe | Meross MSS510 switch | 192.168.0.140 | 48:e1:e9:ef:6b:be | |
| 29 | Switch 6bee | Meross MSS510 switch | 192.168.0.188 | 48:e1:e9:ef:6b:ee | |
| 30 | Switch 6c03 | Meross MSS510 switch | 192.168.0.32 | 48:e1:e9:ef:6c:03 | |
| 31 | Switch 6d21 | Meross MSS510 switch | 192.168.0.141 | 48:e1:e9:ef:6d:21 | |
| 32 | Switch 6d50 | Meross MSS510 switch | 192.168.0.189 | 48:e1:e9:ef:6d:50 | |
| 33 | Switch 6d71 | Meross MSS510 switch | 192.168.0.221 | 48:e1:e9:ef:6d:71 | |
| 34 | Switch 6d9f | Meross MSS510 switch | 192.168.0.15 | 48:e1:e9:ef:6d:9f | |
| 35 | Switch 6da3 | Meross MSS510 switch | 192.168.0.19 | 48:e1:e9:ef:6d:a3 | |
| 36 | Switch 6da5 | Meross MSS510 switch | 192.168.0.21 | 48:e1:e9:ef:6d:a5 | |
| 37 | Switch 6df5 | Meross MSS510 switch | 192.168.0.101 | 48:e1:e9:ef:6d:f5 | |
| 38 | Switch 6e1a | Meross MSS510 switch | 192.168.0.213 | 48:e1:e9:ef:6e:1a | |
| 39 | Switch 6e90 | Meross MSS510 switch | 192.168.0.79 | 48:e1:e9:ef:6e:90 | |
| 40 | Switch 6e9a | Meross MSS510 switch | 192.168.0.89 | 48:e1:e9:ef:6e:9a | |
| 41 | Switch 6f87 | Meross MSS510 switch | 192.168.0.149 | 48:e1:e9:ef:6f:87 | |
| 42 | Switch 705a | Meross MSS510 switch | 192.168.0.183 | 48:e1:e9:ef:70:5a | |

## Other Wi-Fi smart devices

| # | Proposed name | Device | IP | MAC | Notes |
|---|---|---|---|---|---|
| 43 | VOCOlinc Bulb | VOCOlinc L3 bulb | 192.168.0.90 | e4:23:54:17:ff:08 | |
| 44 | Nanoleaf Shapes 66F8 | Nanoleaf Shapes (NL42) | 192.168.0.190 | 80:8a:f7:10:66:f8 | Wi-Fi + Thread BR |
| 45 | Nanoleaf Shapes 6CA6 | Nanoleaf Shapes (NL42) | 192.168.0.75 | 80:8a:f7:10:6c:a6 | Wi-Fi + Thread BR |
| 46 | Nanoleaf ? (Matter) | Nanoleaf Wi-Fi Matter device ? | 192.168.0.139 | 80:8a:f7:23:c8:cf | Matter only, in Apple fabric + 2nd fabric |
| 47 | Unknown Matter device | ? | 192.168.0.193 | 3c:31:74:db:55:28 | Matter, **not in Apple's fabric** |

## Thread devices (no IPv4/MAC on Wi-Fi; reached through border routers)

| # | Proposed name | Device | Thread/HAP ID | Notes |
|---|---|---|---|---|
| 48 | Front Door Lock ? | Schlage Encode Plus (BE499WB) | Encode-Plus.local | HomeKit over Thread |
| 49 | Nanoleaf A19 1WWJ | Nanoleaf Essentials A19 (NL45) | 87:82:67:CD:57:A2 | HomeKit over Thread |
| 50 | Nanoleaf A19 3R4X | Nanoleaf Essentials A19 (NL45) | 35:A5:82:C2:96:65 | HomeKit over Thread |
| 51 | Nanoleaf A19 4565 | Nanoleaf Essentials A19 (NL45) | AE:03:68:3F:7E:B9 | HomeKit over Thread |
| 52 | Nanoleaf A19 96M2 | Nanoleaf Essentials A19 (NL45) | 69:70:CD:68:74:27 | HomeKit over Thread |
| 53 | Matter-Thread device A ? | ? | 3E8F27DE3E6647FC | Matter, in Apple fabric + 2nd fabric |
| 54 | Matter-Thread device B ? | ? | 7A42F12275292777 | Matter, in Apple fabric + 2nd fabric |

## Non-smart clients seen

| IP | MAC | Guess |
|---|---|---|
| 192.168.0.211 | bc:33:29:b4:93:e2 | PlayStation 5 |
| 192.168.0.98 | 82:84:cb:f5:f0:34 | Private MAC: iPhone/iPad/Watch |
| 192.168.0.133 | 26:7a:fd:7c:d1:19 | Private MAC: iPhone/iPad/Watch |
| 192.168.0.187 | 3a:60:04:c4:84:ca | Private MAC: iPhone/iPad/Watch |

## Matter fabrics seen

| Fabric ID | Likely owner | Members |
|---|---|---|
| 724CFE1FC19C2CA8 | Apple Home | Apple TV, #46, #53, #54 |
| 8E7AB5CF23900107 | ? 2nd ecosystem | #46, #53, #54 |
| 054897967B5FBD1E | ? 3rd ecosystem | #47 |
| 19D71CB34A7D29AE | ? (Aqara M3 Matter bridge) | #10 |

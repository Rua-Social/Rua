# Studio storage stack

Decided 20 August 2026. Live edit on the Mac. Archive on the old tower.
Do not cut from the tower. Do not fill the Studio SSD. T7s are capture only.
A working location the instance record names for a current client deliverable
stays that location. This note does not move it.

## Flow

Lumix → T7 (field) → Thunderbolt 5 4 TB NVMe on the M4 Max Studio (FCP library,
current job) → when posted, old PC over 10 GbE (originals + masters). Recut:
copy back to the NVMe first.

The Studio already has Thunderbolt 5 and 10 GbE. Direct Cat6/Cat6a, no switch.

## Keep

- Corsair 850i
- Existing boot SSD (SATA is fine on the tower)
- T7s for Lumix capture only
- Tower case (already holds two 3.5" disks)
- FM2 board and HyperX DDR3: scrap

## Buy

Live edit:

- Thunderbolt 5 NVMe enclosure (Acasis-class), not TB4
- 4 TB NVMe (990 Pro / SN850X class), APFS, FCP library on it, straight into a Studio TB5 port

Archive PC:

- ASUS TUF Gaming B550-PLUS WIFI II, Elara, €141.79
  (`90MB19U0-M0EAY0`). 6 SATA, 2.5G onboard, HDMI, BIOS Flashback, 10G NIC slot
- Ryzen 5 5600G, CeX `SCPUAMD5600G` €120. Fallback: Pro 3700 `SCPUAMDP3700` €70
- 2× 16 GB DDR4-3200 288-pin desktop, CeX `SMEM16G32002` €60 each.
  Fallback: 2× 16 GB DDR4-2666 `SMEM16G2666`
- 10GBase-T NIC, RJ45, used Intel X540 / X550 class
- Two Toshiba MG07ACA14TE 14 TB SATA
  https://www.bargainhardware.co.uk/toshiba-mg07aca14te-14tb-enterprise-lff-3-5in-sata-iii-6gbps-7-2k-256mb-hdd
- Short Cat6/Cat6a if none on the desk

TrueNAS on the existing boot SSD. Two Toshibas as a mirror. 14 TB usable.

## Do not buy

GPU, SAS disks, HBA, extra boot NVMe for the tower, 2.5G NIC, CeX 1 TB disks.
Whisper / Plex / tape indexer are later, after files live on this stack.
The tower M.2 slots exist; they are not this purchase.

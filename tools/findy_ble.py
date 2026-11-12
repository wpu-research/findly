#!/usr/bin/env python3
"""Findy BLE komut satırı aracı (Nordic UART Service üzerinden satır tabanlı komutlar).

Örnekler:
    python3 tools/findy_ble.py scan
    python3 tools/findy_ble.py status
    python3 tools/findy_ble.py name DENIZ
    python3 tools/findy_ble.py friend 2 ALI
    python3 tools/findy_ble.py cfg sf 9
    python3 tools/findy_ble.py avatar avatar.rgb          # avatar_convert.py çıktısı (18432 bayt)
    python3 tools/findy_ble.py log kayit.csv --seconds 600

Cihaz seçimi: --address <MAC>, verilmezse adı "Findy" ile başlayan ilk cihaz taranır.
Protokol firmware/src/ble_link.cpp başlığında tanımlıdır. DONANIMLA DENENMEDİ.
"""
import argparse
import asyncio
import sys
import zlib

try:
    from bleak import BleakClient, BleakScanner
except ImportError:
    sys.exit("Hata: 'bleak' kurulu değil. Kurulum: pip install bleak")

NUS_RX = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"  # telefon -> cihaz (yazma)
NUS_TX = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"  # cihaz -> telefon (bildirim)
AVATAR_BYTES = 96 * 96 * 2


class Link:
    def __init__(self, client):
        self.client = client
        self.q = asyncio.Queue()
        self.buf = b""
        self.chunk = 20

    def _on_notify(self, _h, data):
        self.buf += bytes(data)
        while b"\n" in self.buf:
            line, self.buf = self.buf.split(b"\n", 1)
            self.q.put_nowait(line.decode("utf-8", "replace").rstrip("\r"))

    async def start(self):
        await self.client.start_notify(NUS_TX, self._on_notify)
        mtu = getattr(self.client, "mtu_size", 23)
        self.chunk = max(20, min(244, mtu - 3))

    async def send(self, data: bytes):
        for i in range(0, len(data), self.chunk):
            await self.client.write_gatt_char(NUS_RX, data[i:i + self.chunk], response=False)
            await asyncio.sleep(0.005)  # cihaz tamponunu taşırmamak için kısa bekleme

    async def line(self, text, timeout=5.0):
        await self.send((text + "\n").encode())
        return await asyncio.wait_for(self.q.get(), timeout)


async def find_device(address):
    if address:
        return address
    print("Findy cihazı taranıyor...", file=sys.stderr)
    devs = await BleakScanner.discover(timeout=8.0)
    for d in devs:
        if d.name and d.name.startswith("Findy"):
            print(f"Bulundu: {d.name} {d.address}", file=sys.stderr)
            return d.address
    sys.exit("Hata: 'Findy' adlı cihaz bulunamadı (cihaz uyanık ve reklam yapıyor mu?)")


async def cmd_scan(_a):
    for d in await BleakScanner.discover(timeout=8.0):
        print(f"{d.address}  {d.name}")


async def run(a):
    addr = await find_device(a.address)
    async with BleakClient(addr) as client:
        link = Link(client)
        await link.start()
        c = a.cmd
        if c == "status":
            print(await link.line("STATUS"))
        elif c == "name":
            print(await link.line("NAME " + a.value.upper()))
        elif c == "friend":
            print(await link.line(f"FRIEND {a.id} {a.value.upper()}"))
        elif c == "cfg":
            print(await link.line(f"CFG {a.key} {a.value}"))
        elif c == "avatar":
            data = open(a.file, "rb").read()
            if len(data) != AVATAR_BYTES:
                sys.exit(f"Hata: avatar {AVATAR_BYTES} bayt olmalı (şu an {len(data)}); avatar_convert.py kullanın")
            r = await link.line(f"AVATAR BEGIN {len(data)}")
            if r != "OK":
                sys.exit(f"Cihaz reddetti: {r}")
            await link.send(data)
            crc = zlib.crc32(data) & 0xFFFFFFFF
            r = await link.line(f"AVATAR END {crc:08x}", timeout=15.0)
            print(r)
            if r != "OK":
                sys.exit(1)
        elif c == "log":
            r = await link.line("LOG ON")
            if r != "OK":
                sys.exit(f"Cihaz reddetti: {r}")
            print(f"Kayıt {a.file} dosyasına yazılıyor ({a.seconds} sn)...", file=sys.stderr)
            end = asyncio.get_event_loop().time() + a.seconds
            with open(a.file, "w", encoding="utf-8") as f:
                while True:
                    left = end - asyncio.get_event_loop().time()
                    if left <= 0:
                        break
                    try:
                        s = await asyncio.wait_for(link.q.get(), min(left, 1.0))
                    except asyncio.TimeoutError:
                        continue
                    if s.startswith("LOG,") or s.startswith("LOGCOLS,"):
                        f.write(s.split(",", 1)[1] + "\n")
                        f.flush()
            await link.line("LOG OFF")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--address", help="cihaz BLE adresi (verilmezse taranır)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("scan")
    sub.add_parser("status")
    p = sub.add_parser("name"); p.add_argument("value", help="en çok 8 karakter, A-Z 0-9")
    p = sub.add_parser("friend"); p.add_argument("id", type=int, choices=range(1, 6)); p.add_argument("value")
    p = sub.add_parser("cfg"); p.add_argument("key", help="sf | pwr | standby | search | decl | calib"); p.add_argument("value")
    p = sub.add_parser("avatar"); p.add_argument("file")
    p = sub.add_parser("log"); p.add_argument("file"); p.add_argument("--seconds", type=int, default=300)
    a = ap.parse_args()
    asyncio.run(cmd_scan(a) if a.cmd == "scan" else run(a))


if __name__ == "__main__":
    main()

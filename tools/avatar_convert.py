#!/usr/bin/env python3
"""Resim -> Findy avatarı: 96x96, dairesel kırpma, RGB565 little-endian ham dosya (18432 bayt).

Kullanım:
    python3 tools/avatar_convert.py foto.jpg avatar.rgb [--preview onizleme.png]

Çıktı biçimi (firmware ile aynı): her piksel 2 bayt, little-endian uint16 RGB565,
satır satır, sol üstten başlar. Daire dışındaki pikseller siyah (0x0000) yazılır.
Önce merkezden kare kırpılır, sonra 96x96'ya küçültülür.
"""
import argparse
import struct
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("Hata: Pillow kurulu değil. Kurulum: pip install Pillow")

SIZE = 96
EXPECTED_BYTES = SIZE * SIZE * 2  # 18432


def convert(path, preview=None):
    img = Image.open(path).convert("RGB")
    w, h = img.size
    side = min(w, h)
    left, top = (w - side) // 2, (h - side) // 2
    img = img.crop((left, top, left + side, top + side)).resize((SIZE, SIZE), Image.LANCZOS)

    # Dairesel maske (yarıçap 48). Firmware da aynı daireyle çizer; dışı siyah.
    mask = Image.new("L", (SIZE * 4, SIZE * 4), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, SIZE * 4 - 1, SIZE * 4 - 1), fill=255)
    mask = mask.resize((SIZE, SIZE), Image.LANCZOS)
    black = Image.new("RGB", (SIZE, SIZE), (0, 0, 0))
    img = Image.composite(img, black, mask)

    out = bytearray()
    px = img.load()
    for y in range(SIZE):
        for x in range(SIZE):
            r, g, b = px[x, y]
            v = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            out += struct.pack("<H", v)
    assert len(out) == EXPECTED_BYTES
    if preview:
        img.save(preview)
    return bytes(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="kaynak resim (jpg/png/...)")
    ap.add_argument("output", help="çıktı ham dosya (18432 bayt)")
    ap.add_argument("--preview", help="isteğe bağlı: 96x96 önizleme PNG'si")
    a = ap.parse_args()
    try:
        data = convert(a.input, a.preview)
    except FileNotFoundError:
        sys.exit(f"Hata: dosya bulunamadı: {a.input}")
    except OSError as e:
        sys.exit(f"Hata: resim okunamadı: {e}")
    with open(a.output, "wb") as f:
        f.write(data)
    print(f"{a.output}: {len(data)} bayt yazıldı")


if __name__ == "__main__":
    main()

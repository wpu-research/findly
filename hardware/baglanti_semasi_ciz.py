#!/usr/bin/env python3
"""Findy P0 baglanti semasi uretici.

Cikti: baglanti-semasi.svg (el yapimi SVG yazici) ve baglanti-semasi.png
(matplotlib onizleme). Ayni cizim ilkelleri (primitives) iki arka uca verilir.

Kullanim:  python3 baglanti_semasi_ciz.py
"""
import os
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

W, H = 1700, 1150
HERE = os.path.dirname(os.path.abspath(__file__))

BG = "#FAFAF7"
RED, BLK, BLUE, GRN, ORG = "#D32F2F", "#111111", "#1565C0", "#2E7D32", "#EF6C00"
GRAY, LGRAY = "#555555", "#9AA0A6"
FONT = "DejaVu Sans, Arial, sans-serif"

P = []  # ilkel listesi


def rect(x, y, w, h, fill="none", stroke=BLK, sw=1.5, rx=0, dash=None):
    P.append(("rect", x, y, w, h, fill, stroke, sw, rx, dash))


def line(pts, color=BLK, sw=2.2, dash=None):
    P.append(("line", pts, color, sw, dash))


def circ(cx, cy, r, fill="none", stroke=BLK, sw=1.5):
    P.append(("circ", cx, cy, r, fill, stroke, sw))


def poly(pts, fill="none", stroke=BLK, sw=1.5):
    P.append(("poly", pts, fill, stroke, sw))


def text(x, y, s, size=12, anchor="start", weight="normal", color=BLK, italic=False):
    P.append(("text", x, y, s, size, anchor, weight, color, italic))


# ------------------------------------------------------------------ yerlesim
HX = 715            # RAK13002 baslik noktalarinin x'i
MX = 1010           # modul pin x'i
Y0, DY = 405, 28    # ilk pin y, aralik
ys = {}
cur = Y0
for grp in ([1, 2, 3, 4, 5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]):
    for k in grp:
        ys[k] = cur
        cur += DY
    cur += 55

# (no, silkscreen, tel etiketi, renk, modul pin adi)
WIRES = [
    (1, "VCC", "3V3 (surekli)", RED, "VCC"),
    (2, "GND", "GND", BLK, "GND"),
    (3, "SCK", "PIN_SPI_SCK  P0.03", BLUE, "CLK"),
    (4, "SDI*", "PIN_SPI_MOSI  P0.30 (*)", BLUE, "DIN"),
    (5, "CS", "WB_SPI_CS  P0.26", BLUE, "CS"),
    (6, "IO3", "WB_IO3  P0.21", ORG, "DC"),
    (7, "IO4", "WB_IO4  P0.04", ORG, "RST"),
    (8, "IO5", "WB_IO5  P0.09 (NFC pini)", ORG, "BL"),
    (9, "VCC", "3V3 (surekli)", RED, "VIN"),
    (10, "GND", "GND", BLK, "GND"),
    (11, "SDA1", "WB_I2C1_SDA  P0.13", GRN, "SDA"),
    (12, "SCL1", "WB_I2C1_SCL  P0.14", GRN, "SCL"),
]
TR = lambda s: (s.replace("surekli", "sürekli"))  # noqa: E731

# ------------------------------------------------------------------ baslik
text(30, 36, "Findy P0 tezgâh prototipi — bağlantı şeması", 22, weight="bold")
text(30, 60, "Kablolar RAK13002 başlığından (2,54 mm) harici modüllere gider; "
     "RAK4631 / RAK12500 / pil / USB kartın üzerindedir.", 13, color=GRAY)

# ------------------------------------------------------------------ pil / USB
rect(30, 140, 110, 76, "#FFFFFF", sw=1.5, rx=6)
text(85, 163, "LiPo 3,7 V", 13, "middle", "bold")
text(85, 181, "JST-PH 2 mm", 11, "middle")
text(85, 197, "kutup ölç!", 11, "middle", color=RED)
line([(140, 158), (170, 158)], RED, 2.4)
line([(140, 180), (170, 180)], BLK, 2.4)
text(155, 153, "VBAT", 8, "middle", color=RED)
text(155, 194, "GND", 8, "middle")

rect(30, 245, 110, 56, "#FFFFFF", sw=1.5, rx=6)
text(85, 266, "USB-C", 13, "middle", "bold")
text(85, 283, "şarj 350 mA, veri", 10, "middle")
line([(140, 273), (190, 273)], RED, 2.4)
text(165, 267, "5 V", 9, "middle", color=RED)

# ------------------------------------------------------------------ RAK19007
rect(190, 130, 545, 900, "#F3F3EF", "#444444", 2.2, rx=10)
text(345, 156, "RAK19007 taban kartı (2. nesil)", 12, weight="bold")
rect(170, 145, 52, 46, "#FFFFFF", sw=1.2, rx=4)
text(196, 163, "P2", 11, "middle", "bold")
text(196, 180, "PHR-2", 8, "middle")

# RAK4631
rect(215, 195, 230, 140, "#E8F0FE", BLUE, 1.8, rx=6)
text(330, 220, "CPU yuvası: RAK4631", 13, "middle", "bold")
text(330, 240, "nRF52840 (BLE) + SX1262", 11, "middle")
text(330, 258, "LoRa 868 MHz (EU868 sürümü)", 11, "middle")
text(330, 276, "SX1262 pinleri modül içi", 11, "middle", color=GRAY)
text(330, 294, "(NSS/DIO1/BUSY/RESET/ANT_SW", 10, "middle", color=GRAY)
text(330, 308, "P1.10/15/14/06/05; DIO3=TCXO)", 10, "middle", color=GRAY)
text(330, 326, "SW1=P1.01  IO1=P0.17  IO2=P1.02", 10, "middle", color=GRAY)
# RAK12500
rect(470, 195, 240, 140, "#E6F4EA", GRN, 1.8, rx=6)
text(590, 220, "Yuva A: RAK12500 GNSS", 13, "middle", "bold")
text(590, 240, "u-blox ZOE-M8Q", 11, "middle")
text(590, 258, "I2C1, adres 0x42 (*)", 11, "middle")
text(590, 276, "IO1 = 1PPS (kullanma)", 11, "middle", color=ORG)
text(590, 294, "IO2 = GNSS RST + 3V3_S EN", 11, "middle", color=ORG)
text(590, 312, "V_BCKP yok → sıcak başlangıç yok (*)", 10, "middle", color=RED)
text(590, 326, "Yuva C'ye TAKMA (IO3/IO4 çakışır)", 10, "middle", color=RED)
# kart ici I2C1 / 40 pin
line([(445, 262), (470, 262)], GRN, 2.4)
text(457, 254, "I2C1", 9, "middle", color=GRN)
# antenler
for ax_, label, sub in ((330, "868 MHz anten", "u.FL/IPEX (LoRa)"),
                        (590, "GNSS anteni", "IPEX (aktif/pasif ?)")):
    line([(ax_, 195), (ax_, 108)], BLK, 1.6)
    line([(ax_, 108), (ax_ - 12, 90)], BLK, 1.6)
    line([(ax_, 108), (ax_ + 12, 90)], BLK, 1.6)
    text(ax_ + 22, 98, label, 12, "start", "bold")
    text(ax_ + 22, 112, sub, 10, "start", color=GRAY)

# RAK13002
rect(215, 355, 500, 655, "#FFF8E1", ORG, 1.8, rx=6)
text(230, 378, "IO yuvası: RAK13002 IO adaptörü", 13, weight="bold")
text(230, 396, "40 pin WisConnector → 2,54 mm başlık (silkscreen adları)", 11, color=GRAY)
line([(330, 335), (330, 355)], GRAY, 3, dash="5,3")
text(338, 349, "40 pin WisConnector", 10, color=GRAY)
for no, sil, lab, col, mod in WIRES:
    y = ys[no]
    text(HX - 12, y + 4, sil, 12, "end", "bold")
# kalan baslik pinleri (motor / tus)
extra = {13: ("VCC", RED), 14: ("SW1", ORG), 15: ("GND", BLK), 16: ("IO6", ORG)}
for no, (sil, col) in extra.items():
    text(HX - 12, ys[no] + 4, sil, 12, "end", "bold")
text(235, 430, "Başlık düzeni (4 sütun × 8 sıra, üretici tablosu):", 11, weight="bold")
for i, t in enumerate(("Sütun 1: VCC GND IO1 IO3 IO4 IO5 IO6 IO7",
                       "Sütun 2: VCC GND SCL1 SDA1 SCL2 SDA2 LED1 LED2",
                       "Sütun 3: VCC GND TXD0 RXD0 TXD1 RXD1 AIN0 AIN1",
                       "Sütun 4: VCC GND CS SDI SDO SCK RST SW1")):
    text(235, 450 + i * 17, t, 10.5, color=GRAY)
text(235, 526, "Şemada kullanılan pinler tek sütunda gösterildi;", 10.5, color=GRAY)
text(235, 542, "gerçekte farklı sütunlardandır. IO2 başlıkta YOK,", 10.5, color=GRAY)
text(235, 558, "3V3_S ayrı bir başlık pini olarak listelenmemiş (*).", 10.5, color=GRAY)
# baslik gorsel cizgisi
rect(HX - 4, ys[1] - 14, 8, ys[16] - ys[1] + 28, "#222222", "#222222", 1, rx=2)
for k, y in ys.items():
    circ(HX, y, 3.5, "#E0B000", "#222222", 1)
text(HX - 12, ys[1] - 22, "başlık", 10, "end", color=GRAY)

# ------------------------------------------------------------------ modul: GC9A01
top = ys[1] - 28
bot = ys[8] + 22
rect(MX, top, 290, bot - top, "#FDECEA", "#B71C1C", 1.8, rx=6)
text(MX + 145, top - 8, "1,28\" yuvarlak TFT, GC9A01 (ör. Waveshare 19192)", 12, "middle", "bold")
circ(MX + 225, (top + bot) / 2, 46, "#222222", "#222222", 1)
circ(MX + 225, (top + bot) / 2, 38, "#4A6FA5", "#222222", 1)
text(MX + 225, (top + bot) / 2 + 4, "240×240", 10, "middle", color="#FFFFFF")
text(MX + 225, bot - 8, "SPI, 3,3 V", 10, "middle", color=GRAY)
for no, sil, lab, col, mod in WIRES[:8]:
    y = ys[no]
    text(MX + 10, y + 4, mod, 12, weight="bold")
# ------------------------------------------------------------------ modul: LSM303AGR
top2 = ys[9] - 24
bot2 = ys[12] + 17
rect(MX, top2, 290, bot2 - top2, "#EDE7F6", "#4527A0", 1.8, rx=6)
text(MX + 145, top2 - 8, "LSM303AGR (ör. Adafruit 4413)", 12, "middle", "bold")
text(MX + 225, top2 + 40, "ivme 0x19", 11, "middle")
text(MX + 225, top2 + 58, "manyeto 0x1E", 11, "middle")
text(MX + 225, top2 + 76, "I2C 3,3 V", 10, "middle", color=GRAY)
for no, sil, lab, col, mod in WIRES[8:12]:
    text(MX + 10, ys[no] + 4, mod, 12, weight="bold")

# ------------------------------------------------------------------ teller
for no, sil, lab, col, mod in WIRES:
    y = ys[no]
    line([(HX, y), (MX, y)], col, 2.4)
    text((HX + MX) / 2, y - 5, TR(lab), 10, "middle", color=col)

# ------------------------------------------------------------------ tus
yb, yg = ys[14], ys[15]
line([(HX, yb), (810, yb)], ORG, 2.4)
text(760, yb - 5, "WB_SW1  P1.01", 10, "middle", color=ORG)
circ(815, yb, 3, BLK)
line([(815, yb), (840, yb - 12)], BLK, 2)
circ(845, yb, 3, BLK)
line([(845, yb), (900, yb)], ORG, 2.4)
line([(900, yb), (900, yg)], BLK, 2.4)
line([(900, yg), (HX, yg)], BLK, 2.4)
text(830, yb + 22, "S1 tuş", 11, "middle", "bold")
text(758, yg - 5, "GND", 10, "middle")

# ------------------------------------------------------------------ VCC -> motor
yv = ys[13]
line([(HX, yv), (1250, yv)], RED, 2.4)
text(860, yv - 5, "3V3 (sürekli)", 10, "middle", color=RED)

# ------------------------------------------------------------------ motor surucu
yi = ys[16]
line([(HX, yi), (800, yi)], ORG, 2.4)
text(758, yi - 5, "WB_IO6  P0.10", 10, "middle", color=ORG)
rect(800, yi - 8, 40, 16, "#FFFFFF", BLK, 1.4)
text(820, yi + 22, "R1 100 Ω", 10, "middle")
line([(840, yi), (930, yi)], ORG, 2.4)
circ(880, yi, 3, ORG, ORG)
line([(880, yi), (880, yi + 14)], BLK, 2)
rect(872, yi + 14, 16, 26, "#FFFFFF", BLK, 1.4)
text(866, yi + 36, "R2 100 kΩ", 10, "end")
line([(880, yi + 40), (880, yi + 50)], BLK, 2)
line([(870, yi + 50), (890, yi + 50)], BLK, 2)
line([(874, yi + 55), (886, yi + 55)], BLK, 2)
line([(877, yi + 60), (883, yi + 60)], BLK, 2)
# Q1
rect(930, yi - 25, 74, 70, "#FFFFFF", BLK, 1.8, rx=3)
text(967, yi + 2, "Q1", 12, "middle", "bold")
text(967, yi + 16, "N-MOSFET", 9, "middle")
text(967, yi + 28, "(mantık seviyesi)", 8, "middle", color=GRAY)
text(936, yi - 8, "G", 9, color=GRAY)
text(998, yi - 12, "D", 9, "end", color=GRAY)
text(998, yi + 40, "S", 9, "end", color=GRAY)
line([(1004, yi), (1250, yi)], BLK, 2.4)
line([(967, yi + 45), (967, yi + 50)], BLK, 2.4)
line([(957, yi + 50), (977, yi + 50)], BLK, 2)
line([(961, yi + 55), (973, yi + 55)], BLK, 2)
line([(964, yi + 60), (970, yi + 60)], BLK, 2)
text(985, yi + 64, "GND (başlık GND pini)", 9, color=GRAY)
# motor
line([(1100, yv), (1100, yi - 52)], RED, 2.4)
circ(1100, yi - 26, 26, "#FFFFFF", BLK, 1.8)
text(1100, yi - 22, "M", 16, "middle", "bold")
text(1134, yi - 38, "M1 titreşim", 11)
text(1134, yi - 24, "motoru (ERM)", 11)
text(1134, yi - 10, "3 V; akım ölç", 11)
# ters diyot: katot ustte (VCC), anot altta (drain)
dy0 = yi - 40
line([(1250, yv), (1250, dy0)], RED, 2.4)
poly([(1238, dy0), (1262, dy0), (1250, dy0 + 22)], "#FFFFFF", BLK, 1.6)
line([(1238, dy0 + 22), (1262, dy0 + 22)], BLK, 2.4)
line([(1250, dy0 + 22), (1250, yi)], BLK, 2.4)
text(1270, dy0 + 8, "D1", 11, weight="bold")
text(1270, dy0 + 21, "Schottky", 10)
text(1270, dy0 + 34, "(flyback)", 10, color=GRAY)
circ(1100, yi, 3, BLK, BLK)
circ(1250, yi, 3, BLK, BLK)

# ------------------------------------------------------------------ lejant ve notlar
LX, LY = 1340, 130
rect(LX, LY, 330, 168, "#FFFFFF", "#444444", 1.4, rx=6)
text(LX + 12, LY + 22, "Lejant", 13, weight="bold")
for i, (c, t) in enumerate(((RED, "Besleme (3V3 / VBAT / 5 V)"), (BLK, "GND"),
                            (BLUE, "SPI"), (GRN, "I2C"), (ORG, "GPIO"))):
    yy = LY + 44 + i * 24
    line([(LX + 14, yy), (LX + 64, yy)], c, 3)
    text(LX + 76, yy + 4, t, 12)
text(LX + 12, LY + 164, "* = üretici belgesinde DOĞRULANAMADI", 10, color=RED)

NX, NY = 1340, 320
rect(NX, NY, 330, 385, "#FFFFFF", "#444444", 1.4, rx=6)
text(NX + 12, NY + 22, "Dikkat / doğrulama notları", 13, weight="bold")
notes = [
    ("(*) SDI/SDO: SDI=MOSI mu MISO mu", RED),
    ("    belgede yok; ilk güçte ölç.", RED),
    ("IO1: Yuva A'daki RAK12500 1PPS'i", BLK),
    ("    taşır → kullanma.", BLK),
    ("IO2: 3V3_S anahtarı + GNSS RST →", BLK),
    ("    GPIO olarak kullanma.", BLK),
    ("IO5/IO6 = nRF52 NFC pinleri", BLK),
    ("    (P0.09/P0.10): NFC kapalı GPIO", BLK),
    ("    ayarı yazılımda doğrulanacak.", BLK),
    ("Display BL: modülde sürücü", BLK),
    ("    transistör var mı ölç; yoksa", BLK),
    ("    N-MOSFET ile sür (bağlantı", BLK),
    ("    tablosu bölüm 5).", BLK),
    ("Q1: Vgs(th) < 1,5 V, Id ≥ 0,5 A", BLK),
    ("    (veri sayfası kontrol edilecek).", BLK),
    ("Pil: JST-PH ↔ PHR-2 kutup ters", RED),
    ("    olabilir; takmadan önce ölç.", RED),
    ("WB_A0 = pil gerilimi (kart içi);", GRAY),
    ("    başlıktaki AIN0'a bir şey bağlama.", GRAY),
]
for i, (t, c) in enumerate(notes):
    text(NX + 12, NY + 46 + i * 17.3, t, 11, color=c)

# ------------------------------------------------------------------ baslik blogu
rect(30, 1065, 1640, 75, "#FFFFFF", "#222222", 2)
line([(500, 1065), (500, 1140)], "#222222", 1.2)
line([(1000, 1065), (1000, 1140)], "#222222", 1.2)
line([(1380, 1065), (1380, 1140)], "#222222", 1.2)
text(45, 1092, "Findy P0 bağlantı şeması v0.1", 18, weight="bold")
text(45, 1118, "Tezgâh prototipi (RAK WisBlock) — 1 cihaz", 12, color=GRAY)
text(515, 1092, "Tarih: 2026-11-11", 14, weight="bold")
text(515, 1118, "Durum: KONSEPT", 14, weight="bold", color=RED)
text(1015, 1088, "Kaynak: RAK docs + RAK-nRF52-Arduino variant.h; ayrıntı:", 11)
text(1015, 1104, "baglanti-tablosu.md, dogrulama-notlari.md", 11)
text(1015, 1124, "Sipariş / lehim öncesi * işaretliler ölçülecek.", 11, color=RED)
text(1395, 1092, "Çizim: baglanti_semasi_ciz.py", 11)
text(1395, 1110, "Ölçek yok (şematik).", 11, color=GRAY)
text(1395, 1126, "Hardware/ klasörü", 11, color=GRAY)

# ================================================================== SVG yazici
def svg_out(path):
    o = []
    a = o.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
      f'viewBox="0 0 {W} {H}" font-family="{FONT}">')
    a('<title>Findy P0 bağlantı şeması v0.1 (KONSEPT, 2026-11-11)</title>')
    a(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{BG}"/>')
    for p in P:
        k = p[0]
        if k == "rect":
            _, x, y, w, h, fill, stroke, sw, rx, dash = p
            d = f' stroke-dasharray="{dash}"' if dash else ""
            a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
              f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
        elif k == "line":
            _, pts, c, sw, dash = p
            d = f' stroke-dasharray="{dash}"' if dash else ""
            s = " ".join(f"{x},{y}" for x, y in pts)
            a(f'<polyline points="{s}" fill="none" stroke="{c}" stroke-width="{sw}" '
              f'stroke-linecap="round" stroke-linejoin="round"{d}/>')
        elif k == "circ":
            _, cx, cy, r, fill, stroke, sw = p
            a(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
        elif k == "poly":
            _, pts, fill, stroke, sw = p
            s = " ".join(f"{x},{y}" for x, y in pts)
            a(f'<polygon points="{s}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
        elif k == "text":
            _, x, y, s, size, anchor, weight, color, italic = p
            an = {"start": "start", "middle": "middle", "end": "end"}[anchor]
            it = ' font-style="italic"' if italic else ""
            a(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{an}" '
              f'font-weight="{weight}" fill="{color}"{it} xml:space="preserve">{escape(s)}</text>')
    a("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(o))
    ET.parse(path)  # gecerli XML mi?


# ================================================================== matplotlib
def png_out(path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, FancyBboxPatch, Circle, Polygon

    fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")
    fig.patch.set_facecolor(BG)
    pxpt = 0.72
    for p in P:
        k = p[0]
        if k == "rect":
            _, x, y, w, h, fill, stroke, sw, rx, dash = p
            if rx:
                patch = FancyBboxPatch((x + rx, y + rx), w - 2 * rx, h - 2 * rx,
                                       boxstyle=f"round,pad={rx},rounding_size={rx}",
                                       fc=fill, ec=stroke, lw=sw * pxpt)
            else:
                patch = Rectangle((x, y), w, h, fc=fill, ec=stroke, lw=sw * pxpt)
            ax.add_patch(patch)
        elif k == "line":
            _, pts, c, sw, dash = p
            xs, ys_ = zip(*pts)
            ls = (0, tuple(float(t) for t in dash.split(","))) if dash else "-"
            ax.plot(xs, ys_, color=c, lw=sw * pxpt, linestyle=ls,
                    solid_capstyle="round", solid_joinstyle="round")
        elif k == "circ":
            _, cx, cy, r, fill, stroke, sw = p
            ax.add_patch(Circle((cx, cy), r, fc=fill, ec=stroke, lw=sw * pxpt))
        elif k == "poly":
            _, pts, fill, stroke, sw = p
            ax.add_patch(Polygon(pts, closed=True, fc=fill, ec=stroke, lw=sw * pxpt))
        elif k == "text":
            _, x, y, s, size, anchor, weight, color, italic = p
            ax.text(x, y, s, fontsize=size * pxpt, ha={"start": "left", "middle": "center", "end": "right"}[anchor],
                    va="baseline", fontweight=weight, color=color,
                    fontstyle="italic" if italic else "normal", family="DejaVu Sans")
    fig.savefig(path, dpi=100, facecolor=BG)
    plt.close(fig)


if __name__ == "__main__":
    svg_out(os.path.join(HERE, "baglanti-semasi.svg"))
    png_out(os.path.join(HERE, "baglanti-semasi.png"))
    print("tamam: baglanti-semasi.svg (gecerli XML) + baglanti-semasi.png")

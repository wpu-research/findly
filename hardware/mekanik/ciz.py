#!/usr/bin/env python3
"""Findy P1 — teknik resimler (SVG + önizleme PNG). Ölçüler yalnızca params.py'dan.

Kullanım:  python3 ciz.py          (cizimler/*.svg ve onizleme/*.png üretir)
"""
import math, os
import params as P
from cizim_lib import Sheet, View, tablo, fmt, text_olcu, KAGIT

HERE = os.path.dirname(os.path.abspath(__file__))
SVG_DIR = os.path.join(HERE, "cizimler")
PNG_DIR = os.path.join(HERE, "onizleme")
TS = 2.5     # varsayılan metin boyu (mm)


def pol(r, a_deg, cx=0.0, cy=0.0):
    a = math.radians(a_deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def halka_sektor(r0, r1, a0, a1, n=None):
    n = n or max(4, int(abs(a1 - a0) / 3))
    dis = [pol(r1, a0 + (a1 - a0) * i / n) for i in range(n + 1)]
    ic = [pol(r0, a1 - (a1 - a0) * i / n) for i in range(n + 1)]
    return dis + ic


def ust_profil():
    """Üst çerçeve kesit profili (r,z) — govde.profil_ust ile AYNI değerler."""
    R, z0, h = P.R_DIS, P.AYRIM_Z, P.TOPLAM
    zk = P.Z["cam"][0] - P.KORNIS_KAL
    return [(P.R_IC, z0), (R, z0), (R, h), (P.ISIK_R1, h), (P.ISIK_R1, h - P.ISIK_DERINLIK),
            (P.ISIK_R0, h - P.ISIK_DERINLIK), (P.ISIK_R0, h), (P.CAM_YUVA_D / 2, h),
            (P.CAM_YUVA_D / 2, P.Z["cam"][0]), (P.KORNIS_D / 2, P.Z["cam"][0]),
            (P.KORNIS_D / 2, zk), (P.R_IC, zk)]


# =====================================================================================
def cizim_01():
    sh = Sheet(ad="01-genel-gorunum")
    s = 2.0
    sh.cerceve("GENEL GÖRÜNÜM — üst / yan / alt", "2:1", "FND-P1-01")
    R = P.R_DIS
    # ---------------- ÜST GÖRÜNÜŞ ----------------
    V1 = View(sh, 105, 205, s)
    sh.text(105, 275, "ÜST GÖRÜNÜŞ", 3.4, "middle", bold=True)
    V1.circle(0, 0, R, 0.55)
    V1.circle(0, 0, P.ISIK_R1, 0.25)
    V1.circle(0, 0, P.ISIK_R0, 0.25)
    V1.circle(0, 0, P.CAM_D / 2, 0.25)
    V1.circle(0, 0, P.EKRAN_AKTIF_D / 2, 0.3, "dash")
    V1.merkez_cizgisi(0, 0, R, R, 3)
    # tuş (yan, 0°)
    h = P.TUS_BAS_R
    V1.poly([(R, -h), (R + P.TUS_BAS_UZ, -h), (R + P.TUS_BAS_UZ, h), (R, h)], 0.4)
    # kesit düzlemi A-A: Y ekseni (düşey)
    x0, _ = V1.P(0, 0)
    for yy in (V1.P(0, -R - 7)[1], V1.P(0, R + 7)[1]):
        pass
    sh.line([V1.P(0, -R - 7), V1.P(0, -R - 1)], 0.6)
    sh.line([V1.P(0, R + 1), V1.P(0, R + 7)], 0.6)
    sh.line([V1.P(0, -R - 1), V1.P(0, R + 1)], 0.12, "dashdot")
    for sgn, yl in ((1, R + 8.5), (-1, -R - 8.5)):
        px, py = V1.P(0, sgn * (R + 7))
        sh.ok((px + 5.5, py), 1, 0, 2.2)   # bakış yönü oku (sağa)
        sh.line([(px, py), (px + 5.5, py)], 0.4)
        sh.text(px - 1.8, py + (1.6 if sgn > 0 else -4.2), "A", 3.4, "end", bold=True)
    # etiketler (sol)
    gx = V1.P(-1, 0)[0] - 40   # sol sütun sağ ucu
    def sol(ang, r, y, txt):
        hdf = V1.P(*pol(r, ang))
        sh.lider(hdf, (V1.P(-R, 0)[0] - 4, y), txt, TS, "end")
    sol(150, P.CAM_D / 2, 252, "Ø35 kapak camı (siyah cam)")
    sol(165, P.EKRAN_AKTIF_D / 2, 240, "Ø32,4 ekran aktif alanı (tipik*)")
    sol(180 - 22, 18.8, 228, "lime ışık halkası oluğu")
    # etiketler (sağ)
    hd = V1.P(R + 0.5, h)
    sh.lider(hd, (V1.P(R, 0)[0] + 12, 238), "yan tuş (lime), 0° = saat 3", TS, "start")
    sh.lider(V1.P(0, R + 7), (V1.P(0, 0)[0] + 25, 268), "A–A kesit düzlemi (12–6 ekseni)", TS, "start")
    # ölçüler
    V1.olcu((-R, -2), (R, -2), 46, "Ø40", side=-1, size=3.0, tpos=0.22)
    sh.text(90, 148.5, "tuş başı Ø3,4, çıkıntı 0,8", 2.2, "middle") if False else None

    # ---------------- YAN GÖRÜNÜŞ ----------------
    V2 = View(sh, 105, 92, s)
    sh.text(90, 126, "YAN GÖRÜNÜŞ (A–A ekseninden bakış, −X yönü hariç)", 3.0, "middle", bold=True) if False else None
    sh.text(105, 127, "YAN GÖRÜNÜŞ", 3.4, "middle", bold=True)
    T, c = P.TOPLAM, P.ALT_KAMFER
    V2.poly([(-R + c, 0), (R - c, 0), (R, c), (R, T), (-R, T), (-R, c)], 0.55)
    V2.line([(-R, P.AYRIM_Z), (R, P.AYRIM_Z)], 0.2, "dashdot")
    # cam yüzü ve ışık halkası oluğu (görünmez: kesikli)
    V2.line([(-P.ISIK_R1, T - P.ISIK_DERINLIK), (P.ISIK_R1, T - P.ISIK_DERINLIK)], 0.12, "dot")
    # tuş (sağ)
    zt, ht = P.TUS_Z, P.TUS_BAS_R
    V2.poly([(R, zt - ht), (R + P.TUS_BAS_UZ, zt - ht), (R + P.TUS_BAS_UZ, zt + ht), (R, zt + ht)], 0.4)
    # bayonet kulakları (60°, 180°, 300° -> x izdüşümü)
    z0, z1 = P.BYN_KULAK_Z0, P.BYN_KULAK_Z0 + P.BYN_KULAK_KAL
    Rk = R + P.BYN_KULAK_RAD
    V2.poly([(-Rk, z0), (-R, z0), (-R, z1), (-Rk, z1)], 0.4)
    xa, xb = Rk * math.cos(math.radians(75)), Rk * math.cos(math.radians(45))
    V2.poly([(xa, z0), (xb, z0), (xb, z1), (xa, z1)], 0.3, None)
    # ölçüler (sağ)
    V2.olcu((R, 0), (R, T), 24, side=-1, size=2.8)
    V2.olcu((R, 0), (R, P.AYRIM_Z), 12, side=-1)
    V2.olcu((R, P.AYRIM_Z), (R, T), 12, side=-1)
    V2.olcu((R, 0), (R, zt), 36, "10,4 (tuş ekseni)", side=-1, size=2.4)
    # ölçüler (sol)
    V2.olcu((-Rk, 0), (-Rk, z0), 8, side=1)
    V2.olcu((-Rk, z0), (-Rk, z1), 8, side=1)
    V2.olcu((-R, -0), (R, 0), 8, "Ø40", side=-1, size=2.8)
    # etiketler
    sh.lider(V2.P(R - 6, P.AYRIM_Z), (V2.P(R, 0)[0] + 40, V2.P(0, P.AYRIM_Z)[1] + 0.0 + 14.0), "alt gövde / üst çerçeve ayrım düzlemi", 2.3, "start") if False else None
    sh.lider(V2.P(-12, P.AYRIM_Z), (V2.P(-R, 0)[0] - 6, V2.P(0, T)[1] + 10), "ayrım düzlemi z=8,4", 2.3, "end")
    sh.lider(V2.P(-(Rk + R) / 2 * 0.0 - Rk + 0.4, (z0 + z1) / 2), (V2.P(-R, 0)[0] - 26, V2.P(0, 7)[1] + 9.0), "bayonet kulağı", 2.3, "end")

    # ---------------- ALT GÖRÜNÜŞ ----------------
    V3 = View(sh, 300, 205, s)
    sh.text(300, 275, "ALT GÖRÜNÜŞ (arka kapak)", 3.4, "middle", bold=True)
    V3.circle(0, 0, R, 0.55)
    V3.circle(0, 0, R - P.ALT_KAMFER, 0.25)
    V3.merkez_cizgisi(0, 0, R, R, 3)
    for a in P.kulak_acilari():
        a0, a1 = a - P.BYN_KULAK_GEN / 2, a + P.BYN_KULAK_GEN / 2
        V3.poly(halka_sektor(R, R + P.BYN_KULAK_RAD, a0, a1), 0.45)
    # 120° ve 30° açı ölçüleri
    ra = R + 5.5
    pts = V3.arc(0, 0, ra, 60, 180, 0.15)
    for ang in (60, 180):
        px, py = V3.P(*pol(ra, ang)); tx, ty = -math.sin(math.radians(ang)), math.cos(math.radians(ang))
        sh.ok((px, py), tx * (-1 if ang == 60 else 1), ty * (-1 if ang == 60 else 1))
        sh.line([V3.P(*pol(R + 1.2, ang)), V3.P(*pol(ra + 1.2, ang))], 0.15)
    sh.text(*V3.P(*pol(ra + 0.0, 120)), "120°", 2.6, "middle", rot=120 - 90, valign="baseline") if False else None
    mx, my = V3.P(*pol(ra + 2.6, 120))
    sh.text(mx, my, "120° aralık", 2.4, "middle", rot=30)
    ra2 = R + 3.5
    for ang in (300,):
        V3.arc(0, 0, ra2 + 0.0, ang - 15, ang + 15, 0.15)
        for aa in (ang - 15, ang + 15):
            sh.line([V3.P(*pol(R + 0.8, aa)), V3.P(*pol(ra2 + 1.0, aa))], 0.15)
    mx, my = V3.P(*pol(ra2 + 1.2, 300))
    sh.text(mx + 4, my - 3.0, "30°", 2.4, "start")
    # etiketler
    sh.lider(V3.P(*pol(R + 0.4, 180)), (V3.P(-R, 0)[0] - 8, 238), "bayonet kulağı ×3 (60°, 180°, 300°)", 2.3, "end")
    sh.lider(V3.P(*pol(R - 0.4, 40)), (V3.P(R, 0)[0] + 7, 244), "pah 0,8", 2.3, "start")
    sh.text(300, 152.5, "şarj yöntemi (pogo/manyetik/USB-C) henüz seçilmedi", 2.2, "middle") if False else None
    V3.olcu((-R, -2), (R, -2), 46, "Ø40", side=-1, size=3.0, tpos=0.22)
    V3.olcu((-(R + P.BYN_KULAK_RAD), 0), (R + P.BYN_KULAK_RAD, 0), 0, "Ø41,6 (kulak ucu, yalnız 3 yerde)", side=1, size=2.3) if False else None

    # ---------------- ANA ÖLÇÜLER TABLOSU ----------------
    kol = [("Ölçü", 70), ("Değer", 40), ("Etiket", 95)]
    sat = [
        ["Dış çap (gövde)", "Ø40", "hedef"],
        ["Toplam kalınlık (yığın toplamı)", f"{fmt(P.TOPLAM)}  (≤ {fmt(P.TOPLAM_HEDEF_MAX)})", "hedef"],
        ["Alt gövde / üst çerçeve yüksekliği", f"{fmt(P.ALT_H)} / {fmt(P.UST_H)}", "varsayım"],
        ["Yan duvar kalınlığı", fmt(P.DUVAR), "varsayım"],
        ["Kapak camı çapı", f"Ø{fmt(P.CAM_D)}", "varsayım"],
        ["Ekran aktif alanı (1,28\" yuvarlak)", f"Ø{fmt(P.EKRAN_AKTIF_D)}", "tipik — veri sayfasıyla doğrulanacak"],
        ["Işık halkası oluğu (lime)", f"Ø{fmt(2*P.ISIK_R0)}–{fmt(2*P.ISIK_R1)}", "varsayım"],
        ["Yan tuş: konum / yükseklik (z)", f"0° (saat 3) / {fmt(P.TUS_Z)}", "varsayım"],
        ["Tuş başı çap / çıkıntı", f"Ø{fmt(2*P.TUS_BAS_R)} / {fmt(P.TUS_BAS_UZ)}", "varsayım"],
        ["Bayonet kulağı: adet × genişlik / çıkıntı", f"{P.BYN_SAYI} × {fmt(P.BYN_KULAK_GEN,0)}° / {fmt(P.BYN_KULAK_RAD)}", "varsayım"],
    ]
    tablo(sh, 205, 143, kol, sat, 5.6, 2.4)
    sh.text(205, 77.0, "* Ekran aktif alanı tipik değerdir; seçilecek panelin veri sayfasıyla doğrulanacaktır.", 2.2)
    sh.text(205, 73.2, "Bayonet kulakları dış ölçüyü yalnız 3 bölgede Ø41,6'ya çıkarır. Tuş deliği ve şarj arayüzü bu konseptte çizilmemiştir.", 2.2)
    sh.text(205, 69.4, "Gövde iki parçadır: alt gövde (arka kapak dâhil) + üst çerçeve; birleşim düzlemi z = 8,4.", 2.2)
    return sh


# =====================================================================================
def cizim_02():
    sh = Sheet(ad="02-kesit")
    s = 5.0
    sh.cerceve("KESİT A–A — katman yığını", "5:1", "FND-P1-02")
    OX, OY = 225.0, 140.0
    V = View(sh, OX, OY, s)
    R = P.R_DIS
    T = P.TOPLAM
    z = P.Z
    sh.text(OX, 244, "KESİT A–A (düzlem: Y ekseni, 12–6 saat; sol = 6 saat tarafı)", 3.4, "middle", bold=True)

    def grup(k):
        a, b = z[k]
        sh.grup({"data-katman": k, "data-z0": a, "data-z1": b, "data-olcek": s, "data-oy": sh.H - OY})

    cap = P.ALT_KAMFER
    # --- alt gövde: arka kapak (katman) + duvarlar (tarama: d45)
    grup("arka")
    a, b = z["arka"]
    V.poly([(-R + cap, a), (R - cap, a), (R, a + cap), (R, b), (-R, b), (-R, a + cap)], 0.5, hatch="d45", hs=1.5)
    sh.grup_bitir()
    for sg in (-1, 1):
        V.poly([(sg * R, z["pil"][0]), (sg * P.R_IC, z["pil"][0]), (sg * P.R_IC, P.ALT_H), (sg * R, P.ALT_H)], 0.5, hatch="d45", hs=1.5)
    # --- LiPo pil (dikey çizgi taraması), kesitte Y ekseni boyunca 30 mm
    grup("pil")
    a, b = z["pil"]
    V.poly([(-P.PIL_BOY / 2, a), (P.PIL_BOY / 2, a), (P.PIL_BOY / 2, b), (-P.PIL_BOY / 2, b)], 0.45, hatch="v", hs=1.2)
    sh.grup_bitir()
    # --- bileşenler: zarf (kesikli) + RAK4630 bloğu (çapraz tarama)
    a, b = z["bilesen"]
    V.line([(-17.6, a), (17.6, a), (17.6, b), (-17.6, b), (-17.6, a)], 0.18, "dash")
    grup("bilesen")
    ry0, ry1 = -P.RAK_EN / 2 - 6.0 + 6.0 - 6.0, 0  # yer tutucu (aşağıda yeniden tanımlanır)
    rak_y0, rak_y1 = -13.5, -13.5 + P.RAK_EN        # kart yerleşiminde RAK: y = -13,5 .. +1,5
    V.poly([(rak_y0, a), (rak_y1, a), (rak_y1, b), (rak_y0, b)], 0.45, hatch="cross", hs=1.3)
    sh.grup_bitir()
    # --- kart (dolgu)
    grup("kart")
    a, b = z["kart"]
    V.poly([(-P.R_KART, a), (P.R_KART, a), (P.R_KART, b), (-P.R_KART, b)], 0.5, "#9a9a9a")
    sh.grup_bitir()
    # --- orta çerçeve / boşluk (iki halka bölümü; tarama d135 seyrek)
    grup("orta")
    a, b = z["orta"]
    for sg in (-1, 1):
        V.poly([(sg * 15.5, a), (sg * P.R_IC, a), (sg * P.R_IC, b), (sg * 15.5, b)], 0.4, hatch="d135", hs=1.0)
    sh.grup_bitir()
    # --- panel (yatay çizgi)
    grup("panel")
    a, b = z["panel"]
    V.poly([(-P.PANEL_D / 2, a), (P.PANEL_D / 2, a), (P.PANEL_D / 2, b), (-P.PANEL_D / 2, b)], 0.45, hatch="h", hs=0.8)
    sh.grup_bitir()
    # --- kapak camı (nokta)
    grup("cam")
    a, b = z["cam"]
    V.poly([(-P.CAM_D / 2, a), (P.CAM_D / 2, a), (P.CAM_D / 2, b), (-P.CAM_D / 2, b)], 0.45, hatch="dots", hs=0.9)
    sh.grup_bitir()
    # --- üst çerçeve duvarları (d135, geniş aralık)
    pr = ust_profil()
    for sg in (-1, 1):
        V.poly([(sg * r, zz) for r, zz in pr], 0.5, hatch="d135", hs=1.5)
    # orta çizgi
    V.line([(0, -3), (0, T + 3)], 0.15, "dashdot")
    # ---------- sol etiketler ----------
    L = [  # (attach (y,z), metin)
        ((-18.8, T - 0.5 - 0.1), "lime ışık halkası oluğu"),
        ((-15.0, z["cam"][0] + 0.5), "Kapak camı Ø35"),
        ((-15.5, z["panel"][0] + 0.8), "1,28\" TFT panel Ø33 (aktif Ø32,4)"),
        ((-19.2, 10.6), "üst çerçeve (parça 2)"),
        ((-17.0, z["orta"][0] + 0.3), "Orta çerçeve / boşluk"),
        ((-17.0, z["kart"][0] + 0.4), "Kart (PCB) Ø36"),
        ((-10.0, z["bilesen"][0] + 1.5), "Bileşenler (RAK4630 en yüksek)"),
        ((-19.2, 6.8), "alt gövde duvarı (parça 8)"),
        ((-13.0, z["pil"][0] + 2.0), "LiPo pil (30 mm bu kesitte)"),
        ((-17.0, z["arka"][0] + 0.6), "Arka kapak"),
    ]
    ys = [V.P(a[0], a[1])[1] for a, _ in L]
    # en az 6.6 mm aralık
    yl = list(ys)
    for i in range(1, len(yl)):
        yl[i] = min(yl[i], yl[i - 1] - 6.6)
    kay = (ys[0] - yl[0] + ys[-1] - yl[-1]) / 2
    xl = V.P(-R, 0)[0] - 14
    for (at, txt), y in zip(L, yl):
        hdf = V.P(*at)
        sh.line([hdf, (xl, y), (xl - 1.0, y)], 0.15)
        sh.dot(hdf[0], hdf[1], 0.45)
        sh.text(xl - 2.0, y - 0.9, txt, 2.5, "end")
    # ---------- üst yatay ölçüler ----------
    top = V.P(0, T)[1]
    sh.olcu((V.P(-P.EKRAN_AKTIF_D / 2, 0)[0], top), (V.P(P.EKRAN_AKTIF_D / 2, 0)[0], top), 6, "Ø32,4 aktif alan (tipik)", side=1, size=2.6)
    sh.olcu((V.P(-P.CAM_D / 2, 0)[0], top), (V.P(P.CAM_D / 2, 0)[0], top), 13, "Ø35 kapak camı", side=1, size=2.6)
    sh.olcu((V.P(-R, 0)[0], top), (V.P(R, 0)[0], top), 20, "Ø40", side=1, size=3.2)
    # pil genişliği ve kart içeride (satır içi)
    a, b = z["pil"]
    ym = V.P(0, (a + b) / 2)[1]
    px0, px1 = V.P(-P.PIL_BOY / 2, 0)[0], V.P(P.PIL_BOY / 2, 0)[0]
    sh.poly([(OX - 10, ym - 2.2), (OX + 10, ym - 2.2), (OX + 10, ym + 2.6), (OX - 10, ym + 2.6)], 0, KAGIT)
    sh.line([(px0, ym), (px1, ym)], 0.15)
    sh.ok((px0, ym), -1, 0); sh.ok((px1, ym), 1, 0)
    sh.text(OX, ym - 0.9, "30", 2.6, "middle")
    # ---------- sağ zincir ölçü (yatay metin) ----------
    zs = [0] + [P.Z[k][1] for k in ("arka", "pil", "bilesen", "kart", "orta", "panel", "cam")]
    xe = V.P(R, 0)[0]
    xd = xe + 14
    for zz in zs:
        y = V.P(0, zz)[1]
        sh.line([(xe + 1.0, y), (xd + 1.5, y)], 0.15)
        sh.line([(xd - 1.2, y - 1.2), (xd + 1.2, y + 1.2)], 0.4)
    sh.line([(xd, V.P(0, 0)[1]), (xd, V.P(0, T)[1])], 0.15)
    for k in ("arka", "pil", "bilesen", "kart", "orta", "panel", "cam"):
        a, b = P.Z[k]
        sh.text(xd + 2.0, V.P(0, (a + b) / 2)[1] - 0.9, fmt(b - a), 2.4, "start")
    # toplam / alt gövde / üst çerçeve
    sh.olcu(V.P(R, 0), V.P(R, P.AYRIM_Z), 34, "8,4 alt gövde", side=-1, size=2.5)
    sh.olcu(V.P(R, P.AYRIM_Z), V.P(R, T), 34, "4,0", side=-1, size=2.5, tshift=0.0)
    sh.olcu(V.P(R, 0), V.P(R, T), 48, f"{fmt(T)} toplam (hedef ≤ {fmt(P.TOPLAM_HEDEF_MAX)})", side=-1, size=3.0)
    # ---------- tablo ----------
    kol = [("No", 9), ("Katman (üstten alta)", 66), ("Kalınlık (mm)", 26), ("z alt → z üst (mm)", 38), ("Etiket", 56)]
    sat = []
    for i, (k, ad, t, et) in enumerate(P.YIGIN, 1):
        a, b = P.Z[k]
        sat.append([str(i), ad, fmt(t), f"{fmt(a)} → {fmt(b)}", et])
    sat.append(["", "TOPLAM", fmt(P.TOPLAM), f"0 → {fmt(P.TOPLAM)}", f"hedef ≤ {fmt(P.TOPLAM_HEDEF_MAX)} mm; pay {fmt(P.TOPLAM_HEDEF_MAX - P.TOPLAM)}"])
    tablo(sh, 12, 112, kol, sat, 6.0, 2.5, kalin_son=True)
    # notlar
    nx = 215
    notlar = [
        "Notlar",
        "• Kesit şematiktir; bileşenler yalnız RAK4630 gösterilmiştir (kesikli zarf = 3,0 mm bileşen katmanı).",
        "• Pil–bileşen arası boşluk 0 mm: yığın hedefinde şişme/yalıtım payı yok (açık risk).",
        "• Pil 25×30: kesitte 30 mm görünür; planda Ø36,8 iç boşluğa SIĞMAZ (bkz. 04, README).",
        "• Panel/FPC: konnektör yüksekliği 0,6 mm orta çerçeve payına sığmayabilir (doğrulanacak).",
        "• Tarama: alt gövde 45°, üst çerçeve/orta çerçeve 135°, pil dikey, panel yatay, cam nokta,",
        "  bileşen çapraz, kart dolu gri.",
    ]
    for i, n in enumerate(notlar):
        sh.text(nx, 108 - i * 4.4, n, 2.5 if i else 2.8, bold=(i == 0))
    return sh


# =====================================================================================
def cizim_03():
    sh = Sheet(ad="03-patlatilmis")
    s = 1.5
    k = 0.3          # oblik derinlik kısaltması (y ekseni)
    sh.cerceve("PATLATILMIŞ GÖRÜNÜŞ — parça listesi", "1,5:1 (oblik)", "FND-P1-03")
    CX = 105.0
    sh.text(CX, 283, "PATLATILMIŞ GÖRÜNÜŞ (oblik izdüşüm: x, z ölçekli; derinlik ×0,3)", 3.0, "middle", bold=True)

    def E(cx, cy, rx, ry):  # elips noktaları
        return [(cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a))) for a in range(0, 361, 6)]

    def disc(yt, r, h, ic_r=None, ic_fill=True, num=None):
        """Üst yüz merkezi (CX, yt), yarıçap r mm, kalınlık h mm."""
        rx, ry, hh = r * s, r * s * k, h * s
        yb = yt - hh
        front = [(CX + rx * math.cos(math.radians(a)), yb + ry * math.sin(math.radians(a))) for a in range(180, 361, 6)]
        body = [(CX - rx, yt)] + front + [(CX + rx, yt)]
        sh.poly(body, 0, KAGIT)
        sh.line([(CX - rx, yt), (CX - rx, yb)], 0.4); sh.line([(CX + rx, yt), (CX + rx, yb)], 0.4)
        sh.line(front, 0.4)
        sh.poly(E(CX, yt, rx, ry), 0.45, KAGIT)
        if ic_r:
            sh.poly(E(CX, yt, ic_r * s, ic_r * s * k), 0.3, KAGIT if ic_fill else None)

    def kutu3(cx, yt, x0, x1, y0, y1, h, ymerkez_yt=None):
        """Kutu: üst yüz dikdörtgeni (y derinlik), ön yüz aşağıda. (cx,yt) = model (0,0) üst yüz."""
        X = lambda x: cx + x * s
        Yb = lambda y: yt + y * s * k
        hh = h * s
        sh.poly([(X(x0), Yb(y0) - hh), (X(x1), Yb(y0) - hh), (X(x1), Yb(y0)), (X(x0), Yb(y0))], 0.35, KAGIT)   # ön
        sh.poly([(X(x0), Yb(y0)), (X(x1), Yb(y0)), (X(x1), Yb(y1)), (X(x0), Yb(y1))], 0.35, KAGIT)             # üst

    # dikey konumlar (üst yüz merkezi, sayfa y)
    Y = {"cam": 268, "ust": 240, "panel": 207, "orta": 182, "kart": 156, "bil": 128, "pil": 100, "alt": 74}
    # alt -> üst çiz (üstteki parçalar alttakini kapatabilir)
    # 8 alt gövde
    disc(Y["alt"], P.R_DIS, P.ALT_H, ic_r=P.R_IC)
    # kulaklar (basit işaret): yok
    # 7 pil (25x30)
    kutu3(CX, Y["pil"], -P.PIL_EN / 2, P.PIL_EN / 2, -P.PIL_BOY / 2, P.PIL_BOY / 2, P.PIL_KAL)
    # 6 bileşen grubu: RAK + motor + küçük bloklar (alt yüz, kart ayak izi kesikli)
    sh.poly(E(CX, Y["bil"], P.R_KART * s, P.R_KART * s * k), 0.2, None)
    sh.els[-1] = ("poly", sh.els[-1][1], 0.2, None, None)
    sh.line(E(CX, Y["bil"], P.R_KART * s, P.R_KART * s * k), 0.18, "dash")
    kutu3(CX, Y["bil"], -11.5, 11.5, -13.5, 1.5, P.KALINLIK["bilesen"])
    kutu3(CX, Y["bil"], 12.5, 15.5, -5.5, -2.5, 1.0)
    kutu3(CX, Y["bil"], -13.5 + 0, -9.5 + 0, 5.5 + 0, 8.5, 1.0) if False else None
    kutu3(CX, Y["bil"], 12.5, 14.5, 6.0, 8.0, 1.0)
    kutu3(CX, Y["bil"], -13.25, -8.75, 5.75, 10.25, 1.0)
    # 5 kart
    disc(Y["kart"], P.R_KART, P.KALINLIK["kart"])
    # 4 orta çerçeve (halka)
    disc(Y["orta"], P.R_IC, P.KALINLIK["orta"], ic_r=15.5)
    # 3 panel
    disc(Y["panel"], P.PANEL_D / 2, P.KALINLIK["panel"], ic_r=P.EKRAN_AKTIF_D / 2, ic_fill=False)
    # 2 üst çerçeve
    disc(Y["ust"], P.R_DIS, P.UST_H, ic_r=P.CAM_YUVA_D / 2)
    # ışık halkası oluğu (iki elips)
    sh.line(E(CX, Y["ust"], P.ISIK_R0 * s, P.ISIK_R0 * s * k), 0.2)
    sh.line(E(CX, Y["ust"], P.ISIK_R1 * s, P.ISIK_R1 * s * k), 0.2)
    # 1 kapak camı
    disc(Y["cam"], P.CAM_D / 2, P.KALINLIK["cam"])
    # eksen
    sh.line([(CX, Y["alt"] - 21), (CX, Y["cam"] + 14)], 0.15, "dashdot")
    # tuş (9): üst çerçevenin 0° yan yüzünde
    tx = CX + P.R_DIS * s + 26
    ty = Y["ust"] - (P.AYRIM_Z + P.UST_H - P.TUS_Z) * s
    L = P.TUS_BOY * s
    sh.poly([(tx, ty - P.TUS_FLANS_R * s), (tx + P.TUS_FLANS_KAL * s, ty - P.TUS_FLANS_R * s), (tx + P.TUS_FLANS_KAL * s, ty + P.TUS_FLANS_R * s), (tx, ty + P.TUS_FLANS_R * s)], 0.35, KAGIT)
    sh.poly([(tx + P.TUS_FLANS_KAL * s, ty - P.TUS_GOVDE_R * s), (tx + L - P.TUS_BAS_UZ * s, ty - P.TUS_GOVDE_R * s), (tx + L - P.TUS_BAS_UZ * s, ty + P.TUS_GOVDE_R * s), (tx + P.TUS_FLANS_KAL * s, ty + P.TUS_GOVDE_R * s)], 0.35, KAGIT)
    sh.poly([(tx + L - P.TUS_BAS_UZ * s, ty - P.TUS_BAS_R * s), (tx + L, ty - P.TUS_BAS_R * s), (tx + L, ty + P.TUS_BAS_R * s), (tx + L - P.TUS_BAS_UZ * s, ty + P.TUS_BAS_R * s)], 0.35, KAGIT)
    sh.line([(tx + L + 1, ty), (CX + P.R_DIS * s + 2, ty)], 0.15, "dashdot")
    # balonlar
    bx = 172.0
    def balon(n, hedef, y=None):
        y = hedef[1] if y is None else y
        sh.line([hedef, (bx - 3.2, y)] if abs(hedef[1] - y) < 0.01 else [hedef, (bx - 8, y), (bx - 3.2, y)], 0.15)
        sh.dot(hedef[0], hedef[1], 0.45)
        sh.circle(bx, y, 3.2, 0.35, None, KAGIT)
        sh.text(bx, y - 1.0, str(n), 3.0, "middle")
    def rimx(r): return CX + r * s
    balon(1, (rimx(P.CAM_D / 2), Y["cam"] - 0.5 * s))
    balon(2, (rimx(P.R_DIS), Y["ust"] - 2 * s))
    balon(3, (rimx(P.PANEL_D / 2), Y["panel"] - 0.8 * s))
    balon(4, (rimx(P.R_IC), Y["orta"] - 0.3 * s))
    balon(5, (rimx(P.R_KART), Y["kart"] - 0.4 * s))
    balon(6, (CX + 15.5 * s, Y["bil"] - 1.0 * s))
    balon(7, (CX + P.PIL_EN / 2 * s, Y["pil"] - 2.1 * s))
    balon(8, (rimx(P.R_DIS), Y["alt"] - 4 * s))
    balon(9, (tx + 3.0, ty + P.TUS_FLANS_R * s), y=Y["ust"] + 18)
    # Parça listesi
    kol = [("No", 8), ("Parça", 50), ("Adet", 10), ("Ölçü (mm)", 40), ("Not", 80)]
    sat = [
        ["1", "Kapak camı (siyah)", "1", f"Ø{fmt(P.CAM_D)} × {fmt(P.KALINLIK['cam'])}", "varsayım; kenarı üst çerçeveye yapıştırılır"],
        ["2", "Üst çerçeve", "1", f"Ø{fmt(P.D_DIS)} × {fmt(P.UST_H)}", "govde-ust-cerceve.stl; ışık halkası oluğu, cam yuvası"],
        ["3", "1,28\" yuvarlak TFT panel", "1", f"Ø{fmt(P.PANEL_D)} × {fmt(P.KALINLIK['panel'])}", "aktif Ø32,4 tipik; veri sayfasıyla doğrulanacak"],
        ["4", "Orta çerçeve / boşluk", "1", f"Ø{fmt(2*P.R_IC)}/Ø31 × {fmt(P.KALINLIK['orta'])}", "şematik; FPC payı; STL üretilmedi"],
        ["5", "Kart (PCB)", "1", f"Ø{fmt(P.KART_D)} × {fmt(P.KALINLIK['kart'])}", "yerleşim önerisi: 04; şema/gerber yok"],
        ["6", "Bileşen grubu (kart alt yüzü)", "1", f"yükseklik ≤ {fmt(P.KALINLIK['bilesen'])}", "RAK4630 15×23, GNSS, LSM303AGR, PMIC, motor"],
        ["7", "LiPo pil", "1", f"{fmt(P.PIL_EN)}×{fmt(P.PIL_BOY)}×{fmt(P.PIL_KAL)}", "250–300 mAh sınıfı; katalogdan doğrulanacak; SIĞMIYOR*"],
        ["8", "Alt gövde + arka kapak", "1", f"Ø{fmt(P.D_DIS)} × {fmt(P.ALT_H)}", "govde-alt.stl; bayonet kulakları ×3 dâhil"],
        ["9", "Yan tuş (lime)", "1", f"Ø{fmt(2*P.TUS_BAS_R)} baş, L {fmt(P.TUS_BOY)}", "tus.stl; tuş deliği gövdede YOK (basitleştirme)"],
        ["10", "Aparat: kol bandı / anahtarlık / kolye", "1", f"Ø{fmt(2*P.AP_R_DIS)} × {fmt(P.AP_H)}", "bayonet ile takılır; bkz. çizim 05 ve stl/"],
    ]
    H = tablo(sh, 205, 285, kol, sat, 7.0, 2.4)
    ty0 = 285 - H - 6
    notlar = [
        "* Pil 25×30 mm dikdörtgeninin köşegeni (39,1) iç boşluk çapını (36,8) aşar: ≤ 22×28 pil veya",
        "  kesik/yuvarlak hücre gerekir (bkz. 04). Katman yığını (12,4) bu varsayımla çizilmiştir.",
        "Montaj sırası: 8 → 7 → 5+6 (kart, bileşenler aşağı bakar) → 4 → 3 → 2 → 1; tuş (9), 2 takılırken",
        "yan delikten yerleştirilir. Alt gövde–üst çerçeve birleşimi yapıştırma/ultrasonik (vida yok).",
        "Parça numaraları: balonlar soldaki istif, numaralar tabloyla aynıdır. Ölçüler hedef/varsayımdır.",
    ]
    for i, n in enumerate(notlar):
        sh.text(205, ty0 - i * 4.3, n, 2.4)
    return sh

# =====================================================================================
# Kart yerleşim önerisi: blok konumları (mm, kart merkezi orijin, +x sağ = 0°, +y üst = saat 12)
def yerlesim():
    r = P.RAK_EN
    return {
        "rak":   dict(x0=-P.RAK_BOY / 2, x1=P.RAK_BOY / 2, y0=-13.5, y1=-13.5 + P.RAK_EN),
        "yama":  dict(cx=0.0, cy=9.0, w=P.GNSS_YAMA),
        "keep":  dict(cx=0.0, cy=9.0, w=P.GNSS_KEEPOUT),
        "gnss":  dict(cx=-11.0, cy=8.0, w=P.GNSS_IC),
        "lsm":   dict(cx=13.5, cy=7.0, w=P.LSM_KENAR),
        "pmic":  dict(cx=14.0, cy=-4.0, w=P.PMIC_KENAR),
        "motor": dict(cx=-14.6, cy=-3.0, r=P.MOTOR_D / 2),
        "tus":   dict(cx=16.5, cy=0.0, w=P.TUS_SW[0], h=P.TUS_SW[1]),
        "fpc":   dict(cx=0.0, cy=-15.8, w=P.FPC_KON[0], h=P.FPC_KON[1]),
        "pilk":  dict(cx=-13.0, cy=-9.5, w=P.PIL_KON[0], h=P.PIL_KON[1]),
        "feed":  dict(x=P.RAK_BOY / 2, y=-10.0),
    }


def cizim_04():
    sh = Sheet(ad="04-kart-yerlesim")
    s = 4.0
    sh.cerceve("KART YERLEŞİM ÖNERİSİ — Ø36 yuvarlak kart", "4:1", "FND-P1-04")
    CX, CY = 122.0, 150.0
    V = View(sh, CX, CY, s)
    L = yerlesim()
    sh.text(CX, 253, "YERLEŞİM ÖNERİSİ (blok düzeyinde) — şema veya gerber DEĞİLDİR", 3.2, "middle", bold=True)
    sh.text(CX, 248.2, "Üstten görünüş, şeffaf gösterim: bileşenler kartın alt yüzünde; FPC konnektörü üst yüzde. Tuş 0° = sağ.", 2.3, "middle")
    # iç boşluk, kart
    V.circle(0, 0, P.R_IC, 0.25, "dash")
    V.circle(0, 0, P.R_KART, 0.65)
    V.merkez_cizgisi(0, 0, P.R_KART, P.R_KART, 3)

    def rect(cx, cy, w, h, lw=0.4, dash=None, fill=None, hatch=None):
        pts = [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]
        if dash:
            V.line(pts + [pts[0]], lw, dash)
        else:
            V.poly(pts, lw, fill, hatch)

    # 868 MHz anten keep-out bandı (alt kenar) — tarama
    band = [V.P(*pol(18.0, a)) for a in range(235, 306, 5)] + [V.P(*pol(16.6, a)) for a in range(305, 234, -5)]
    sh.poly(band, 0.25, None, "d45", 1.3)
    # RAK4630
    r = L["rak"]
    V.poly([(r["x0"], r["y0"]), (r["x1"], r["y0"]), (r["x1"], r["y1"]), (r["x0"], r["y1"])], 0.55, None)
    mx, my = V.P(0, (r["y0"] + r["y1"]) / 2)
    sh.text(mx, my + 3.5, "RAK4630", 3.4, "middle", bold=True)
    sh.text(mx, my - 0.5, "nRF52840 + SX1262", 2.6, "middle")
    sh.text(mx, my - 4.2, "≈15×23 mm, h ≈3,0 — veri sayfasıyla doğrulanacak", 2.1, "middle")
    # GNSS yama + keep-out
    y = L["yama"]; rect(y["cx"], y["cy"], y["w"], y["w"], 0.55)
    kp = L["keep"]; rect(kp["cx"], kp["cy"], kp["w"], kp["w"], 0.3, "dash")
    sh.text(*V.P(0, 9.9), "GNSS yama anten", 2.7, "middle")
    sh.text(*V.P(0, 7.2), "12×12 (üst yüz!)", 2.4, "middle")
    sh.text(*V.P(0, 4.6), "keep-out 15×15", 2.2, "middle")
    # GNSS IC, LSM, PMIC, motor, tuş, fpc, pil konnektörü
    g = L["gnss"]; rect(g["cx"], g["cy"], g["w"], g["w"], 0.45)
    l_ = L["lsm"]; rect(l_["cx"], l_["cy"], l_["w"], l_["w"], 0.45)
    pm = L["pmic"]; rect(pm["cx"], pm["cy"], pm["w"], pm["w"], 0.45)
    m = L["motor"]; V.circle(m["cx"], m["cy"], m["r"], 0.45)
    t = L["tus"]; rect(t["cx"], t["cy"], t["w"], t["h"], 0.45)
    f = L["fpc"]; rect(f["cx"], f["cy"], f["w"], f["h"], 0.45, None, None, "d135")
    pk = L["pilk"]; rect(pk["cx"], pk["cy"], pk["w"], pk["h"], 0.45, None, None, "cross")
    # pil izi (altta, kesikli 25x30) — köşeler iç boşluğu aşar
    pw, ph = P.PIL_EN, P.PIL_BOY
    V.line([(-pw / 2, -ph / 2), (pw / 2, -ph / 2), (pw / 2, ph / 2), (-pw / 2, ph / 2), (-pw / 2, -ph / 2)], 0.3, "uzun")
    sh.text(*V.P(-pw / 2 + 0.4, ph / 2 + 1.0), "pil 25×30 (altta, kesikli) — köşeler Ø36,8 dışında", 2.2, "start") if False else None
    et_pil = True
    # RF besleme noktası
    fd = L["feed"]
    V.circle(fd["x"], fd["y"], 0.7, 0.5, None, "#000")
    # ---- numaralı çakışma işaretleri ----
    def isaret(n, x, y):
        px, py = V.P(x, y)
        sh.circle(px, py, 3.0, 0.5, None, KAGIT)
        sh.text(px, py - 1.0, str(n), 3.0, "middle", bold=True)
        return px, py
    # ---- etiketler (leader) ----
    def et(hdf, xy, txt, anchor="start", size=2.4):
        sh.lider(V.P(*hdf), xy, txt, size, anchor)
    xl = V.P(-P.R_KART, 0)[0] - 8
    xr = V.P(P.R_KART, 0)[0] + 8
    et((m["cx"] - 3, m["cy"] + 2), (xl, V.P(0, -1.0)[1]), "titreşim motoru Ø6", "end")
    et((g["cx"] - 2, g["cy"] + 1), (xl, V.P(0, 6.5)[1]), "GNSS modülü", "end")
    et((pk["cx"] - 1, pk["cy"] - 0.5), (xl, V.P(0, -9.0)[1]), "pil bağlantısı", "end")
    et((l_["cx"] + 1, l_["cy"] + 0.5), (xr, V.P(0, 9.0)[1]), "LSM303AGR (2×2)", "start")
    et((t["cx"] + 1.5, t["cy"]), (xr, V.P(0, 2.5)[1]), "yan tuş mikro anahtarı (0°)", "start")
    et((pm["cx"] + 1.5, pm["cy"] - 0.5), (xr, V.P(0, -4.0)[1]), "şarj / PMIC (3×3)", "start")
    et((f["cx"] + 3.0, f["cy"] - 0.8), (V.P(0, -19.5)[0] + 38, V.P(0, -19.5)[1] - 1.5), "ekran FPC kon. (üst yüz)", "start")
    et((fd["x"], fd["y"]), (xr, V.P(0, -9.5)[1]), "868 MHz RF besleme noktası", "start")
    et((P.PIL_EN / 2, P.PIL_BOY / 2), (xr, V.P(0, 17.0)[1]), "pil 25×30 (altta, kesikli)", "start")
    # çakışma işaretleri
    isaret(1, 0.0, 16.9 + 0)  if False else None
    px, py = isaret(1, 10.8, 14.8)
    px, py = isaret(2, -10.8, -14.4)
    px, py = isaret(3, -12.5, 12.6)
    isaret(4, 13.8, -15.8)
    isaret(5, 6.8, -16.6)
    isaret(6, -11.9, -3.0)
    # ölçüler
    V.olcu((-P.R_KART, 0), (P.R_KART, 0), 0.0, "Ø36", side=1, size=2.6, tpos=0.5) if False else None
    sh.olcu(V.P(-P.R_KART, -P.R_KART), V.P(P.R_KART, -P.R_KART), 6.5, "Ø36 kart", side=-1, size=2.8, tpos=0.5) if False else None
    sh.olcu(V.P(-P.R_KART, 0), V.P(P.R_KART, 0), 0, "", side=1) if False else None
    yb = V.P(0, -P.R_KART)[1]
    sh.olcu((V.P(-P.R_KART, 0)[0], yb - 0.0), (V.P(P.R_KART, 0)[0], yb), 17, "Ø36 kart (iç boşluk Ø36,8)", side=-1, size=2.8, ext=1.5, gap=-0.0)
    sh.olcu(V.P(-P.RAK_BOY / 2, -13.5), V.P(P.RAK_BOY / 2, -13.5), 0.0, "", side=1) if False else None
    # RAK ölçüleri: iç
    rx0, ry0 = V.P(-P.RAK_BOY / 2, 0); rx1 = V.P(P.RAK_BOY / 2, 0)[0]
    # ---- sağ panel: blok tablosu ----
    kol = [("Blok", 50), ("Ölçü (plan, mm)", 38), ("Merkez x ; y", 26), ("Durum", 40)]
    def mrk(d): return f"{fmt(d['cx'], 1)} ; {fmt(d['cy'], 1)}"
    sat = [
        ["RAK4630 (nRF52840+SX1262)", f"{fmt(P.RAK_BOY)} × {fmt(P.RAK_EN)}", "0 ; -6,0", "doğrulanacak"],
        ["GNSS yama anten", f"{fmt(P.GNSS_YAMA)} × {fmt(P.GNSS_YAMA)} (12–15)", mrk(L["yama"]), "doğrulanacak"],
        ["GNSS yama keep-out", f"{fmt(P.GNSS_KEEPOUT)} × {fmt(P.GNSS_KEEPOUT)}", mrk(L["keep"]), "varsayım"],
        ["GNSS modülü", f"{fmt(P.GNSS_IC)} × {fmt(P.GNSS_IC)}", mrk(L["gnss"]), "doğrulanacak"],
        ["LSM303AGR", f"{fmt(P.LSM_KENAR)} × {fmt(P.LSM_KENAR)}", mrk(L["lsm"]), "doğrulanacak"],
        ["Şarj / PMIC", f"{fmt(P.PMIC_KENAR)} × {fmt(P.PMIC_KENAR)}", mrk(L["pmic"]), "varsayım"],
        ["Titreşim motoru", f"Ø{fmt(P.MOTOR_D)}", mrk(L["motor"]), "varsayım"],
        ["Yan tuş anahtarı", f"{fmt(P.TUS_SW[0])} × {fmt(P.TUS_SW[1])}", mrk(L["tus"]), "varsayım"],
        ["Ekran FPC konnektörü", f"{fmt(P.FPC_KON[0])} × {fmt(P.FPC_KON[1])}", mrk(L["fpc"]), "varsayım"],
        ["Pil bağlantısı", f"{fmt(P.PIL_KON[0])} × {fmt(P.PIL_KON[1])}", mrk(L["pilk"]), "varsayım"],
        ["868 MHz RF besleme", "nokta", f"{fmt(L['feed']['x'], 1)} ; {fmt(L['feed']['y'], 1)}", "doğrulanacak"],
    ]
    TX = 254
    H = tablo(sh, TX, 287, kol, sat, 5.4, 2.3)
    y0 = 287 - H - 6
    sh.text(TX, y0, "ÇAKIŞMA / AÇIK RİSK İŞARETLERİ (çizimdeki numaralı daireler)", 2.9, bold=True)
    risk = [
        ("1", "GNSS yama anten ekranın/camın ALTINDA kalıyor: gökyüzü görüşü ve ITO/metal gölgesi (spec riski).",
              "Keep-out köşeleri kart kenarına değiyor (r≈18,1). Alternatif: yama kenara/kayışa ya da üst yüze açık pencere."),
        ("2", "868 MHz anten kartta YOK: λ/4 ≈ 86 mm. Yalnız RF besleme noktası ve alt kenar keep-out bandı",
              "ayrıldı (taranmış bölge); RAK4630 köşeleri bu banda giriyor. Anten: kayış/askı içi veya FPC çevre anteni."),
        ("3", "GNSS girişi (1575 MHz) ile 868 MHz RAK4630 aynı bölgede: karışma/gürültü payı doğrulanmadı.", ""),
        ("4", "Pil 25×30 (kesikli): köşegen 39,1 > iç Ø36,8 — SIĞMAZ. ≤22×28 pil veya kesik köşe gerekir;",
              "RAK4630 (h 3,0) ile pil arasında düşey boşluk da 0 mm (yığın hedefi)."),
        ("5", "Ekran FPC konnektörü (üst yüz) yüksekliği 0,6 mm orta çerçeve payına sığmayabilir.",
              "Konnektör RAK4630 kenarına yalnız 1,3 mm; kablo kıvrımı doğrulanacak."),
        ("6", "Titreşim motoru ile RAK4630 arası 0,1 mm; motor ve yan tuş mıknatıssal etkisi pusula için ölçülecek.", ""),
    ]
    yy = y0 - 5.2
    for n, a, b in risk:
        sh.circle(TX + 2.5, yy + 0.9, 2.1, 0.4, None, KAGIT)
        sh.text(TX + 2.5, yy + 0.0, n, 2.4, "middle", bold=True)
        sh.text(TX + 6.5, yy, a, 2.3)
        if b:
            yy -= 3.7
            sh.text(TX + 6.5, yy, b, 2.3)
        yy -= 5.2
    sh.text(TX, yy - 1.0, "Bu çizim bir yerleşim ÖNERİSİDİR: şema, ağ listesi, katman dizilimi ve gerber yoktur. Konumlar", 2.3)
    sh.text(TX, yy - 4.6, "kullanıcı onayıyla ve bileşen veri sayfalarıyla yeniden çizilecektir. Tüm değerler hedef/varsayımdır.", 2.3)
    return sh

# =====================================================================================
def cizim_05():
    import govde
    sh = Sheet(ad="05-aparatlar")
    sh.cerceve("TAŞIMA APARATLARI — kol bandı / anahtarlık / kolye + bayonet", "1,25:1 ve 2:1", "FND-P1-05")
    s = 1.25
    YC = 208.0
    xo = P.BANT_AYAK_IC + P.BANT_AYAK_KAL
    y_ayak0 = govde._ayak_y0()

    def cradle(V, ghost_hole=True):
        V.circle(0, 0, P.AP_R_DIS, 0.55)
        V.circle(0, 0, P.AP_R_IC, 0.3)
        V.circle(0, 0, P.AP_TABAN_DELIK_R, 0.22, "dash")
        V.merkez_cizgisi(0, 0, P.AP_R_DIS, P.AP_R_DIS, 2)
        for a in P.kulak_acilari():
            a0 = a + P.BYN_DONUS + P.BYN_AP_KULAK_GEN / 2 - P.BYN_AP_KULAK_GEN / 2 - 15
            a0 = a + P.BYN_DONUS - 15
            V.poly(halka_sektor(P.AP_KULAK_R_IC, P.AP_R_IC, a0, a0 + P.BYN_AP_KULAK_GEN), 0.35, None, "d45", 0.9)

    def yan(V, tur):
        R_, H_ = P.AP_R_DIS, P.AP_H
        V.poly([(-R_, 0), (R_, 0), (R_, H_), (-R_, H_)], 0.5)
        V.line([(-P.AP_R_IC, P.AP_TABAN), (P.AP_R_IC, P.AP_TABAN)], 0.15, "dash")
        # modül (kesikli) oturmuş
        z0 = P.MODUL_OTURMA_Z; z1 = z0 + P.TOPLAM
        V.line([(-P.R_DIS, z0), (-P.R_DIS, z1), (P.R_DIS, z1), (P.R_DIS, z0), (-P.R_DIS, z0)], 0.3, "dash")
        if tur == "bant":
            V.poly([(-xo + 0.5, 0), (xo - 0.5, 0), (xo - 0.5, P.BANT_YUKSEK), (-xo + 0.5, P.BANT_YUKSEK)], 0.35, None) if False else None
            for sg in (-1, 1):
                x0, x1 = sorted((sg * P.BANT_AYAK_IC, sg * xo))
                V.poly([(x0, 0), (x1, 0), (x1, P.BANT_YUKSEK), (x0, P.BANT_YUKSEK)], 0.4)
        else:
            V.line([(-P.HALKA_DIS_R, 0), (-P.HALKA_DIS_R, P.HALKA_KAL), (P.HALKA_DIS_R, P.HALKA_KAL), (P.HALKA_DIS_R, 0)], 0.3, "dash")
        V.olcu((-R_, 0), (R_, 0), 7.5, f"Ø{fmt(2*R_)}", side=-1, size=2.4)
        V.olcu((R_, 0), (R_, H_), 6, fmt(H_), side=-1, size=2.3)

    cols = [(75.0, "bant"), (210.0, "anahtarlik"), (345.0, "kolye")]
    basl = {"bant": "KOL BANDI YUVASI", "anahtarlik": "ANAHTARLIK HALKASI", "kolye": "KOLYE ASKISI"}
    for cx, tur in cols:
        sh.text(cx, 281, basl[tur], 3.4, "middle", bold=True)
        V = View(sh, cx, YC, s)
        cradle(V)
        if tur == "bant":
            for sy in (1, -1):
                for sg in (1, -1):
                    x0, x1 = sorted((sg * P.BANT_AYAK_IC, sg * xo))
                    ya, yb = sorted((sy * y_ayak0, sy * P.BANT_BAR_Y1))
                    V.poly([(x0, ya), (x1, ya), (x1, yb), (x0, yb)], 0.4, None)
                ya, yb = sorted((sy * P.BANT_BAR_Y0, sy * P.BANT_BAR_Y1))
                V.poly([(-xo + 0.5, ya), (xo - 0.5, ya), (xo - 0.5, yb), (-xo + 0.5, yb)], 0.45, None, "d135", 0.9)
                # bant (hayalet)
                for sg in (1, -1):
                    V.line([(sg * P.BANT_EN / 2, sy * (P.BANT_BAR_Y0 + 0.2)), (sg * P.BANT_EN / 2, sy * 40)], 0.2, "dash")
            sh.olcu(V.P(-P.BANT_EN / 2, 40), V.P(P.BANT_EN / 2, 40), 3.5, f"{fmt(P.BANT_EN)} bant", side=1, size=2.4)
            sh.lider(V.P(0.0, P.BANT_BAR_Y1), (V.P(0, 0)[0] + 24, V.P(0, 32)[1]), "bant barı 3×25, h 4", 2.3, "start")
            sh.lider(V.P(0.0, (P.AP_R_DIS + P.BANT_BAR_Y0) / 2), (V.P(0, 0)[0] + 24, V.P(0, 28)[1]), "pencere 2,1 (bant ≤ 2,0)", 2.3, "start")
            sh.lider(V.P(11.5, 19.6), (V.P(0, 0)[0] - 26, V.P(0, 31)[1]), "ayak 2×(inş.)", 2.3, "end") if False else None
        else:
            cy = P.HALKA_MERKEZ_Y
            V.circle(0, cy, P.HALKA_DIS_R, 0.5)
            V.circle(0, cy, P.HALKA_IC_R, 0.4)
            if tur == "anahtarlik":
                V.circle(0, cy + 3.0, 8.5, 0.25, "dash")
                sh.text(*V.P(-11.5, cy + 8.0), "split-ring Ø~25", 2.3, "end")
            else:
                # ip + kopma kilidi
                for sg in (-1, 1):
                    V.line([(sg * 0.4, cy + 3.2), (sg * 16, cy + 26)], 0.25, "dash")
                kx, ky = V.P(-12.0, cy + 18.0)
                kk = [(kx - 3.4, ky - 2.4), (kx + 3.4, ky - 2.4), (kx + 3.4, ky + 2.4), (kx - 3.4, ky + 2.4)]
                sh.poly(kk, 0.45, KAGIT)
                sh.line([(kx, ky - 2.4), (kx, ky + 2.4)], 0.3)
                sh.lider((kx - 3.4, ky + 1.0), (kx - 12, ky + 12), "çekince açılan kilit", 2.3, "end")
                sh.text(kx - 12 - 1.0, ky + 12 - 4.0, f"(breakaway) {fmt(P.KOLYE_KOPMA_KGF[0])}–{fmt(P.KOLYE_KOPMA_KGF[1])} kgf hedef", 2.1, "end")
                sh.text(kx - 12 - 1.0, ky + 12 - 7.0, "doğrulanacak", 2.1, "end")
            sh.olcu(V.P(-P.HALKA_IC_R, cy), V.P(P.HALKA_IC_R, cy), 0.0, "", side=1) if False else None
            sh.lider(V.P(P.HALKA_DIS_R * 0.7, cy + P.HALKA_DIS_R * 0.7), (V.P(0, 0)[0] + 24, V.P(0, cy + 1)[1]),
                     f"halka Ø{fmt(2*P.HALKA_DIS_R)} / delik Ø{fmt(2*P.HALKA_IC_R)}", 2.3, "start") if tur == "anahtarlik" else \
                sh.lider(V.P(P.HALKA_DIS_R * 0.7, cy + P.HALKA_DIS_R * 0.7), (V.P(0, 0)[0] + 24, V.P(0, cy + 4)[1]),
                         f"halka Ø{fmt(2*P.HALKA_DIS_R)} / delik Ø{fmt(2*P.HALKA_IC_R)}", 2.3, "start")
        # yan görünüş
        V2 = View(sh, cx, 150.0, s)
        yan(V2, tur)
    sh.text(345, 131.5, "Kolye: anahtarlık aparatının halkası kullanılır;", 2.1, "middle")
    sh.text(345, 128.0, "ipte ayrı çekince açılan kilit (ayrı parça, STL yok).", 2.1, "middle")
    # ------------------------------------------------ bayonet detay (üstten)
    s2 = 2.0
    BX, BY = 108.0, 66.0
    VB = View(sh, BX, BY, s2)
    sh.text(BX, 129, "BAYONET ARAYÜZÜ (üstten)", 3.0, "middle", bold=True)
    VB.circle(0, 0, P.AP_R_DIS, 0.5)
    VB.circle(0, 0, P.AP_R_IC, 0.3)
    VB.circle(0, 0, P.R_DIS, 0.3, "dash")
    VB.merkez_cizgisi(0, 0, P.AP_R_DIS, P.AP_R_DIS, 2)
    Rk = P.R_DIS + P.BYN_KULAK_RAD
    for a in P.kulak_acilari():
        a0 = a + P.BYN_DONUS - 15
        VB.poly(halka_sektor(P.AP_KULAK_R_IC, P.AP_R_IC, a0, a0 + P.BYN_AP_KULAK_GEN), 0.4, None, "d45", 1.0)
        pts = halka_sektor(P.R_DIS, Rk, a + P.BYN_DONUS - 15, a + P.BYN_DONUS + 15)
        VB.line(pts + [pts[0]], 0.3, "dash")
        VB.poly(halka_sektor(P.R_DIS, Rk, a - 15, a + 15), 0.5, None, "cross", 0.8)
    a = P.kulak_acilari()[0]
    rr = P.AP_R_DIS + 4.0
    VB.arc(0, 0, rr, a, a + P.BYN_DONUS, 0.3)
    px, py = VB.P(*pol(rr, a + P.BYN_DONUS))
    sh.ok((px, py), -math.sin(math.radians(a + P.BYN_DONUS)), math.cos(math.radians(a + P.BYN_DONUS)))
    tx, ty = VB.P(*pol(rr + 1.5, a + P.BYN_DONUS + 8))
    sh.text(tx, ty + 1.0, f"{fmt(P.BYN_DONUS, 0)}° kilit dönüşü", 2.3, "end")
    xl = VB.P(-P.AP_R_DIS, 0)[0] - 6
    ka = P.kulak_acilari()
    sh.lider(VB.P(*pol(P.AP_R_IC - 0.4, ka[0] + 60)), (xl, VB.P(0, 14)[1]), "aparat iç kulağı", 2.3, "end")
    sh.lider(VB.P(*pol(Rk - 0.4, ka[1])), (xl, VB.P(0, 2)[1]), "modül kulağı, giriş", 2.3, "end")
    sh.lider(VB.P(*pol(Rk - 0.4, ka[1] + P.BYN_DONUS)), (xl, VB.P(0, -12)[1]), "modül kulağı, kilit", 2.3, "end")
    # ---- açılım ----
    DX, DY, sc = 160.0, 102.0, 2.2
    k_ac = math.pi * (P.R_DIS + P.AP_R_IC) / 2 / 180.0
    VD = View(sh, DX, DY, sc)
    sh.text(DX, 129, "AÇILIM (silindirik kesit açılmış; 1 kulak aralığı)", 3.0, "start", bold=True)
    sh.text(DX, 124.6, "z: aparat tabanından; modül tabanı z = 1,6'da oturur", 2.2, "start")
    A0 = -30.0
    X = lambda ang: (ang - A0) * k_ac
    xs = X(90.0)
    VD.poly([(0, 0), (xs, 0), (xs, P.AP_TABAN), (0, P.AP_TABAN)], 0.4, None, "d45", 1.0)
    VD.poly([(X(30), P.AP_KULAK_Z0), (X(90), P.AP_KULAK_Z0), (X(90), P.AP_KULAK_Z0 + P.AP_KULAK_KAL), (X(30), P.AP_KULAK_Z0 + P.AP_KULAK_KAL)], 0.45, None, "d45", 1.0)
    VD.line([(0, P.AP_H), (xs, P.AP_H)], 0.4)
    VD.line([(0, P.AP_TABAN), (0, P.AP_H)], 0.4); VD.line([(xs, P.AP_TABAN), (xs, P.AP_H)], 0.4)
    zm0 = P.MODUL_OTURMA_Z + P.BYN_KULAK_Z0
    zm1 = zm0 + P.BYN_KULAK_KAL
    VD.line([(X(-15), zm0), (X(15), zm0), (X(15), zm1), (X(-15), zm1), (X(-15), zm0)], 0.5)
    VD.line([(X(30), zm0), (X(60), zm0), (X(60), zm1), (X(30), zm1), (X(30), zm0)], 0.35, "dash")
    px, py = VD.P(X(30) - 0.3, (zm0 + zm1) / 2)
    sh.line([VD.P(X(15) + 0.3, (zm0 + zm1) / 2), (px, py)], 0.3)
    sh.ok((px, py), 1, 0, 1.8)
    sh.text(*VD.P(X(0), zm1 + 0.25), "modül kulağı (giriş)", 2.0, "middle")
    sh.text(*VD.P(X(60), zm0 - 1.3), "modül kulağı (kilit)", 2.0, "middle")
    sh.text(*VD.P(X(60), P.AP_KULAK_Z0 + P.AP_KULAK_KAL + 0.45), "aparat iç kulağı", 2.0, "middle")
    # dikey zincir ölçü (yatay metin)
    xe = VD.P(xs, 0)[0]
    xd = xe + 6
    zs = [0, P.AP_TABAN, zm0, zm1, P.AP_KULAK_Z0, P.AP_KULAK_Z0 + P.AP_KULAK_KAL, P.AP_H]
    for zz in zs:
        y = VD.P(0, zz)[1]
        sh.line([(xe + 0.8, y), (xd + 1.2, y)], 0.15)
        sh.line([(xd - 1.0, y - 1.0), (xd + 1.0, y + 1.0)], 0.35)
    sh.line([(xd, VD.P(0, 0)[1]), (xd, VD.P(0, P.AP_H)[1])], 0.15)
    for z0_, z1_ in zip(zs[:-1], zs[1:]):
        d = z1_ - z0_
        if d < 0.3:
            continue
        sh.text(xd + 2.0, VD.P(0, (z0_ + z1_) / 2)[1] - 0.7, fmt(d), 2.0, "start")
    sh.lider(VD.P(X(60) + 4.0, (zm1 + P.AP_KULAK_Z0) / 2), (xd + 14, VD.P(0, 4.3)[1] + 8.5), "eksenel boşluk 0,2", 2.0, "start") if False else None
    sh.text(xd + 11, VD.P(0, 6.3)[1] - 0.7, "← 0,2 boşluk", 2.0, "start")
    # yatay açı ölçüleri (altta)
    yb = VD.P(0, 0)[1]
    def aci_olcu(a0, a1, off, txt):
        sh.olcu((VD.P(X(a0), 0)[0], yb), (VD.P(X(a1), 0)[0], yb), off, txt, side=-1, size=2.2, ext=1.0)
    aci_olcu(-30, 30, 5, "boşluk 60°")
    aci_olcu(30, 90, 5, "aparat kulağı 60°")
    aci_olcu(-15, 15, 12, "modül kulağı 30°")
    aci_olcu(-30, 90, 19, "120° aralık (3 kulak)")
    # ---- arayüz tablosu ----
    TX = 290.0
    kol = [("Öğe", 34), ("Açı", 28), ("R (mm)", 28), ("z (mm)", 30)]
    sat = [
        ["Modül kulağı ×3", f"{fmt(P.BYN_KULAK_GEN,0)}° (60/180/300)", f"{fmt(P.R_DIS)} → {fmt(Rk)}", f"{fmt(P.BYN_KULAK_Z0)}–{fmt(P.BYN_KULAK_Z0+P.BYN_KULAK_KAL)} (modül)"],
        ["Aparat iç kulağı ×3", f"{fmt(P.BYN_AP_KULAK_GEN,0)}°", f"{fmt(P.AP_KULAK_R_IC)} → {fmt(P.AP_R_IC)}", f"{fmt(P.AP_KULAK_Z0)}–{fmt(P.AP_KULAK_Z0+P.AP_KULAK_KAL)} (aparat)"],
        ["Aparat iç / dış Ø", "—", f"Ø{fmt(2*P.AP_R_IC)} / Ø{fmt(2*P.AP_R_DIS)}", f"h {fmt(P.AP_H)}, taban {fmt(P.AP_TABAN)}"],
        ["Boşluk / dönüş", f"{fmt(P.BYN_DONUS,0)}° (CCW)", f"{fmt(P.BYN_YAN_BOS)} radyal", f"{fmt(P.BYN_YAN_BOS)} eksenel"],
        ["Kol bandı", f"{fmt(P.BANT_EN)} geniş", f"{fmt(P.BANT_KAL)} kalın", "pencere 2,1"],
    ]
    tablo(sh, TX, 126, kol, sat, 5.4, 2.0)
    sh.text(TX, 126 - 5.4 * 6 - 3.5, "Tüm değerler varsayımdır (FDM 0,2 mm boşluk).", 2.1)
    # ---- gerekçe ----
    GX = 160.0
    sh.text(GX, 74, "SEÇİM: 3 kulaklı BAYONET (çeyrek tur yerine 45° dönüş). GEREKÇE:", 2.6, bold=True)
    ger = [
        "1) Çekme yükü (kolye/anahtarlık) radyal kulaklara biner; plastik kanca yorulması yok, çekince kendiliğinden açılmaz.",
        "2) Tuş ve pusula yönü için modülün aparatta dönmemesi gerekir; bayonet açısal kilitler, geçmeli halka dönmeye izin verir.",
        "3) Esnek parça/boolean gerektirmez: STL'de yalnız halka sektörü; FDM'de 0,2 mm boşlukla basılabilir.",
        "4) Dezavantaj: 3 kulak = 3 takma konumu (120°); yön için bir kulağı farklı genişlikte yapmak gerekir (bu sürümde",
        "   YAPILMADI). Gevşemeye karşı çentik/sürtünme ve su dayanımı (o-ring) sonraki sürüme bırakıldı.",
    ]
    for i, t in enumerate(ger):
        sh.text(GX, 70 - i * 3.6, t, 2.15)
    return sh


if __name__ == "__main__":
    os.makedirs(SVG_DIR, exist_ok=True); os.makedirs(PNG_DIR, exist_ok=True)
    import sys
    secim = sys.argv[1:] or ["01", "02", "03", "04", "05"]
    for k in secim:
        sh = globals()[f"cizim_{k}"]()
        sh.kaydet(SVG_DIR, PNG_DIR)
        for u in sh.denetle() + sh.uyarilar:
            print(f"[{sh.ad}] UYARI: {u}")
        print("tamam:", sh.ad)

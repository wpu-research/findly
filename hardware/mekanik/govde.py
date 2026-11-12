#!/usr/bin/env python3
"""Findy P1 — 3B yazdırılabilir prototip gövde (saf Python ağ üretimi).

CAD çekirdeği yok: parçalar döndürme yüzeyleri (revolve), kutular ve
sektör prizmalarından kurulur. Her KABUK ayrı ve kapalıdır; birbirine
değen/örtüşen kabuklar (ör. bayonet kulakları, halka) dilimleyicide
birleştirilir (boolean YAPILMAZ). Çıktı: ikili STL, stl/ altına.

Kullanım:  python3 govde.py
"""
import math, os, struct
import params as P

HERE = os.path.dirname(os.path.abspath(__file__))
STL_DIR = os.path.join(HERE, "stl")


class Mesh:
    """Kabuklardan oluşan üçgen ağ. Her kabuk kendi köşe noktalarını taşır."""

    def __init__(self, ad):
        self.ad = ad
        self.v = []          # köşeler
        self.t = []          # (i,j,k)
        self.kabuklar = []   # (ad, t_başlangıç, t_bitiş)

    # -- yardımcılar -------------------------------------------------
    def _bitir(self, ad, v0, t0):
        """Kabuğun hacim işaretini düzelt (negatifse yüzleri çevir)."""
        vol = 0.0
        for (a, b, c) in self.t[t0:]:
            vol += _det(self.v[a], self.v[b], self.v[c]) / 6.0
        if vol < 0:
            for n in range(t0, len(self.t)):
                a, b, c = self.t[n]
                self.t[n] = (a, c, b)
        self.kabuklar.append((ad, t0, len(self.t)))

    def _tri(self, a, b, c):
        if a == b or b == c or a == c:
            return
        self.t.append((a, b, c))

    # -- primitifler -------------------------------------------------
    def revolve(self, ad, profil, n=P.N_SEG, tx=0.0, ty=0.0, tz=0.0):
        """(r,z) profilini z ekseni etrafında döndür. r>=0. Profil basit ve kapalı."""
        # profili saat yönü tersine çevir (alan işareti)
        alan = 0.0
        for i in range(len(profil)):
            r0, z0 = profil[i]
            r1, z1 = profil[(i + 1) % len(profil)]
            alan += r0 * z1 - r1 * z0
        if alan < 0:
            profil = profil[::-1]
        v0, t0 = len(self.v), len(self.t)
        m = len(profil)
        idx = {}

        def vid(i, k):
            r, z = profil[i]
            if abs(r) < 1e-12:                 # eksen noktası: tek köşe
                key = ("p", i)
            else:
                key = (i, k % n)
            if key not in idx:
                th = 2 * math.pi * (k % n) / n
                idx[key] = len(self.v)
                self.v.append((r * math.cos(th) + tx, r * math.sin(th) + ty, z + tz))
            return idx[key]

        for i in range(m):
            j = (i + 1) % m
            for k in range(n):
                a, b = vid(i, k), vid(j, k)
                c, d = vid(j, k + 1), vid(i, k + 1)
                self._tri(a, b, c)
                self._tri(a, c, d)
        self._bitir(ad, v0, t0)

    def kutu(self, ad, x0, x1, y0, y1, z0, z1):
        v0, t0 = len(self.v), len(self.t)
        b = len(self.v)
        for z in (z0, z1):
            for (x, y) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
                self.v.append((x, y, z))
        quads = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        for q in quads:
            self._tri(b + q[0], b + q[1], b + q[2])
            self._tri(b + q[0], b + q[2], b + q[3])
        self._bitir(ad, v0, t0)

    def sektor(self, ad, r0, r1, a0, a1, z0, z1, n=P.N_SEG):
        """Halka sektörü prizması; açılar n-dilim ızgarasına oturur (derece)."""
        k0 = round(a0 / 360.0 * n)
        k1 = round(a1 / 360.0 * n)
        assert abs(k0 * 360.0 / n - a0) < 1e-6 and abs(k1 * 360.0 / n - a1) < 1e-6, (a0, a1)
        v0, t0 = len(self.v), len(self.t)
        ks = list(range(k0, k1 + 1))
        # köşe tabloları: [halka(0 dış,1 iç)][z(0,1)][k]
        id_ = {}
        for ri, r in enumerate((r1, r0)):
            for zi, z in enumerate((z0, z1)):
                for k in ks:
                    th = 2 * math.pi * k / n
                    id_[(ri, zi, k)] = len(self.v)
                    self.v.append((r * math.cos(th), r * math.sin(th), z))
        for k in ks[:-1]:
            kk = k + 1
            O = lambda zi, q: id_[(0, zi, q)]
            I = lambda zi, q: id_[(1, zi, q)]
            # dış yüz
            self._tri(O(0, k), O(0, kk), O(1, kk)); self._tri(O(0, k), O(1, kk), O(1, k))
            # iç yüz
            self._tri(I(0, k), I(1, kk), I(0, kk)); self._tri(I(0, k), I(1, k), I(1, kk))
            # üst
            self._tri(O(1, k), O(1, kk), I(1, kk)); self._tri(O(1, k), I(1, kk), I(1, k))
            # alt
            self._tri(O(0, k), I(0, kk), O(0, kk)); self._tri(O(0, k), I(0, k), I(0, kk))
        # uç kapakları
        for k, s in ((ks[0], 1), (ks[-1], -1)):
            a, b, c, d = id_[(0, 0, k)], id_[(0, 1, k)], id_[(1, 1, k)], id_[(1, 0, k)]
            if s == 1:
                self._tri(a, b, c); self._tri(a, c, d)
            else:
                self._tri(a, c, b); self._tri(a, d, c)
        self._bitir(ad, v0, t0)

    # -- çıktı -------------------------------------------------------
    def yaz_stl(self, yol):
        with open(yol, "wb") as f:
            f.write((self.ad + " - Findy P1 konsept prototip").encode("ascii", "replace")[:80].ljust(80, b" "))
            f.write(struct.pack("<I", len(self.t)))
            for (a, b, c) in self.t:
                A, B, C = self.v[a], self.v[b], self.v[c]
                u = (B[0]-A[0], B[1]-A[1], B[2]-A[2]); w = (C[0]-A[0], C[1]-A[1], C[2]-A[2])
                nx, ny, nz = (u[1]*w[2]-u[2]*w[1], u[2]*w[0]-u[0]*w[2], u[0]*w[1]-u[1]*w[0])
                L = math.sqrt(nx*nx + ny*ny + nz*nz) or 1.0
                f.write(struct.pack("<3f", nx/L, ny/L, nz/L))
                for p in (A, B, C):
                    f.write(struct.pack("<3f", *p))
                f.write(b"\0\0")


def _det(a, b, c):
    return (a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0]) + a[2]*(b[0]*c[1]-b[1]*c[0]))


# ------------------------------------------------------------------ profiller
def profil_alt():
    R, H, c = P.R_DIS, P.ALT_H, P.ALT_KAMFER
    return [(0, 0), (R - c, 0), (R, c), (R, H), (P.R_IC, H),
            (P.R_IC, P.KALINLIK["arka"]), (0, P.KALINLIK["arka"])]


def profil_ust():
    R, z0, h = P.R_DIS, P.AYRIM_Z, P.TOPLAM
    z_kornis_alt = P.Z["cam"][0] - P.KORNIS_KAL
    return [(P.R_IC, z0), (R, z0), (R, h),
            (P.ISIK_R1, h), (P.ISIK_R1, h - P.ISIK_DERINLIK),
            (P.ISIK_R0, h - P.ISIK_DERINLIK), (P.ISIK_R0, h),
            (P.CAM_YUVA_D / 2, h), (P.CAM_YUVA_D / 2, P.Z["cam"][0]),
            (P.KORNIS_D / 2, P.Z["cam"][0]), (P.KORNIS_D / 2, z_kornis_alt),
            (P.R_IC, z_kornis_alt)]


def profil_tus():
    L = P.TUS_BOY
    c = 0.3
    return [(0, 0), (P.TUS_FLANS_R, 0), (P.TUS_FLANS_R, P.TUS_FLANS_KAL),
            (P.TUS_GOVDE_R, P.TUS_FLANS_KAL), (P.TUS_GOVDE_R, L - P.TUS_BAS_UZ),
            (P.TUS_BAS_R, L - P.TUS_BAS_UZ), (P.TUS_BAS_R, L - c),
            (P.TUS_BAS_R - c, L), (0, L)]


def profil_aparat():
    return [(P.AP_TABAN_DELIK_R, 0), (P.AP_R_DIS, 0), (P.AP_R_DIS, P.AP_H),
            (P.AP_R_IC, P.AP_H), (P.AP_R_IC, P.AP_TABAN), (P.AP_TABAN_DELIK_R, P.AP_TABAN)]


def _kulak_aralik(orta, gen):
    n = P.N_SEG
    adim = 360.0 / n
    a0 = round((orta - gen / 2) / adim) * adim
    a1 = round((orta + gen / 2) / adim) * adim
    return a0, a1


def modul_kulaklari(m):
    for i, a in enumerate(P.kulak_acilari()):
        a0, a1 = _kulak_aralik(a, P.BYN_KULAK_GEN)
        m.sektor(f"bayonet_kulak_{i+1}", P.R_DIS, P.R_DIS + P.BYN_KULAK_RAD, a0, a1,
                 P.BYN_KULAK_Z0, P.BYN_KULAK_Z0 + P.BYN_KULAK_KAL)


def aparat_kulaklari(m):
    # aparat kulakları: modül kulağının KİLİT konumunda (BYN_DONUS saat yönü tersi) üstünde
    for i, a in enumerate(P.kulak_acilari()):
        orta = a + P.BYN_DONUS + P.BYN_AP_KULAK_GEN / 2 - P.BYN_KULAK_GEN / 2
        a0, a1 = _kulak_aralik(orta, P.BYN_AP_KULAK_GEN)
        m.sektor(f"aparat_kulak_{i+1}", P.AP_KULAK_R_IC, P.AP_R_IC, a0, a1,
                 P.AP_KULAK_Z0, P.AP_KULAK_Z0 + P.AP_KULAK_KAL)


# ------------------------------------------------------------------ parçalar
def alt():
    m = Mesh("govde-alt")
    m.revolve("kap_ve_arka_kapak", profil_alt())
    modul_kulaklari(m)
    return m


def ust():
    m = Mesh("govde-ust-cerceve")
    m.revolve("ust_cerceve", profil_ust())
    return m


def tus():
    m = Mesh("tus")
    m.revolve("tus", profil_tus())
    return m


def _halka(m, ad, cx, cy, r_ic, r_dis, z0, z1):
    m.revolve(ad, [(r_ic, 0), (r_dis, 0), (r_dis, z1 - z0), (r_ic, z1 - z0)], tx=cx, ty=cy, tz=z0)


def aparat_anahtarlik():
    m = Mesh("aparat-anahtarlik")
    m.revolve("aparat_kap", profil_aparat())
    aparat_kulaklari(m)
    _halka(m, "anahtarlik_halkasi", 0.0, P.HALKA_MERKEZ_Y, P.HALKA_IC_R, P.HALKA_DIS_R, 0, P.HALKA_KAL)
    return m


def _ayak_y0():
    return math.sqrt(P.AP_R_IC ** 2 - P.BANT_AYAK_IC ** 2) + 0.1   # iç yüzü duvar içinde kalır


def aparat_kolbandi():
    m = Mesh("aparat-kolbandi")
    m.revolve("aparat_kap", profil_aparat())
    aparat_kulaklari(m)
    xi, xo = P.BANT_AYAK_IC, P.BANT_AYAK_IC + P.BANT_AYAK_KAL
    for sy in (1, -1):
        y_in = sy * _ayak_y0()                   # duvar içine gömülü başlangıç
        y_out = sy * P.BANT_BAR_Y1
        y0, y1 = min(y_in, y_out), max(y_in, y_out)
        for sx in (1, -1):
            x0, x1 = sorted((sx * xi, sx * xo))
            m.kutu(f"bant_ayak_{'+' if sx>0 else '-'}x_{'+' if sy>0 else '-'}y", x0, x1, y0, y1, 0, P.BANT_YUKSEK)
        b0, b1 = sorted((sy * P.BANT_BAR_Y0, sy * P.BANT_BAR_Y1))
        m.kutu(f"bant_bar_{'+' if sy>0 else '-'}y", -(xo - 0.5), xo - 0.5, b0, b1, 0, P.BANT_YUKSEK)
    return m


PARCALAR = {
    "govde-alt": alt,
    "govde-ust-cerceve": ust,
    "tus": tus,
    "aparat-anahtarlik": aparat_anahtarlik,
    "aparat-kolbandi": aparat_kolbandi,
}


# ------------------------------------------------------------------ beklenen değerler (dogrula.py kullanır)
def _pappus(profil):
    """Profilin döndürme hacmi (analitik, çokgen düzeltmesiz)."""
    s = 0.0
    m = len(profil)
    for i in range(m):
        r0, z0 = profil[i]; r1, z1 = profil[(i + 1) % m]
        s += (r0 + r1) * (r0 * z1 - r1 * z0)
    return abs(2 * math.pi * s / 6.0)


def _poli_duzelt(n=P.N_SEG):
    # n-gen alanı / daire alanı
    return n * math.sin(2 * math.pi / n) / (2 * math.pi)


def _sektor_hacim(r0, r1, a0, a1, h):
    return 0.5 * (r1 ** 2 - r0 ** 2) * math.radians(a1 - a0) * h


def beklenen():
    """Her parça için: bbox (min,max) ve yaklaşık hacim — params'tan analitik."""
    n = P.N_SEG
    dz = _poli_duzelt(n)
    out = {}
    # ortak: kulak sektörleri
    def kulak_xy(rr, orta, gen, kos=None):
        pts = []
        for a in (orta - gen / 2, orta + gen / 2):
            for r in rr:
                pts.append((r * math.cos(math.radians(a)), r * math.sin(math.radians(a))))
        return pts

    def bbox_xy(daire_r, extra):
        xs = [daire_r, -daire_r] + [p[0] for p in extra]
        ys = [daire_r, -daire_r] + [p[1] for p in extra]
        return (min(xs), min(ys)), (max(xs), max(ys))

    # alt
    ex = []
    for a in P.kulak_acilari():
        a0, a1 = _kulak_aralik(a, P.BYN_KULAK_GEN)
        for aa in (a0, a1):
            ex.append(((P.R_DIS + P.BYN_KULAK_RAD) * math.cos(math.radians(aa)),
                       (P.R_DIS + P.BYN_KULAK_RAD) * math.sin(math.radians(aa))))
        # yay üzerindeki uç değerler (eksen kesişimi 90° katları kulak içindeyse)
        for ax in (0, 90, 180, 270, 360):
            if a0 <= ax <= a1:
                ex.append(((P.R_DIS + P.BYN_KULAK_RAD) * math.cos(math.radians(ax)),
                           (P.R_DIS + P.BYN_KULAK_RAD) * math.sin(math.radians(ax))))
    lo, hi = bbox_xy(P.R_DIS, ex)
    vol = _pappus(profil_alt()) * dz
    for a in P.kulak_acilari():
        a0, a1 = _kulak_aralik(a, P.BYN_KULAK_GEN)
        vol += _sektor_hacim(P.R_DIS, P.R_DIS + P.BYN_KULAK_RAD, a0, a1, P.BYN_KULAK_KAL) * dz
    out["govde-alt"] = dict(min=(lo[0], lo[1], 0.0), max=(hi[0], hi[1], P.ALT_H), hacim=vol)
    # üst çerçeve
    out["govde-ust-cerceve"] = dict(min=(-P.R_DIS, -P.R_DIS, P.AYRIM_Z), max=(P.R_DIS, P.R_DIS, P.TOPLAM),
                                    hacim=_pappus(profil_ust()) * dz)
    # tuş
    r = P.TUS_FLANS_R
    out["tus"] = dict(min=(-r, -r, 0.0), max=(r, r, P.TUS_BOY), hacim=_pappus(profil_tus()) * dz)
    # aparat ortak
    def aparat_kulak_ex():
        ex2, vol2 = [], 0.0
        for a in P.kulak_acilari():
            orta = a + P.BYN_DONUS + P.BYN_AP_KULAK_GEN / 2 - P.BYN_KULAK_GEN / 2
            a0, a1 = _kulak_aralik(orta, P.BYN_AP_KULAK_GEN)
            vol2 += _sektor_hacim(P.AP_KULAK_R_IC, P.AP_R_IC, a0, a1, P.AP_KULAK_KAL) * dz
        return vol2
    base_v = _pappus(profil_aparat()) * dz + aparat_kulak_ex()
    # anahtarlık: halka merkezi y
    hv = math.pi * (P.HALKA_DIS_R ** 2 - P.HALKA_IC_R ** 2) * P.HALKA_KAL * dz
    ymax = P.HALKA_MERKEZ_Y + P.HALKA_DIS_R
    out["aparat-anahtarlik"] = dict(min=(-P.AP_R_DIS, -P.AP_R_DIS, 0.0),
                                    max=(P.AP_R_DIS, ymax, max(P.AP_H, P.HALKA_KAL)), hacim=base_v + hv)
    # kol bandı
    xo = P.BANT_AYAK_IC + P.BANT_AYAK_KAL
    ay = (P.BANT_BAR_Y1 - _ayak_y0())
    kv = 4 * P.BANT_AYAK_KAL * ay * P.BANT_YUKSEK + 2 * (2 * (xo - 0.5)) * (P.BANT_BAR_Y1 - P.BANT_BAR_Y0) * P.BANT_YUKSEK
    out["aparat-kolbandi"] = dict(min=(-xo if xo > P.AP_R_DIS else -P.AP_R_DIS, -P.BANT_BAR_Y1, 0.0),
                                  max=(xo if xo > P.AP_R_DIS else P.AP_R_DIS, P.BANT_BAR_Y1, P.AP_H), hacim=base_v + kv)
    return out


def main():
    os.makedirs(STL_DIR, exist_ok=True)
    P.toplam_kontrol()
    for ad, fn in PARCALAR.items():
        m = fn()
        yol = os.path.join(STL_DIR, ad + ".stl")
        m.yaz_stl(yol)
        print(f"{ad:22s} {len(m.v):6d} köşe {len(m.t):6d} üçgen {len(m.kabuklar)} kabuk -> {os.path.relpath(yol, HERE)}")


if __name__ == "__main__":
    main()

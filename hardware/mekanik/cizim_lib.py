"""Küçük teknik resim kütüphanesi: aynı geometriden SVG (mm ölçekli) ve
matplotlib PNG üretir. Sayfa koordinatları mm, y YUKARI. Standart:
açık zemin, siyah çizgi, Türkçe etiket."""
import math
from xml.sax.saxutils import escape
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
import params as P

matplotlib.rcParams["lines.scale_dashes"] = False
matplotlib.rcParams["font.family"] = "DejaVu Sans"
_FP = FontProperties(family="DejaVu Sans")
_FPB = FontProperties(family="DejaVu Sans", weight="bold")
FONT = "DejaVu Sans, Arial, Helvetica, sans-serif"
KAGIT = "#fdfdfb"
DASHES = {None: None, "dash": (2.4, 1.0), "dashdot": (6.0, 1.0, 1.0, 1.0), "dot": (0.6, 1.0), "uzun": (5.0, 1.5)}


def fmt(v, d=2):
    return P.fmt(v, d)


def text_olcu(s, size, bold=False):
    if not s:
        return 0.0
    tp = TextPath((0, 0), s, size=size, prop=_FPB if bold else _FP)
    bb = tp.get_extents()
    return bb.x1


def _icinde(pt, poly):
    x, y = pt
    c = False
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]; x1, y1 = poly[(i + 1) % n]
        if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0) + x0:
            c = not c
    return c


def tarama_cizgileri(poly, aci, aralik):
    """Çokgeni kırpılmış paralel çizgiler (başlangıç/bitiş çiftleri)."""
    a = math.radians(aci)
    d = (math.cos(a), math.sin(a)); n = (-math.sin(a), math.cos(a))
    cs = [p[0] * n[0] + p[1] * n[1] for p in poly]
    k0, k1 = math.floor(min(cs) / aralik), math.ceil(max(cs) / aralik)
    out = []
    for k in range(k0, k1 + 1):
        c = k * aralik + 1e-7
        ts = []
        m = len(poly)
        for i in range(m):
            p, q = poly[i], poly[(i + 1) % m]
            sp = p[0] * n[0] + p[1] * n[1] - c
            sq = q[0] * n[0] + q[1] * n[1] - c
            if (sp < 0) != (sq < 0):
                tp = p[0] * d[0] + p[1] * d[1]
                tq = q[0] * d[0] + q[1] * d[1]
                ts.append(tp + (tq - tp) * sp / (sp - sq))
        ts.sort()
        for i in range(0, len(ts) - 1, 2):
            t0, t1 = ts[i], ts[i + 1]
            out.append(((c * n[0] + t0 * d[0], c * n[1] + t0 * d[1]),
                        (c * n[0] + t1 * d[0], c * n[1] + t1 * d[1])))
    return out


class Sheet:
    def __init__(self, W=420.0, H=297.0, ad="cizim"):
        self.W, self.H, self.ad = W, H, ad
        self.els = []
        self.metinler = []   # (bbox, metin)
        self.uyarilar = []

    # ---- ilkel elemanlar (sayfa mm, y yukarı) ----
    def line(self, pts, lw=0.25, dash=None):
        self.els.append(("line", [tuple(p) for p in pts], lw, dash))

    def poly(self, pts, lw=0.35, fill=None, hatch=None, hs=1.2, attrs=None):
        pts = [tuple(p) for p in pts]
        self.els.append(("poly", pts, lw, fill, attrs))
        if hatch:
            self.hatch(pts, hatch, hs)

    def hatch(self, pts, tur, hs=1.2):
        lw = 0.13
        if tur in ("d45", "cross"):
            for a, b in tarama_cizgileri(pts, 45, hs):
                self.line([a, b], lw)
        if tur in ("d135", "cross"):
            for a, b in tarama_cizgileri(pts, 135, hs):
                self.line([a, b], lw)
        if tur == "h":
            for a, b in tarama_cizgileri(pts, 0, hs):
                self.line([a, b], lw)
        if tur == "v":
            for a, b in tarama_cizgileri(pts, 90, hs):
                self.line([a, b], lw)
        if tur == "dots":
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            x = math.floor(min(xs) / hs) * hs
            while x < max(xs):
                y = math.floor(min(ys) / hs) * hs
                while y < max(ys):
                    if _icinde((x + hs / 2, y + hs / 2), pts):
                        self.els.append(("dot", (x + hs / 2, y + hs / 2), 0.16))
                    y += hs
                x += hs

    def circle(self, cx, cy, r, lw=0.3, dash=None, fill=None):
        self.els.append(("circle", cx, cy, r, lw, dash, fill))

    def arc(self, cx, cy, r, a0, a1, lw=0.3, dash=None, rx=None, ry=None):
        rx = r if rx is None else rx
        ry = r if ry is None else ry
        n = max(8, int(abs(a1 - a0) / 2))
        pts = [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
                cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
        self.line(pts, lw, dash)
        return pts

    def dot(self, x, y, r=0.5):
        self.els.append(("circle", x, y, r, 0.1, None, "#000"))

    def grup(self, attrs=None):
        self.els.append(("g0", attrs or {}))

    def grup_bitir(self):
        self.els.append(("g1",))

    def text(self, x, y, s, size=2.8, anchor="start", rot=0.0, bold=False, valign="baseline", kayit=True):
        """valign: 'baseline' | 'center'. rot derece (CCW)."""
        yb = y
        xb = x
        if valign == "center":
            sh = -0.36 * size
            xb = x - sh * math.sin(math.radians(rot))
            yb = y + sh * math.cos(math.radians(rot))
        self.els.append(("text", xb, yb, s, size, anchor, rot, bold))
        if kayit:
            w = text_olcu(s, size, bold)
            h = size
            if anchor == "start":
                x0, x1 = 0, w
            elif anchor == "middle":
                x0, x1 = -w / 2, w / 2
            else:
                x0, x1 = -w, 0
            c = [(x0, -0.22 * size), (x1, -0.22 * size), (x1, 0.78 * size), (x0, 0.78 * size)]
            a = math.radians(rot)
            pts = [(xb + px * math.cos(a) - py * math.sin(a), yb + px * math.sin(a) + py * math.cos(a)) for px, py in c]
            bb = (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))
            self.metinler.append((bb, s))
        return w if kayit else 0

    def kutulu_metin(self, x, y, s, size=2.8, anchor="start"):
        w = text_olcu(s, size)
        x0 = x if anchor == "start" else (x - w / 2 if anchor == "middle" else x - w)
        self.els.append(("poly", [(x0 - 0.6, y - 0.8), (x0 + w + 0.6, y - 0.8), (x0 + w + 0.6, y + size + 0.0), (x0 - 0.6, y + size + 0.0)], 0.0, KAGIT, None))
        self.text(x, y, s, size, anchor)

    # ---- ölçülendirme ----
    def ok(self, tip, dirx, diry, boy=2.2, gen=0.75):
        """tip=(x,y) ok ucu; (dirx,diry) okun işaret ettiği yön."""
        L = math.hypot(dirx, diry); dx, dy = dirx / L, diry / L
        bx, by = tip[0] - dx * boy, tip[1] - dy * boy
        self.els.append(("poly", [tip, (bx - dy * gen, by + dx * gen), (bx + dy * gen, by - dx * gen)], 0.05, "#000", None))

    def olcu(self, p1, p2, off, metin, side=1, size=2.5, tpos=0.5, tshift=0.0, dis_ok=None, ext=1.5, gap=0.8, dik_metin=None):
        """Doğrusal ölçü (sayfa mm). off: ölçü çizgisinin ofseti (mm, 'side' yönünde).
        p1->p2 yönünün SOL normali * side. tpos: metin konumu çizgi boyunca (0..1)."""
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        L = math.hypot(dx, dy)
        d = (dx / L, dy / L)
        n = (-d[1] * side, d[0] * side)
        a = (p1[0] + n[0] * off, p1[1] + n[1] * off)
        b = (p2[0] + n[0] * off, p2[1] + n[1] * off)
        sg = 1 if off >= 0 else -1
        for p, q in ((p1, a), (p2, b)):
            s = (p[0] + n[0] * gap * sg, p[1] + n[1] * gap * sg)
            e = (q[0] + n[0] * ext * sg, q[1] + n[1] * ext * sg)
            self.line([s, e], 0.15)
        if dis_ok is None:
            dis_ok = L < 7.5
        if dis_ok:
            self.line([(a[0] - d[0] * 4.5, a[1] - d[1] * 4.5), (b[0] + d[0] * 4.5, b[1] + d[1] * 4.5)], 0.15)
            self.ok(a, d[0], d[1]); self.ok(b, -d[0], -d[1])
        else:
            self.line([a, b], 0.15)
            self.ok(a, -d[0], -d[1]); self.ok(b, d[0], d[1])
        # metin
        mx, my = a[0] + (b[0] - a[0]) * tpos, a[1] + (b[1] - a[1]) * tpos
        ang = math.degrees(math.atan2(d[1], d[0]))
        if ang > 90 or ang <= -90:
            ang += 180
        if abs(abs(ang) - 90) < 1e-6:
            ang = 90.0
        up = (-math.sin(math.radians(ang)), math.cos(math.radians(ang)))   # metnin "üstü"
        want = (n[0] * sg, n[1] * sg)
        if up[0] * want[0] + up[1] * want[1] >= 0:
            k = 0.8 + tshift
        else:
            k = -(0.8 + tshift + 0.75 * size)
        self.text(mx + up[0] * k, my + up[1] * k, metin, size, "middle", ang)
        return (a, b)

    def lider(self, hedef, metin_xy, metin, size=2.6, anchor="start", nokta=True, bold=False, kisa=1.0):
        """hedef noktadan metne çizgi; çizgi metin tarafına yatay kısa bir ayakla biter."""
        tx, ty = metin_xy
        self.line([hedef, (tx, ty)], 0.15)
        if nokta:
            self.dot(hedef[0], hedef[1], 0.45)
        w = self.text(tx + (kisa if anchor == "start" else -kisa), ty - size * 0.3, metin, size, anchor, bold=bold)
        # alt çizgi (ayak)
        e = tx + (kisa + w if anchor == "start" else -(kisa + w))
        self.line([(tx, ty - size * 0.45), (e, ty - size * 0.45)], 0.12)
        return w

    # ---- çerçeve + başlık bloğu ----
    def cerceve(self, baslik, olcek, no, sayfa="1/1", aciklama=None):
        W, H = self.W, self.H
        self.poly([(5, 5), (W - 5, 5), (W - 5, H - 5), (5, H - 5)], 0.6)
        bw, bh = 190.0, 46.0
        x0, y0 = W - 5 - bw, 5.0
        self.poly([(x0, y0), (x0 + bw, y0), (x0 + bw, y0 + bh), (x0, y0 + bh)], 0.5, KAGIT)
        # uyarı satırı
        self.line([(x0, y0 + bh - 11), (x0 + bw, y0 + bh - 11)], 0.35)
        self.text(x0 + bw / 2, y0 + bh - 7.3, P.NOT_KONSEPT, 3.5, "middle", bold=True)
        # satır 2: proje
        self.line([(x0, y0 + bh - 20), (x0 + bw, y0 + bh - 20)], 0.25)
        self.text(x0 + 2, y0 + bh - 14.6, "PROJE", 1.8)
        self.text(x0 + 2, y0 + bh - 18.2, f"{P.PROJE} — 40 mm yuvarlak arkadaş bulma cihazı (P1 ürün konsepti)", 2.9, bold=True)
        # satır 3: çizim adı
        self.line([(x0, y0 + bh - 29), (x0 + bw, y0 + bh - 29)], 0.25)
        self.text(x0 + 2, y0 + bh - 23.0, "ÇİZİM ADI", 1.8)
        self.text(x0 + 2, y0 + bh - 27.4, baslik, 3.6, bold=True)
        # satır 4: ölçek / tarih / no / sayfa
        cols = [(0, 62, "ÖLÇEK", olcek), (62, 112, "TARİH", P.TARIH), (112, 160, "ÇİZİM NO", no), (160, 190, "SAYFA", sayfa)]
        for a, b, k, v in cols:
            self.line([(x0 + a, y0), (x0 + a, y0 + bh - 29)], 0.25)
            self.text(x0 + a + 2, y0 + bh - 32.0, k, 1.8)
            self.text(x0 + a + 2, y0 + bh - 36.4, v, 3.0 if len(v) < 24 else 2.4, bold=False)
        self.text(x0 + 2, y0 + 2.2, "Ölçüler mm. Çizen: otomatik (ciz.py). Kaynak: params.py", 2.0)
        self.keepout = (x0, y0, x0 + bw, y0 + bh)

    # ---- QA ----
    def denetle(self):
        sorun = []
        m = self.metinler
        for i in range(len(m)):
            a, sa = m[i]
            if a[0] < 6 or a[1] < 6 or a[2] > self.W - 6 or a[3] > self.H - 6:
                sorun.append(f"sayfa kenarına taşma: '{sa}' {tuple(round(v,1) for v in a)}")
            kx = getattr(self, "keepout", None)
            for j in range(i + 1, len(m)):
                b, sb = m[j]
                ox = min(a[2], b[2]) - max(a[0], b[0])
                oy = min(a[3], b[3]) - max(a[1], b[1])
                if ox > 0.3 and oy > 0.3:
                    sorun.append(f"metin çakışması: '{sa}' ~ '{sb}' ({ox:.1f}x{oy:.1f} mm)")
        return sorun

    # ---- çıktılar ----
    def svg(self):
        W, H = self.W, self.H
        Y = lambda y: H - y
        o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}" font-family="{FONT}">',
             f'<title>{escape(self.ad)}</title>',
             f'<rect x="0" y="0" width="{W}" height="{H}" fill="{KAGIT}"/>']
        for e in self.els:
            k = e[0]
            if k == "line":
                _, pts, lw, dash = e
                d = DASHES[dash]
                da = f' stroke-dasharray="{" ".join(str(v) for v in d)}"' if d else ""
                o.append(f'<polyline fill="none" stroke="#000" stroke-width="{lw}" stroke-linecap="round" stroke-linejoin="round"{da} points="'
                         + " ".join(f"{x:.3f},{Y(y):.3f}" for x, y in pts) + '"/>')
            elif k == "poly":
                _, pts, lw, fill, attrs = e
                at = ""
                if attrs:
                    at = "".join(f' {a}="{escape(str(v))}"' for a, v in attrs.items())
                o.append(f'<polygon fill="{fill or "none"}" stroke="#000" stroke-width="{lw}" stroke-linejoin="round"{at} points="'
                         + " ".join(f"{x:.3f},{Y(y):.3f}" for x, y in pts) + '"/>')
            elif k == "circle":
                _, cx, cy, r, lw, dash, fill = e
                d = DASHES[dash]
                da = f' stroke-dasharray="{" ".join(str(v) for v in d)}"' if d else ""
                o.append(f'<circle cx="{cx:.3f}" cy="{Y(cy):.3f}" r="{r:.3f}" fill="{fill or "none"}" stroke="#000" stroke-width="{lw}"{da}/>')
            elif k == "dot":
                _, p, r = e
                o.append(f'<circle cx="{p[0]:.3f}" cy="{Y(p[1]):.3f}" r="{r}" fill="#000"/>')
            elif k == "g0":
                at = "".join(f' {a}="{escape(str(v))}"' for a, v in e[1].items())
                o.append(f"<g{at}>")
            elif k == "g1":
                o.append("</g>")
            elif k == "text":
                _, x, y, s, size, anchor, rot, bold = e
                an = {"start": "start", "middle": "middle", "end": "end"}[anchor]
                tr = f' transform="rotate({-rot:.3f} {x:.3f} {Y(y):.3f})"' if abs(rot) > 1e-9 else ""
                wt = ' font-weight="bold"' if bold else ""
                o.append(f'<text x="{x:.3f}" y="{Y(y):.3f}" font-size="{size}" text-anchor="{an}"{wt}{tr}>{escape(s)}</text>')
        o.append("</svg>")
        return "\n".join(o)

    def png(self, yol, dpi=110):
        W, H = self.W, self.H
        fig = plt.figure(figsize=(W / 25.4, H / 25.4), dpi=dpi)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
        fig.patch.set_facecolor(KAGIT)
        pt = lambda mm: mm * 72 / 25.4
        for e in self.els:
            k = e[0]
            if k == "line":
                _, pts, lw, dash = e
                d = DASHES[dash]
                kw = {}
                if d:
                    kw["dashes"] = [pt(v) for v in d]
                ax.plot([p[0] for p in pts], [p[1] for p in pts], color="k", lw=pt(lw), solid_capstyle="round", **kw)
            elif k == "poly":
                _, pts, lw, fill, attrs = e
                ax.fill([p[0] for p in pts], [p[1] for p in pts], facecolor=fill or "none", edgecolor="k" if lw > 0 else "none", lw=pt(lw), joinstyle="round")
            elif k == "circle":
                _, cx, cy, r, lw, dash, fill = e
                d = DASHES[dash]
                c = plt.Circle((cx, cy), r, fill=bool(fill), facecolor=fill or "none", edgecolor="k", lw=pt(lw))
                if d:
                    c.set_linestyle((0, [pt(v) for v in d]))
                ax.add_patch(c)
            elif k == "dot":
                _, p, r = e
                ax.add_patch(plt.Circle(p, r, facecolor="k", edgecolor="none"))
            elif k == "text":
                _, x, y, s, size, anchor, rot, bold = e
                ha = {"start": "left", "middle": "center", "end": "right"}[anchor]
                ax.text(x, y, s, fontsize=pt(size), ha=ha, va="baseline", rotation=rot, rotation_mode="anchor",
                        fontweight="bold" if bold else "normal", color="k")
        fig.savefig(yol, dpi=dpi, facecolor=KAGIT)
        plt.close(fig)

    def kaydet(self, klasor_svg, klasor_png):
        import os
        with open(os.path.join(klasor_svg, self.ad + ".svg"), "w", encoding="utf-8") as f:
            f.write(self.svg())
        self.png(os.path.join(klasor_png, self.ad + ".png"))


class View:
    """Model (mm, y yukarı) -> sayfa: ölçek s, model orijini sayfada (ox,oy)."""

    def __init__(self, sh, ox, oy, s):
        self.sh, self.ox, self.oy, self.s = sh, ox, oy, s

    def P(self, x, y):
        return (self.ox + self.s * x, self.oy + self.s * y)

    def Ps(self, pts):
        return [self.P(x, y) for x, y in pts]

    def line(self, pts, lw=0.25, dash=None):
        self.sh.line(self.Ps(pts), lw, dash)

    def poly(self, pts, lw=0.35, fill=None, hatch=None, hs=1.2, attrs=None):
        self.sh.poly(self.Ps(pts), lw, fill, hatch, hs, attrs)

    def circle(self, cx, cy, r, lw=0.3, dash=None, fill=None):
        x, y = self.P(cx, cy)
        self.sh.circle(x, y, r * self.s, lw, dash, fill)

    def arc(self, cx, cy, r, a0, a1, lw=0.3, dash=None):
        x, y = self.P(cx, cy)
        return self.sh.arc(x, y, r * self.s, a0, a1, lw, dash)

    def olcu(self, p1, p2, off, metin=None, **kw):
        if metin is None:
            metin = fmt(math.hypot(p2[0] - p1[0], p2[1] - p1[1]))
        return self.sh.olcu(self.P(*p1), self.P(*p2), off, metin, **kw)

    def merkez_cizgisi(self, cx, cy, yaricap_x, yaricap_y=None, asiri=3.0):
        yaricap_y = yaricap_x if yaricap_y is None else yaricap_y
        x, y = self.P(cx, cy)
        self.sh.line([(x - yaricap_x * self.s - asiri, y), (x + yaricap_x * self.s + asiri, y)], 0.15, "dashdot")
        self.sh.line([(x, y - yaricap_y * self.s - asiri), (x, y + yaricap_y * self.s + asiri)], 0.15, "dashdot")


def tablo(sh, x0, y_ust, kolonlar, satirlar, satir_h=6.0, size=2.5, baslik_size=2.5, kalin_son=False):
    """kolonlar: [(baslik, genislik)], satirlar: [[metin...]]. Hücreye sığmazsa uyarı üretir."""
    W = sum(k[1] for k in kolonlar)
    H = satir_h * (len(satirlar) + 1)
    sh.poly([(x0, y_ust), (x0 + W, y_ust), (x0 + W, y_ust - H), (x0, y_ust - H)], 0.5, KAGIT)
    sh.line([(x0, y_ust - satir_h), (x0 + W, y_ust - satir_h)], 0.4)
    for i in range(1, len(satirlar)):
        sh.line([(x0, y_ust - satir_h * (i + 1)), (x0 + W, y_ust - satir_h * (i + 1))], 0.12)
    x = x0
    for ci, (b, w) in enumerate(kolonlar):
        if ci:
            sh.line([(x, y_ust), (x, y_ust - H)], 0.2)
        if text_olcu(b, baslik_size, True) > w - 2:
            sh.uyarilar.append(f"tablo başlığı sığmıyor: {b}")
        sh.text(x + 1.2, y_ust - satir_h * 0.68, b, baslik_size, bold=True)
        for ri, r in enumerate(satirlar):
            t = r[ci]
            bold = kalin_son and ri == len(satirlar) - 1
            sz = size
            while text_olcu(t, sz, bold) > w - 2.2 and sz > 1.6:
                sz -= 0.1
            if sz < size:
                sh.uyarilar.append(f"tablo hücresi küçültüldü ({sz:.1f}): {t}")
            sh.text(x + 1.2, y_ust - satir_h * (ri + 1) - satir_h * 0.68, t, sz, bold=bold)
        x += w
    return H

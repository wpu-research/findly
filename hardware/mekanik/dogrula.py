#!/usr/bin/env python3
"""Findy P1 — STL ve çizim doğrulaması.

STL: her yönlü kenar tam bir kez, ters yönlüsü tam bir kez geçmeli
     (kapalı + tutarlı yönlü), kabuk hacmi pozitif, sınır kutusu ve hacim
     params.py'dan hesaplanan beklentiyle uyumlu, normaller yüz yönüyle tutarlı.
SVG: geçerli XML; 02-kesit.svg içindeki katman gruplarının (data-katman)
     kalınlıkları toplamı params.TOPLAM ile eşit.
Çıkış kodu 0 = hepsi geçti.
"""
import glob, math, os, struct, sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
import params as P
import govde

HERE = os.path.dirname(os.path.abspath(__file__))
TOL = 1e-3
hatalar = []


def kontrol(ok, mesaj):
    print(("  [OK]  " if ok else "  [HATA] ") + mesaj)
    if not ok:
        hatalar.append(mesaj)


def oku_stl(yol):
    with open(yol, "rb") as f:
        f.read(80)
        n = struct.unpack("<I", f.read(4))[0]
        tris = []
        for _ in range(n):
            d = struct.unpack("<12fH", f.read(50))
            tris.append((d[0:3], (d[3:6], d[6:9], d[9:12])))
    return tris


def stl_dogrula(ad, beklenen):
    yol = os.path.join(HERE, "stl", ad + ".stl")
    print(f"{ad}.stl")
    kontrol(os.path.exists(yol), "dosya var")
    tris = oku_stl(yol)
    # köşe birleştirme (float32 -> 1e-5 mm yuvarlama)
    ids, nokta = {}, []
    def vid(p):
        k = tuple(round(c, 4) for c in p)
        if k not in ids:
            ids[k] = len(nokta); nokta.append(k)
        return ids[k]
    T = [tuple(vid(p) for p in t[1]) for t in tris]
    # 1) yönlü kenar sayımı
    yk = Counter()
    for a, b, c in T:
        for e in ((a, b), (b, c), (c, a)):
            yk[e] += 1
    cift_yon = [e for e, n in yk.items() if n > 1]
    kontrol(not cift_yon, f"hiçbir yönlü kenar 2 kez geçmiyor ({len(cift_yon)} ihlal)")
    sinir = [e for e in yk if (e[1], e[0]) not in yk]
    kontrol(not sinir, f"her kenar tam 2 üçgence, zıt yönlerde paylaşılıyor ({len(sinir)} açık kenar)")
    topl = sum(yk.values())
    kontrol(topl % 3 == 0 and len(yk) * 1 == topl, f"kenar kullanımı tutarlı ({len(yk)} yönlü kenar, {len(T)} üçgen)")
    # 2) dejenere üçgen
    dej = sum(1 for a, b, c in T if len({a, b, c}) < 3)
    kontrol(dej == 0, f"dejenere üçgen yok ({dej})")
    # 3) normal tutarlılığı
    kotu = 0
    for n, (A, B, C) in tris:
        u = [B[i] - A[i] for i in range(3)]; w = [C[i] - A[i] for i in range(3)]
        cr = (u[1]*w[2]-u[2]*w[1], u[2]*w[0]-u[0]*w[2], u[0]*w[1]-u[1]*w[0])
        L = math.sqrt(sum(c*c for c in cr))
        if L < 1e-9:
            continue
        if sum(cr[i] * n[i] for i in range(3)) / L < 0.999:
            kotu += 1
    kontrol(kotu == 0, f"kayıtlı normaller sargı yönüyle tutarlı ({kotu} uyumsuz)")
    # 4) hacim (işaretli) ve bağlı bileşen başına yönelim
    vol = 0.0
    for a, b, c in T:
        A, B, C = nokta[a], nokta[b], nokta[c]
        vol += (A[0]*(B[1]*C[2]-B[2]*C[1]) - A[1]*(B[0]*C[2]-B[2]*C[0]) + A[2]*(B[0]*C[1]-B[1]*C[0])) / 6.0
    kontrol(vol > 0, f"toplam işaretli hacim pozitif ({vol:.1f} mm³)")
    # kabuk (bağlı bileşen) başına hacim
    ebeveyn = list(range(len(nokta)))
    def bul(x):
        while ebeveyn[x] != x:
            ebeveyn[x] = ebeveyn[ebeveyn[x]]; x = ebeveyn[x]
        return x
    for a, b, c in T:
        ebeveyn[bul(a)] = bul(b); ebeveyn[bul(b)] = bul(c)
    hk = defaultdict(float)
    for a, b, c in T:
        A, B, C = nokta[a], nokta[b], nokta[c]
        hk[bul(a)] += (A[0]*(B[1]*C[2]-B[2]*C[1]) - A[1]*(B[0]*C[2]-B[2]*C[0]) + A[2]*(B[0]*C[1]-B[1]*C[0])) / 6.0
    kontrol(all(v > 0 for v in hk.values()), f"{len(hk)} bağlı kabuğun hepsi pozitif hacimli")
    # 5) sınır kutusu
    mn = [min(p[i] for p in nokta) for i in range(3)]
    mx = [max(p[i] for p in nokta) for i in range(3)]
    for i, eks in enumerate("xyz"):
        kontrol(abs(mn[i] - beklenen["min"][i]) < TOL and abs(mx[i] - beklenen["max"][i]) < TOL,
                f"sınır kutusu {eks}: [{mn[i]:.3f}, {mx[i]:.3f}] beklenen [{beklenen['min'][i]:.3f}, {beklenen['max'][i]:.3f}]")
    # 6) hacim (çokgen yaklaşıklığı içinde analitik beklenti; örtüşen kabuklar iki kez sayılır)
    oran = vol / beklenen["hacim"]
    kontrol(abs(oran - 1) < 0.01, f"hacim analitik beklentiyle uyumlu (oran {oran:.4f}, beklenen {beklenen['hacim']:.1f})")


def svg_dogrula():
    print("SVG çizimler")
    dosyalar = sorted(glob.glob(os.path.join(HERE, "cizimler", "*.svg")))
    kontrol(len(dosyalar) >= 5, f"{len(dosyalar)} SVG bulundu")
    for d in dosyalar:
        try:
            ET.parse(d)
            kontrol(True, f"geçerli XML: {os.path.basename(d)}")
        except ET.ParseError as e:
            kontrol(False, f"XML hatası {os.path.basename(d)}: {e}")
    yol = os.path.join(HERE, "cizimler", "02-kesit.svg")
    if not os.path.exists(yol):
        kontrol(False, "02-kesit.svg yok"); return
    ns = {"s": "http://www.w3.org/2000/svg"}
    kok = ET.parse(yol).getroot()
    toplam, adlar = 0.0, []
    for g in kok.iter("{http://www.w3.org/2000/svg}g"):
        k = g.get("data-katman")
        if k:
            z0, z1 = float(g.get("data-z0")), float(g.get("data-z1"))
            toplam += z1 - z0
            adlar.append(k)
            if k in P.KALINLIK:
                kontrol(abs((z1 - z0) - P.KALINLIK[k]) < 1e-9, f"kesit katmanı '{k}' kalınlığı {z1-z0:.3f} = params {P.KALINLIK[k]}")
    kontrol(sorted(adlar) == sorted(P.KALINLIK), f"kesitte tüm katmanlar var ({len(adlar)}/{len(P.KALINLIK)})")
    kontrol(abs(toplam - P.TOPLAM) < 1e-9, f"kesit katman toplamı {toplam:.3f} = params.TOPLAM {P.TOPLAM}")
    # kesit geometrisinin gerçekten çizildiğini de doğrula: gruptaki ilk çokgenin z aralığı
    for g in kok.iter("{http://www.w3.org/2000/svg}g"):
        if g.get("data-katman") and g.get("data-olcek"):
            s = float(g.get("data-olcek")); oy = float(g.get("data-oy"))  # sayfa y = oy - s*z (SVG y aşağı)
            ys = []
            for pl in g.iter("{http://www.w3.org/2000/svg}polygon"):
                for pt in pl.get("points").split():
                    ys.append(float(pt.split(",")[1]))
            if ys:
                z0c, z1c = (oy - max(ys)) / s, (oy - min(ys)) / s
                z0, z1 = float(g.get("data-z0")), float(g.get("data-z1"))
                kontrol(abs(z0c - z0) < 0.01 and abs(z1c - z1) < 0.01,
                        f"  çizilen çokgen z aralığı ({g.get('data-katman')}): {z0c:.2f}..{z1c:.2f}")


def main():
    P.toplam_kontrol()
    print(f"params: yığın toplamı {P.TOPLAM} mm (hedef <= {P.TOPLAM_HEDEF_MAX})")
    bek = govde.beklenen()
    for ad in govde.PARCALAR:
        stl_dogrula(ad, bek[ad])
    svg_dogrula()
    print()
    if hatalar:
        print(f"BAŞARISIZ: {len(hatalar)} hata"); sys.exit(1)
    print("TÜM KONTROLLER GEÇTİ")


if __name__ == "__main__":
    main()

"""Findy P1 konsept — mekanik parametreler (TEK DOĞRULUK KAYNAĞI).

Tüm ölçüler mm. Çizimler (ciz.py), 3B modeller (govde.py) ve doğrulama
(dogrula.py) YALNIZCA bu dosyadan beslenir.

Etiketler:
  hedef        : docs/mimari-v0.1.md bölüm 10'daki konsept hedefi
  varsayım     : bu çalışmada mühendislik varsayımı olarak seçildi
  doğrulanacak : veri sayfası / katalog / prototip ile teyit edilmeli
Hiçbiri ölçülmüş veya doğrulanmış DEĞİLDİR.
"""
import math

PROJE = "Findy"
TARIH = "2026-11-11"
NOT_KONSEPT = "KONSEPT — ÜRETİM İÇİN DEĞİL — ölçüler hedef değerdir"

# ---------------------------------------------------------------- Katman yığını
# Üstten alta. (anahtar, Türkçe ad, kalınlık mm, etiket)
YIGIN = [
    ("cam",        "Kapak camı",                     1.0, "hedef"),
    ("panel",      "1,28\" yuvarlak TFT panel",      1.6, "hedef; doğrulanacak"),
    ("orta",       "Orta çerçeve / boşluk",          0.6, "hedef"),
    ("kart",       "Kart (PCB)",                     0.8, "hedef"),
    ("bilesen",    "Bileşenler (en yüksek: RAK4630)", 3.0, "hedef; doğrulanacak"),
    ("pil",        "LiPo pil",                       4.2, "hedef; katalogdan doğrulanacak"),
    ("arka",       "Arka kapak",                     1.2, "hedef"),
]
TOPLAM = round(sum(k[2] for k in YIGIN), 6)          # 12.4  (hedef <= 13)
TOPLAM_HEDEF_MAX = 13.0                              # hedef: kalınlık <= 13 mm

KALINLIK = {k[0]: k[2] for k in YIGIN}
AD = {k[0]: k[1] for k in YIGIN}

def _z_hesapla():
    """Z koordinatları: arka kapak dış yüzü z=0, cam üst yüzü z=TOPLAM."""
    z, d = 0.0, {}
    for anahtar, _ad, t, _e in reversed(YIGIN):
        d[anahtar] = (round(z, 6), round(z + t, 6))
        z += t
    return d
Z = _z_hesapla()

# ---------------------------------------------------------------- Dış gövde
D_DIS = 40.0            # hedef: dış çap
R_DIS = D_DIS / 2
DUVAR = 1.6             # varsayım: yan duvar (3B baskı için >= 1.2 önerilir)
R_IC = R_DIS - DUVAR    # 18.4  iç boşluk yarıçapı
ALT_KAMFER = 0.8        # varsayım: arka alt kenar pah
ALT_H = Z["bilesen"][1]             # alt gövde yüksekliği (arka kapak+pil+bileşen) = 8.4
UST_H = round(TOPLAM - ALT_H, 6)    # üst çerçeve yüksekliği = 4.0
AYRIM_Z = ALT_H                     # alt gövde / üst çerçeve ayrım düzlemi
BIRLESIM = "yapıştırma / ultrasonik kaynak (varsayım; vida yuvası YOK)"

# ---------------------------------------------------------------- Ekran / cam
EKRAN_AKTIF_D = 32.4    # 1,28" yuvarlak panel aktif alan — TİPİK, panel veri sayfasıyla doğrulanacak
PANEL_D = 33.0          # varsayım: panel modül dış çapı (doğrulanacak)
CAM_D = 35.0            # varsayım: kapak camı çapı (aktif alan + ~1,3 mm kenar)
CAM_YUVA_D = 35.2       # varsayım: üst çerçevedeki cam yuvası (0,1 mm yan boşluk)
KORNIS_D = 33.6         # varsayım: cam altı oturma kenarı iç çapı (panel Ø33 + 0,3 boşluk)
KORNIS_KAL = 0.6        # varsayım: oturma kenarı kalınlığı
ISIK_R0 = 18.4          # varsayım: lime ışık halkası oluğu iç yarıçap
ISIK_R1 = 19.2          # varsayım: dış yarıçap  (genişlik 0,8)
ISIK_DERINLIK = 0.5     # varsayım
ISIK_RENK = "#C6FF3D"   # spec bölüm 7

# ---------------------------------------------------------------- Kart (PCB)
KART_D = 36.0           # hedef/varsayım: ~36 mm yuvarlak kart
R_KART = KART_D / 2
# Bileşen ölçüleri (planda) — HEPSİ doğrulanacak
RAK_BOY, RAK_EN = 23.0, 15.0        # RAK4630 ≈ 15×23 mm — veri sayfasıyla doğrulanacak
GNSS_IC = 4.5                       # GNSS modül (ZOE-M8Q sınıfı 4,5×4,5) — doğrulanacak
GNSS_YAMA = 12.0                    # seramik yama anten ≈ 12×12 (12–15) — doğrulanacak
GNSS_KEEPOUT = 15.0                 # varsayım: yama etrafı toprak/keep-out kare kenarı
LSM_KENAR = 2.0                     # LSM303AGR ≈ 2×2 — doğrulanacak
PMIC_KENAR = 3.0                    # şarj/PMIC ≈ 3×3 — varsayım
MOTOR_D = 6.0                       # titreşim motoru (madeni para tipi) — varsayım/doğrulanacak
TUS_SW = (3.0, 2.6)                 # yan tuş mikro anahtar (yan basmalı) — varsayım
FPC_KON = (8.0, 2.0)                # ekran FPC konnektörü — varsayım; yükseklik doğrulanacak
PIL_KON = (3.0, 2.0)                # pil bağlantı pedi/konnektörü — varsayım

# ---------------------------------------------------------------- Pil
PIL_EN, PIL_BOY = 25.0, 30.0        # ≈ 4,2×25×30 mm sınıfı (250–300 mAh) — katalogdan doğrulanacak
PIL_KAL = KALINLIK["pil"]
PIL_KOSEGEN = math.hypot(PIL_EN, PIL_BOY)
IC_CAP = 2 * R_IC
PIL_SIGAR = PIL_KOSEGEN <= IC_CAP   # False: 25×30 dikdörtgen Ø36,8 iç boşluğa SIĞMAZ (bkz. README riskler)
PIL_ALT_EN, PIL_ALT_BOY = 22.0, 28.0   # öneri: sığan alternatif (köşegen 35,6 <= 36,8) — katalogdan doğrulanacak

# ---------------------------------------------------------------- Tuş
TUS_ACI = 0.0           # derece; üstten bakışta 0° = sağ yan (saat 3). Bant ekseni 12–6 olduğu için çakışmaz
TUS_Z = AYRIM_Z + UST_H / 2          # 10.4: üst çerçeve yan yüzü ortası (varsayım)
TUS_BAS_R = 1.7         # varsayım: tuş başı yarıçapı (Ø3,4)
TUS_BAS_UZ = 0.8        # varsayım: gövde dışına taşan kısım
TUS_GOVDE_R = 1.1       # varsayım: gövde (sap) yarıçapı
TUS_FLANS_R = 2.2       # varsayım: iç flanş yarıçapı (tutucu)
TUS_FLANS_KAL = 0.6     # varsayım
TUS_BOY = TUS_FLANS_KAL + DUVAR + TUS_BAS_UZ     # 3.0 toplam uzunluk
TUS_RENK = "#C6FF3D"

# ---------------------------------------------------------------- Aparat arayüzü: 3 kulaklı bayonet
BYN_SAYI = 3                 # varsayım
BYN_ACI0 = 60.0              # ilk kulağın orta açısı (kulaklar 60°, 180°, 300°) — tuş 0°'den kaçar
BYN_KULAK_GEN = 30.0         # modül kulağı açısal genişlik (derece) — varsayım
BYN_KULAK_RAD = 0.8          # modül kulağı radyal çıkıntı  (R20 -> R20,8) — varsayım
BYN_KULAK_Z0 = 3.0           # modül kulağı alt z (modül koordinatı) — varsayım
BYN_KULAK_KAL = 1.6          # modül kulağı yüksekliği — varsayım
BYN_DONUS = 45.0             # kilitlenme dönüş açısı (derece)
BYN_AP_KULAK_GEN = 60.0      # aparat iç kulağı açısal genişlik
BYN_YAN_BOS = 0.2            # radyal/eksenel boşluk (3B baskı toleransı önerisi 0,2–0,3)
AP_R_IC = R_DIS + BYN_KULAK_RAD + BYN_YAN_BOS     # 21.0 aparat iç yarıçap
AP_DUVAR = 1.4               # varsayım
AP_R_DIS = AP_R_IC + AP_DUVAR                     # 22.4
AP_TABAN = 1.6               # varsayım: aparat taban kalınlığı
AP_TABAN_DELIK_R = 15.0      # varsayım: tabanda Ø30 pencere (arka yüz/şarj erişimi)
AP_KULAK_R_IC = R_DIS + BYN_YAN_BOS               # 20.2 aparat iç kulak uç yarıçapı
AP_KULAK_Z0 = AP_TABAN + BYN_KULAK_Z0 + BYN_KULAK_KAL + BYN_YAN_BOS   # 6.4 (mutlak z)
AP_KULAK_KAL = 1.6
AP_H = AP_KULAK_Z0 + AP_KULAK_KAL + 0.6           # 8.6 aparat yüksekliği
MODUL_OTURMA_Z = AP_TABAN                          # modülün aparatta oturduğu z

# Anahtarlık / kolye halkası
HALKA_DIS_R = 5.0            # varsayım
HALKA_IC_R = 2.2             # varsayım (Ø4,4 delik; Ø1,5–2 split-ring teli)
HALKA_KAL = 3.0              # varsayım
HALKA_MERKEZ_Y = AP_R_DIS + 2.2   # 24.6

# Kol bandı (bant ekseni Y: saat 12–6)
BANT_EN = 20.0               # varsayım: bant genişliği
BANT_KAL = 2.0               # varsayım: bant kalınlığı
BANT_AYAK_IC = BANT_EN / 2 + 0.5       # 10.5 ayak iç yüzü (0,5 boşluk)
BANT_AYAK_KAL = 2.0
BANT_BAR_Y0 = AP_R_DIS + 2.1          # 24.5 bar iç yüzü (pencere 2,1)
BANT_BAR_Y1 = BANT_BAR_Y0 + 3.0       # 27.5
BANT_YUKSEK = 4.0

# Kolye: kopma (breakaway) kilidi hedef kuvveti
KOLYE_KOPMA_KGF = (1.0, 2.5)   # hedef aralık; doğrulanacak (test cihazıyla)

# ---------------------------------------------------------------- Ağ / baskı
N_SEG = 96                   # döndürme yüzeylerinde çevresel dilim sayısı
BASKI_MALZEME = "PETG veya PLA (prototip), gri/grafit; tuş açık yeşil/lime"
BASKI_KATMAN = 0.12          # mm önerilen katman yüksekliği
BASKI_TOLERANS = 0.2         # mm önerilen boşluk (FDM)

# ---------------------------------------------------------------- Gövde STL beklentileri
def kulak_acilari():
    return [BYN_ACI0 + i * 360.0 / BYN_SAYI for i in range(BYN_SAYI)]

def toplam_kontrol():
    assert abs(TOPLAM - 12.4) < 1e-9, TOPLAM
    assert TOPLAM <= TOPLAM_HEDEF_MAX
    assert abs(ALT_H + UST_H - TOPLAM) < 1e-9
    return True

def fmt(v, d=2):
    """Türkçe ondalık virgül, gereksiz sıfırsız."""
    s = f"{v:.{d}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s.replace(".", ",")

if __name__ == "__main__":
    toplam_kontrol()
    print("Toplam kalınlık:", TOPLAM, "mm")
    for k, (a, b) in Z.items():
        print(f"  {k:8s} z {a:5.2f} .. {b:5.2f}")
    print("Pil köşegeni", round(PIL_KOSEGEN, 2), "iç çap", IC_CAP, "sığar mı:", PIL_SIGAR)

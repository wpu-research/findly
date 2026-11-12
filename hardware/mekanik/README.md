# Findy P1 — mekanik konsept (çizimler + prototip gövde)

> **KONSEPT — ÜRETİM İÇİN DEĞİL.** Buradaki bütün ölçüler `docs/mimari-v0.1.md` bölüm 10'daki
> hedeflerden ve bu çalışmada yapılan mühendislik varsayımlarından gelir. **Hiçbiri ölçülmedi
> veya doğrulanmadı.** Yatırımcı/test materyalinde ölçülmüş değer gibi sunulmamalıdır.

Tasarım dili: grafit gövde, yuvarlak siyah cam ekran, ince lime (#C6FF3D) ışık halkası oluğu,
lime yan tuş, kol bandı + anahtarlık + kolye aparatı (aynı modül, 3 taşıma biçimi).

## Dosyalar

| Dosya | İçerik |
|---|---|
| `params.py` | **Tek doğruluk kaynağı.** Her değerin yanında hedef / varsayım / doğrulanacak etiketi. |
| `ciz.py`, `cizim_lib.py` | Teknik resim üreticisi (aynı geometriden SVG + PNG). |
| `cizimler/01-genel-gorunum.svg` | Üst / yan / alt görünüş, ana ölçüler, ana ölçüler tablosu (2:1). |
| `cizimler/02-kesit.svg` | A–A kesiti, 7 katman ölçülü ve farklı taramalı, toplam 12,4 (5:1). |
| `cizimler/03-patlatilmis.svg` | Patlatılmış görünüş, parça numaraları, parça listesi. |
| `cizimler/04-kart-yerlesim.svg` | Ø36 kartta blok yerleşim ÖNERİSİ, anten keep-out, çakışma işaretleri (4:1). |
| `cizimler/05-aparatlar.svg` | Kol bandı / anahtarlık / kolye + bayonet arayüzü (ölçülü, açılım görünümü). |
| `govde.py` (içinde `Mesh` sınıfı) | Saf Python ağ üretimi (döndürme yüzeyi, kutu, halka sektörü) → `stl/`. |
| `stl/govde-alt.stl` | Alt gövde + arka kapak + 3 bayonet kulağı. |
| `stl/govde-ust-cerceve.stl` | Üst çerçeve: cam yuvası, oturma kenarı, lime ışık halkası oluğu. |
| `stl/tus.stl` | Yan tuş (flanşlı). |
| `stl/aparat-anahtarlik.stl` | Aparat kabı + iç bayonet kulakları + anahtarlık/kolye halkası. |
| `stl/aparat-kolbandi.stl` | Aparat kabı + iç bayonet kulakları + bant ayakları ve barları (bant 20 mm). |
| `dogrula.py` | STL ve SVG doğrulaması (aşağıda). |
| `onizle_stl.py` | STL'lerin matplotlib önizlemesi. |
| `onizleme/*.png` | Her SVG'nin PNG'si (`01-…05-…`) ve `stl-*.png`, `stl-hepsi.png`. |

## Yeniden üretme

```bash
cd hardware/mekanik
python3 ciz.py          # cizimler/*.svg + onizleme/0*.png   (tek parametre dosyası: params.py)
python3 govde.py        # stl/*.stl
python3 onizle_stl.py   # onizleme/stl-*.png
python3 dogrula.py      # çıkış kodu 0 = tüm kontroller geçti
```
Gerekenler: python3, matplotlib, numpy (yalnız önizleme). OpenSCAD/CadQuery/Inkscape gerekmez.

## Temel tasarım kararları

- **Toplam kalınlık 12,4 mm** = yığın toplamı (cam 1,0 + panel 1,6 + orta çerçeve 0,6 + kart 0,8 +
  bileşenler 3,0 + pil 4,2 + arka kapak 1,2); hedef ≤ 13 mm, pay 0,6 mm. `params.TOPLAM` bu
  toplamdan **hesaplanır**; çizimler ve STL aynı değerden beslenir.
- **İki parçalı gövde:** alt gövde (arka kapak dâhil, z 0–8,4) + üst çerçeve (z 8,4–12,4).
  Birleşim yapıştırma / ultrasonik kaynak varsayımıdır; vida yuvası yok.
- **Duvar 1,6 mm** (varsayım); iç boşluk Ø36,8; kart Ø36.
- **Tuş:** yan yüzde 0° (saat 3), z = 10,4; bant ekseni 12–6 olduğu için çakışmaz.
- **Aparat arayüzü — 3 kulaklı bayonet, 45° dönüş.** Gerekçe: (1) kolye/anahtarlık çekme yükü
  radyal kulaklara biner, plastik kanca yorulması yok; (2) modül aparatta dönmez → tuş/pusula yönü
  sabit (geçmeli halka dönmeye izin verir); (3) esnek parça gerektirmez, FDM'de 0,2 mm boşlukla
  basılabilir. Çeyrek tur yerine 45° seçildi çünkü kulak aralığı 120°'dir. Ölçüler çizim 05'te.
- **Kolye:** aynı halkalı aparat; boyun ipinde çekince açılan (breakaway) kilit ayrı parça —
  çizimde sembolik, STL'si yok; hedef açılma kuvveti 1–2,5 kgf (doğrulanacak).

## Hangi ölçü hedef / varsayım / doğrulanacak

- **Hedef** (spec): Ø40, yığın katman kalınlıkları, toplam ≤ 13, pil ≈ 4,2×25×30, kart ≈ Ø36.
- **Doğrulanacak:** ekran aktif alanı Ø32,4 (*tipik*, panel veri sayfası), panel dış çapı Ø33, RAK4630
  15×23×~3,0, GNSS modülü ve yama anten, LSM303AGR, pil ölçüleri (katalog), FPC konnektör yüksekliği,
  kolye kopma kuvveti.
- **Varsayım:** duvar, pah, cam çapı Ø35, ışık halkası oluğu, tuş ölçüleri, bayonet kulak boyutları,
  aparat duvarı/tabanı, halka, bant 20×2 mm, bütün bileşen konumları (çizim 04).
`params.py` içinde her satırda etiket var.

## 3B baskı notları (prototip)

- Malzeme: PETG (dayanım) veya PLA (görsel prototip); gövde grafit/gri, tuş açık yeşil/lime.
  Işık halkası oluğu şeffaf/lime reçine veya boyayla doldurulabilir.
- Katman 0,12 mm; nozul 0,4; duvar ≥ 3 çevre. FDM boşluğu 0,2 mm (bayonet, cam yuvası), sıkı
  geçmeler için 0,1 mm denenip küçük parçalarla sınanmalıdır.
- Yönlendirme: `govde-alt` tabanı aşağı (kulaklar 0,2 mm basamak → destek gerekmeyebilir, aşağı
  bakan kulak yüzü 1,6 mm çıkıntıdır; gerekirse destek). `govde-ust-cerceve` cam yuvası aşağı
  bakacak şekilde ters çevirip basmak yüzey kalitesini artırır. `tus` flanş aşağıda. Aparatlar
  tabanı aşağı; iç kulaklar aşağı bakan yüzeydir → ince destek veya 45° pah gerekebilir.
- Dosyalar milimetre, ikili STL; her kabuk kapalıdır. Dilimleyici örtüşen kabukları birleştirmelidir
  (bkz. basitleştirmeler).

## Doğrulama (dogrula.py)

STL başına: her yönlü kenar tam bir kez ve zıt yönlüsü tam bir kez geçiyor (kapalı, tutarlı yönlü),
dejenere üçgen yok, kayıtlı normaller sargıyla tutarlı, tüm bağlı kabukların hacmi pozitif, sınır
kutusu `params.py`'dan analitik hesapla (±0,001 mm) ve hacim analitik beklentiyle (%1) uyumlu.
SVG: hepsi `xml.etree` ile ayrıştırılır; `02-kesit.svg` içindeki katman gruplarının (`data-katman`)
kalınlık toplamı `params.TOPLAM` ile ve çizilen çokgenlerin z aralığı beyan edilen aralıkla eşittir.

## Bilinen basitleştirmeler

- **Boolean yok.** Tuş deliği, USB/şarj açıklığı, vida/mandal yuvası, ışık borusu, cam kenar
  yapıştırma kanalı, pil/kart tutucu çıkıntıları ve gerçek iç kaburga modellenmedi. `tus.stl`
  gövdeye uyacak şekilde ölçülendi ama gövdede karşılığı olan **delik yok**.
- Örtüşen/değen kabuklar: bayonet kulakları ve halka/bant ayakları ayrı kapalı kabuklardır
  (duvara değer veya gömülür); dilimleyici birleştirir. Hacim bu yüzden ayrı kabuk toplamıdır.
- Orta çerçeve/boşluk yalnız çizimde (STL üretilmedi). Kart, pil, panel, cam STL değildir.
- Çevre 96 dilimlidir (çokgen yaklaşıklığı ≈ %0,07 hacim farkı).
- Kolbandı ayakları ve barları kutudur; bant yuvası ölçüleri (20 mm, pencere 2,1) varsayımdır.
- Bayonet 3 kulaklıdır → 120° aralıkla 3 takma konumu; yön için farklı genişlikli bir kulak
  yapılmadı. Gevşemeye karşı çentik/sürtünme yok.

## Açık riskler

1. **868 MHz anten:** λ/4 ≈ 86 mm; Ø36 karta sığmaz. Kartta yalnız RF besleme noktası ve alt kenar
   keep-out bandı ayrıldı; RAK4630 köşeleri bu banda giriyor. Anten kayış/askı içinde veya FPC çevre
   anteni olmak zorunda → menzil hedefini doğrudan etkiler.
2. **GNSS anteni:** seramik yama (12×12) ekran/cam altında kalıyor; keep-out köşeleri kart kenarına
   değiyor. Gökyüzü görüşü/ITO gölgesi çözülmedi (spec riski, çizim 04 işaret 1).
3. **Pil sığmıyor:** 25×30 mm dikdörtgenin köşegeni 39,05 mm > iç çap 36,8 mm. En fazla ≈ 22×28
   (köşegen 35,6) dikdörtgen sığar (`params.PIL_ALT_*`). Çizimler spec'teki 25×30 ile çizilmiş,
   uyumsuzluk açıkça işaretlenmiştir. Pil 3,0 mm bileşen katmanına 0 mm boşlukla oturuyor
   (şişme/yalıtım payı yok).
4. **Ekran FPC konnektörü** yüksekliği 0,6 mm orta çerçeve payına sığmayabilir.
5. **Su dayanımı:** conta/o-ring yeri ve tuş sızdırmazlığı tasarlanmadı; birleşim yapıştırma.
6. **Şarj yöntemi seçilmedi** (pogo / manyetik / USB-C): arka kapakta açıklık yok; aparat tabanında
   Ø30 pencere erişim için bırakıldı. PMIC kartta yalnız yer ayırdı.
7. Titreşim motoru Ø6 ile RAK4630 arası 0,1 mm; motor/tuş mıknatıs etkisi pusula için ölçülecek.
8. Aşağı sarkan/asılı kullanımda (kolye) pusula oku güvenilmezliği mekanik değil algoritma konusu
   (spec bölüm 5).

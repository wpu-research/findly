# Findy P0 — Tezgâh Prototipi Parça Listesi (BOM-P0)

Tarih: 2026-11-11 · Durum: **KONSEPT, sipariş öncesi kontrol gerekli** · Spec: `docs/mimari-v0.1.md`

Bu liste üretici/dağıtıcı belgeleriyle çapraz kontrol edilmiştir; ayrıntı ve
kaynaklar `dogrulama-notlari.md` içindedir. Fiyat yalnızca sayfada görülen ve
tarihli olarak yazılmıştır; görülemeyenler "fiyat kontrol edilecek"tir.
Hiçbir parça henüz sipariş edilmemiştir.

Adet sütunları: **1 cihaz** · **2 cihaz** (Faz 0–4 iki cihazlık deney) · **5 cihaz** (Faz 5).
Programlama/ölçüm ekipmanı ortaktır (cihaz sayısına göre çoğalmaz).

## 1. Ana modüller (cihaz başına)

| # | Parça | Üretici parça no | İşlev | 1 | 2 | 5 | Kaynak | Fiyat (2026-11-11) | Not |
|---|---|---|---|---|---|---|---|---|---|
| 1 | WisBlock Core, nRF52840 + SX1262, **868 MHz (EU868) sürümü** | RAK4631 (Arduino için bu; `RAK4631-R` aynı donanım, RUI3 yazılımlı) | MCU + BLE + LoRa | 1 | 2 | 5 | https://docs.rakwireless.com/product-categories/wisblock/rak4631/datasheet/ · https://docs.rakwireless.com/product-categories/wisblock/rak4631-r/overview/ | fiyat kontrol edilecek (RAK mağaza sayfası 429 döndü; arama özetinde $17,99–$23,99 aralığı geçti, varyant/tarih doğrulanamadı) | Sipariş sayfasında frekans varyantı ("EU868 / H" sürümü) açıkça seçilmeli. `-R` yerine standart RAK4631 tercih edilir (Arduino/PlatformIO için; `-R`'nin önyükleyici durumu DOĞRULANAMADI). Anten konektörü tipi (u.FL/IPEX) RAK4631 sayfasında DOĞRULANAMADI. |
| 2 | WisBlock Base Board 2. nesil | RAK19007 | Taban: yuvalar, şarj, 3V3, USB-C | 1 | 2 | 5 | https://docs.rakwireless.com/product-categories/wisblock/rak19007/datasheet/ | fiyat kontrol edilecek | Pil konektörü JST PHR-2 (2 mm), şarj 350 mA, USB-C. |
| 3 | WisBlock IO adaptörü | RAK13002 | SPI/I2C/GPIO/SW1'i 2,54 mm başlığa çıkarır | 1 | 2 | 5 | https://docs.rakwireless.com/product-categories/wisblock/rak13002/datasheet/ · .../quickstart/ | fiyat kontrol edilecek | Başlığın lehimli gelip gelmediği DOĞRULANAMADI; gelmezse 2,54 mm erkek header + lehim gerekir (aşağıda). |
| 4 | WisBlock GNSS modülü (u-blox ZOE-M8Q) | RAK12500 | GNSS konum + zaman | 1 | 2 | 5 | https://docs.rakwireless.com/product-categories/wisblock/rak12500/datasheet/ | fiyat kontrol edilecek | **Yuva A'ya takılır** (Yuva C'ye değil; bkz. dogrulama-notlari D/E). GNSS anteni paketle gelir mi satıcıya göre değişiyor (bir kullanım kılavuzu "1x GPS Antenna" diyor, RAK mağazası modülü tek başına listeliyor) → siparişte netleştir. Antenin aktif/pasif olduğu DOĞRULANAMADI. |
| 5 | 1,28" yuvarlak IPS TFT modül, GC9A01, 240×240, SPI | Waveshare SKU 19192 ("1.28inch LCD Module") | Ekran | 1 | 2 | 5 | https://www.waveshare.com/1.28inch-lcd-module.htm · https://www.waveshare.com/wiki/1.28inch_LCD_Module | **$14,99** (1–9 adet, sayfada görülen; 10–49: $14,39) | Pinler VCC, GND, DIN, CLK, CS, DC, RST, BL; 3,3 V/5 V; gövde Ø37,5 (40,4×37,5 mm), görünür alan Ø32,4; PH2.0 8 pin 20 cm kablo dahil (diğer ucun tipi DOĞRULANAMADI). BL pininin içinde sürücü transistör olup olmadığı DOĞRULANAMADI → `baglanti-tablosu.md` bölüm 5. Eşdeğer başka satıcı modülü de olur, pin adları satıcıya göre değişir (SDA/SCL ↔ DIN/CLK). |
| 6 | Pusula + ivmeölçer breakout (LSM303AGR) | Adafruit 4413 ("Adafruit LSM303AGR Accelerometer Magnetometer – STEMMA QT / Qwiic") | Heading, hareketsizlik | 1 | 2 | 5 | https://www.adafruit.com/product/4413 | **$12,50** (1–9; $11,25 10–99) — sayfada **stokta yok** (bildirim seçeneği) | I2C 0x19 + 0x1E, 25,4×17,7×4,6 mm, 0,1" header dahil, STEMMA QT kablosu dahil değil. VIN aralığı sayfada belirtilmemiş; 3V3'e bağlanacak. Stok yoksa aynı ürünü listeleyen bayiler: Pimoroni, The Pihut, Core Electronics, Jameco (stok/fiyat bakılmadı). |
| 7 | LiPo pil 3,7 V, korumalı, JST-PH 2 mm | Adafruit 2750 (350 mAh, 36×19,6×5,2 mm) | Besleme | 1 | 2 | 5 | https://www.adafruit.com/product/2750 | **$6,95** (1–9, stokta) | Alternatifler: Adafruit 1578 (500 mAh, 29×36×4,75, $7,95), Adafruit 1317 (150 mAh, 19,75×26,02×3,8, $5,95). Korumalı, 3,0 V'ta keser. **JST-PH (pil) ↔ PHR-2 (RAK19007) kutup sırası ters olabilir: takmadan ölç** (kırmızı = +). RAK19007 pil: 3,7 V Li-Ion, min 500 mA deşarj, 4,3 V'u geçmemeli. |
| 8 | 868 MHz LoRa anteni (u.FL/IPEX) | RAK'ın WisBlock anteni veya muadili | LoRa anten | 1 | 2 | 5 | — | fiyat kontrol edilecek | Parça numarası DOĞRULANAMADI (uydurmadım). **Antensiz verici çalıştırma.** BLE anteni de gerekebilir (RAK4631 modül sayfasında RF_BT pini var; kart üzerindeki konektör tipi DOĞRULANAMADI). |
| 9 | GNSS anteni (IPEX) | RAK12500 ile gelen / muadili | GNSS anten | 1 | 2 | 5 | https://forum.rakwireless.com/t/rak-12500-antenna-upgrade/12233 | fiyat kontrol edilecek | Dış mekân testinde başlık-GNSS için pigtail gerekebilir (forum). |

## 2. Küçük malzeme (cihaz başına)

Parça numaraları gerçek, yaygın parçalardır; **veri sayfası bu görevde okunmadı**, "öneri" olarak al ve sipariş öncesi veri sayfasıyla kontrol et.

| # | Parça | Öneri / değer | İşlev | 1 | 2 | 5 | Fiyat | Not |
|---|---|---|---|---|---|---|---|---|
| 10 | Titreşim motoru (ERM disk, 3 V) | Genel 3 V, ~10 mm disk | PING geri bildirimi | 1 | 2 | 5 | fiyat kontrol edilecek | Akımı bilinmiyor (ölçülecek; ~onlarca mA mertebesi beklenir, DOĞRULANMADI). 3,3 V'ta başlangıç torku yeterli mi denenecek. |
| 11 | N-MOSFET, mantık seviyeli (Vgs(th) < 1,5 V, Id ≥ 0,5 A) | Öneri: BSS138 (SOT-23, breadboard için breakout lazım) **veya** IRLZ44N (TO-220, breadboard'a doğrudan) | Motor sürücü Q1 | 1 | 2 | 5 | fiyat kontrol edilecek | Veri sayfası kontrolü yapılmadı; 3,3 V gate'te Rds(on) kontrol edilecek. 2N7000 gibi yüksek Vgs(th)'li parçalardan kaçın. |
| 12 | Schottky diyot | Öneri: 1N5819 (veya 1N5817) | Motor ters (flyback) diyodu D1 | 1 | 2 | 5 | fiyat kontrol edilecek | Katot +3V3 tarafı. |
| 13 | Direnç 100 Ω, ¼ W | — | R1 gate seri | 1 | 2 | 5 | fiyat kontrol edilecek | |
| 14 | Direnç 100 kΩ, ¼ W | — | R2 gate pull-down | 1 | 2 | 5 | fiyat kontrol edilecek | Açılışta/uykuda motor kapalı kalsın. |
| 15 | Kondansatör 100 µF elektrolitik (≥10 V) + 100 nF seramik | — | Motor beslemesi gevşetme | 1+1 | 2+2 | 5+5 | fiyat kontrol edilecek | Motor kalkış akımı 3V3 hattını çökertebilir (RAK19007 regülatör akım limiti sayfada yok). |
| 16 | Tuş (tact switch 6 mm) | Genel | S1 / WB_SW1 | 1 | 2 | 5 | fiyat kontrol edilecek | Dahili pull-up kullanılır, harici direnç yok. |
| 17 | Breadboard (400 delik) | Genel | Kablolama | 1 | 2 | 5 | fiyat kontrol edilecek | |
| 18 | Jumper kablo | Erkek-dişi ve erkek-erkek, 10–20 cm | RAK13002 başlığı → breadboard/modüller | ~25 | ~50 | ~125 | fiyat kontrol edilecek | Renk kodu: kırmızı 3V3, siyah GND, mavi SPI, yeşil I2C, turuncu GPIO. |
| 19 | 2,54 mm erkek header şeridi (40'lık) | Genel | RAK13002/LSM303AGR/ekran için gerekirse | 1 | 2 | 5 | fiyat kontrol edilecek | LSM303AGR ile 0,1" header "dahil" ama lehimlenmemiş olabilir. |
| 20 | USB-C veri kablosu | Genel | Programlama + şarj | 1 | 2 | 5 | fiyat kontrol edilecek | |
| 21 | Lehim malzemesi (havya, lehim) | — | Header lehimi | ortak | | | — | Kısa lehim işi: header'lar. |

## 3. Ölçüm ve geliştirme ekipmanı (ortak)

| # | Ekipman | Parça no | İşlev | Adet | Kaynak | Fiyat |
|---|---|---|---|---|---|---|
| 22 | Akım profilleyici | Nordic Power Profiler Kit II (PPK2) | Faz 4 ortalama akım, TX/RX/GNSS profil (ölçüm aralığı 200 nA–1 A) | 1 | https://www.nordicsemi.com/Products/Development-hardware/Power-Profiler-Kit-2/ | fiyat kontrol edilecek (arama özetlerinde lansman fiyatı $89, dağıtıcılarda daha yüksek; tarih doğrulanamadı) |
| 23 | Multimetre | Genel | Kısa devre, gerilim, süreklilik | 1 | — | — |
| 24 | Mantık analizörü (isteğe bağlı) | Genel 8 kanal | SPI/I2C hata ayıklama | 1 | — | fiyat kontrol edilecek |
| 25 | SWD programlayıcı (isteğe bağlı) | J-Link/benzeri | USB önyükleyici çalışmazsa | 0–1 | — | fiyat kontrol edilecek |

PPK2 ile ölçüm düzeni: PPK2 "Ampere meter" kipinde LiPo ile RAK19007 arasına seri;
sabit pil yerine "Source meter" kipi 3,7–4,2 V ile de kullanılabilir (PPK2 kullanım
kılavuzuyla doğrula).

## 4. Toplam özet (parça kalemi başına)

| Kalem | 1 | 2 | 5 |
|---|---|---|---|
| RAK4631 / RAK19007 / RAK13002 / RAK12500 | 1'er | 2'şer | 5'er |
| Ekran modülü (19192) | 1 | 2 | 5 |
| LSM303AGR (4413) | 1 | 2 | 5 |
| LiPo | 1 | 2 | 5 |
| Anten (LoRa + GNSS) | 1+1 | 2+2 | 5+5 |
| Motor + Q1 + D1 + R1 + R2 + 2 kondansatör + tuş | 1 takım | 2 | 5 |

**Güncelleme (12 Kasım 2026):** RAK mağazası arama sayfasında liste fiyatları
görüldü (RAK4631 $17,99 · RAK19007 $9,99 · RAK13002 $6,00 · RAK12500 $19,00 ·
LoRa PCB anteni $3,00); 2 cihazlık toplam `alisveris-listesi.md` içindedir.
Aynı gün ürün sayfalarından: RAK4631 EU868/Arduino stokta ve LoRa + BLE anteniyle
geliyor (madde 8 ayrıca alınmaz); RAK12500 kutusunda GNSS anteni var (madde 9
ayrıca alınmaz) ama modül **stokta yok**; Adafruit 4413 hâlâ stokta yok.
Bölüm 5'teki 2. ve 3. sorular yanıtlandı; 1., 4. ve 5. açık.

Fiyat toplamı çıkarılmadı: dört RAK parçasının fiyatı doğrulanamadı. Görülen
kalemlerin birim toplamı (ekran $14,99 + pusula $12,50 + pil $6,95) = **$34,44 / cihaz**
(stoksuz kalemin fiyatı dahil, 2026-11-11 sayfa fiyatları, vergi/kargo yok).

## 5. Sipariş öncesi açık sorular

1. Adafruit 4413 stokta yok → bayi veya bekleme; yoksa muadil LSM303AGR breakout aranır (aynı I2C adresleri korunmalı).
2. RAK4631 varyantı: EU868 + Arduino önyükleyicili sürüm; `-R` ile farkı satıcıya sor.
3. RAK12500 paketinde GNSS anteni var mı, aktif mi?
4. RAK13002'nin 2,54 mm başlığı lehimli mi?
5. Waveshare 19192 BL pini sürücülü mü (modül şeması)?

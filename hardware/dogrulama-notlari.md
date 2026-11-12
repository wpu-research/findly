# Findy P0 — Doğrulama Notları (a–j)

Tarih: 2026-11-11 · Durum: **KONSEPT** · Spec dosyaları değiştirilmedi.
Durum etiketleri: **DOĞRULANDI** (üretici/birincil belge) · **KISMEN** (ikincil kaynak, çelişki veya eksik) · **DOĞRULANAMADI**.
Not: Üretici sayfalarından bazıları (RAK mağaza, ST, Semtech) erişim hatası/zaman aşımı verdi; SX1262 ve LSM303AGR sayısal değerleri üretici PDF'lerinin bayi aynasından okundu (aşağıda belirtilmiştir).

## Özet

| Madde | Durum |
|---|---|
| a. RAK4631 variant.h sembol→GPIO | DOĞRULANDI (WB_*), SX1262 pinleri DOĞRULANDI, TCXO 1,8 V KISMEN |
| b. WB_IO2 → 3V3_S | KISMEN (evet, ama polarite yazılı değil; RAK13002'ye hangi hattın gittiği belirsiz) |
| c. RAK19007 | DOĞRULANDI (pil ölçüm pini hariç: KISMEN) |
| d. RAK13002 | KISMEN (sinyaller var, atama yapılabilir; SDI/SDO ve VCC hattı belirsiz) |
| e. RAK12500 | KISMEN (ZOE-M8Q DOĞRULANDI; I2C adresi, yedek besleme belirsiz) |
| f. GC9A01 modül | DOĞRULANDI (Waveshare 19192); BL akımı/sürücüsü DOĞRULANAMADI |
| g. LSM303AGR / Adafruit 4413 | DOĞRULANDI |
| h. Akımlar | KISMEN (mertebe doğru; TX +14 dBm ve RX değerleri düzeltilmeli) |
| i. 869,4–869,65 MHz kuralı | DOĞRULANDI (AB); Türkiye KISMEN; Kıbrıs DOĞRULANAMADI |
| j. P1 adayları | DOĞRULANDI (RAK4630, MAX-M10S, çıplak panel, LiPo örnekleri) |

## a. RAK4631 variant.h ve SX1262 iç pinleri — DOĞRULANDI / KISMEN

Kaynak (birincil): https://raw.githubusercontent.com/RAKWireless/RAK-nRF52-Arduino/master/variants/WisCore_RAK4631_Board/variant.h

| Sembol | Arduino no | nRF52840 | Yuva yorumu (variant.h) |
|---|---|---|---|
| WB_IO1 | 17 | P0.17 | SLOT_A, SLOT_B |
| WB_IO2 | 34 | P1.02 | SLOT_A, SLOT_B |
| WB_IO3 | 21 | P0.21 | SLOT_C |
| WB_IO4 | 4 | P0.04 | SLOT_C |
| WB_IO5 | 9 | P0.09 (NFC1) | SLOT_D |
| WB_IO6 | 10 | P0.10 (NFC2) | SLOT_D |
| WB_SW1 | 33 | P1.01 | IO_SLOT |
| WB_A0 | 5 | P0.05 (AIN3) | IO_SLOT |
| WB_A1 | 31 | P0.31 (AIN7) | IO_SLOT |
| WB_I2C1_SDA / SCL | 13 / 14 | P0.13 / P0.14 | SENSOR_SLOT, IO_SLOT |
| WB_I2C2_SDA / SCL | 24 / 25 | P0.24 / P0.25 | IO_SLOT |
| WB_SPI_CS | 26 | P0.26 | IO_SLOT |
| PIN_SPI_SCK / WB_SPI_CLK | 3 | P0.03 | IO_SLOT |
| PIN_SPI_MISO / WB_SPI_MISO | 29 | P0.29 | IO_SLOT |
| PIN_SPI_MOSI / WB_SPI_MOSI | 30 | P0.30 | IO_SLOT |

(P1.x için Arduino numarası = 32 + x: WB_IO2 = 34 = P1.02 bu kuralla tutarlı.)

SX1262 modül içi (kaynak: RAK4631 veri sayfası https://docs.rakwireless.com/product-categories/wisblock/rak4631/datasheet/ ; çapraz: Meshtastic https://raw.githubusercontent.com/meshtastic/firmware/master/variants/nrf52840/rak4631/variant.h): NSS P1.10 (42), SCK P1.11 (43), MOSI P1.12 (44), MISO P1.13 (45), BUSY P1.14 (46), DIO1 P1.15 (47), NRESET P1.06 (38), ANT_SW/`SX126X_POWER_EN` P1.05 (37). DIO2 antenna anahtarını sürer (`SX126X_DIO2_AS_RF_SWITCH`), DIO3 TCXO'yu besler. RXEN/TXEN **tanımlı değil**. **TCXO gerilimi 1,8 V** yalnızca Meshtastic `variant.h` içinde (`SX126X_DIO3_TCXO_VOLTAGE 1.8`); RAK belgesi değeri vermiyor → KISMEN. RAK veri sayfası P1.07'nin şematikte anahtara bağlı olduğunu ama başlatılmaması gerektiğini söylüyor.

**Çelişki:** Meshtastic belge sayfası (https://meshtastic.org/docs/configuration/rak-gpio-mapping) SW1'i P0.01 ve A0'ı P0.04/AIN2 gösteriyor; RAK'ın `variant.h` değerleri SW1=33 (P1.01), A0=5 (P0.05/AIN3) → **RAK `variant.h` esas alındı**. Aynı Meshtastic sayfasında IO1/IO2 açıklamaları da değiş-tokuş görünüyor (güvenilmez ikincil kaynak).

Ek: RAK4631 sayfasındaki 40 pinli tablo 24–28. pinleri `QSPI_DIO2 / QSPI_CE / SCLK / QSPI_DIO1 / QSPI_DIO0` diye adlandırıyor; RAK19007 tablosu aynı pinler için `IO7 / SPI_CS / SPI_CLK / SPI_MISO / SPI_MOSI` diyor. Aynı fiziksel pinlerin iki adı var; yazılım için `variant.h` adları geçerli.

## b. WB_IO2 ve 3V3_S — KISMEN

Kaynak: https://docs.rakwireless.com/product-categories/wisblock/rak19007/datasheet/ ; https://raw.githubusercontent.com/meshtastic/firmware/master/variants/nrf52840/rak4631/variant.h

- RAK19007: çekirdek pin 30 (IO2) "3V3_S enable" için kullanılır; sensör yuvası A–D pin 11 ve 14 = 3V3_S ("CPU modülü tarafından kapatılabilir"). **Dört sensör yuvası da 3V3_S ile beslenir.** DOĞRULANDI.
- **Polarite** RAK sayfasında yok. Meshtastic: `PIN_3V3_EN (34)`, "enables 3.3V periphery like GPS or IO Module", "Do not toggle this for GPS power savings" → YÜKSEK = açık sözleşmesi, ve "IO Module" de 3V3_S'e bağlı gibi yazılmış. KISMEN.
- RAK forumu: bazı taban sürümlerinde WB_IO2'de pull-down olduğu söyleniyor (https://forum.rakwireless.com/t/can-t-use-wb-io1-and-wb-io2-pins-on-rak4631-with-rak19007/14979) → açılışta IO2 sürülmezse 3V3_S kapalı kalabilir.
- **Spec bölüm 3: "GNSS güç WB_IO2 — 3V3_S hattını açar/kapatır" doğru**, ama bölüm 3 ve 6'nın bunun sonucunu (bkz. e, sıcak başlangıç) hesaba katmadığı görülüyor.
- Belirsiz: RAK13002 veri sayfası 40 pinli tabloda hem `3V3` (pin 5, 17, 18) hem `3V3_S` (pin 6) listeliyor; RAK19007 IO yuvası pin tablosu sayfada yok; RAK13002 başlığında "VCC" yazıyor. **Başlıktaki VCC'nin 3V3 mü 3V3_S mi olduğu DOĞRULANAMADI** (ilk güçte ölçülecek).

## c. RAK19007 — DOĞRULANDI (pil ölçüm pini KISMEN)

Kaynak: https://docs.rakwireless.com/product-categories/wisblock/rak19007/datasheet/

- Yuvalar: CPU, **IO**, sensör **A, B, C, D** (24 pin). A–C 10 mm modül, D 23 mm'ye kadar (GNSS destekli). Boyut 30×60 mm.
- 2,54 mm başlıklar (3 adet; özellik listesi "dört" diyor, sayfada tutarsız): **J10** BOOT, GND, TX1, RX1 · **J11** AIN1, IO1, IO2, VBAT · **J12** VDD (3,3 V), GND, SCL (I2C1), SDA (I2C1).
- Sensör yuvası pinleri (A/B/C/D): 10 = IO2/IO1/IO4/IO6; 12 = IO1/IO2/IO3/IO5; 11 ve 14 = 3V3_S; 9 ve 16 = VDD; 7/8 = I2C1 SCL/SDA; 3–6 = SPI; A ve D'de ayrıca TXD1/RXD1.
- Pil: **JST PHR-2, 2 mm**, dişi, "P2". 3,3 V min / 3,7 V tip. / **4,3 V max**. Şarj: USB-C'den 4,5–5,5 V, **350 mA**, kırmızı LED. Güneş: JST ZHR-2 1,5 mm, 5,5 V max.
- Akım: sızıntı <2 µA, boşta <10 µA, LoRa TX'te 130 mA.
- Pil gerilimi ölçümü: sayfa AIN pinini **belirtmiyor** (sadece J11 pin 4 = VBAT; J11 analog girişi AIN0'dan AIN1'e değişti). WB_A0 = P0.05/AIN3 (variant.h), Meshtastic yorumu: `AIN3 = VBAT * (1.5/2.5)`, `ADC_MULTIPLIER 1.73`. RAK forumu da WB_A0'ın "pile bir direnç üzerinden bağlı" olduğunu söylüyor (https://forum.rakwireless.com/t/wisblock-rak4631-rak13002-io-adaptor-pin-wb-a0-adc-voltage/6637) ve harici gerilim için WB_A1'i öneriyor. **Spec: "WB_A0 taban kartındaki bölücü" → büyük olasılıkla doğru, ama RAK19007 sayfası bunu yazmıyor (KISMEN).**

## d. RAK13002 — KISMEN

Kaynak: https://docs.rakwireless.com/product-categories/wisblock/rak13002/datasheet/ ; .../quickstart/

- 25×35 mm, WisConnector ile IO yuvasına, "standart 2,54 mm başlık". 40 pin tablosu: GND 3/4/39/40, 3V3 5/17/18, 3V3_S 6, SW1 10, TXD0/RXD0 11/12, RST 13, LED1/2 14/15, SDA1/SCL1 19/20, AIN0/AIN1 21/22, IO7 24, SPI_CS/CLK/MISO/MOSI 25–28, IO1 29, **IO3 31, IO4 32**, UART1 33/34, SDA2/SCL2 35/36, **IO5 37, IO6 38**. **IO2 (pin 30) NC.**
- Başlık serigrafi (hızlı başlangıç sayfası, 4 sütun × 8 sıra):
  - Sütun 1: VCC GND IO1 IO3 IO4 IO5 IO6 IO7
  - Sütun 2: VCC GND SCL1 SDA1 SCL2 SDA2 LED1 LED2
  - Sütun 3: VCC GND TXD0 RXD0 TXD1 RXD1 AIN0 AIN1
  - Sütun 4: VCC GND CS SDI SDO SCK RST SW1
- **Mimari atamasının fiziksel olarak yapılabilirliği: EVET.** Ekran CS (CS), SCK (SCK), MOSI (SDI*), DC=IO3, RST=IO4, BL=IO5, motor=IO6, tuş=SW1, I2C1 (SDA1/SCL1), VCC/GND hepsi başlıkta mevcut.
- **Çakışmalar:**
  1. IO1, RAK12500 (Yuva A) 1PPS'ini taşır (bkz. e). RAK13002'de IO1 başlığa çıkıyor ama kullanılmamalı.
  2. IO2 başlıkta yok; 3V3_S/GNSS RESET hattı olduğu için de yok sayılmalı.
  3. RAK12500 **Yuva C'ye takılırsa** (RAK12500 yalnızca A veya C'yi destekler) pin 10/12 = IO4/IO3 olur → ekran RST/DC ile çakışır. **Yuva A kullanılmalı.**
  4. IO5/IO6 = P0.09/P0.10 = NFC pinleri.
- **DOĞRULANAMADI:** (i) SDI/SDO'nun MOSI/MISO olup olmadığı (başlık sırası CS, SDI, SDO, SCK; 40 pin tablosundaki sıra CS, CLK, MISO, MOSI) — ölçülecek; (ii) başlık VCC'sinin 3V3 mü 3V3_S mi olduğu; (iii) başlığın lehimli gelip gelmediği.
- Sayfadaki başlık tablosunda IO2 yok, IO7 var (metin "WB_IO1–IO6" diyor): tutarsız.

## e. RAK12500 — KISMEN

Kaynak: https://docs.rakwireless.com/product-categories/wisblock/rak12500/datasheet/ ; .../quickstart/ ; u-blox ZOE-M8: https://content.u-blox.com/sites/default/files/ZOE-M8_DataSheet_UBX-16008094.pdf

- **Çip: u-blox ZOE-M8Q — DOĞRULANDI.** GPS, GLONASS, QZSS, BeiDou desteği; 10×23 mm; VDD 2,7–3,3–3,6 V.
- **Yuva:** A (UART/I2C) veya C (yalnızca I2C) — DOĞRULANDI. Birbirine bağlı pinler: UART, I2C, 1PPS (pin 12), RESET, VDD, GND (3V3_S pin 11/14).
- RAK pin tablosunda "pin 10 = IO6" yazıyor (yuva A'da pin 10 = IO2; IO6 yalnızca D'de) → sayfa tutarsız; Yuva A için forum + Meshtastic kaynaklı eşleme: **IO1 = 1PPS, IO2 = GNSS RESET (ve 3V3_S enable)** (Meshtastic `variant.h`: "IO1 is hooked to PPS (pin 12 on header) = gpio 17", "IO2 is hooked to GPS RESET = gpio 34, but ... also used to control 3V3_S power"). Resmi sayfa slot tablosunun içeriğini göstermiyor → KISMEN.
- **I2C adresi:** RAK sayfasında/hızlı başlangıçta **yok**; ZOE-M8 veri sayfası DDC'yi "I2C uyumlu, yalnızca slave" olarak tanımlıyor, 7-bit adresi çıkarılan metinde yok. u-blox varsayılanı olan 0x42 yaygın bilgidir ama **bu görevde birincil kaynaktan doğrulanamadı** → ilk güçte taranacak.
- **Akım (ZOE-M8Q veri sayfası, Tablo 13):** edinim 22 mA (GPS/QZSS/SBAS) – 28 mA (GPS+GLONASS), izleme (sürekli) 21–25 mA — bunlar **DC/DC'li** tahmindir; DC/DC'siz 32,5–40 mA (RAK12500'ün hangisi olduğu belirsiz). Güç tasarruf modu 1 Hz: 8,5–9,0 mA. En yüksek 67 mA. SW yedek modu 20 µA, HW yedek 15 µA. (RAK sayfasındaki "çalışma akımı <15 µA" yanıltıcı; bu ZOE'nin yedek akımıdır.) Spec'in "izleme ~20–25 mA" değeri **doğru**.
- **Yedek besleme / sıcak başlangıç — ÖNEMLİ:** RAK12500 pin tablosunda **V_BCKP pini yok**. ZOE-M8 veri sayfası: "V_BCKP beslenmiyorsa VCC'nin kesilmesi tüm verileri siler ve soğuk başlangıç olur"; soğuk TTFF tip. **26 s**, sıcak **1 s** (Tablo 1). RAK forumunda 3V3_S'in WB_IO2 ile kesilmesinin ardından modülün yeniden uydu araması gerektiği ("1 dakikayı bulabilir") yazılı (https://forum.rakwireless.com/t/putting-the-rak12500-to-sleep-and-waking-it-up-again/4858). **Yani spec'teki "WB_IO2 ile GNSS kapat/aç" şeması her açılışta soğuk başlangıçtır** (bkz. hata listesi H1). Yazılım yedek modu (UBX-RXM-PMREQ, 20 µA, VCC açık kalır) bunu önler.
- Konnektör: GNSS anteni için IPEX (RAK mağaza/forum); paketle anten gelip gelmediği satıcıya göre değişiyor; aktif/pasif DOĞRULANAMADI.

## f. 1,28" GC9A01 modül — DOĞRULANDI (BL hariç)

Kaynaklar: https://www.waveshare.com/1.28inch-lcd-module.htm ; https://www.waveshare.com/wiki/1.28inch_LCD_Module ; çıplak panel: https://cdn.shopify.com/s/files/1/0264/7629/files/DM-TFTR128-446_Datasheet.pdf

- Waveshare 19192: pinler **VCC, GND, DIN, CLK, CS, DC, RST, BL**; çalışma gerilimi 3,3 V/5 V; 4 telli SPI; 240×240, IPS, görünür alan Ø32,4 mm; modül **40,4×37,5 mm, gövde Ø37,5 mm**; PH2.0 8 pin kablo dahil; wiki SSS'de en fazla 31,2 mA @ 3,3 V; fiyat $14,99 (2026-11-11 sayfa).
- Başka satıcı modülleri: pin adları SDA/SCL, ölçüler farklı (Adafruit 42,4×36,2×5,4 mm; bir genel modül 38×45,5×4,5 mm — arama özeti).
- **Arka ışık akımı: modül için DOĞRULANAMADI** (Waveshare belirtmiyor). Çıplak panel DM-TFTR128-446: arka ışık 2 LED paralel, **3,0 V'ta tip. 40 mA, maks. 60 mA**; IDD 8 mA; panel VDD 2,4–3,3 V.

## g. LSM303AGR / Adafruit 4413 — DOĞRULANDI

Kaynaklar: https://www.adafruit.com/product/4413 ; ST veri sayfası (bayi aynası, Rev 11): https://datasheet.chipsmall.com/LSM303AGRTR/208805.pdf ; ST tasarım notu DT0131 (https://www.st.com.cn/resource/en/design_tip/dt0131-digital-magnetometer-and-ecompass-efficient-design-tips--stmicroelectronics.pdf)

- **I2C 7-bit adresleri: ivme 0x19 (0011001b), manyeto 0x1E (0011110b)** — DOĞRULANDI. Adafruit 4413 sayfası aynı adresleri veriyor.
- Besleme Vdd 1,71–3,6 V. Akım (ST Tablo 5, okunabilirlik düşük): ivmeölçer yaklaşık 4–13 µA (moda göre; ör. 50 Hz normal 12,6 µA, düşük güç 50 Hz 7,7 µA), manyetometre 20 Hz'de düşük güç **50 µA**, yüksek çözünürlük **200 µA**, güç kapalı 2 µA. Spec'in "~0,05 mA" değeri yalnızca düşük güçlü manyetometre kipi için tutuyor (toplam ~0,06 mA); yüksek çözünürlükte 0,2 mA.
- Adafruit 4413 = "Adafruit LSM303AGR Accelerometer Magnetometer – STEMMA QT / Qwiic": 25,4×17,7×4,6 mm, 3,3 V ve 5 V mantık, **$12,50**, sayfada **stokta yok**. Kartta regülatör var (AP2112K veya eşdeğeri; ≥150 mA). VIN aralığı belirtilmemiş. Adafruit rehberine göre manyeto sürücüsü `Adafruit_LIS2MDL`, ivme sürücüsü `Adafruit_LSM303_Accel` (arama özeti).

## h. Akımlar — KISMEN

Kaynaklar: SX1262 veri sayfası Rev 1.1 (bayi aynası) https://datasheet.chipsmall.com/SX1262IMLTRT/249951.pdf ; RAK4631 https://docs.rakwireless.com/product-categories/wisblock/rak4631/datasheet/ ; ZOE-M8 (e).

| Tüketici | Spec tahmini | Belgelenen | Sonuç |
|---|---|---|---|
| SX1262 RX (LoRa 125 kHz) | ~5 mA | **4,6 mA (DC-DC)**, 8,8 mA (LDO); RX boosted 5,3/10,1 mA | Çip için doğru; modül düzeyinde RAK 17 mA diyor ("LoRa Rx @ 37,5 kbps", koşul belirsiz) |
| SX1262 TX +14 dBm | ~45 mA | **45 mA yalnızca "+14 dBm optimal ayarlarıyla"**; PA +22 dBm eşleşmesi ayarında +14 dBm = **90 mA** | Düzeltilmeli (aşağıda H6) |
| SX1262 TX +22 dBm | — | **118 mA** (868 MHz, +22 dBm eşleşme); RAK4631 modül: 125 mA @20 dBm, 92 mA @17 dBm | RAK19007: 130 mA tepe |
| SX1262 uyku | — | 160 nA (soğuk), 600 nA (yapılandırma saklı) | — |
| nRF52840 + modül uykusu | ~0,01 mA | **RAK4631: LoRa+BT uykuda 2,0 µA**; RAK19007 boşta <10 µA; RAK4630 modül "tek seferlik uyku" 4,42 µA | Spec'in 0,01 mA'ı muhafazakâr, doğru mertebe |
| GNSS izleme | 20–25 mA | 21–25 mA (DC/DC'li) / 32,5–40 mA (DC/DC'siz) | Doğru |
| LSM303AGR | ~0,05 mA | 0,05 mA (LP manyeto) – 0,2 mA (HR) | Doğru mertebe |

Hesap kontrolü (bu görevde yapıldı): FindyLink paketi 30 bayt, SF8/BW125/CR4-5/8 önek/CRC açık/açık başlık: **hava süresi ≈ 123 ms**. Görev döngüsü: BEKLEME (15 sn çerçeve) **%0,82**, ARAMA (5 sn) **%2,5** → %10 sınırının altında. Dinleme oranı: dilim başına dinleme = ±GUARD (120 ms) + paket; "±" iki yan ise 4×(240+123)/15 000 ≈ %9,7, tek yan ise %6,5 → spec'in "%6"sı yalnızca dar yorumla; ARAMA'da (5 sn çerçeve) %19–29'a çıkar (RX 5 mA'de ≈1–1,5 mA ortalama).

## i. 869,4–869,65 MHz kuralı — DOĞRULANDI (AB) / KISMEN (TR) / DOĞRULANAMADI (KKTC)

- **AB/CEPT (birincil metin):** ERC/DEC/(01)04 Ek 1 (belge tarihi 2001, son değişiklik 2007; https://docdb.cept.org/download/2369): **869,4–869,65 MHz: 500 mW e.r.p., görev döngüsü < %10** (bir saatlik süreye göre), kanal aralığı 25 kHz **veya tüm bant tek kanal (yüksek hızlı veri)**, anten bütünleşik veya özel. Spec'teki 125 kHz BW, 869,525 MHz merkez ±62,5 kHz → bandın içinde. İkincil kaynaklar: bazı belgeler %10 yerine LBT+AFA alternatifini de listeliyor. Not: bu 2007 tarihli karar metnidir; güncel ERC Rec 70-03/EN 300 220 sürümü bu görevde doğrulanmadı.
- **Güç birimi:** 500 mW **e.r.p.** (≈ +27 dBm); +22 dBm iletim + anten kazancı e.r.p. sınırının altında kalmalı.
- **Türkiye:** Arama özeti BTK "Sınıf 1 teknik ölçüt" belgesinde 869,4–869,65 MHz için 500 mW e.r.p., %10 görev çevrimi veya LBT+AFA, standart TS EN 300 220 yazdığını söylüyor; **belge doğrudan açılamadı (404)** → KISMEN. Kaynak (açılamadı): https://www.btk.gov.tr/uploads/pages/sinif1-teknik-olcut.pdf
- **Kıbrıs (KKTC):** BTHK (bthk.org) düzenleyici; 868 MHz KET bandı için bir kural/muafiyet metni **bulunamadı** → DOĞRULANAMADI; BTHK'ya (Telsiz Tüzüğü / Ulusal Frekans Planı) sorulmalı. Kıbrıs Cumhuriyeti (güney) için de bu görevde kaynak aranmadı.
- CE/RED sertifikasyonu bu belgenin kapsamı dışında.

## j. P1 adayları — DOĞRULANDI (ayrıntı `BOM-P1-aday.md`)

- **RAK4630** modül: **15×23×3 mm**, 44 pin; LoRa anten pini RF_LoRa (pin 37), BLE RF_BT (pin 15). https://docs.rakwireless.com/product-categories/wisduo/rak4630-module/datasheet/ . (RAK4631 çekirdek kartı ise 20×30 mm.)
- **u-blox MAX-M10S:** sürekli izleme 25 mW; 3,0 V'ta VCC akımı edinim 8–13 mA, izleme 7,5–10 mA (+V_IO ≈2,1–2,3 mA), güç tasarruf kipi 4,5–5 mA (+V_IO 2 mA), SW bekleme VCC 120 nA + V_IO 37–46 µA, HW yedek 28 µA; boyut ≈ **9,7×10,1×2,5 mm**; V_BCKP pini var. https://content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf
- **Çıplak 1,28" panel:** Display Module DM-TFTR128-446: 35,6×38,1×1,5 mm, görünür alan 32,4×32,4, GC9A01, 4 hat SPI, arka ışık 3,0 V/40 mA (tip.). 
- **LiPo örnekleri (Adafruit, katalog):** 150 mAh 19,75×26,02×3,8 mm; 350 mAh 36×19,6×5,2 mm; 500 mAh 29×36×4,75 mm.

---

## Mimari belgesinde (`docs/mimari-v0.1.md`) düzeltilmesi gereken yerler

**H1 — (YÜKSEK) §3 ve §6: GNSS'i WB_IO2/3V3_S ile kesip açma, soğuk başlangıç demektir.** RAK12500'de V_BCKP pini yok; ZOE-M8 veri sayfası VCC kesilince tüm verinin silineceğini ve soğuk başlangıç (tip. 26 s, gerçekte zayıf sinyalde 1 dk) olacağını söylüyor. §6'daki "30 sn'de bir konum, GNSS %15 görev döngüsü ≤ 3,5 mA" modeli bu yüzden tutmaz (26 sn edinim + 22–28 mA, görev döngüsü ≈ %90). Öneri: 3V3_S/IO2'yi sürekli AÇIK tut; GNSS'i yazılım yedek moduyla (UBX-RXM-PMREQ, ZOE-M8Q'da SW yedek akımı 20 µA, sıcak başlangıç ≈ 1 s) veya güç tasarruf kipiyle (1 Hz ≈ 9 mA) yönet; bütçeyi buna göre yeniden hesapla. Meshtastic de IO2'yi GPS güç tasarrufu için oynatmamayı öneriyor.

**H2 — §3: "`WB_IO1` boş (yedek)" yanlış.** Yuva A'daki RAK12500 WB_IO1'i 1PPS çıkışı olarak kullanır (RAK12500 pin 12 = 1PPS, Yuva A pin 12 = IO1; Meshtastic `PIN_GPS_PPS (17)`). IO1 yedek değil; başka işe verilmemeli.

**H3 — §3: WB_IO2 hem GNSS RESET hem 3V3_S enable.** "GNSS güç" tek işlev gibi yazılmış. Polarite RAK sayfasında yok; bazı taban sürümlerinde pull-down var → açılışta sürmek gerekir. RAK13002 başlığında IO2 yok (kablolanamaz).

**H4 — §2/§3: RAK12500 yuvası belirtilmeli: yalnızca Yuva A.** Yuva C'de IO3/IO4 devreye girer (ekran DC/RST ile çakışır); ayrıca Yuva C yalnızca I2C. Çizimde "Yuva A" doğru; ama "neden C değil" belgelenmemiş.

**H5 — §3: WB_IO5/WB_IO6 = P0.09/P0.10 NFC pinleri.** Arka ışık (PWM) ve motor bu pinlerde; NFC'nin GPIO yapılması gerekir (UICR; RAK BSP'de nasıl yapıldığı DOĞRULANAMADI). Alternatif: IO3/IO4'ten birini PWM'e kullan (P0.21/P0.04) ve IO5/IO6'yı tuş/yedek yap — ya da NFC ayarını ilk testte doğrula.

**H6 — §6 tablosu: SX1262 TX +14 dBm ≈ 45 mA yalnızca "optimal ayarla" geçerli.** Varsayılan +22 dBm PA eşleşmesinde +14 dBm ≈ 90 mA, RAK'ın modül ölçümü 92 mA @17 dBm / 125 mA @20 dBm. TX katkısı ≈ 0,3 mA yerine ≈ 0,6 mA olabilir. RX: DC/DC modunda 4,6 mA, LDO'da 8,8 mA (RAK sayfası 17 mA yazıyor, koşul belirsiz). Dinleme oranı %6 yerine ±GUARD yorumuna göre %6,5–9,7; ARAMA kipinde %19–29.

**H7 — §3: "Pil gerilimi WB_A0 — taban kartındaki bölücü" belgelenmemiş.** RAK19007 sayfası AIN pinini yazmıyor; WB_A0 = P0.05/AIN3, bölücü 1,5/2,5 (Meshtastic); RAK13002 başlığında AIN0 olarak çıkıyor → başka sinyal bağlanmamalı; harici ADC için WB_A1.

**H8 — §6: "ZOE-M8Q izleme ~20–25 mA" doğru** (21–25 mA DC/DC'li; DC/DC'siz 32,5–40 mA). Edinim 22–28 mA ve en yüksek 67 mA eklenmeli (regülatör/pil için tepe).

**H9 — §10 (P1): pil ölçüsü "~4×25×30 mm, 250–300 mAh" 40 mm yuvarlak gövdeye sığmaz.** Dikdörtgenin köşegeni √(25²+30²) ≈ 39,1 mm; 40 mm dış çap − cidar (örn. 2×2 mm) iç çapı ≈ 36 mm. Katalog örnekleri: 150 mAh 19,75×26,02 (köşegen 32,7 mm → sığar), 350 mAh 36×19,6 (köşegen 41 mm → sığmaz), 500 mAh 29×36 (46 mm → sığmaz). Yığın hesabında ekran modülü: çıplak panel 35,6×38,1×1,5 mm; RAK4630 15×23×3 mm, MAX-M10S ≈9,7×10,1×2,5 mm. Ayrıca 150 mAh pille 7 mA ortalama ≈ 21 saat, 250–300 mAh ≈ 36–43 saat.

**H10 — §4: frekans notu.** AB 869,4–869,65 MHz (%10, 500 mW e.r.p.) doğru (ERC/DEC/(01)04); "duty cycle bir saatlik süreye göre" ve "güç e.r.p." ifadeleri eklenmeli. Türkiye için BTK metni doğrulanamadı; Kıbrıs (KKTC) için hiçbir metin bulunamadı. FindyLink hava süresi ≈ 123 ms (SF8, 30 bayt) → BEKLEME %0,82, ARAMA %2,5.

**H11 — §3: WB_SW1 = P1.01 (Arduino 33).** Meshtastic belge sayfası P0.01 diyor; RAK `variant.h` P1.01'dir. Spec sembolik ad kullandığı için sorun yok; ama bağlantı tablosunda P1.01 kullanıldı.

**H12 — Eksik:** RAK13002 başlığı SDI/SDO adlandırması MOSI/MISO ile eşleşmiyor olabilir (DOĞRULANAMADI); başlıktaki VCC'nin 3V3/3V3_S durumu belirsiz. Spec'e "ilk güçte ölç" notu eklenmeli.

## DOĞRULANAMAYANLAR (toplu)

1. SDI/SDO ↔ MOSI/MISO (RAK13002).
2. RAK13002 başlık VCC'si: 3V3 mü 3V3_S mi.
3. 3V3_S polaritesi (RAK sayfası yazmıyor; Meshtastic'e göre YÜKSEK=açık).
4. RAK12500 I2C adresi (u-blox varsayılanı 0x42, birincil kaynakta bu görevde bulunamadı), yedek besleme (V_BCKP) düzeni, anten aktif/pasif, paketle anten.
5. RAK19007 pil ölçüm pininin resmi olarak yazılması (WB_A0 = AIN3 ikincil kaynaktan).
6. Waveshare 19192 BL pininin türü ve akımı.
7. WB_IO5/IO6 için NFC→GPIO ayarının RAK BSP'deki yeri.
8. SX1262 TCXO gerilimi (1,8 V) RAK belgesinde.
9. RAK4631 anten konektör tipi; RAK mağaza fiyatları (429 hatası); RAK4631 ↔ RAK4631-R önyükleyici farkı.
10. BTK belgesinin doğrudan okunması; KKTC kuralı.
11. Pil konnektörü (JST-PH ↔ PHR-2) kutup sırası.
12. SX1262 değerleri: resmi Semtech PDF'i bu görevde açılamadı; Rev 1.1 (Aralık 2017) bayi aynası kullanıldı.

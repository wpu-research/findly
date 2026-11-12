# Findy P0 — Bağlantı Tablosu (telden tele)

Tarih: 2026-11-11 · Durum: **KONSEPT** · Çizim: `baglanti-semasi.svg` / `.png` · Spec: `docs/mimari-v0.1.md`
Doğrulama ayrıntıları ve kaynak URL'leri: `dogrulama-notlari.md` (harf kodları A–J).

Gösterim: P0.x = nRF52840 port 0 pini x; P1.x = port 1 pini x; Arduino numarası parantez içinde (P1.x = 32+x).
Kaynak kodları: **V** = RAK-nRF52-Arduino `variant.h` (WB_* değerleri) · **R13** = RAK13002 belgeleri · **R19** = RAK19007 belgeleri · **R12** = RAK12500 belgeleri · **R46** = RAK4631 veri sayfası · **M** = Meshtastic RAK4631 `variant.h` (üretici dışı, çapraz kontrol) · **W** = Waveshare 1.28" modül sayfası · **AF** = Adafruit 4413 sayfası.
"(*)" = DOĞRULANAMADI / ilk güçte ölçülecek.

## 0. Önemli uyarılar (okumadan başlama)

1. **WB_IO2 hem 3V3_S anahtarıdır hem RAK12500'ün RESET'idir** (Yuva A). GPIO olarak kullanma; polarite RAK sayfasında yazılı değil (Meshtastic sözleşmesi: YÜKSEK = açık). Bazı taban kartı sürümlerinde WB_IO2'de pull-down olduğu bildirilmiş → yazılımda `WB_IO2`yi açılışta YÜKSEK sür.
2. **WB_IO1, Yuva A'daki RAK12500'ün 1PPS çıkışıdır.** Boş değildir; kullanma.
3. **RAK12500'ü Yuva A'ya tak.** Yuva C'de pin 10/12 = IO4/IO3 olur → ekran RST/DC ile çakışır.
4. **WB_IO5 ve WB_IO6 = P0.09/P0.10 = nRF52840 NFC pinleri.** GPIO olarak kullanmak için NFC pinlerinin GPIO yapılması gerekir (UICR ayarı; RAK BSP'de bunun nasıl yapıldığı DOĞRULANAMADI) → ilk testte tuş/LED benzeri basit bir sınama yap.
5. **RAK13002 başlığındaki "VCC" pininin 3V3 mü 3V3_S mi olduğu DOĞRULANAMADI** (başlıkta "3V3_S" ayrı listelenmemiş; veri sayfasındaki 40 pinli tabloda hem 3V3 hem 3V3_S var). Ekran/LSM303AGR/motor hangi hatta bağlanırsa, GNSS'i kapatmak için WB_IO2'yi DÜŞÜK yapmak onları da kapatabilir. İlk güçte ölçülür (bölüm 6, adım 5).
6. **SDI/SDO = MOSI/MISO eşlemesi belgede yok** (*) → bölüm 6, adım 8.

## 1. Sinyal bağlantıları (harici kablolar)

Kablo = RAK13002 2,54 mm başlığı ↔ harici modül/devre. Başlık sütun/sıra düzeni (R13): sütun 1 `VCC GND IO1 IO3 IO4 IO5 IO6 IO7`, sütun 2 `VCC GND SCL1 SDA1 SCL2 SDA2 LED1 LED2`, sütun 3 `VCC GND TXD0 RXD0 TXD1 RXD1 AIN0 AIN1`, sütun 4 `VCC GND CS SDI SDO SCK RST SW1`.

### 1a. GC9A01 1,28" ekran (Waveshare 19192) — SPI + 3 GPIO

| # | Modül pini | RAK13002 başlık serigrafi | WisBlock sinyal / Arduino adı | nRF52840 GPIO (Arduino no) | Renk | Doğrulama |
|---|---|---|---|---|---|---|
| 1 | VCC | VCC | 3V3 | — | kırmızı | R13 (VCC), W (3,3 V/5 V) · (*) hat 3V3 mü 3V3_S mi |
| 2 | GND | GND | GND | — | siyah | R13, W |
| 3 | CLK (SCL) | SCK | WB_SPI_CLK = `PIN_SPI_SCK` | P0.03 (3) | mavi | V, R13 |
| 4 | DIN (SDA/MOSI) | SDI (*) | WB_SPI_MOSI = `PIN_SPI_MOSI` | P0.30 (30) | mavi | V; SDI=MOSI (*) DOĞRULANAMADI |
| 5 | CS | CS | WB_SPI_CS | P0.26 (26) | mavi | V, R13 |
| 6 | DC | IO3 | WB_IO3 | P0.21 (21) | turuncu | V, R13 |
| 7 | RST | IO4 | WB_IO4 | P0.04 (4) | turuncu | V, R13 |
| 8 | BL | IO5 | WB_IO5 | P0.09 (9) — NFC1 pini | turuncu | V, R13; M (IO5 = P0.09) · BL sürücüsü (*) bölüm 5 |

Not: Ekran SPI'ı (P0.03/P0.29/P0.30) ile SX1262'nin SPI'ı (P1.11–P1.13, modül içi) ayrı pin kümeleridir; çakışma yok (R46, V). MISO (WB_SPI_MISO, P0.29) kullanılmaz; SDO'ya bir şey bağlama.

### 1b. LSM303AGR (Adafruit 4413) — I2C1

| # | Modül pini | RAK13002 başlık serigrafi | WisBlock sinyal | nRF52840 GPIO (Arduino no) | Renk | Doğrulama |
|---|---|---|---|---|---|---|
| 9 | VIN | VCC (ikinci VCC pini) | 3V3 | — | kırmızı | AF (VIN aralığı belirtilmemiş; regülatörlü kart) |
| 10 | GND | GND | GND | — | siyah | AF |
| 11 | SDA | SDA1 | WB_I2C1_SDA = `PIN_WIRE_SDA` | P0.13 (13) | yeşil | V, R13 |
| 12 | SCL | SCL1 | WB_I2C1_SCL = `PIN_WIRE_SCL` | P0.14 (14) | yeşil | V, R13 |

Adresler: ivme 0x19, manyeto 0x1E (AF, ST). Diğer pinler (INT, CS) bağlanmaz. Pull-up: RAK19007 veya Adafruit kartında olup olmadığı DOĞRULANAMADI; tarama başarısızsa harici 4,7 kΩ→3V3 dene.

### 1c. Tuş ve titreşim motoru

| # | Bağlantı | RAK13002 başlık serigrafi | WisBlock sinyal | nRF52840 GPIO (Arduino no) | Renk | Doğrulama |
|---|---|---|---|---|---|---|
| 13 | S1 bir ucu | SW1 | WB_SW1 | P1.01 (33) | turuncu | V (SW1=33); R13. Not: Meshtastic belge sayfası SW1'i P0.01 gösteriyor — RAK `variant.h` ile çelişiyor, RAK değerine uyuldu. |
| 14 | S1 diğer ucu | GND | GND | — | siyah | — |
| 15 | R1 (100 Ω) girişi | IO6 | WB_IO6 | P0.10 (10) — NFC2 pini | turuncu | V, R13, M |
| 16 | Motor + ucu, D1 katodu, C1/C2 | VCC (üçüncü VCC pini) | 3V3 | — | kırmızı | R13 · (*) 3V3/3V3_S |
| 17 | Q1 kaynak (S), R2, C1/C2 − | GND | GND | — | siyah | — |

## 2. Kart içi bağlantılar (kablo yok; kayıt amaçlı)

| Sinyal | Nereden → nereye | nRF52840 GPIO (Arduino no) | Kaynak |
|---|---|---|---|
| I2C1 (SDA/SCL) | RAK4631 → Yuva A (RAK12500, pin 8/7) ve IO yuvası (RAK13002 SDA1/SCL1) | P0.13 / P0.14 | V, R19 |
| RAK12500 1PPS | Yuva A pin 12 → WB_IO1 | P0.17 (17) | R12 (1PPS pin 12), R19 (Yuva A pin 12 = IO1), M (yorum: "IO1 is hooked to PPS") |
| RAK12500 RESET + 3V3_S enable | Yuva A pin 10 → WB_IO2 | P1.02 (34) | R19 ("IO2 used for 3V3_S enable", Yuva A pin 10 = IO2), M; RESET için forum |
| Pil gerilimi | taban kartı bölücüsü → WB_A0 | P0.05 / AIN3 (5) | V (WB_A0=5), M ("AIN3 with VBAT divider = VBAT·1.5/2.5", ADC_MULTIPLIER 1.73), R46 (P0.05/AIN3). RAK19007 sayfası AIN pini belirtmiyor (R19 sadece J11 pin 4 = VBAT diyor) |
| SX1262 NSS | modül içi | P1.10 (42) | R46, M |
| SX1262 SCK / MOSI / MISO | modül içi | P1.11 (43) / P1.12 (44) / P1.13 (45) | R46 (Arduino numaraları 32+x'ten hesaplandı) |
| SX1262 BUSY | modül içi | P1.14 (46) | R46, M |
| SX1262 DIO1 | modül içi | P1.15 (47) | R46, M |
| SX1262 NRESET | modül içi | P1.06 (38) | R46, M |
| RF anahtarı güç (ANT_SW / `SX126X_POWER_EN`) | modül içi | P1.05 (37) | R46, M. RXEN/TXEN **yok** (M'de yorumlu; "GPIO 39/TXEN tanımlanmamalı" notu). |
| DIO2 → RF anahtarı | modül içi | (DIO2, nRF pini yok; R46: P1.07 şematikte bağlı ama "başlatma" deniyor) | R46, M (`SX126X_DIO2_AS_RF_SWITCH`) |
| DIO3 → TCXO gerilimi | modül içi | — | R46 (DIO3 TCXO'yu besler); gerilim 1,8 V: yalnızca M (`SX126X_DIO3_TCXO_VOLTAGE 1.8`), RAK belgesinde yok → KISMEN |

## 3. Besleme hatları

| Hat | Kaynağı | Hangi uçlarda | Not / kaynak |
|---|---|---|---|
| **VBAT** | LiPo → P2 (JST PHR-2, 2 mm) | RAK19007 çekirdek konektör pin 1–2; J11 pin 4 | 3,3 V min / 3,7 V tip. / **4,3 V max**; şarj 4,2 V/350 mA, USB-C'den; "pil 4,3 V'u geçmemeli" (R19). Kırmızı = +, kutup ölç. |
| **VBUS 5 V** | USB-C | şarj girişi | 4,5–5,5 V; güneş paneli girişi JST ZHR-2 (1,5 mm), 5,5 V max (R19) |
| **3V3 (sürekli)** | taban kartı regülatörü | çekirdek pin 5/6/17/18; RAK13002 pin 5, 17, 18; J12 pin 1 (VDD, "3,3 V") | RAK13002 başlığında 4 adet "VCC" pini var (R13). Hangi ana hatta bağlı olduğu (*) |
| **3V3_S** | taban kartında WB_IO2 ile anahtarlanan 3,3 V | tüm sensör yuvaları A–D pin 11 ve 14 (R19); RAK12500 pin 11, 14 (R12); RAK13002 40 pinli tabloda pin 6 | IO2 kapatınca 3V3_S kapanır; RAK19007 IO yuvası tablosu sayfada yok → RAK13002'ye 3V3_S gelip gelmediği (*) |
| **VDD** | CPU modülünden gelen seviye | sensör yuvaları pin 9 ve 16; J12 pin 1 | "MCU IO seviyesi 3,3 V değilse sensör kartı için üretilir"; RAK4631'de 3,3 V |
| **GND** | — | tüm modüller | Başlıkta 4 GND pini; tek bir GND dönüşü zincirleme yapma, her modül için ayrı GND pini kullan |

Güç dağılımı: ekran, LSM303AGR ve motor RAK13002 başlığındaki VCC pinlerinden beslenir (kırmızı hatlar); RAK12500 yuvadan beslenir. Boş taban kartı akımı: sızıntı <2 µA, boşta (MCU/sensörler uykuda) <10 µA, LoRa TX anında 130 mA'e çıkabilir (R19).

## 4. Motor sürücü devresi (Q1)

```
 3V3 ──┬──────────────┬───────────┐
       │              │           │
     (100µF       katot K      motor +
      + 100nF)        D1 ▼        M1 (ERM, 3 V)
       │          anot A          │
       │              │       motor −
       │              └───────────┤
 GND ──┘                          │
                            Q1 drain (D)
 WB_IO6 ──[R1 100Ω]──┬── Q1 gate (G)
                     │
                  [R2 100kΩ]      Q1 source (S) ── GND
                     │
                    GND
```

| Bileşen | Değer / tip | İşlev |
|---|---|---|
| Q1 | N-MOSFET, mantık seviyeli: Vgs(th) < 1,5 V, Id ≥ 0,5 A, Rds(on) 3,3 V'ta düşük (öneri BSS138 veya IRLZ44N; veri sayfası kontrol edilecek) | Düşük-taraf anahtar |
| R1 | 100 Ω | Gate seri direnci (GPIO'daki gate şarj akımı darbesini ve zil sesini sınırlar) |
| R2 | 100 kΩ | Gate pull-down: açılış/uykuda kapalı |
| D1 | Schottky, ör. 1N5819 | Motor endüktansının ters (flyback) gerilimini şöntler; **katot +3V3 tarafında** |
| C1 / C2 | 100 µF / 100 nF, motor + ile GND arasında, motora yakın | Kalkış akımı çökmesini sınırlar |

Boyutlama notu (tahmin): ERM motor akımı ölçülecek; Q1'in Id değeri ve D1 akımı bu ölçüme göre kontrol edilir. 3V3 hattı motorla birlikte LoRa TX (≈90–130 mA) ve GNSS ile çakışırsa regülatör limiti RAK19007 sayfasında yazmadığı için dikkat (*).

## 5. Ekran arka ışığı (BL) — iki durum

Waveshare 19192 sayfası BL pini için tür bilgisi vermiyor (**DOĞRULANAMADI**: transistör girişi mi, doğrudan LED mi). Güvenli yol:

1. Ekran VCC/GND bağlı, BL **bağlantısız** iken multimetreyle 3V3→BL kısa akımını ölç (BL pini 3V3'e 1 kΩ üzerinden): akım < 1 mA ise BL bir transistör/mantık girişidir → **BL'yi doğrudan WB_IO5'e bağla** (PWM ile kısılabilir).
2. Akım onlarca mA ise BL doğrudan LED hattıdır → WB_IO5'e **bağlama**; ekran-tarafı BL'yi Q2 (motordakiyle aynı tip N-MOSFET) ile sür: WB_IO5 → R1' 100 Ω → Q2 gate (R2' 100 kΩ pull-down), Q2 drain → BL (LED katodu tarafıysa) — LED'in anot/katot yönü modül şemasından doğrulanmadan bu bağlantı yapılmaz (**DOĞRULANAMADI**).
3. Çıplak panel (P1) için referans: DM-TFTR128-446 arka ışığı 2 LED paralel, 3,0 V'ta tip. 40 mA / maks. 60 mA (bkz. `BOM-P1-aday.md`) — 3,3 V hattından seri dirençsiz sürülmez.

## 6. Kurulum sırası ve ilk enerji verme kontrol listesi

### 6.1 Sıra

1. Güçsüz: RAK4631'i CPU yuvasına, **RAK12500'ü Yuva A'ya**, RAK13002'yi IO yuvasına tak. Konnektörleri eşit bastır (WisBlock'ta yuva yön işareti var).
2. Anten: **LoRa anteni ve GNSS anteni takılmadan enerji verme** (verici antensiz çalıştırılmamalı).
3. RAK13002 başlığının lehimli olduğunu kontrol et; değilse header'ı lehimle.
4. Breadboard üzerinde Q1/R1/R2/D1/C1/C2/S1'i kur; modülleri jumperlarla `baglanti-semasi` rengine göre bağla (kırmızı/siyah/mavi/yeşil/turuncu). Henüz USB ve pil TAKILI DEĞİL.

### 6.2 Kısa devre kontrolü (güç yokken)

5. Multimetre süreklilik: RAK13002 başlığı VCC ↔ GND **açık devre** olmalı. Ekran VCC ↔ GND, LSM303AGR VIN ↔ GND, motor + ↔ GND açık olmalı (D1/R2 yönüne dikkat: R2 gate–GND arasında 100 kΩ okunur, VCC–GND'de değil).
6. D1 yönü: multimetre diyot modunda katot (çizgili uç) +3V3 tarafı.

### 6.3 İlk enerji (önce USB, pil yok)

7. USB-C ile bağla. RAK19007 kırmızı LED şarjda yanar (pil yokken davranışı sayfada yok). Herhangi bir parça ısınıyorsa hemen USB'yi çek.
8. Gerilim ölçümleri (RAK13002 başlığı VCC–GND): **3,2–3,4 V** beklenir. Ardından yazılımla WB_IO2'yi YÜKSEK/DÜŞÜK yap ve başlık VCC'nin değişip değişmediğine bak → 3V3 mü 3V3_S mi bilgisini **kayda geçir** (bölüm 0, madde 5). Ekran VCC'si, LSM VIN'i, motor + ucu aynı gerilimde olmalı.
9. SPI SDI/SDO eşlemesi: yazılımdan P0.30'u (pin 30) GPIO olarak 1 Hz sür; hangi başlık pininin (SDI mi SDO mu) değiştiğini ölç. DIN'i o pine bağla (*).
10. I2C taraması (Wire, SDA=13, SCL=14, 100 kHz): beklenen adresler **0x19, 0x1E, 0x42**. 0x42 yalnızca WB_IO2 YÜKSEK iken ve GNSS açıkken görünür (adres 0x42 u-blox varsayılanıdır; RAK belgesinde yazmıyor (*)). 0x19/0x1E yoksa: SDA/SCL ters mi, VIN gerilimi var mı, pull-up (4,7 kΩ).
11. Tuş: `pinMode(WB_SW1, INPUT_PULLUP)`, basınca LOW okunmalı.
12. Ekran: DC/RST/CS sürülüp arka ışık testi (BL durumu bölüm 5'e göre).
13. Motor: kısa (100 ms) darbe, PPK2 ile tepe akımı ölç; Q1 ısınmamalı.

### 6.4 Pil

14. Pil takmadan önce LiPo konektöründe kırmızı kablonun RAK19007 P2'deki + ucuna denk geldiğini multimetreyle kontrol et (JST-PH pil ↔ PHR-2 soket; kutup ters olabilir). Pil gerilimi 3,0–4,2 V arası olmalı (4,3 V'u geçmemeli).
15. `analogRead(WB_A0)` ile pil gerilimini oku (P0.05/AIN3; bölücü oranı belgelenmedi — Meshtastic ADC_MULTIPLIER 1,73; ADC çözünürlüğü kodda ayarlanır; multimetreyle kalibre et (*)).
16. Pille PPK2 ölçümü: nRF52840 uykuda, LoRa uykuda, GNSS kapalı: kart toplamı onlarca µA mertebesinde olmalı (R19: boşta <10 µA; R46: modül uykusu 2 µA). Belirgin yüksekse (mA) ekran/LSM/motor devresinde sızıntı ara.

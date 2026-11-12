# Findy — Referans Mimari v0.1

Tarih: 11 Kasım 2026. Durum: **doğrulanmamış tasarım.** Hiçbir parça alınmadı,
hiçbir ölçüm yapılmadı. Bu belge, deney planındaki A adayını (sub-GHz LoRa +
GNSS + pusula) ilk yapılacak prototip olarak somutlaştırır. Radyo mimarisi
**seçilmiş değildir**; seçim `deney-duzenegi-plani.md` sonuçlarıyla yapılır.
B/C/D adayları bu yazılımın radyo katmanı değiştirilerek denenir.

Bu belge yazılım, çizim ve parça listesi için tek kaynak (spec) belgesidir.

> **Önce bölüm 12'yi okuyun.** Üretici belgeleriyle yapılan doğrulama bölüm 3, 4, 6
> ve 10'da hatalar buldu; düzeltmeler bölüm 12'dedir ve öncekilerin yerine geçer.

## 1. İki Aşama

| Aşama | Ne | Amaç |
|---|---|---|
| **P0 — Tezgâh prototipi** | RAK WisBlock hazır modülleri + yuvarlak ekran, lehimsiz/az lehimli | Deney planının Faz 0–5'i. Boyut önemsiz. |
| **P1 — Ürün konsepti** | 40 mm yuvarlak gövde, özel kart | Mekanik çizim ve yerleşim hedefi. Kart tasarımı (şema/gerber) bu sürümde **yok**. |

P0 ile P1 aynı radyo+işlemci modülünü kullanır (P0: RAK4631 çekirdek kartı,
P1: üzerindeki RAK4630 modülü), böylece P0 ölçümleri P1'e taşınabilir. Anten
farklı olacağı için menzil taşınmaz.

## 2. P0 Blok Şeması

```
              +----------------------- RAK19007 taban kartı ----------------------+
 LiPo 3.7V ---| şarj + 3V3 reg.     3V3 (sürekli)        3V3_S (WB_IO2 ile anahtarlı) |
 USB-C -------|                        |                        |                   |
              |  [RAK4631 çekirdek]    |                        |                   |
              |   nRF52840 (BLE)       |                        |                   |
              |   SX1262 (LoRa 868) ---+--> anten (868 MHz)     |                   |
              |        |  SPI   I2C1   UART  GPIO               |                   |
              +--------|-----|------|-----|---------------------|-------------------+
                       |     |            |                     |
     IO yuvası: RAK13002 adaptör          |        Yuva A: RAK12500 GNSS (I2C1, 3V3_S)
        |-- SPI  --> GC9A01 1.28" yuvarlak TFT (CS, DC, RST, BL)
        |-- I2C1 --> LSM303AGR pusula + ivmeölçer (3V3 sürekli)
        |-- GPIO --> tuş (WB_SW1), titreşim motoru sürücüsü (WB_IO6)
```

## 3. Pin Ataması (WisBlock sinyal adlarıyla)

Yazılım yalnızca bu sembolik adları kullanır (RAK4631 Arduino BSP `variant.h`).
Fiziksel pin/başlık konumu `hardware/baglanti-tablosu.md` içinde, üretici
belgesiyle doğrulanarak verilir.

| İşlev | Sinyal | Not |
|---|---|---|
| LoRa SX1262 | modül içi | NSS, DIO1, BUSY, RESET, anten anahtarı modül içinde bağlı; TCXO DIO3'ten, RF anahtarı DIO2'den |
| Ekran SCK / MOSI | `PIN_SPI_SCK` / `PIN_SPI_MOSI` | MISO kullanılmaz |
| Ekran CS | `WB_SPI_CS` | |
| Ekran DC | `WB_IO3` | |
| Ekran RST | `WB_IO4` | |
| Ekran arka ışık | `WB_IO5` | PWM; modülde sürücü transistör yoksa N-MOSFET ile |
| Titreşim motoru | `WB_IO6` | N-MOSFET + ters diyot |
| Tuş | `WB_SW1` | Aktif düşük, dahili pull-up, uykudan uyandırır |
| GNSS güç | `WB_IO2` | 3V3_S hattını açar/kapatır |
| GNSS veri | I2C1 (`WB_I2C1_SDA/SCL`), adres 0x42 | u-blox UBX protokolü |
| Pusula + ivmeölçer | I2C1, 0x19 (ivme) / 0x1E (manyeto) | LSM303AGR |
| Pil gerilimi | `WB_A0` | Taban kartındaki bölücü üzerinden |

`WB_IO1` boş (yedek). I2C1 hattında iki cihaz var (GNSS, LSM303AGR).

## 4. Radyo Protokolü "FindyLink" v0

### Fiziksel katman
- Frekans 869,525 MHz (AB 869,4–869,65 MHz alt bandı: %10 görev döngüsü sınırı). Kullanılacak ülkede yasal koşul sipariş öncesi doğrulanacak.
- LoRa: BW 125 kHz, SF8, CR 4/5, önek 8 sembol, CRC açık, sync word 0x46.
- Güç: varsayılan +14 dBm (ayarlanabilir, modül üst sınırı +22 dBm).
- Hepsi derleme zamanı ayarı; Faz 1'de SF7/SF8/SF9 karşılaştırılır.

### Çerçeve ve dilimler (5 cihaz)
- Bir çerçeve 5 eşit dilime bölünür; cihaz `node_id` (0–4) numaralı dilimde yayın yapar.
- Çerçeve süresi kipe göre: **BEKLEME 15 sn**, **ARAMA 5 sn**. Gruptan herhangi biri ARAMA kipindeyse (pakette bayrak) herkes ARAMA'ya geçer; son ARAMA bayrağından 60 sn sonra BEKLEME'ye dönülür.
- Zaman kaynağı önceliği: (1) GNSS UTC zamanı → çerçeve başlangıcı `utc_ms mod çerçeve_süresi == 0`; (2) GNSS yoksa alınan ilk geçerli paketten çıkarılan çerçeve fazı; (3) hiçbiri yoksa kendi serbest saat.
- Alıcı, her diğer dilimin başında `±GUARD_MS` (varsayılan 120 ms) + paket süresi kadar dinler, sonra radyo uyur. Zaman eşitlemesi yokken bir tam çerçeve boyunca sürekli dinler ve bunu 4 çerçevede bir tekrarlar.

### Paket (şifresiz başlık + şifreli yük + doğrulama)
Tüm çok baytlı alanlar little-endian.

| Alan | Bayt | Açıklama |
|---|---|---|
| `magic` | 1 | 0xF1 |
| `group_id` | 2 | Grup anahtarının BLAKE2s özetinin ilk 2 baytı |
| `hdr` | 1 | bit 0–2 `node_id`, bit 3–7 protokol sürümü (0) |
| `counter` | 4 | Cihaz başına artan sayaç (tekrar saldırısı ve nonce için); kalıcı saklanır, her açılışta +1000 atlanır |
| — şifreli yük — | 14 | ChaCha20-Poly1305 ile |
| `lat_e7` | 4 | int32, derece × 1e7 |
| `lon_e7` | 4 | int32 |
| `fix_age_s` | 1 | Son konumun yaşı (sn, 255 = doymuş / konum yok) |
| `hacc_m` | 1 | Yatay doğruluk tahmini (m, 255 = bilinmiyor) |
| `batt_pct` | 1 | 0–100 |
| `flags` | 1 | bit0 ARAMA, bit1 PING (arkadaşı titret), bit2 hareketsiz, bit3–7 PING hedef maskesi için ayrılmış |
| `ping_target` | 1 | bit i = node i hedef (PING bayrağı varsa) |
| `rsv` | 1 | 0 |
| `tag` | 8 | Poly1305 etiketinin ilk 8 baytı |

Toplam 30 bayt. Nonce (12 bayt) = `node_id` (1) ‖ 0x00×7 ‖ `counter` (4).
Ek doğrulanmış veri (AAD) = ilk 8 bayt (başlık). Anahtar: 32 baytlık grup anahtarı.
Alıcı: `group_id` uymuyorsa veya etiket tutmuyorsa paketi atar; aynı `node_id`
için son kabul edilen `counter`'dan küçük/eşit olanı atar.

### Eşleşme (v0, bilinen zayıflıkla)
- İki cihazda tuşa 5 sn basılır → EŞLEŞME kipi (30 sn). Radyo en düşük güçte (−9 dBm) çalışır.
- Grubu olmayan cihaz **katılımcı**, grubu olan (veya ilk basan) **kurucu**dur. Kurucu `PAIR_OFFER` (magic 0xF2, grup anahtarı 32 bayt, atanan `node_id`, CRC16) yayınlar; katılımcı yalnızca RSSI > −45 dBm (temas mesafesi) ise kabul eder ve `PAIR_ACK` gönderir.
- **Bilinen zayıflık:** anahtar havadan açık gider. Yakındaki bir dinleyici ele geçirebilir. v0.2'de X25519 anahtar değişimi + ekranda doğrulama kodu ile değiştirilecek. v0 yalnızca deney içindir.
- Kurucu en çok 5 `node_id` dağıtır; dolunca teklif etmez.

## 5. Konum, Yön, Mesafe

- Mesafe: haversine. Yön açısı (bearing): kendi konumundan arkadaş konumuna büyük daire başlangıç açısı.
- Ok açısı = bearing − pusula başı (heading). Heading: LSM303AGR ivme + manyeto ile eğim düzeltmeli; manyetik sapma (declination) v0'da ayar sabiti.
- Pusula kalibrasyonu: açılışta ve menüden "8 çiz" hard-iron ofset kalibrasyonu; ofsetler kalıcı saklanır.
- Cihaz yataya göre 60°'den fazla eğikse (kolye gibi asılı) ok gizlenir, "düz tut" simgesi gösterilir.
- Güven göstergesi: `hacc_m` toplamı mesafenin yarısından büyükse ok yerine yalnızca mesafe halkası ("yakınında") gösterilir. Eşik deneyle ayarlanacak.
- Konum yaşı > 60 sn ise arkadaş soluk çizilir; > 5 dk ise "son görülme" olarak işaretlenir.

## 6. Güç Yönetimi

Hedef: ortalama ≤ 7 mA. Aşağıdakiler **veri sayfası tipik değerlerine dayalı tahmindir**, Faz 4'te ölçülecek.

| Tüketici | Durum | Tahmini akım | Görev oranı (BEKLEME) | Katkı |
|---|---|---|---|---|
| nRF52840 | uyku + RTC | ~0,01 mA | ~%100 | ~0,01 mA |
| SX1262 RX | dinleme | ~5 mA | ~%6 | ~0,3 mA |
| SX1262 TX | +14 dBm | ~45 mA | ~%0,7 | ~0,3 mA |
| GNSS (ZOE-M8Q) | izleme | ~20–25 mA | hedef ≤ %15 | ≤ ~3,5 mA |
| Ekran | açık | ~20–40 mA | kullanıma bağlı | ayrı senaryo |
| LSM303AGR | düşük güç | ~0,05 mA | %100 | ~0,05 mA |

Sonuç: **GNSS bütçenin en büyük kalemi ve en büyük risk.** Kurallar:
- GNSS görev döngülü: BEKLEME'de 30 sn'de bir konum; ARAMA'da 5 sn'de bir veya sürekli.
- İvmeölçer 60 sn hareketsizlik görürse GNSS kapatılır, pakete "hareketsiz" bayrağı konur, son konum yayınlanmaya devam eder.
- Ekran varsayılan kapalı. Tuş veya bilek kaldırma → avatar 3 sn → radar ekranı; 10 sn etkileşimsizlikte kapanır.
- P1 için daha düşük güçlü bir GNSS (u-blox M10 sınıfı) hedeflenir.

## 7. Arayüz (240×240 yuvarlak)

| Ekran | İçerik |
|---|---|
| AVATAR | Kendi avatarı (96×96 RGB565, 2× büyütülmüş, dairesel maske) + lime halka. Uyanınca 3 sn. |
| RADAR | Merkez = ben. En çok 4 arkadaş, yönüne göre çevrede nokta, mesafeye göre 3 halka (≤50 m, ≤200 m, >200 m). Seçili arkadaş için büyük ok + ad + mesafe (ör. "DENIZ 24 m"). |
| EŞLEŞME | İlerleme halkası, atanan numara. |
| DURUM | Pil, GNSS durumu, grup üye sayısı, sürüm. |

Tuş: kısa bas = uyandır / sonraki arkadaş · çift bas = DURUM · 1,5 sn bas = seçili arkadaşa PING (onu titretir, ARAMA kipini başlatır) · 5 sn bas = EŞLEŞME · 10 sn bas = gruptan çık.

Renkler: arka plan siyah, vurgu lime `#C6FF3D`, metin beyaz, soluk gri `#5A5F66`.

## 8. Telefon Bağlantısı (isteğe bağlı, BLE)

Nordic UART Service üzerinden satır tabanlı komutlar. Bulma işlevi telefonsuz çalışır.

| Komut | İşlev |
|---|---|
| `NAME <ad>` | Kendi adı (≤ 8 karakter, ASCII büyük harf) |
| `AVATAR BEGIN <bayt>` … ikili parçalar … `AVATAR END <crc32>` | 96×96 RGB565 (18 432 bayt) avatar yükleme |
| `STATUS` | JSON durum satırı |
| `LOG ON/OFF` | Deney kaydı: alınan her paket için CSV satırı (zaman, node, RSSI, SNR, konumlar) |
| `CFG <anahtar> <değer>` | SF, güç, çerçeve süresi, declination |

v0'da arkadaş adları/avatarları radyodan aktarılmaz; arkadaşlar "1–5" numarasıyla
ve varsa `NAME` komutuyla elle girilen adla gösterilir (`FRIEND <id> <ad>`).

## 9. Yazılım Yapısı

```
firmware/
  platformio.ini            # env:rak4631 (hedef), env:native (birim testleri)
  lib/findy_core/           # TAŞINABİLİR C++17, donanım bağımsız, Arduino'suz derlenir
    geo.{h,cpp}             # haversine, bearing, ok açısı
    packet.{h,cpp}          # paket kodlama/çözme (şifreleme arayüzü soyut)
    slots.{h,cpp}           # çerçeve/dilim zamanlayıcı, kip geçişleri
    group.{h,cpp}           # üye tablosu, tekrar koruması, yaşlandırma
    compass.{h,cpp}         # eğim düzeltmeli heading, kalibrasyon matematiği
    button.{h,cpp}          # basış süresi/çift basış durum makinesi
    power_model.{h,cpp}     # kip başına görev oranı → tahmini ortalama akım
  src/                      # donanım katmanı (Arduino, RAK4631)
    main.cpp, board_pins.h, radio_sx1262.cpp, gnss_ublox.cpp,
    imu_lsm303agr.cpp, display_ui.cpp, ble_link.cpp, storage.cpp, crypto_port.cpp
  test/                     # yerel (PC) birim testleri — donanımsız çalışır
tools/
  findy_ble.py              # BLE komut satırı aracı (avatar yükleme, log alma)
  avatar_convert.py         # resim → 96×96 RGB565
```

## 10. P1 — Ürün Konsepti (40 mm)

Hedef dış ölçü: çap 40 mm, kalınlık hedefi ≤ 13 mm (yığın hesabı çizimde).

Katman yığını (üstten alta, hedef değerler):

| Katman | Kalınlık |
|---|---|
| Kapak camı | 1,0 mm |
| 1,28" yuvarlak TFT panel | ~1,6 mm |
| Orta çerçeve / boşluk | 0,6 mm |
| Kart (PCB) | 0,8 mm |
| Bileşenler (en yüksek: radyo modülü) | ~3,0 mm |
| LiPo pil (~4×25×30 mm sınıfı, 250–300 mAh, katalogdan doğrulanacak) | ~4,2 mm |
| Arka kapak | 1,2 mm |
| **Toplam** | **~12,4 mm** |

P1 açık riskleri:
- **868 MHz anten.** Çeyrek dalga ~86 mm; 40 mm gövdeye sığmaz. Seçenekler: gövde çevresinde kıvrımlı FPC anten, kayışın/askının içinde anten, çip anten (verim düşük). Menzil hedefini doğrudan etkiler; ayrı anten çalışması gerekir.
- GNSS anteni (seramik yama ~12–15 mm) ekranın altında kalamaz; yerleşim çakışması.
- Su dayanımı, şarj yöntemi (pogo pin / manyetik / USB-C) seçilmedi.

## 12. Düzeltmeler (11 Kasım 2026, üretici belgeleriyle doğrulama sonrası)

Yukarıdaki bölümler ilk yazıldığı haliyle bırakıldı; **aşağıdakiler onların yerine geçer.**
Kaynaklar ve ayrıntı: `hardware/dogrulama-notlari.md` (H numaraları oradaki maddelerdir).

| # | Yanlış olan | Doğrusu / karar |
|---|---|---|
| H1 | §3, §6: GNSS `WB_IO2` ile kapatılıp açılır, görev oranı ≤ %15 | RAK12500'de yedek besleme (V_BCKP) yok; besleme kesilince her açılış soğuk başlangıçtır (tipik ~26 sn). **3V3_S çalışırken kesilmez.** v0 yazılımında GNSS sürekli 1 Hz açık. Güç tasarrufu ancak yazılım yedek kipi / güç tasarruf kipiyle ve ölçümden sonra. |
| H2 | §3: `WB_IO1` boş | Yuva A'daki RAK12500 `WB_IO1`'i 1PPS çıkışı olarak kullanır. Başka işe bağlanmaz. İleride dilim zamanlaması için PPS okunabilir. |
| H3/H4 | §3: `WB_IO2` yalnızca güç anahtarı | Aynı hat GNSS RESET'tir ve RAK13002 başlığında yoktur. Açılışta yazılım YÜKSEK sürer. RAK12500 **yalnızca Yuva A'ya** takılır (Yuva C'de ekranın DC/RST pinleriyle çakışır). |
| H5 | §3: arka ışık `WB_IO5`, motor `WB_IO6` | Bu pinler nRF52840'ın NFC pinleridir (P0.09/P0.10). Derleme bayrağı `CONFIG_NFCT_PINS_AS_GPIOS` eklendi; çalıştığı ilk donanım testinde doğrulanacak. |
| H6 | §6: TX +14 dBm ≈ 45 mA, RX görev oranı ≈ %6 | TX +14 dBm, varsayılan PA ayarında ≈ 90 mA olabilir (45 mA yalnızca optimize ayarda). RX görev oranı guard iki yanda sayılınca ≈ %9,7 (BEKLEME). |
| H7 | §3: pil ölçümü `WB_A0`, taban kartı bölücüsü | Üretici sayfasında yazmıyor; topluluk kaynağına göre doğru. İlk güçte multimetreyle karşılaştırılacak. |
| H9 | §10: pil ~4×25×30 mm, 250–300 mAh | **Sığmıyor** (köşegen ≈ 39 mm, iç boşluk Ø36,8). Katalogdan sığan örnek: ~20×26×3,8 mm, 150 mAh. |
| H10 | §4: "%10 görev döngüsü" | Sınır bir saatlik pencerede ve 500 mW e.r.p. olarak tanımlı. AB için doğrulandı; Türkiye kısmen, Kıbrıs doğrulanamadı. |

### Düzeltilmiş güç tablosu (hâlâ tahmin, ölçülmedi)

| Tüketici | P0 (RAK12500, sürekli GNSS) | P1 hedefi (M10 sınıfı GNSS, yedek beslemeli, görev döngülü) |
|---|---|---|
| GNSS | ~21–25 mA | 30 sn'de ~2 sn sıcak başlangıç varsayımıyla ~0,7 mA |
| LoRa RX (BEKLEME) | ~0,5 mA | ~0,5 mA |
| LoRa TX (BEKLEME) | ~0,4–0,75 mA | ~0,4–0,75 mA |
| İşlemci + sensör | ~0,1 mA | ~0,1 mA |
| **Toplam (ekran kapalı)** | **~22–26 mA** | **~1,7–2 mA** |

Sonuçlar:
- **P0 pil ömrü hedefi karşılamaz ve karşılaması beklenmez.** P0 menzil ve yön doğruluğunu ölçmek içindir; pil ömrü için değil.
- **P1 için 40 mm + 2–3 gün hedefi kâğıt üzerinde sınırda.** 150 mAh pil 60 saat için ortalama ≤ 2,5 mA ister. Yukarıdaki ~2 mA'lık P1 tahmini ekran kullanımını içermez ve "her 30 sn'de 2 sn'de konum" varsayımına dayanır — bu varsayım doğrulanmadı.
- Hedef tutmazsa seçenekler: çapı ~44–46 mm'ye büyütmek, gövdeye uygun (yuvarlak/özel) pil bulmak, kalınlığı artırmak, ya da pil hedefini ~1,5 güne indirmek. Karar kullanıcıya aittir ve Faz 4 ölçümünden sonra verilmelidir.

## 11. Bu Sürümde Olmayanlar

Telefon uygulaması · özel kart şeması ve gerber · sertifikasyon (CE/RED) ·
kapalı mekân konumlama · UWB · radyodan ad/avatar paylaşımı · güvenli eşleşme.

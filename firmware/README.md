# Findy P0 — Firmware

Referans: `docs/mimari-v0.1.md` (tek kaynak). Hedef: RAK4631 (nRF52840 + SX1262), WisBlock taban kartı
RAK19007, RAK12500 GNSS, GC9A01 yuvarlak ekran, LSM303AGR. **Henüz hiçbir donanım yok; hiçbir parça
alınmadı. Bu yazılım yalnızca PC'de birim testlerle ve kod incelemesiyle sınanmıştır.**

## Neyin doğrulandığı / doğrulanmadığı

| Parça | Durum |
|---|---|
| `lib/findy_core` (geo, packet, slots, group, compass, button, power_model, crypto_ref) | PC'de g++ ile derlendi, 33 birim testi geçti (RFC 8439 ve BLAKE2s vektörleri dahil) |
| `src/*` (donanım katmanı) | **Derlenmedi.** Bu makinede RAK nRF52 çekirdeği ve kütüphaneler yok. Yalnızca `main.cpp`, sahte `Arduino.h` ile sözdizimi/arayüz uyumu için `-fsyntax-only` denendi; RadioLib/GFX/SparkFun/Bluefruit/LittleFS çağrılarının hiçbiri derlenmedi |
| Pin atamaları, I2C adresleri, register değerleri | Belgeden/hafızadan; kod içinde `DOĞRULANACAK` ile işaretli |
| Menzil, pil ömrü, GNSS zaman doğruluğu, RX/TX akımları | **Ölçülmedi.** `power_model` yalnızca veri sayfası tahminlerini hesaplar |
| `platformio.ini` | Hiç çalıştırılmadı (PlatformIO yok); `env:native` özellikle denenmedi |

## Klasör yapısı

```
firmware/
  platformio.ini
  lib/findy_core/   taşınabilir C++17 çekirdek (Arduino'suz)
  src/              RAK4631 donanım katmanı (pinler yalnızca board_pins.h'de)
  test/             PC birim testleri + run_native_tests.sh
tools/              findy_ble.py (BLE aracı), avatar_convert.py (resim -> RGB565)
```

## Testleri çalıştırma (PlatformIO gerekmez)

```
bash firmware/test/run_native_tests.sh
```

Yalnızca `g++` (C++17) gerekir; AddressSanitizer + UBSan açık derlenir. Çıkış kodu 0 = hepsi geçti.
`FINDY_TEST_OUT=<dizin>` ile çıktı dizini verilebilir (varsayılan geçici dizin). PlatformIO `env:native`
tanımı vardır ama denenmemiştir; esas yol betiktir.

## Hedef derlemesi ve yükleme (denenmedi)

1. PlatformIO kur (`pip install platformio`).
2. `cd firmware && pio run -e rak4631` — ilk çalıştırmada `nordicnrf52` platformu ve `lib_deps`
   (RadioLib, Adafruit GFX, Adafruit GC9A01A, SparkFun u-blox GNSS) indirilir.
3. Yükleme: `pio run -e rak4631 -t upload` (RAK4631 bootloader'ı UF2/DFU; kart çift-reset ile bootloader'a
   alınabilir). Seri monitör: `pio device monitor`.
4. İlk derlemede beklenen sorunlar: C++17 bayrağının araç zincirince kabulü, `PIN_LORA_*` / `WB_*`
   makrolarının BSP'deki gerçek adları, RadioLib/SparkFun API sürüm farkları. Hepsi `DOĞRULANACAK` yorumlarıyla işaretlidir.

## Tasarım özeti

- Paket: 8 bayt açık başlık + 14 bayt şifreli yük + 8 bayt etiket = **30 bayt**; ChaCha20-Poly1305
  (etiket ilk 8 bayt), nonce = `node_id ‖ 0×7 ‖ counter`, AAD = başlık. `group_id` = BLAKE2s(anahtar)[0..2].
- Şifreleme `ICrypto` arayüzünün arkasındadır; hedefte de `RefCrypto` (bağımsız, ek kütüphanesiz) kullanılır.
  Yan kanal dayanıklılığı için özel çaba yoktur; üretim öncesi inceleme gerekir.
- Zamanlama: `findy_core/slots`. Tüm düğümler zaman damgasını 64 bit `ms` olarak verir (`millis64()` sarmayı önler).
- Tuş olayları **bırakılışta** üretilir (1,5 sn basış, 5 sn basışın yan etkisi olarak PING göndermesin diye).
  Kısa basış, çift basış penceresi (400 ms) yüzünden o kadar gecikmeli bildirilir.

## BLE (Nordic UART) komutları

Satır sonu `\n`. Cihaz `OK`, `ERR <neden>` ya da tek satır JSON döner.

| Komut | İşlev |
|---|---|
| `NAME <ad>` | ≤ 8 karakter, A-Z 0-9 |
| `FRIEND <1-5> <ad>` | arkadaş adı (v0'da radyodan aktarılmaz) |
| `STATUS` | JSON durum |
| `LOG ON/OFF` | alınan her paket için CSV satırı (`LOGCOLS,...` başlığı ilk satır) |
| `CFG sf\|pwr\|standby\|search\|decl\|calib <değer>` | SF 7-9, güç dBm, çerçeve süreleri (sn), declination (°), pusula kalibrasyonu |
| `AVATAR BEGIN 18432` ... ham veri ... `AVATAR END <crc32 hex>` | avatar yükleme; CRC32 zlib ile aynı |

Araç: `python3 tools/findy_ble.py status|name|friend|cfg|avatar|log` (`pip install bleak`).
Avatar hazırlama: `python3 tools/avatar_convert.py foto.jpg avatar.rgb` (96×96, daire, RGB565 little-endian, 18 432 bayt).
**Not:** `CFG sf` ve çerçeve süreleri tüm grup cihazlarında aynı olmalıdır; cihazlar arasında eşitlenmez.

## Spec'ten sapmalar / kendi kararlarım

1. **Tuş olayları bırakılışta**, süre eşiğine göre (yukarıda).
2. **ARAMA yayılımı:** spec "gruptan biri ARAMA'daysa herkes ARAMA'ya geçer; son bayraktan 60 sn sonra dön" der ama bayrağı
   kimin koyacağını belirtmez. Burada başlatıcı 60 sn bayrak koyar; BEKLEME'de bayraklı paket alan düğüm bir kez 60 sn röle
   eder (süre uzamaz, döngü olmaz). Dönüş = bilinen **son bayraklı paketin dilim başlangıcı + 60 sn** (herkes ortak anda döner).
   Sonuç: 60 sn'lik tek bir ARAMA, röleler yüzünden toplamda ~60-65 sn bayrak, ~120-125 sn ARAMA kipi sürebilir. UTC yoksa
   dönüşte BEKLEME çerçeve fazı bu ortak çapaya göre yeniden kurulur.
3. **Faz modeli:** `ağ_fazı = (yerel_ms + offset) mod 15000`; 5 sn'lik ARAMA çerçevesi 15 sn'nin böleni olduğundan tek ofset iki kipe de uyar.
4. **Dinleme penceresi** `[dilim_başı − guard, dilim_başı + guard + hava_süresi)`. SF8/BW125 için 30 baytın hava süresi ≈ 123 ms
   (Semtech formülü, elle hesap, ölçülmedi). Bu pencereyle BEKLEME RX görev oranı ≈ %9,7'dir; spec tablosundaki ~%6 değerinden
   yüksek, çünkü ±120 ms guard dahil. Modelde ortalama ≈ 4,3 mA (GNSS %15 varsayımıyla); spec toplamı ≈ 4,2 mA.
5. **PAIR_ACK** biçimi spec'te yok: `0xF3 ‖ group_id(2) ‖ node_id ‖ CRC16`. PAIR_OFFER: `0xF2 ‖ anahtar(32) ‖ node_id ‖ CRC16` (36 bayt).
   CRC16 = CCITT-FALSE. Anahtarsız (ilk basan) iki cihazda: 3-5 sn teklif dinler, gelmezse kendi anahtarını üretip kurucu olur.
6. **Sayaç kalıcılığı:** açılışta `kayıtlı + 1000` atlanır ve hemen yazılır; çalışırken her 256 pakette bir yazılır (256 < 1000 olduğundan
   güç kesintisinde nonce yeniden kullanılmaz). Replay denetimi yalnızca **etiket doğrulandıktan sonra** sayacı ilerletir.
7. **Eksen düzeni:** çekirdek `x=sağ, y=ekran üstü, z=ekrandan dışarı` bekler; sensör→aygıt eşlemesi `board_pins.h`'de ve tezgâhta kalibre edilmeli.
8. **Avatar dosya biçimi** (spec "96×96 RGB565" der, bayt sırası yok): little-endian.
9. `node_id ≥ 5` olan paketler (3 bitlik alan 5-7 alabilir) `BadVersion` koduyla reddedilir.

## `DOĞRULANACAK` listesi (özet)

- SX1262 pinleri (`PIN_LORA_*`: NSS 42, SCLK 43, MOSI 44, MISO 45, BUSY 46, DIO1 47, RESET 38 — hafızadan), LoRa için ayrı SPI bloğu
  (`SPIClass(NRF_SPIM2, ...)`), TCXO 1,8 V, DIO2 RF anahtarı, RadioLib `syncWord` 0x46 genişletmesi, `getTimeOnAir` birimi.
- `WB_SPI_CS` adı, `WB_SW1` tuşunun gerçek yeri, `Wire` = I2C1 varsayımı, `analogWrite` ile PWM arka ışık.
- Adafruit_LittleFS `File` API'si ve sil+yaz ile güç kesintisi dayanıklılığı.
- Bluefruit `configPrphConn` imzası, `sd_rand_application_vector_get` başlık yolu.
- SparkFun u-blox: `getTimeValid/getDateValid/getMillisecond/getHorizontalAccEst/powerOff` adları.
- LSM303AGR register değerleri (CTRL/CFG), otomatik adres artışı, ivme/manyeto eksen farkları.
- Pil bölücü katsayısı (1,73) ve 3,0 V iç referans.

## Bilinen eksikler

- **Donanım katmanı derlenmedi**; ilk gerçek derlemede API uyumsuzlukları çıkması beklenir.
- **GNSS görev döngüsü yok:** v0'da GNSS sürekli 1 Hz açık kalır ve 3V3_S hiç kesilmez (RAK12500'de V_BCKP yok; kesmek her
  seferinde soğuk başlangıç demek — bkz. `docs/mimari-v0.1.md` bölüm 12, H1). Spec'teki "30 sn'de bir konum, ≤ %15 görev" **uygulanmadı**;
  bu yüzden P0'ın ortalama akımı 7 mA hedefinin çok üstünde olacaktır.
- **GNSS UTC doğruluğu bilinmiyor:** PPS/TIMEPULSE bağlı değil, I2C ile okunan zaman damgası gecikmeli olabilir; hata ±120 ms guard'ı aşarsa dilimler kayar.
  UTC varken paketten faz düzeltmesi yapılmaz (öncelik kuralı). Bu ölçülmeli.
- Bilek kaldırma ile uyandırma yok (yalnızca tuş). Ekran yeniden çizimi tam kare (≈100 ms SPI; 5 Hz) — güç/CPU maliyeti ölçülmedi.
- Radyo uykusu: dinleme dışında SX1262 `standby` (sleep değil); uyku akımı hedefi (spec 0,01 mA MCU) için nRF52 System ON uyku optimizasyonu yapılmadı
  (Arduino `delay(2)` döngüsü kullanılıyor).
- Eşleşme güvensiz (spec'in bilinen zayıflığı): anahtar havadan açık gider.
- Menü yok: pusula kalibrasyonu açılışta (ofset yoksa) ya da `CFG calib 1` ile başlar.
- Kapalı mekân, çoklu-yol, çakışma/kayıp paket senaryoları simüle edilmedi (testlerdeki kanal kusursuzdur).

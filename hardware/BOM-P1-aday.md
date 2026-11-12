# Findy P1 — Ürün Konsepti Aday Parçaları (BOM-P1-aday)

Tarih: 2026-11-11 · Durum: **ADAY LİSTESİ, SEÇİLMİŞ DEĞİL** · Spec: `docs/mimari-v0.1.md` §10
Her satırda: neden aday + açık risk. Sayısal değerler üretici/katalog sayfasından; kaynak URL ve doğrulama durumu `dogrulama-notlari.md` (j). Fiyat: görülemeyenler "fiyat kontrol edilecek".

Hedef: çap 40 mm, kalınlık ≤ 13 mm, ortalama akım ≤ 7 mA, P0 ile aynı radyo+işlemci ailesi.

| # | Parça | Üretici parça no | Ölçü / temel değer | Neden aday | Açık risk | Kaynak | Fiyat |
|---|---|---|---|---|---|---|---|
| 1 | LoRa + BLE modülü (nRF52840 + SX1262 + TCXO) | RAK4630 (WisDuo) | **15×23×3 mm**, 44 pin; RF_LoRa pin 37, RF_BT pin 15; modül "tek seferlik uyku" 4,42 µA, boşta 3,35 mA (3,3 V), 15 bayt TX ≈ 67,8 mA @3,6 V (RAK5005 üzerinde) | P0'daki RAK4631 çekirdek kartının içindeki aynı modül → P0 ölçümleri taşınır (spec §1) | 23 mm uzunluk 40 mm daireye tek başına büyük pay; anten pinli/IPEX'li sürüm seçimi ve 868 MHz anten çözümü yok; modül sertifika durumu bu görevde bakılmadı | https://docs.rakwireless.com/product-categories/wisduo/rak4630-module/datasheet/ | fiyat kontrol edilecek |
| 2 | Düşük güçlü GNSS modülü | u-blox MAX-M10S | **≈9,7×10,1×2,5 mm**; sürekli izleme 25 mW; 3,0 V'ta VCC edinim 8–13 mA, izleme 7,5–10 mA, güç tasarruf 4,5–5 mA (+V_IO 2–2,3 mA); SW bekleme VCC 120 nA + V_IO 37–46 µA; HW yedek 28 µA; V_BCKP pini var | ZOE-M8Q (21–25 mA) yerine ~⅓ akım; spec §6 "M10 sınıfı" hedefi; V_BCKP ile sıcak başlangıç mümkün | 9,7×10,1 mm modül + anten (seramik yama ~12–15 mm) ekranın altına sığmaz; arka kapakta yerleşim; P0'daki ZOE-M8Q ile kütüphane/komut farkı (M10 farklı UBX-CFG-VALSET) | https://content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf | fiyat kontrol edilecek |
| 3 | GNSS (referans, P0 ile aynı) | u-blox ZOE-M8Q | izleme 21–25 mA, edinim 22–28 mA, SW yedek 20 µA; V_BCKP var (çip) | P0 ile kod uyumu | Akım bütçesi M10'a göre kötü; boyut bu görevde okunamadı (DOĞRULANAMADI) | https://content.u-blox.com/sites/default/files/ZOE-M8_DataSheet_UBX-16008094.pdf | fiyat kontrol edilecek |
| 4 | 1,28" yuvarlak TFT, çıplak panel (GC9A01, 4 hat SPI) | Display Module DM-TFTR128-446 | **35,6×38,1×1,5 mm** (FPC ile), görünür alan 32,4×32,4 mm, 240×240, parlaklık 400 cd/m²; arka ışık 2 LED paralel **3,0 V'ta tip. 40 mA (maks. 60)**; IDD 8 mA (VDD 2,4–3,3 V) | Spec'teki "~1,6 mm panel" hedefine yakın (1,5 mm); P0 ekranıyla aynı sürücü (GC9A01) → yazılım aynı | Arka ışık 40 mA 3,3 V hattından seri dirençle güvenli sürülemez (Vf 2,9–3,1 V) → akım sürücü lazım; FPC pin sayısı/aralığı ve konektör bu görevde çıkarılamadı; 35,6 mm genişlik 40 mm gövdede çok dar cidar bırakır | https://cdn.shopify.com/s/files/1/0264/7629/files/DM-TFTR128-446_Datasheet.pdf (displaymodule.com) | fiyat kontrol edilecek (sayfa 429) |
| 5 | 1,28" yuvarlak TFT, geliştirme kartı (kıyas) | Waveshare 19192 | Gövde 40,4×37,5 (Ø37,5), görünür alan Ø32,4 | P0'da kullanılıyor; P1 çıplak panelinin ölçü kıyası | Gövde Ø37,5 > P1 hedefi için fazla | https://www.waveshare.com/1.28inch-lcd-module.htm | $14,99 (2026-11-11) |
| 6 | LiPo 150 mAh | Adafruit 1317 | 19,75×26,02×3,8 mm, 4,65 g, korumalı, JST-PH | 40 mm daireye sığar (köşegen ≈32,7 mm); ince | 150 mAh · 7 mA ortalama ≈ 21 saat (festival günü için kısa) | https://www.adafruit.com/product/1317 | $5,95 (1–9) |
| 7 | LiPo 350 mAh | Adafruit 2750 | 36×19,6×5,2 mm, 8,2 g | Kapasite | **Köşegen ≈41 mm → 40 mm gövdeye sığmaz**; kalınlık 5,2 > spec'in 4,2 mm bütçesi | https://www.adafruit.com/product/2750 | $6,95 (1–9) |
| 8 | LiPo 500 mAh | Adafruit 1578 | 29×36×4,75 mm, 10,5 g | Kapasite | **Köşegen ≈46 mm → sığmaz** | https://www.adafruit.com/product/1578 | $7,95 (1–9) |
| 9 | LiPo ~250–300 mAh, ~4×25×30 mm (spec hedefi) | katalogdan doğrulanacak | Köşegen √(25²+30²) ≈ 39,1 mm | Spec §10 hedefi | **40 mm − cidar iç çapına sığmaz** (≈36 mm); doğrulanmış bir katalog parçası bulunamadı → DOĞRULANAMADI | — | fiyat kontrol edilecek |
| 10 | Pusula + ivme (çıplak çip) | ST LSM303AGR | LGA-12; Vdd 1,71–3,6 V; ivme ~4–13 µA, manyeto 50 µA (LP) | P0 ile aynı çip | Pakette ölçü bu görevde okunamadı; kalibrasyon P0'dan taşınır | https://datasheet.chipsmall.com/LSM303AGRTR/208805.pdf (ST aynası) | fiyat kontrol edilecek |

## Yığın notları (spec §10 ile karşılaştırma)

| Katman | Spec | Belgelenen aday değeri |
|---|---|---|
| Panel | ~1,6 mm | DM-TFTR128-446: 1,5 mm |
| Radyo modülü | ~3,0 mm | RAK4630: 3 mm |
| GNSS modülü | (belirtilmemiş) | MAX-M10S ≈ 2,5 mm (tipik) |
| Pil | ~4,2 mm | 150 mAh: 3,8 mm; 500 mAh: 4,75 mm; 350 mAh: 5,2 mm |

## Açık riskler (özet)

1. **Anten (868 MHz ve GNSS)**: bu liste anten adayı içermiyor; gövde içine sığacak LoRa anteni ve GNSS yaması ayrı çalışma ister. RAK4630'un anten pin/IPEX sürümü seçilecek.
2. **Pil–gövde uyumsuzluğu**: katalogdaki 250–300 mAh sınıfı küçük LiPo'ların dikdörtgen köşegeni 40 mm daireye sığmayabilir; yuvarlak/kare pil veya 150 mAh sınıfı gerekebilir.
3. **Arka ışık akımı**: panel 40 mA @3,0 V ister → akım sürücüsü + PWM; ekran kullanımı bütçeyi (spec: 20–40 mA ayrı senaryo) doğrudan belirler.
4. **GNSS yerleşimi**: modül ve anten ekran altında kalamaz; radyo modülüyle birlikte tek PCB'ye 40 mm dairede sığdırma çizimde doğrulanmadı.
5. Bu liste yalnızca belge okumasına dayanır; hiçbir parça alınmadı, ölçülmedi.

# Findy P0 — Alışveriş Listesi (2 cihazlık deney düzeneği)

Tarih: 12 Kasım 2026 · Durum: **liste kullanıcı tarafından onaylandı (12 Kasım 2026); hiçbir şey sipariş edilmedi.**
Kaynak parça listesi: `BOM-P0.md` · doğrulama: `dogrulama-notlari.md`.

**Sipariş öncesi kontrol yapıldı (12 Kasım 2026, mağaza ürün sayfaları).** Fiyat ve
stok o günkü sayfa bilgisidir. Kargo, gümrük ve vergi **dahil değildir**. Faz 5
(5 cihaz) için adetler `BOM-P0.md` içindedir; önce 2 cihazla başlanması önerilir.

> **İki parça ana mağazasında stokta yok, başka satıcıda bulundu (12 Kasım 2026):**
> RAK12500 GNSS modülü Rokland'da (ABD), LSM303AGR pusula modülü Pimoroni'de (İngiltere).
> Bu satıcıların teslimat ülkesine gönderim yapıp yapmadığı kontrol edilmedi.
> **RAK12500 üretimden kalkıyor** (aşağıya bakın).

## 1. RAK mağazası (store.rakwireless.com)

| Parça | Adet | Birim | Tutar | Stok | Sepette seçilecek / not |
|---|---|---|---|---|---|
| WisBlock Starter Kit: RAK19007 + RAK4631 | 2 | $24,99 | $49,98 | var | Ürün: **"RAK19007+RAK4631 … with Arduino"**, frekans: **EU868**. Kutuda: taban, çekirdek, LoRa anteni, BLE anteni, USB-C kablo, vida. |
| RAK13002 IO adaptörü | 2 | $6,00 | $12,00 | var | Başlığın lehimli gelip gelmediği mağaza sayfasında yazmıyor; header ve havya hazır olsun. |
| **Ara toplam** | | | **$61,98** | | |

RAK12500 bu mağazada stokta yok ($19,00); Rokland'dan alınacak (bölüm 1b).

- Paket yerine ayrı almak da mümkün: RAK4631 (EU868 / "RAK4631 Arduino", $17,99, stokta)
  + RAK19007 ($9,99, stokta) = $27,98; paket cihaz başına $2,99 ucuz. RAK4631 tek
  başına da LoRa ve BLE anteniyle geliyor.
- **Antenler ayrıca alınmıyor** (önceki listede vardı, çıkarıldı). Kutudaki LoRa
  anteninin 868 MHz olduğu sayfada açıkça yazmıyor; gelince etiketi kontrol edilmeli.
  Gerekirse yedek: "PCB Antenna for LoRa MHF-1", varyant **863-870 MHz**, $3,00, stokta.

## 1b. GNSS — Rokland (store.rokland.com, ABD'den gönderir)

| Parça | Adet | Birim | Tutar | Stok | Not |
|---|---|---|---|---|---|
| RAK12500 GNSS (ZOE-M8Q) | 2 | $26,97 | $53,94 | var | RAK mağazasına göre birim $7,97 pahalı. RAK'ın ürün sayfasına göre kutuda GNSS anteni var; Rokland paketi için ayrıca doğrulanmadı. |

**Üretimden kalkma uyarısı.** Rokland ürün sayfasındaki 2 Eylül 2026 tarihli nota göre
u-blox ZOE-M8Q'yu sonlandırdı; RAK12500 mevcut stok bitince satılmayacak. RAK'ın kendi
mağazasında stok olmaması bununla uyumlu. 2 cihazlık deney için sorun değil, ama Faz 5
(5 cihaz) için sonradan 3 adet daha bulunamayabilir. Ürün (P1) zaten başka bir GNSS
kullanacağı için ürün tasarımını etkilemez.

### RAK12500 için seçenekler

**Kullanıcı kararı (12 Kasım 2026): Rokland'dan 2 adet RAK12500 alınacak.** Faz 5 için
parça bulunamama riski kabul edildi; o aşamada RAK12501'e geçiş gerekebilir.

1. **Rokland'dan 2 adet almak (seçildi):** yazılım değişmez. Faz 5 düşünülüyorsa
   şimdiden 5 adet almak stok riskini kaldırır (+$80,91).
2. RAK12501 (Quectel L76K; RAK'ta $8,90, Rokland'da $13,97, ikisinde de stokta) almak. **Bu yazılım değişikliği gerektirir:**
   mevcut kod u-blox modülünü I2C üzerinden okuyor; RAK12501 seri porttan NMEA verir.
   Zaman doğruluğu ve güç tüketimi de farklı olur. Karar verilmedi.

## 2. Ekran — Waveshare

| Parça | Adet | Birim | Tutar | Stok | Not |
|---|---|---|---|---|---|
| 1,28" yuvarlak LCD modül, GC9A01 (SKU 19192) | 2 | $14,99 | $29,98 | sayfada stok bilgisi görülmedi | Kablo dahil. Muadil GC9A01 modül de olur; pin adları değişir. |

## 3. Pusula ve pil — Adafruit ya da bayisi

| Parça | Adet | Birim | Tutar | Stok | Not |
|---|---|---|---|---|---|
| LSM303AGR breakout (Adafruit 4413) | 2 | £10,75 | £21,50 | **Pimoroni'de var** | shop.pimoroni.com (İngiltere); fiyatın sterlin olduğu varsayıldı (mağazanın varsayılan para birimi). Adafruit ($12,50), The Pi Hut ve Core Electronics'te stokta yok. |
| LiPo 350 mAh, JST-PH 2 mm (Adafruit 2750) | 2 | $6,95 | $13,90 | var | Adafruit sayfasında lityum pil kargo kısıtı uyarısı var (ayrıntısı okunmadı); yerelden muadil (3,7 V, korumalı, JST-PH 2 mm) almak daha kolay olabilir. **Takmadan kutup sırasını ölç.** |
| **Ara toplam** | | | **$13,90 + £21,50** | | |

## 4. Yerel elektronikçi (fiyat bakılmadı)

Cihaz başına birer takım; 2 cihaz için:

- 2 × titreşim motoru (3 V, ~10 mm disk)
- 2 × mantık seviyeli N-MOSFET (öneri IRLZ44N; veri sayfası kontrol edilmedi)
- 2 × Schottky diyot (1N5819)
- 2 × 100 Ω, 2 × 100 kΩ direnç
- 2 × 100 µF elektrolitik (≥ 10 V), 2 × 100 nF seramik kondansatör
- 2 × tuş (6 mm tact switch)
- 2 × breadboard (400 delik)
- ~50 jumper kablo (erkek-dişi ve erkek-erkek)
- 2 × 40'lık 2,54 mm erkek header
- Havya ve lehim (yoksa)

USB-C kablo RAK paketinde geliyor; ayrıca alınmaz.

## 5. Ölçüm ekipmanı (ortak, bir kez)

| Ekipman | Gerekli mi | Fiyat |
|---|---|---|
| Nordic Power Profiler Kit II (PPK2) | **Pil kararı için gerekli** (akım ölçümü) | Doğrulanmadı; arama özetlerinde $89 ve üstü geçti. |
| Multimetre | Gerekli (ilk güç verişte pin/kutup ölçümü) | Bakılmadı |
| Mantık analizörü, SWD programlayıcı | İsteğe bağlı | Bakılmadı |

## Toplam

| Kalem | Tutar |
|---|---|
| RAK mağazası (paket + RAK13002) | $61,98 |
| Rokland (RAK12500) | $53,94 |
| Waveshare (ekran) | $29,98 |
| Adafruit ya da yerel (pil) | $13,90 |
| Pimoroni (pusula) | £21,50 |
| **Fiyatı görülen kalemler, 2 cihaz** | **$159,80 + £21,50** |

İki para birimi kur çevrilmeden ayrı yazıldı. Dört ayrı satıcı olduğu için kargo dört kez ödenir.
Buna **dahil olmayanlar:** yerel küçük malzeme, PPK2 ve diğer ölçüm ekipmanı, kargo,
gümrük, vergi. Bu tezgâh prototipinin maliyetidir, ürün birim maliyeti değildir.

## Kontrol sonuçları (12 Kasım 2026)

| # | Soru | Sonuç |
|---|---|---|
| 1 | RAK4631'de EU868 ve Arduino sürümü var mı? | **Evet**, stokta, $17,99 (paket içinde $24,99). |
| 2 | RAK12500 paketinde GNSS anteni var mı? | **Evet** (1 adet). RAK'ta stokta yok; **Rokland'da var** ($26,97). Parça üretimden kalkıyor. |
| 3 | RAK4631 ile BLE anteni geliyor mu? | **Evet**, LoRa anteniyle birlikte. |
| 4 | LSM303AGR stok durumu | Adafruit, The Pi Hut, Core Electronics'te yok; **Pimoroni'de var** (£10,75). |
| 5 | Pil nereden alınacak? | Adafruit'te stokta; kargo kısıtı uyarısı var. Açık. |
| 6 | Gümrük ve kargo bedeli | Kontrol edilemedi: mağazalar adres girilmeden hesaplamıyor. Açık. |
| 7 | RAK13002 başlığı lehimli mi? | Mağaza sayfasında yazmıyor. Açık. |
| 8 | Rokland ve Pimoroni teslimat ülkesine gönderiyor mu? | Kontrol edilmedi. Açık. |

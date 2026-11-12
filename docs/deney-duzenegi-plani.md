# Findy — İki Cihazlı Deney Düzeneği Planı (v1)

Tarih: 11 Kasım 2026. Durum: **plan** — hiçbir parça alınmadı, hiçbir ölçüm yapılmadı.
Hedefler için bkz. `docs/hedef-ozellikler.md`.

## Amaç

Üç soruyu ölçümle cevaplamak:

1. Hangi radyo, bilekte taşınırken ve kalabalıkta 300–500 m'de güvenilir bağlantı veriyor?
2. Yön oku hangi yöntemle, hangi mesafeden itibaren işe yarıyor?
3. Bu ikisi 2–3 günlük pil hedefinin güç bütçesine (ortalama ~3,5–7 mA) sığıyor mu?

Bu bir ürün prototipi değildir. Hazır geliştirme kartları kullanılır; boyut ve
görünüm bu aşamada önemsizdir.

## Denenecek Adaylar

| # | Bağlantı | Yön / mesafe yöntemi | Neden aday |
|---|---|---|---|
| A | Sub-GHz LoRa (868 MHz) | GNSS + pusula | Menzil payı en geniş; gövde soğurması 2,4 GHz'e göre düşük. |
| B | BLE Coded PHY (2,4 GHz) | GNSS + pusula | Telefon bağlantısıyla aynı radyo → tek çip, en düşük maliyet. Kalabalıkta menzil riski. |
| C | 2,4 GHz LoRa (SX1280) | Radyonun kendi uçuş-süresi mesafe ölçümü | GNSS'siz mesafe vaat ediyor; yön yine ayrı çözülmeli. |
| D | (yakın mesafe eki) UWB | UWB mesafe + açı | Son 20–30 m için hassas ok. Tek başına menzili yetmez; A/B/C'nin üstüne eklenir. |

Aday kart türleri (sipariş öncesi güncel model, stok ve fiyat kontrol edilecek):

- A: SX1262 + GNSS içeren hazır izleyici kartları (ör. LilyGO T-Beam / T-Echo, Heltec Wireless Tracker sınıfı).
- B: nRF52840 geliştirme kartı veya dongle + ayrı GNSS modülü.
- C: SX1280 modüllü geliştirme kartı.
- D: Qorvo DW3000 tabanlı UWB geliştirme kiti.
- Hepsi için: manyetometre (pusula) modülü, veri kaydı için microSD veya telefon bağlantısı, güç ölçümü için akım profilleyici (ör. Nordic PPK2).

Her adaydan **iki adet** gerekir. Öneri: önce A ve B alınır; C ve D ilk sonuçlara göre eklenir.

Sipariş öncesi kontrol: kullanılacak ülkede 868 MHz bandının lisanssız kullanım
koşulları (güç ve görev döngüsü sınırı).

## Aşamalar

### Faz 0 — Masa başı (1–2 gün)
- İki kart birbirine konum paketi gönderir; her paket zaman damgası, RSSI, SNR ve iki tarafın GNSS konumuyla kaydedilir.
- Çıktı: çalışan kayıt düzeni ve kayıtları tabloya çeviren betik.

### Faz 1 — Açık alan menzil (1 gün)
- Düz, görüş hattı açık bir alan. Mesafeler: 50, 100, 200, 300, 400, 500, 700 m.
- Her mesafede üç taşıma biçimi: elde, bilekte, cepte. Ayrıca gövde arada (sırt dönük) durumu.
- Her nokta en az 100 paket.
- Ölçülen: paket teslim oranı, RSSI, SNR.
- Gerçek mesafe: önceden işaretlenmiş noktalar (harita/şerit metre), cihazın kendi GNSS'i değil.

### Faz 2 — Yön ve mesafe doğruluğu (1 gün)
- Mesafeler: 5, 10, 20, 50, 100, 300 m; her birinde 8 yönde hedef.
- Ölçülen: gösterilen ok ile gerçek yön arasındaki açı hatası, mesafe hatası, ilk doğru oka kadar geçen süre.
- Beklenen bulgu (doğrulanacak): iki cihazın GNSS hataları toplandığı için yakın mesafede ok anlamsızlaşır. Bu deneyin asıl çıktısı **okun bozulduğu mesafe eşiğidir** — UWB (D) gerekip gerekmediğini o belirler.
- Pusula: kart yatay / bilekte eğik / hareket halinde ayrı ayrı.

### Faz 3 — Kalabalık (1 etkinlik)
- Gerçek kalabalık bir ortam (konser, pazar, kampüs etkinliği); mümkünse küçük bir açık hava etkinliği.
- Faz 1'in bilekte ölçümleri tekrarlanır; ulaşılabilen en uzak mesafe ve paket kaybı kaydedilir.
- Kayıt yalnızca kendi iki cihazımızın verisidir; başka kimsenin verisi toplanmaz.

### Faz 4 — Güç ölçümü (1–2 gün, masa başı)
- Akım profilleyiciyle her adayın üç durumu: uyku, dinleme, gönderme (+ GNSS açık/kapalı).
- Üç kullanım senaryosu için ortalama akım hesaplanır: "arkadaş yakında" (seyrek güncelleme), "aktif arama" (sık güncelleme + ekran açık), "bekleme".
- Sonuç 3,5–7 mA bütçesiyle karşılaştırılır.
- Ekran: aday ekran türlerinin (renkli LCD/AMOLED, yansıtıcı memory-in-pixel) avatar gösterirken akımı ölçülür; "istenince göster" ve "sürekli göster" senaryoları ayrı hesaplanır.

### Faz 5 — Grup ve kolye (Faz 1–4'te seçilen adayla)
- Kart sayısı 5'e çıkarılır; 5 cihaz aynı anda yayındayken paket çakışması, güncelleme gecikmesi ve ortalama akım ölçülür.
- Kolye konumu: kart göğüste asılıyken Faz 1 menzil ölçümü ve Faz 2 pusula ölçümü tekrarlanır.

## Kabul Ölçütleri

Kullanıcı 11 Kasım 2026'da onayladı. Bunlar deneyin geçme eşikleridir,
ölçülmüş sonuç değildir.

| Ölçüt | Eşik |
|---|---|
| Bağlantı | Bilekte, açık alanda 300 m'de paket teslim oranı ≥ %90 |
| Kalabalık | Kalabalıkta 150 m'de paket teslim oranı ≥ %80 |
| Güncelleme gecikmesi | Aktif aramada ≤ 5 sn |
| Yön | 30 m ve üzerinde açı hatası ≤ ±30° |
| Mesafe | 30 m ve üzerinde hata ≤ %20 veya ±10 m (büyük olan) |
| Güç | Tipik festival günü karışımında ortalama ≤ 7 mA |

## Teslim Edilecekler

- `validation/deney/` altında ham kayıtlar (CSV) ve her fazın kısa ölçüm raporu.
- Aday karşılaştırma tablosu: menzil, kalabalık, yön eşiği, ortalama akım, tahmini parça maliyeti.
- Tek sayfalık mimari öneri — veya "hedeflerden biri gevşetilmeli" sonucu.

## Riskler ve Bilinmeyenler

- Geliştirme kartı antenleri nihai 40 mm gövdedeki antenden iyi olacaktır; ölçülen menzil üst sınırdır, ürün menzili değildir.
- GNSS'in ilk konum süresi ve güç tüketimi, pil bütçesini tek başına aşabilir.
- Kalabalık testi tekrarlanabilir değildir; tek etkinlik sonucu kesin kabul edilmemeli.
- Kapalı mekân bu planın dışındadır.

## Başlamadan Önce Kullanıcıdan Gerekenler

1. Parça bütçesi ve siparişi kimin vereceği.
2. Donanımı kimin kurup yazılımını kimin yazacağı.
3. ~~Kabul ölçütlerinin onayı.~~ Onaylandı (11 Kasım 2026).
4. ~~Gruptaki cihaz sayısı hedefi.~~ Cevap: 5'e kadar. İlk fazlar yine iki kartla yapılır; 5 kart yalnızca Faz 5'te gerekir.
5. ~~Avatarın istenince mi sürekli mi görüneceği.~~ Cevap: istenince. Faz 4'te "sürekli göster" senaryosu yalnızca karşılaştırma için ölçülür.

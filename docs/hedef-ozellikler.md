# Findy — Hedef Özellikler (v1)

Karar tarihi: 11 Kasım 2026. Kararı veren: kullanıcı.

Bu belgedeki değerler **tasarım hedefidir**; hiçbiri ölçülmedi veya doğrulanmadı.
Sunumda veya yatırımcı görüşmesinde ölçülmüş performans gibi sunulmamalıdır.

## Hedefler

| Özellik | Hedef | Not |
|---|---|---|
| Menzil | 300–500 m, açık alan | İki cihazın birbirini bulabildiği en uzak mesafe. Kapalı mekân ayrı test konusu. |
| Boyut | ~40 mm çap, yuvarlak modül | Akıllı saat boyutu; kol bandı ve anahtarlıkta aynı modül. Kalınlık henüz belirlenmedi. |
| Pil | Tek şarjla 2–3 gün | Hafta sonu festivalini şarjsız çıkarmak. |
| Fiyat | İki cihazlık set 60–90 $ perakende | BOM hedefi buradan türetilecek; henüz maliyet çalışması yok. |

## Ek İstekler (11 Kasım 2026, kullanıcı önerisi)

Kullanıcı bunları "nasıl olur" diye önerdi; hedef olarak kaydedildi, fizibilitesi doğrulanmadı.

| İstek | Kapsam | Etkisi |
|---|---|---|
| 5 cihaza kadar eşleşme | Bir grupta en çok 5 cihaz | Radyo tarafında kolay: her cihaz kendi konumunu sırayla yayınlar. Asıl iş arayüzde: ekranda 4 arkadaş aynı anda nasıl gösterilecek (ör. halka çevresinde 4 nokta + seçilen kişi için ok). Satış paketi de etkilenir (ikili set + tekli ek cihaz). |
| Ekranda kişisel fotoğraf / avatar | Kullanıcı kendi görselini yükler | Görsel yüklemek için telefon uygulaması gerekir (yalnızca kurulumda; bulma işlevi telefonsuz kalır). Arkadaş avatarları eşleşme anında yakın mesafeden aktarılmalı; uzun menzil bağlantısı görsel taşıyamaz. |
| Kolye olarak takma | Kol bandı ve anahtarlığa ek üçüncü taşıma biçimi | Mekanik: aynı modül için kolye aparatı; boyun askısında güvenlik için çekince açılan kilit. Cihaz dik asılı dururken pusula oku güvenilmez — ok, cihaz elde yatay tutulunca okunur ya da eğim düzeltmesi (ivmeölçer) gerekir. |

**Avatar ile pil hedefi çatışıyor.** Kolyede avatarın sürekli görünmesi istenirse,
renkli LCD/AMOLED ekran açıkken tek başına onlarca mA çeker; 3,5–7 mA ortalama
bütçeyi aşar. Üç yol vardı; **kullanıcı 1. yolu seçti (11 Kasım 2026)**:

1. Avatar yalnızca tuşa basınca / bilek kaldırınca birkaç saniye görünür — pil hedefi korunur.
2. Sürekli açık, düşük güçlü yansıtıcı ekran (memory-in-pixel veya e-kâğıt) — pil korunur ama renk sınırlı ve karanlıkta aydınlatma olmadan görünmez.
3. Sürekli açık renkli ekran — pil hedefi 2–3 günden yaklaşık bir geceye düşer.

## Hedeflerin Getirdiği Kısıtlar

Bunlar hedeflerden çıkan mantıksal sonuçlardır, seçilmiş mimari değildir.

- **Güç bütçesi.** ~~40 mm gövdeye 250–350 mAh pil sığar, ortalama ~3,5–7 mA yeter.~~
  **Düzeltme (11 Kasım 2026):** mekanik çizim ve katalog taraması bu varsayımı
  çürüttü. 40 mm gövdeye sığan hazır pil ~150 mAh sınıfıdır; 2–3 gün için bu
  **ortalama ≤ ~2,5 mA** demektir. Boyut ve pil hedefi birlikte kâğıt üzerinde
  sınırda; ayrıntı ve seçenekler `mimari-v0.1.md` bölüm 12'de. Onaylanan
  "ortalama ≤ 7 mA" kabul ölçütü bu yüzden pil hedefini tek başına garanti etmez.
  **Kullanıcı kararı (11 Kasım 2026):** boyut mu pil hedefi mi esneyecek, gerçek
  akım ölçüldükten sonra karar verilecek; o zamana kadar iki hedef de değişmez.
- **Menzil tek başına UWB'yi eler.** UWB hassas yön ve mesafe verir ama tipik
  menzili bu hedefin altındadır. 300–500 m için uzun menzilli bir bağlantı
  (aday: BLE Coded PHY, sub-GHz/LoRa) gerekir.
- **Yön oku ayrı bir problem.** Uzun menzilli radyolar mesafeyi kaba, yönü hiç
  vermez. Yön için adaylar: GNSS + pusula (açık alanda), yakın mesafede UWB,
  ya da RSSI ile "ısınıyor/soğuyor" arayüzü. Hangisinin yeteceği deneyle
  belirlenecek.
- **Fiyat, iki radyolu tasarımı zorlar.** Uzun menzil + UWB + GNSS + yuvarlak
  ekran birlikte 60–90 $ set fiyatına sığmayabilir; BOM çalışması hangi
  bileşenin feda edileceğini gösterecek.

## Açık Sorular

1. ~~Mesafe ve yön için kabul edilebilir hata ne?~~ Cevap (11 Kasım 2026): 30 m ve
   üzerinde yön ≤ ±30°, mesafe ≤ %20 veya ±10 m. 30 m altı için eşik yok; Faz 2
   sonucuna göre belirlenecek.
2. Kalabalık (insan gövdesi 2,4 GHz'i güçlü soğurur) menzili ne kadar düşürür?
3. ~~Bir grupta kaç cihaz eşleşebilmeli?~~ Cevap: 5'e kadar (11 Kasım 2026).
4. Kalınlık ve ağırlık hedefi.
5. Su/toz dayanımı hedefi.
6. ~~Avatar ne zaman görünsün?~~ Cevap: istenince (tuş / bilek kaldırma), birkaç saniye. Pil hedefi 2–3 gün olarak kalır; renkli ekran kullanılabilir.

## Sonraki Adım

İki cihazlı deney düzeneği: hazır geliştirme kartlarıyla aday radyoların açık
alanda ve kalabalıkta menzilini, ve aday yön yöntemlerinin doğruluğunu ölçmek.

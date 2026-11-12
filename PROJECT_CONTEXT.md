# Findly / Findy — Devam Bağlamı

Son kayıt tarihi: 11 Kasım 2026. Yerel saat dilimi: Asia/Nicosia.

## Hedef Özellikler (11 Kasım 2026, kullanıcı kararı)

Menzil 300–500 m açık alan · çap ~40 mm · pil 2–3 gün · iki cihazlık set 60–90 $ perakende.
Ek istekler (aynı gün, kullanıcı önerisi): 5 cihaza kadar eşleşme · ekranda kişisel fotoğraf/avatar · kolye olarak takma. Avatar istenince (tuş / bilek kaldırma) birkaç saniye görünür; sürekli açık ekran pil hedefi nedeniyle seçilmedi.
Bunlar tasarım hedefidir, ölçülmüş değer değildir. Ayrıntı, kısıtlar ve açık sorular: `docs/hedef-ozellikler.md`.

## Prototip Tasarım Paketi v0.1 (11 Kasım 2026)

Kullanıcı "bütün projeyi yap: teknik çizimler, parçalar, bağlantı şemaları, kodlar" dedi. Üretilenler:

- `docs/mimari-v0.1.md` — referans mimari, radyo protokolü, pin ataması. **Bölüm 12 düzeltmeleri önceki bölümlerin yerine geçer.**
- `firmware/` — RAK4631 cihaz yazılımı. Taşınabilir çekirdek (`lib/findy_core`) PC'de test edildi: 33 test geçiyor (`bash firmware/test/run_native_tests.sh`). **Donanım katmanı (`src/`) 12 Kasım 2026'da RAK4631 için derlendi (hata yok; RAM %29,5, Flash %30,6), ama hiçbir kartta çalıştırılmadı.** Kart tanımı PlatformIO'da olmadığı için `firmware/boards/` ve `firmware/variants/` altına RAK deposundan alındı.
- `hardware/BOM-P0.md`, `BOM-P1-aday.md`, `baglanti-tablosu.md`, `baglanti-semasi.svg/.png`, `dogrulama-notlari.md` — üretici belgeleriyle doğrulanmış parça listesi ve bağlantı şeması. RAK parçalarının fiyatı görülemedi.
- `hardware/mekanik/` — 40 mm ürün konseptinin 5 teknik çizimi (SVG + PNG önizleme), 5 yazdırılabilir STL, `params.py`, `dogrula.py`.
- `tools/findy_ble.py`, `tools/avatar_convert.py` — telefon yerine bilgisayardan ayar/avatar yükleme.

Durum: **hiçbir parça alınmadı, hiçbir donanım kurulmadı, hiçbir ölçüm yapılmadı.** Radyo mimarisi hâlâ seçilmiş değildir; bu paket deney planındaki A adayının prototipidir.

Bilinen en önemli açıklar:
1. 40 mm gövdeye ancak ~150 mAh pil sığıyor; 2–3 gün hedefi kâğıt üzerinde sınırda (mimari bölüm 12). **Kullanıcı kararı (11 Kasım 2026): boyut mu pil hedefi mi esneyecek, gerçek akım ölçüldükten sonra karar verilecek.** O zamana kadar 40 mm ve 2–3 gün hedefleri değişmeden kalır.
2. 868 MHz anten 40 mm gövdeye sığmıyor; anten çözümü yok.
3. Eşleşme güvensiz (anahtar havadan açık gidiyor); yalnızca deney için.
4. Özel kart şeması/gerber, telefon uygulaması ve sertifikasyon yok.

## Kullanıcının Onayladığı Ürün Fikri

Parti ve festivallerde arkadaşların birbirini bulabilmesi için eşleşen cihazlardan oluşan bir ürün prototipi üzerinde çalışılıyor.

- Yuvarlak ekranlı, küçük bir ana modül.
- Aynı modül kol bandı veya anahtarlık olarak kullanılabilmeli.
- Temel arkadaş bulma işlevi telefon ve internet olmadan çalışabilmeli.
- Telefona da isteğe bağlı bağlanabilmeli.
- Konuşmada yatırımcı sunumu için istenen ürün adı: **Findy**.
- Son klasör talebi: **Desktop/Urunler/Findly**. Bu talep tek başına marka değiştirme onayı sayılmaz.

## Tasarım ve İçerik

Ana konsept: grafit gövde, yuvarlak siyah cam ekran, ince lime ışık halkası, lime yan tuş, kol bandı ve anahtarlık aparatı. Ekrandaki DENIZ, yön oku ve 24 m örnek arayüz değerleridir.

Konuşmada bir endüstriyel tasarım promptu, 15 saniyelik erken video senaryosu, en fazla 10 saniyelik festival videosu promptu ve en fazla 10 saniyelik patlamalı ürün animasyonu promptu verildi. Patlamalı görünüm kontrollü katman ayrışmasıdır; iç elektronik yerleşim temsilidir. Promptlar `docs/prompts.md` içinde özgün halleriyle korunur; 15 saniyelik senaryo tarihsel bir sürümdür, son video süre talebi en fazla 10 saniyedir.

## Teslim Edilen Sunum

Ana dosya: `findy-yatirimci-sunumu-v2.html`.

- Kullanıcının verdiği HTML'in görsel dili temel alındı.
- İki dikey festival videosu ve yatay patlamalı ürün videosu dosyanın içine gömüldü.
- Gömülü videoların özgün dosyalarla SHA-256 eşleşmesi doğrulandı.
- Açık/koyu tema, tam ekran, bölüm navigasyonu ve tek video oynatımı bulunur.
- 1440, 1024, 768, 390 ve 360 piksel genişlikte yatay taşma kontrol edildi.
- Üç video için gerçek tarayıcı oynatımı doğrulandı; JavaScript hatası görülmedi.
- Referanslardaki eksik finansal ve ekip alanlarına sahte değer eklenmedi; doğrulama planına dönüştürüldü.
- Sonradan Downloads/Findly içinde bulunan iki ek görsel, ekran kaydı ve Findly adlı ek HTML de kaynak arşive alındı; içerikleri yeniden yorumlanmadı.

## Henüz Doğrulanmayanlar

Çalışan donanım prototipi, gerçek menzil, konum/yön doğruluğu, pil süresi, su dayanımı, BOM maliyeti, üretim planı, resmi ürün güvenliği değerlendirmeleri, ekip özgeçmişleri, müşteri/satış verisi ve yatırım koşulları bu çalışmada doğrulanmadı.

Telefon bağlantısı ile diğer cihazın yönünü/mesafesini ölçme ayrı teknik işlerdir. Radyo/ölçüm mimarisi seçilmiş kabul edilmez. İlk teknik doğrulama için açık alan etkinlikleri düşünülüyor; kapalı mekân ayrı test gerektirir. Ürün acil durum veya arama-kurtarma cihazı olarak konumlandırılmıyor.

## Sonraki Mantıklı Adımlar

1. Findy / Findly marka yazımını kullanıcıyla netleştirmek.
2. ~~Hedef menzil, boyut, pil ve fiyat beklentilerini belirlemek.~~ Yapıldı (11 Kasım 2026), bkz. `docs/hedef-ozellikler.md`.
3. Ölçüm mimarisini iki cihazlı deney düzeneğinde doğrulamak. Plan yazıldı (11 Kasım 2026): `docs/deney-duzenegi-plani.md`. Kabul ölçütleri onaylandı. Parça alınmadı, ölçüm yapılmadı; parça bütçesi ve işi kimin yapacağı açık.
4. Arkadaş eşleşmesi ve buluşma akışını gerçek kullanıcılarla test etmek.
5. Donanım fizibilitesinden sonra ücretli pilot ve yatırım kapsamını sayısallaştırmak.

Kullanıcı 11 Kasım 2026'da 2. adımı istedi ve hedefleri belirledi. Diğer adımlar henüz istenmedi; sıradaki mantıklı iş 3. adımdır (iki cihazlı deney düzeneği).

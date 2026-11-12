# Findly — Proje ve Konuşma Arşivi

Proje konumu: `/home/wpu/Desktop/Urunler/Findly`.

Bu konuşmada kullanılan ürün adı **Findy**'dir. Proje klasörü kullanıcının son talebiyle **Findly** olarak adlandırılmıştır; mevcut dosyalardaki marka adları değiştirilmemiştir.

## Sunumu Aç

`findy-yatirimci-sunumu-v2.html` dosyasına çift tıklayın. Ürün görseli ve üç video HTML'in içindedir; ayrı dosya veya internet gerektirmez. Açık/koyu tema, tam ekran ve ok tuşlarıyla bölüm geçişi bulunur.

## Kaydedilenler

- `assets/images/`: Downloads/Findly içindeki üç özgün ürün görseli.
- `assets/videos/`: Üç konsept videosu ve mevcut ekran kaydı.
- `references/`: Kullanıcının referans sunumları; Findy ve Findly adlı sürümler aynen korunur.
- `docs/conversation.md`: Bu oturumdaki görünür kullanıcı ve asistan mesajlarının okunabilir kaydı.
- `docs/conversations/`: Oturum bazında JSONL mesajları ve araç çağrısı kayıtları.
- `docs/prompts.md`: Konuşmada verilen görsel ve video promptlarının özgün metinleri.
- `PROJECT_CONTEXT.md`: Ürün kararları, mevcut durum ve açık teknik/ticari sorular.
- `validation/original/`: Sunum teslimindeki ekran görüntüleri, medya temas sayfaları ve kontrol raporu.
- `validation/latest/`: Taşınma öncesinde proje içindeki kaynaklarla tekrarlanan kontroller.
- `docs/migration-manifest.json`: Taşınan dosyaların boyutları, SHA-256 özetleri ve kaynakları.

## Prototip Tasarım Paketi v0.1 (11 Kasım 2026)

Doğrulanmamış tasarım: parça alınmadı, donanım kurulmadı, ölçüm yapılmadı.

- `findy-teknik-ozet.html`: mimari, bağlantı şeması, çizimler ve fiyatlı alınacaklar listesi tek sayfada. Yeniden üretim: `python3 tools/build_findy_teknik_ozet.py`.
- `docs/hedef-ozellikler.md`, `docs/deney-duzenegi-plani.md`: hedefler ve deney planı.
- `docs/mimari-v0.1.md`: referans mimari ve radyo protokolü (önce bölüm 12).
- `firmware/`: RAK4631 cihaz yazılımı; çekirdek testleri `bash firmware/test/run_native_tests.sh`. Donanım katmanı derlenmedi.
- `hardware/`: parça listeleri, bağlantı tablosu ve şeması, doğrulama notları.
- `hardware/alisveris-listesi.md`: 2 cihazlık deney düzeneği için mağaza bazında sipariş listesi (sipariş verilmedi).
- `hardware/mekanik/`: teknik çizimler (`cizimler/`, önizleme `onizleme/`), 3B baskı dosyaları (`stl/`).
- `tools/findy_ble.py`, `tools/avatar_convert.py`: bilgisayardan ayar ve avatar yükleme.

## Komutlar

Proje klasöründe:

```sh
rtk proxy python3 tools/build_findy_presentation.py
rtk proxy python3 tools/check_findy_presentation.py
rtk proxy python3 tools/export_findly_conversation.py
```

Sunum oluşturucu ve doğrulayıcı artık Downloads'a bağlı değildir; kaynakları proje içinden okur. Gereksinimler: Python 3, Pillow, FFmpeg; tarayıcı kontrolü için Playwright ve Chrome/Chromium.

Konuşma dışa aktarıcısı yerel Codex oturum kaydından görünür mesajları ve araç kayıtlarını alır. Sistem/geliştirici talimatları, iç analiz ve gizli akıl yürütme kayıtları arşive dahil edilmez. Yeni bir oturum ayrıca kaydedilebilir; önceki oturum dosyaları korunur.

## Sunumun Sınırları

Görseller ve videolar AI destekli konsept çalışmalarıdır; çalışan donanım veya saha performansı kanıtı değildir. Paylaşılmamış ekip, fiyat, yatırım tutarı, hisse oranı veya pazar büyüklüğü uydurulmamıştır. Menzil, pil süresi, ölçüm doğruluğu ve birim maliyet henüz doğrulanmamıştır.

Downloads/Findly içindeki kaynaklar yedek olarak korunur. Eski PartyAi klasöründeki yönetilen `.git`, `.codex`, `.agents` ve `.aws` alanları proje dosyası sayılmaz ve taşınmaz.

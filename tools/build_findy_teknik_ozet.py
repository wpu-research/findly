#!/usr/bin/env python3
"""Findy teknik özet sayfasını üretir: findy-teknik-ozet.html (tek dosya, internet gerektirmez).

Kaynaklar proje içindedir: hardware/baglanti-semasi.svg ve hardware/mekanik/cizimler/*.svg
sayfaya gömülür. Metin içeriği docs/mimari-v0.1.md, hardware/alisveris-listesi.md ve
docs/deney-duzenegi-plani.md ile elle eşlenmiştir; onlar değişirse burası da güncellenmeli.

Kullanım: python3 tools/build_findy_teknik_ozet.py
"""
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "findy-teknik-ozet.html"


def img(path: Path, alt: str) -> str:
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f'<img alt="{alt}" src="data:image/svg+xml;base64,{data}">'


CAPTIONS = {
    "01": "Genel görünüş",
    "02": "Kesit",
    "03": "Patlatılmış görünüş",
    "04": "Kart yerleşimi",
    "05": "Aparatlar (kol bandı, anahtarlık/kolye)",
}


def drawings() -> str:
    parts = []
    for p in sorted((ROOT / "hardware/mekanik/cizimler").glob("*.svg")):
        cap = CAPTIONS.get(p.name[:2], p.stem)
        parts.append(f'<figure class="draw">{img(p, cap)}<figcaption>{cap}</figcaption></figure>')
    return "\n".join(parts)


HTML = r"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Findy — Teknik Özet</title>
<style>
:root{--bg:#f6f7f4;--card:#fff;--ink:#16181a;--mut:#5d646b;--line:#dfe2dc;--acc:#5a7d00;--accbg:#eef5d6;--warn:#9a5b00;--warnbg:#fff3dc;--bad:#a12a2a;--badbg:#fde8e6;--ok:#1f6b3a;--okbg:#e3f4e8}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#101214;--card:#181b1e;--ink:#eceeea;--mut:#9aa1a8;--line:#2a2f34;--acc:#c6f24e;--accbg:#26300f;--warn:#f0b65a;--warnbg:#33270f;--bad:#f08a80;--badbg:#3a1a17;--ok:#7fd69a;--okbg:#14301e}}
:root[data-theme="dark"]{--bg:#101214;--card:#181b1e;--ink:#eceeea;--mut:#9aa1a8;--line:#2a2f34;--acc:#c6f24e;--accbg:#26300f;--warn:#f0b65a;--warnbg:#33270f;--bad:#f08a80;--badbg:#3a1a17;--ok:#7fd69a;--okbg:#14301e}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1040px;margin:0 auto;padding:24px 16px 64px}
header h1{font-size:clamp(28px,5vw,44px);margin:0 0 4px;letter-spacing:-.02em}
header p{margin:0;color:var(--mut)}
nav{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);margin:16px -16px 24px;padding:10px 16px;display:flex;gap:14px;flex-wrap:wrap;font-size:14px;z-index:5}
nav a{color:var(--mut);text-decoration:none}nav a:hover{color:var(--acc)}
nav button{margin-left:auto;background:none;border:1px solid var(--line);color:var(--ink);border-radius:8px;padding:2px 10px;cursor:pointer;font:inherit}
h2{font-size:24px;margin:44px 0 12px;letter-spacing:-.01em}
h3{font-size:17px;margin:24px 0 8px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
.note{border-radius:12px;padding:14px 16px;margin:12px 0}
.note.warn{background:var(--warnbg);color:var(--warn)}
.note.bad{background:var(--badbg);color:var(--bad)}
.note b{color:inherit}
.grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr))}
.kpi .v{font-size:24px;font-weight:650;letter-spacing:-.01em}
.kpi .l{color:var(--mut);font-size:13px}
.kpi .s{font-size:13px;margin-top:4px}
.tw{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--card)}
table{border-collapse:collapse;width:100%;font-size:14.5px}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:12.5px;text-transform:uppercase;letter-spacing:.04em;color:var(--mut);font-weight:600}
tr:last-child td{border-bottom:0}
td.n,th.n{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
tr.sum td{font-weight:650;background:var(--accbg)}
.tag{display:inline-block;font-size:12px;border-radius:999px;padding:1px 9px;white-space:nowrap}
.tag.ok{background:var(--okbg);color:var(--ok)}.tag.warn{background:var(--warnbg);color:var(--warn)}.tag.bad{background:var(--badbg);color:var(--bad)}
code{font:13.5px ui-monospace,Menlo,Consolas,monospace;background:var(--accbg);padding:1px 5px;border-radius:5px}
ul{padding-left:20px;margin:8px 0}li{margin:3px 0}
figure{margin:0}
figure img{display:block;width:100%;height:auto;background:#fff;border-radius:10px;border:1px solid var(--line)}
figcaption{font-size:13px;color:var(--mut);margin-top:6px}
.draws{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
.blk{width:100%;height:auto;display:block}
.blk rect{fill:var(--card);stroke:var(--line);stroke-width:1.5}
.blk rect.core{stroke:var(--acc);stroke-width:2}
.blk text{fill:var(--ink);font:13px system-ui,sans-serif;text-anchor:middle}
.blk text.s{fill:var(--mut);font-size:11px}
.blk line{stroke:var(--mut);stroke-width:1.5}
.pkt{display:flex;border-radius:8px;overflow:hidden;font-size:13px;text-align:center;border:1px solid var(--line)}
.pkt div{padding:8px 4px;border-right:1px solid var(--line)}.pkt div:last-child{border:0}
.pkt .h{flex:8;background:var(--card)}.pkt .e{flex:14;background:var(--accbg)}.pkt .t{flex:8;background:var(--card)}
footer{margin-top:48px;color:var(--mut);font-size:13px}
@media print{nav{display:none}body{background:#fff}}
</style>
</head>
<body>
<div class="wrap">
<header>
<h1>Findy — Teknik Özet</h1>
<p>Prototip tasarım paketi v0.1 · 12 Kasım 2026 · festival ve partilerde arkadaş bulma cihazı</p>
</header>

<nav>
<a href="#durum">Durum</a><a href="#hedef">Hedefler</a><a href="#mimari">Mimari</a><a href="#radyo">Radyo</a>
<a href="#baglanti">Bağlantı</a><a href="#mekanik">Mekanik</a><a href="#alisveris">Alınacaklar</a><a href="#acik">Açık konular</a>
<button id="th" type="button">Tema</button>
</nav>

<div class="note bad"><b>Bu bir kâğıt tasarımıdır.</b> Hiçbir parça alınmadı, hiçbir donanım kurulmadı, hiçbir ölçüm yapılmadı. Menzil, pil süresi ve akım değerleri hedef ya da veri sayfası tahminidir; ölçülmüş performans olarak sunulmamalıdır. Radyo mimarisi seçilmiş değildir: bu paket, deney planındaki A adayının (868&nbsp;MHz LoRa + GNSS + pusula) prototipidir.</div>

<h2 id="durum">Durum</h2>
<div class="tw"><table>
<tr><th>Parça</th><th>Durum</th><th>Açıklama</th></tr>
<tr><td>Mimari ve radyo protokolü</td><td><span class="tag ok">yazıldı</span></td><td>Üretici belgeleriyle karşılaştırmada çıkan hatalar düzeltildi (mimari belgesi bölüm 12).</td></tr>
<tr><td>Yazılım çekirdeği</td><td><span class="tag ok">test edildi</span></td><td>Konum, paket, şifreleme, zamanlama, pusula, tuş: bilgisayarda 33 testin hepsi geçiyor.</td></tr>
<tr><td>Yazılım donanım katmanı</td><td><span class="tag bad">derlenmedi</span></td><td>Radyo, ekran, GNSS, BLE sürücü kodu yazıldı ama hiç derlenmedi; ilk derlemede hata beklenir.</td></tr>
<tr><td>Parça listesi</td><td><span class="tag ok">doğrulandı</span></td><td>Üretici sayfalarından. Bazı ayrıntılar (anten, başlık lehimi) doğrulanamadı.</td></tr>
<tr><td>Bağlantı şeması</td><td><span class="tag warn">kısmen</span></td><td>Doğrulanamayan pinler şemada işaretli; ilk güç verişte ölçülecek.</td></tr>
<tr><td>Teknik çizimler ve 3B baskı dosyaları</td><td><span class="tag warn">konsept</span></td><td>Geometri kontrolünden geçti; tuş deliği, şarj açıklığı, vida yok. Basılmadı.</td></tr>
<tr><td>Parça siparişi</td><td><span class="tag bad">verilmedi</span></td><td>Liste onaylandı (12 Kasım 2026); tüm parçalar için stokta satıcı bulundu, sipariş bekliyor.</td></tr>
</table></div>

<h2 id="hedef">Hedefler</h2>
<div class="grid">
<div class="card kpi"><div class="l">Menzil</div><div class="v">300–500 m</div><div class="s">açık alan</div></div>
<div class="card kpi"><div class="l">Boyut</div><div class="v">~40 mm</div><div class="s">yuvarlak modül</div></div>
<div class="card kpi"><div class="l">Pil</div><div class="v">2–3 gün</div><div class="s">tek şarj</div></div>
<div class="card kpi"><div class="l">Fiyat</div><div class="v">60–90 $</div><div class="s">iki cihazlık set, perakende</div></div>
</div>
<p>Ek istekler: 5 cihaza kadar eşleşme · ekranda kişisel avatar (tuşa basınca birkaç saniye) · kol bandı, anahtarlık ve kolye olarak takma.</p>

<h3>Onaylanan kabul ölçütleri (deney düzeneği)</h3>
<div class="tw"><table>
<tr><th>Ölçüt</th><th>Eşik</th></tr>
<tr><td>Bilekte, açık alan, 300 m paket ulaşma oranı</td><td>≥ %90</td></tr>
<tr><td>Kalabalıkta, 150 m paket ulaşma oranı</td><td>≥ %80</td></tr>
<tr><td>Aktif aramada konum gecikmesi</td><td>≤ 5 sn</td></tr>
<tr><td>Yön hatası (30 m ve üzeri)</td><td>≤ ±30°</td></tr>
<tr><td>Mesafe hatası (30 m ve üzeri)</td><td>≤ %20 ya da ±10 m</td></tr>
<tr><td>Ortalama akım</td><td>≤ 7 mA (pil hedefini tek başına garanti etmez, aşağıya bakın)</td></tr>
</table></div>

<h2 id="mimari">Mimari</h2>
<p>İki aşama var. <b>P0</b>, hazır modüllerle masada kurulan deney düzeneğidir; menzil ve yön doğruluğunu ölçmek içindir. <b>P1</b>, 40 mm gövdeye sığacak ürün konseptidir; özel kart gerektirir ve henüz şeması yoktur.</p>

<div class="card">
<svg class="blk" viewBox="0 0 760 330" role="img" aria-label="Blok şema">
<line x1="380" y1="165" x2="120" y2="55"/><line x1="380" y1="165" x2="120" y2="165"/><line x1="380" y1="165" x2="120" y2="275"/>
<line x1="380" y1="165" x2="640" y2="55"/><line x1="380" y1="165" x2="640" y2="165"/><line x1="380" y1="165" x2="640" y2="275"/>
<line x1="380" y1="165" x2="380" y2="45"/><line x1="380" y1="165" x2="380" y2="285"/>
<rect class="core" x="280" y="115" width="200" height="100" rx="12"/>
<text x="380" y="150">RAK4631</text><text class="s" x="380" y="170">nRF52840 işlemci + BLE</text><text class="s" x="380" y="186">SX1262 LoRa 868 MHz</text>
<rect x="30" y="28" width="180" height="54" rx="10"/><text x="120" y="52">GNSS · RAK12500</text><text class="s" x="120" y="69">u-blox ZOE-M8Q · I2C</text>
<rect x="30" y="138" width="180" height="54" rx="10"/><text x="120" y="162">Pusula + ivmeölçer</text><text class="s" x="120" y="179">LSM303AGR · I2C</text>
<rect x="30" y="248" width="180" height="54" rx="10"/><text x="120" y="272">Tuş</text><text class="s" x="120" y="289">kısa · çift · uzun basış</text>
<rect x="550" y="28" width="180" height="54" rx="10"/><text x="640" y="52">Yuvarlak ekran 1,28"</text><text class="s" x="640" y="69">GC9A01 · 240×240 · SPI</text>
<rect x="550" y="138" width="180" height="54" rx="10"/><text x="640" y="162">Titreşim motoru</text><text class="s" x="640" y="179">MOSFET + diyot üzerinden</text>
<rect x="550" y="248" width="180" height="54" rx="10"/><text x="640" y="272">Telefon / bilgisayar</text><text class="s" x="640" y="289">BLE · yalnızca ayar ve avatar</text>
<rect x="300" y="8" width="160" height="40" rx="10"/><text x="380" y="33">868 MHz anten</text>
<rect x="290" y="282" width="180" height="42" rx="10"/><text x="380" y="300">LiPo pil + şarj</text><text class="s" x="380" y="315">RAK19007 taban · USB-C</text>
</svg>
</div>

<h3>Nasıl çalışır</h3>
<ul>
<li>Her cihaz kendi konumunu GNSS'ten alır ve gruba LoRa ile şifreli yayınlar. Telefon ve internet gerekmez.</li>
<li>Alan cihaz, iki konumdan mesafeyi ve kerterizi hesaplar; pusula yönünü çıkararak ekranda oku çizer.</li>
<li>Pusula eğim düzeltmelidir; cihaz 60°'den fazla eğikse ok gizlenir (kolyede asılıyken güvenilmez).</li>
<li>Ekranlar: avatar, radar (4 arkadaş + seçilen kişi için ok), eşleşme, durum.</li>
<li>Tuş: kısa basış ekranı açar/arkadaş değiştirir · 1,5 sn seçili arkadaşa titreşimli çağrı · 5 sn eşleşme · 10 sn gruptan çıkış.</li>
<li>Telefon/bilgisayar bağlantısı yalnızca ad, avatar ve ayar yüklemek içindir (BLE).</li>
</ul>

<h3>Güç bütçesi (tahmin, ölçülmedi)</h3>
<div class="tw"><table>
<tr><th>Aşama</th><th class="n">Ortalama akım</th><th>Açıklama</th></tr>
<tr><td>P0 deney düzeneği</td><td class="n">≈ 22–26 mA</td><td>GNSS modülünün yedek beslemesi yok; kapatılırsa her seferinde soğuk başlar, bu yüzden sürekli açık.</td></tr>
<tr><td>P1 ürün hedefi</td><td class="n">≈ 1,7–2 mA</td><td>Daha düşük güçlü, aralıklı çalışan GNSS varsayımıyla; ekran hariç.</td></tr>
<tr><td>2–3 gün için gereken</td><td class="n">≤ ~2,5 mA</td><td>40 mm gövdeye sığan hazır pil ~150 mAh sınıfı.</td></tr>
</table></div>
<div class="note warn"><b>Boyut ile pil hedefi çatışıyor.</b> Kâğıt üzerinde sınırda. Karar (11 Kasım 2026): boyut mu pil hedefi mi esneyecek, gerçek akım ölçüldükten sonra belirlenecek. Seçenekler: çapı 44–46 mm'ye büyütmek, özel biçimli pil, daha kalın gövde ya da pil hedefini ~1,5 güne indirmek.</div>

<h2 id="radyo">Radyo protokolü (FindyLink v0)</h2>
<div class="tw"><table>
<tr><th>Parametre</th><th>Değer</th></tr>
<tr><td>Frekans</td><td>869,525 MHz (AB 869,4–869,65 MHz alt bandı)</td></tr>
<tr><td>Modülasyon</td><td>LoRa · BW 125 kHz · SF8 · CR 4/5</td></tr>
<tr><td>Çıkış gücü</td><td>+14 dBm (varsayılan)</td></tr>
<tr><td>Erişim</td><td>5 dilimli zaman paylaşımı; her cihazın kendi dilimi</td></tr>
<tr><td>Çerçeve</td><td>Bekleme kipi 15 sn · arama kipi 5 sn (biri arama başlatınca grup 60 sn arama kipine geçer)</td></tr>
<tr><td>Zaman kaynağı</td><td>GNSS saati → alınan paketten faz kilidi → serbest çalışma; koruma payı ±120 ms</td></tr>
<tr><td>Paket</td><td>30 bayt; hesaplanan hava süresi ≈ 123 ms (ölçülmedi)</td></tr>
<tr><td>Şifreleme</td><td>ChaCha20-Poly1305, grup anahtarı; tekrar saldırısına karşı sayaç</td></tr>
</table></div>
<h3>Paket yapısı</h3>
<div class="pkt"><div class="h">Başlık · 8 bayt<br>grup, cihaz no, sayaç</div><div class="e">Şifreli yük · 14 bayt<br>enlem, boylam, konum yaşı, doğruluk, pil, bayraklar</div><div class="t">Doğrulama etiketi · 8 bayt</div></div>
<div class="note warn"><b>Eşleşme güvensiz.</b> v0'da grup anahtarı, cihazlar birbirine değdirilirken düşük güçte ama açık olarak gönderilir. Yalnızca deney için kabul edilebilir; ürün öncesi güvenli anahtar değişimiyle değiştirilecek.</div>

<h2 id="baglanti">Bağlantı şeması (P0)</h2>
<figure>__WIRING__<figcaption>Telden tele tablo: <code>hardware/baglanti-tablosu.md</code>. Doğrulanamayan pinler ilk güç verişte multimetreyle ölçülecek.</figcaption></figure>

<h2 id="mekanik">Mekanik konsept (P1)</h2>
<div class="grid">
<div class="card kpi"><div class="l">Dış çap</div><div class="v">40 mm</div></div>
<div class="card kpi"><div class="l">Kalınlık</div><div class="v">12,4 mm</div></div>
<div class="card kpi"><div class="l">Kart çapı</div><div class="v">36 mm</div><div class="s">iç çap 36,8 · duvar 1,6 mm</div></div>
<div class="card kpi"><div class="l">Aparat arayüzü</div><div class="v">3 tırnak</div><div class="s">çevirmeli kilit, 45°</div></div>
</div>
<p>Ölçüler hedef değerdir. İki parçalı gövde, tuş saat 3 yönünde. Aynı modül kol bandına ve anahtarlık aparatına takılır; kolye, anahtarlık aparatının halkasını kullanır.</p>
<div class="draws">
__DRAWINGS__
</div>

<h2 id="alisveris">Alınacaklar listesi (2 cihaz)</h2>
<p>Fiyat ve stok, 12 Kasım 2026'da mağaza ürün sayfalarından kontrol edildi. Kargo, gümrük ve vergi dahil değildir.</p>
<div class="note warn"><b>İki parça ana mağazasında yok, başka satıcıda bulundu:</b> RAK12500 GNSS modülü Rokland'da, LSM303AGR pusula modülü Pimoroni'de stokta. Bu satıcıların teslimat ülkesine gönderim yapıp yapmadığı kontrol edilmedi. Rokland sayfasındaki nota göre RAK12500 üretimden kalkıyor (u-blox ZOE-M8Q sonlandırıldı); 2 cihazlık deney için sorun değil, 5 cihazlık aşamada parça bulunamayabilir.</div>
<div class="tw"><table>
<tr><th>Parça</th><th>İşlev</th><th>Nereden</th><th class="n">Adet</th><th class="n">Birim</th><th class="n">Tutar</th><th>Sepette dikkat</th></tr>
<tr><td>WisBlock Starter Kit (RAK19007 + RAK4631)</td><td>İşlemci + BLE + LoRa, taban kartı, antenler, USB-C kablo</td><td>RAK</td><td class="n">2</td><td class="n">$24,99</td><td class="n">$49,98</td><td>"with Arduino" ve EU868 seçilecek · stokta</td></tr>
<tr><td>RAK13002</td><td>Pinleri dışarı çıkaran adaptör</td><td>RAK</td><td class="n">2</td><td class="n">$6,00</td><td class="n">$12,00</td><td>Stokta · başlık lehimli mi belli değil</td></tr>
<tr><td>RAK12500</td><td>GNSS (u-blox ZOE-M8Q)</td><td>Rokland (ABD)</td><td class="n">2</td><td class="n">$26,97</td><td class="n">$53,94</td><td>Rokland'da stokta (RAK'ta yok) · <span class="tag warn">üretimden kalkıyor</span></td></tr>
<tr><td>1,28" yuvarlak LCD (SKU 19192)</td><td>Ekran, GC9A01</td><td>Waveshare</td><td class="n">2</td><td class="n">$14,99</td><td class="n">$29,98</td><td>Stok bilgisi görülmedi · muadil GC9A01 modül de olur</td></tr>
<tr><td>LSM303AGR (Adafruit 4413)</td><td>Pusula + ivmeölçer</td><td>Pimoroni (İngiltere)</td><td class="n">2</td><td class="n">£10,75</td><td class="n">£21,50</td><td>Pimoroni'de stokta · Adafruit'te yok</td></tr>
<tr><td>LiPo 350 mAh (Adafruit 2750)</td><td>Pil</td><td>Adafruit / yerel</td><td class="n">2</td><td class="n">$6,95</td><td class="n">$13,90</td><td>Stokta · kargo kısıtı uyarısı var; kutup sırasını ölç</td></tr>
<tr class="sum"><td colspan="5">Fiyatı görülen kalemler, 2 cihaz</td><td class="n">$159,80 + £21,50</td><td>kur çevrilmedi · dört ayrı satıcı</td></tr>
</table></div>

<h3>Tutara dahil olmayanlar</h3>
<div class="tw"><table>
<tr><th>Kalem</th><th>Fiyat</th><th>Not</th></tr>
<tr><td>Akım ölçüm cihazı (Nordic PPK2)</td><td>doğrulanmadı</td><td>Pil kararı için gerekli. Arama özetlerinde $89 ve üstü geçti.</td></tr>
<tr><td>Küçük malzeme (2 takım)</td><td>bakılmadı</td><td>Titreşim motoru, N-MOSFET, Schottky diyot, 100 Ω ve 100 kΩ direnç, 100 µF ve 100 nF kondansatör, tuş, breadboard, ~50 jumper kablo, header.</td></tr>
<tr><td>Multimetre, havya</td><td>bakılmadı</td><td>Varsa gerekmez.</td></tr>
<tr><td>Kargo, gümrük, vergi</td><td>bakılmadı</td><td></td></tr>
</table></div>
<p>Bu, deney düzeneğinin maliyetidir; ürünün birim maliyeti değildir. Ürün maliyet çalışması henüz yapılmadı.</p>

<h2 id="acik">Açık konular</h2>
<div class="tw"><table>
<tr><th>Konu</th><th>Durum</th></tr>
<tr><td>Pil – boyut çatışması</td><td>~150 mAh sığıyor; karar akım ölçümünden sonra.</td></tr>
<tr><td>868 MHz anten</td><td>40 mm gövdede çözüm yok; kayış içi ya da çevre anteni ayrı çalışma ister.</td></tr>
<tr><td>GNSS anteni</td><td>40 mm gövdede yeri belirlenmedi.</td></tr>
<tr><td>Güvenli eşleşme</td><td>v0 güvensiz; ürün öncesi değişecek.</td></tr>
<tr><td>Özel kart</td><td>Şema ve üretim dosyaları yok.</td></tr>
<tr><td>Telefon uygulaması</td><td>Yok; ayar ve avatar şimdilik bilgisayardan (<code>tools/findy_ble.py</code>).</td></tr>
<tr><td>Sertifikasyon ve frekans kuralları</td><td>AB için doğrulandı, Türkiye için kısmen, Kıbrıs için doğrulanamadı.</td></tr>
<tr><td>Kalınlık/ağırlık ve su dayanımı hedefi</td><td>Belirlenmedi.</td></tr>
<tr><td>Siparişi kim verecek, düzeneği kim kuracak</td><td>Belirlenmedi.</td></tr>
</table></div>

<footer>
Kaynak belgeler proje klasöründe: <code>docs/mimari-v0.1.md</code> · <code>docs/deney-duzenegi-plani.md</code> · <code>hardware/BOM-P0.md</code> · <code>hardware/alisveris-listesi.md</code> · <code>hardware/dogrulama-notlari.md</code> · <code>firmware/README.md</code>.
Bu sayfa <code>tools/build_findy_teknik_ozet.py</code> ile üretilir.
</footer>
</div>
<script>
document.getElementById('th').onclick=function(){var r=document.documentElement,d=r.dataset.theme||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');r.dataset.theme=d==='dark'?'light':'dark'};
</script>
</body>
</html>
"""


def main() -> None:
    wiring = img(ROOT / "hardware/baglanti-semasi.svg", "Bağlantı şeması")
    html = HTML.replace("__WIRING__", wiring).replace("__DRAWINGS__", drawings())
    OUT.write_text(html, encoding="utf-8")
    print(f"{OUT} yazıldı: {OUT.stat().st_size/1024:.0f} KB, "
          f"{html.count('<figure')} şekil")


if __name__ == "__main__":
    main()

import argparse
import base64
import json
import re
import subprocess
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


def data_uri(content, media_type):
    return f"data:{media_type};base64,{base64.b64encode(content).decode('ascii')}"


def poster_uri(video_path, seconds):
    command = [
        "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
        "-ss", str(seconds), "-i", str(video_path),
        "-frames:v", "1", "-vf", "scale=540:-2",
        "-f", "image2pipe", "-vcodec", "mjpeg", "-q:v", "3", "pipe:1",
    ]
    return data_uri(subprocess.check_output(command), "image/jpeg")


def replace_section(document, section_id, content):
    pattern = rf'<section\b[^>]*\bid="{re.escape(section_id)}"[^>]*>.*?</section>'
    document, count = re.subn(pattern, lambda match: content, document, flags=re.S)
    if count != 1:
        raise ValueError(f"Expected one section: {section_id}; found {count}")
    return document


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, default=ROOT / "references" / "findy-yatirimci-sunumu.html")
    parser.add_argument("--output", type=Path, default=ROOT / "findy-yatirimci-sunumu-v2.html")
    arguments = parser.parse_args()
    document = arguments.reference.read_text(encoding="utf-8")
    required_files = [
        ASSETS / "videos" / "gemini_generated_video_e3e40a4a.mp4",
        ASSETS / "videos" / "gemini_generated_video_017ede88.mp4",
        ASSETS / "videos" / "gemini_generated_video_91056a3b.mp4",
        ASSETS / "images" / "Gemini_Generated_Image_5jhsst5jhsst5jhs.jpeg",
    ]
    for media_path in required_files:
        if not media_path.is_file():
            raise FileNotFoundError(media_path)

    film_specs = [
        (required_files[0], "01", "Kalabalıkta yeniden buluşma", "Bilekteki yön oku, kalabalığın içinden geçen kısa bir yolculuk ve arkadaşla yeniden buluşma.", "portrait", 7),
        (required_files[1], "02", "Bir bakışta yönünü bul", "Cihaz ekranından buluşma anına: yön ve mesafe arayüzünü anlatan ikinci kullanım senaryosu.", "portrait", 4),
        (required_files[2], "03", "İçeriden Findy", "Anahtarlık aparatından ayrılan modül ve katmanların açıldığı patlamalı ürün animasyonu.", "landscape", 4),
    ]
    film_cards = []
    for video_path, number, title, description, orientation, seconds in film_specs:
        film_cards.append(f'''<article class="film-card {orientation}">
          <div class="film-heading"><span class="film-number">{number}</span><span>10 sn · AI konsept filmi</span></div>
          <div class="film-frame">
            <video controls playsinline preload="none" poster="{poster_uri(video_path, seconds)}" aria-label="Findy: {title}" data-filename="{video_path.name}">
              <source src="{data_uri(video_path.read_bytes(), 'video/mp4')}" type="video/mp4">
              Tarayıcınız video oynatmayı desteklemiyor.
            </video>
          </div>
          <h3>{title}</h3><p>{description}</p>
          {'<div class="film-detail"><span>Tek modül.</span><span>İki taşıma biçimi.</span><span>Aynı Findy deneyimi.</span></div>' if orientation == 'landscape' else ''}
        </article>''')

    document = replace_section(document, "video", f'''<section class="video-sec" id="video">
      <div class="wrap">
        <p class="kicker">Ürün filmleri · 3 × 10 saniye</p>
        <h2>Findy’yi hareket halinde görün.</h2>
        <p class="lead">İki festival hikâyesi ve bir patlamalı ürün animasyonu. Aynı modülün kullanım deneyimi ve tasarım yaklaşımı.</p>
        <div class="film-grid">{''.join(film_cards)}</div>
        <p class="disclosure">Görsel ve videolar AI destekli konsept gösterimleridir; çalışan donanım, gerçek saha testi veya doğrulanmış menzil kanıtı değildir. İç bileşenler ve ekrandaki mesafeler temsilidir.</p>
      </div>
    </section>''')

    document = document.replace("Yatırımcı sunumu, [TARİH]", "Yatırımcı sunumu · 3 Kasım 2026 · Ürün konsepti")
    document = document.replace("Kalabalıkta kaybolmak bitti.", "Kalabalıkta<br>birbirini bul.")
    document = document.replace(
        "Findy, festival ve parti kalabalığında arkadaşların birbirini telefonsuz bulmasını sağlayan, avuç içi büyüklüğünde yuvarlak bir cihaz. Ekranındaki ok ve mesafe, seni doğrudan arkadaşına götürür.",
        "Findy, festival ve parti kalabalığında arkadaşların birbirini telefonsuz bulmasını hedefleyen yuvarlak ekranlı bir cihaz konsepti. Tek bir modül, kol bandı veya anahtarlık olarak taşınır; telefona bağlantı isteğe bağlıdır.",
    )
    document = document.replace("<span>Şebeke ve internet gerekmez</span>", "<span>Şebekeden bağımsızlık hedefi</span>")
    document = document.replace("<span>Grup, isim ve ayarlar</span>", "<span>İsim, grup ve ayar desteği</span>")
    document = document.replace('<li><a href="#video">Video</a></li>', '<li><a href="#video">3 film</a></li>')

    document = replace_section(document, "problem", '''<section class="problem" id="problem"><div class="wrap">
      <p class="kicker">Problem hipotezi</p><h2>Gecenin odağı ekran değil, arkadaşların olsun.</h2>
      <p class="lead">Findy’nin başlangıç sorusu: kalabalıkta ayrılan arkadaşlar, tekrar tekrar mesajlaşmadan daha kolay buluşabilir mi?</p>
      <div class="grid3">
        <div><h3>“Neredesin?” döngüsü</h3><p>Birbirini tarif etmek, mesajları kontrol etmek ve buluşma noktası aramak deneyimi bölebilir.</p></div>
        <div><h3>Dikkat isteyen ekran</h3><p>Ürün hipotezi: kısa bir bakışla anlaşılabilen bir yönlendirme, kalabalıkta daha az dikkat gerektirebilir.</p></div>
        <div><h3>Birlikte yaşanan gece</h3><p>Satın alınmak istenen şey bir takip ekranı değil; arkadaş grubuyla daha kolay yeniden buluşma deneyimi.</p></div>
      </div>
      <p class="disclosure">Bu ihtiyaçlar henüz kullanıcı araştırması sonuçları olarak sunulmamaktadır. Görüşmeler ve saha pilotuyla doğrulanacaktır.</p>
    </div></section>''')

    document = replace_section(document, "teknoloji", '''<section class="tech" id="teknoloji"><div class="wrap">
      <p class="kicker">Teknik doğrulama planı</p><h2>Telefonsuz kullanım. Ölçülerek seçilecek mimari.</h2>
      <div class="tech-grid"><div class="layers">
        <div class="layer"><strong>Eşleşme</strong><span>Hedef: karşılıklı onayla arkadaş veya grup oluşturma; kullanıcının eşleşmeyi sonlandırabilmesi.</span></div>
        <div class="layer"><strong>Cihazdan cihaza</strong><span>Temel bulma işlevini telefon ve internet zorunluluğu olmadan çalıştırma hedefi.</span></div>
        <div class="layer"><strong>Yön ve mesafe</strong><span>Gösterim yöntemi, anten yerleşimi ve ölçüm yaklaşımı prototip testleriyle seçilecek.</span></div>
        <div class="layer"><strong>Geri bildirim</strong><span>Yuvarlak ekran, LED halka ve titreşim için okunabilirlik ve enerji tüketimi testleri.</span></div>
        <div class="layer"><strong>Telefon desteği</strong><span>İsteğe bağlı bağlantı: arkadaş isimleri, grup ayarları ve cihaz yönetimi.</span></div>
      </div><div class="note"><h3>Henüz verilmemiş sözler</h3>
        <p>Menzil, yön doğruluğu, pil süresi, su dayanımı ve birim maliyet için doğrulanmış değer paylaşılmadı. Sunum bu alanlarda performans iddiası içermez.</p>
        <p style="margin-top:18px">İlk doğrulama odağı açık alan etkinlikleri. Kapalı mekân ve yoğun insan kalabalığı ayrıca test edilecek.</p>
        <p style="margin-top:18px">Konum/yön ölçümü ile telefon bağlantısı ayrı doğrulama başlıklarıdır. Kullanılacak teknoloji henüz seçilmiş kabul edilmez.</p>
      </div></div>
    </div></section>''')

    document = replace_section(document, "pazar", '''<section id="pazar"><div class="wrap">
      <p class="kicker">Pazara giriş ve iş modeli</p><h2>İlk kullanıcı arkadaş grubu. İlk kapı etkinlik.</h2>
      <p class="lead">Başlangıç odağı: açık alan festivallerinde birlikte gelen arkadaş grupları. İlk adım geniş bir pazar iddiası değil, doğru kullanıcı ve ücretli kullanım isteğini doğrulamak.</p>
      <div class="business-grid">
        <article class="business-card"><span class="model-number">01 / TÜKETİCİ</span><h3>Arkadaş paketleri</h3><p>İkili ve grup paketleriyle cihaz satışı. Temel senaryoda her kullanıcı bir Findy taşır.</p><strong>Ölçülecek: paket başına ödeme isteği</strong></article>
        <article class="business-card"><span class="model-number">02 / ORGANİZATÖR</span><h3>Etkinlikte kiralama</h3><p>Organizatörle pilot; teslim, iade, şarj ve yeniden kullanım operasyonunun birlikte denenmesi.</p><strong>Ölçülecek: kiralama başına net katkı</strong></article>
        <article class="business-card"><span class="model-number">03 / AKSESUAR</span><h3>Aynı modüle yeni kullanım</h3><p>Kol bandı ve anahtarlık aparatı için farklı taşıma seçenekleri; modülün kullanımını genişletme.</p><strong>Ölçülecek: aksesuar ekleme oranı</strong></article>
      </div>
      <div class="positioning"><div><p class="kicker">Yatırım tezi</p><h3>Önce deneyimi kanıtla, sonra dağıtımı büyüt.</h3></div><p>Findy’nin test edilecek değeri: sade ekran, modüler taşıma ve etkinliğe uygun kullanım. Fiyat, maliyet, pazar büyüklüğü ve gelir projeksiyonu için henüz doğrulanmış veri sunulmadı.</p></div>
      <div class="validation-row"><div><strong>Talep</strong><span>Kullanıcı görüşmeleri ve fiyat testi</span></div><div><strong>Ekonomi</strong><span>Tedarikçi teklifi, hasar ve iade maliyeti</span></div><div><strong>Dağıtım</strong><span>Pilot etkinlik ve organizatör görüşmeleri</span></div></div>
    </div></section>''')

    document = replace_section(document, "yol", '''<section class="tech" id="yol"><div class="wrap">
      <p class="kicker">Aşama bazlı yol haritası</p><h2>Konseptten ilk sahaya.</h2>
      <ol class="road">
        <li><time>AŞAMA 01</time><h3>Teknik fizibilite</h3><p>İki cihazlı deney düzeneği; yön, mesafe, bağlantı kaybı ve enerji tüketimi ölçümleri.</p></li>
        <li><time>AŞAMA 02</time><h3>Kullanılabilir prototip</h3><p>Gövde, kol bandı ve anahtarlık aparatı; eşleşme ve ekran akışlarının kullanıcılarla denenmesi.</p></li>
        <li><time>AŞAMA 03</time><h3>Kontrollü saha pilotu</h3><p>Etkinlik ortamında buluşma başarısı, kullanım sıklığı, pil tüketimi ve ödeme isteği ölçümü.</p></li>
        <li><time>AŞAMA 04</time><h3>Üretime geçiş kararı</h3><p>Pilot sonucuna göre maliyet, ürün güvenliği değerlendirmeleri ve üretim planı için devam / durdur kararı.</p></li>
      </ol><p class="disclosure">Bu akış bir çalışma planıdır; taahhüt edilmiş teslim takvimi, imzalı organizatör anlaşması veya tamamlanmış sertifikasyon değildir.</p>
    </div></section>''')

    document = replace_section(document, "ekip", '''<section id="ekip"><div class="wrap">
      <p class="kicker">İhtiyaç duyulan yetkinlikler</p><h2>Üç disiplin. Tek ürün deneyimi.</h2>
      <div class="business-grid">
        <article class="business-card"><span class="model-number">DONANIM</span><h3>Radyo ve gömülü sistemler</h3><p>Haberleşme, yön/mesafe yaklaşımı, anten yerleşimi ve enerji bütçesinin doğrulanması.</p></article>
        <article class="business-card"><span class="model-number">ÜRÜN</span><h3>Tasarım ve kullanıcı deneyimi</h3><p>Modüler gövde, ekran okunabilirliği, eşleşme akışı ve telefondaki isteğe bağlı deneyim.</p></article>
        <article class="business-card"><span class="model-number">PAZARA GİRİŞ</span><h3>Etkinlik ve operasyon</h3><p>Pilot ortakları, kullanıcı araştırması, teslim/iade süreci ve gelir modelinin test edilmesi.</p></article>
      </div><p class="disclosure">Bu bölüm mevcut ekip üyeleri veya özgeçmişleri yerine ihtiyaç duyulan rolleri gösterir; kurucu ve ekip bilgileri paylaşılmadığı için isim eklenmemiştir.</p>
    </div></section>''')

    document = replace_section(document, "yatirim", '''<section class="ask" id="yatirim"><div class="wrap ask-grid">
      <div><p class="kicker">Yatırım görüşmesinin odağı</p><h2>Birlikte ilk sahaya çıkalım.</h2>
        <div class="ask-statement">Konsept →<br>Çalışan prototip →<br>Ölçülebilir pilot.</div>
        <p class="lead">Aranan destek: teknik prototipleme, ürünleştirme ve doğru etkinlik ortağına erişim.</p>
        <a class="cta" href="#video">Ürün filmlerine dön <span aria-hidden="true">↗</span></a>
      </div><div class="ask-priorities"><h3>İlk sermayenin açacağı kapılar</h3>
        <div><span>01</span><p><strong>Teknik riski azaltmak</strong><br>Ölçüm mimarisi, radyo bağlantısı ve pil testleri.</p></div>
        <div><span>02</span><p><strong>Kullanılabilir ürünü oluşturmak</strong><br>Elektronik prototip, gövde ve iki taşıma aparatı.</p></div>
        <div><span>03</span><p><strong>Talebi sahada doğrulamak</strong><br>Kontrollü pilot, fiyat testi ve operasyon ölçümü.</p></div>
        <p class="ask-disclosure">Yatırım tutarı, hisse oranı ve değerleme kurucu onayıyla netleştirilecek. Bu sunuma uydurma finansal rakam veya yatırım koşulu eklenmemiştir.</p>
      </div>
    </div></section>''')

    document = re.sub(r'<link\b[^>]*href="https://fonts\.[^"]*"[^>]*>', "", document)
    document = document.replace("[YIL]", "2026")
    document = document.replace("<footer>", "<footer><strong>Findy</strong><br>")
    document = document.replace("Gizli, yalnızca yatırımcı görüşmesi içindir", "Ürün konsepti · Yatırımcı görüşmesi için hazırlanmıştır")
    document = re.sub(r'<!--.*?-->', "", document, flags=re.S)

    extra_css = '''
      [hidden]{display:none!important}
      .nav-in{gap:18px}.nav ul{gap:0}.nav ul a{padding:8px 9px;font-size:13px}
      .nav-actions{display:flex;gap:8px;margin-left:auto}.nav ul+.nav-actions{margin-left:0}
      .nav-action{background:var(--panel);border:1px solid var(--line);color:var(--ink);font:700 13px var(--body);border-radius:999px;padding:9px 13px;cursor:pointer;white-space:nowrap}
      .nav-action:hover{background:var(--bg-2)}.nav ul a[aria-current="location"]{background:var(--bg-2);color:var(--amber)}
      .hero h1{font-size:clamp(42px,6.6vw,88px);line-height:1.02;letter-spacing:-.05em}
      .hero-fig{position:relative}.hero-fig::after{content:"AI ürün konsepti";position:absolute;right:18px;bottom:16px;padding:5px 12px;font-size:12px;border-radius:999px;background:#ffffffde;color:#343943}
      .film-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr) minmax(0,1.35fr);gap:24px;margin-top:44px;align-items:start}
      .film-card{padding:16px;border:1px solid var(--line);border-radius:28px;background:var(--panel);overflow:hidden;min-width:0}
      .film-heading{display:flex;align-items:center;justify-content:space-between;gap:8px;font-size:11px;color:var(--ink-2);margin:0 2px 14px;letter-spacing:.01em}
      .film-number{font:700 14px var(--display);color:var(--amber)}
      .film-frame{aspect-ratio:9/16;background:#090a10;border-radius:18px;overflow:hidden;isolation:isolate}
      .landscape .film-frame{aspect-ratio:16/9}
      .film-frame video{display:block;width:100%;height:100%;object-fit:contain;background:#090a10}
      .film-card h3{font-size:18px;line-height:1.35;margin:22px 2px 10px;letter-spacing:-.03em}
      .film-card>p{font-size:14px;color:var(--ink-2);line-height:1.7;margin:0 2px 5px}
      .film-detail{display:grid;gap:12px;border-top:1px solid var(--line);margin:28px 2px 0;padding-top:24px;font:700 clamp(15px,1.4vw,19px) var(--display);letter-spacing:-.02em}
      .film-detail span:last-child{color:var(--amber)}
      .disclosure{font-size:13px;line-height:1.8;color:var(--ink-2);margin-top:28px;max-width:100ch}
      .business-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px;margin-top:48px}
      .business-card{background:var(--panel);border:1px solid var(--line);border-radius:26px;padding:30px;display:flex;flex-direction:column;gap:20px;min-width:0}
      .model-number{font-size:12px;font-weight:700;color:var(--amber);letter-spacing:.08em}
      .business-card h3{font-size:21px;line-height:1.35}.business-card p{font-size:16px;color:var(--ink-2)}
      .business-card>strong{font-size:13px;font-weight:700;color:var(--rose);margin-top:auto;padding-top:8px}
      .positioning{margin-top:36px;padding:36px;border:1px solid var(--line);border-radius:26px;background:var(--bg-2);display:grid;grid-template-columns:1fr 1fr;gap:36px;align-items:center}
      .positioning h3{font-size:24px}.positioning>p{color:var(--ink-2);font-size:16px}.positioning .kicker{font-size:13px}
      .validation-row{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:28px;margin-top:32px}
      .validation-row>div{border-top:2px solid var(--line);padding-top:18px}.validation-row strong{display:block;color:var(--amber);margin-bottom:8px}.validation-row span{font-size:15px;color:var(--ink-2)}
      .ask-statement{font-family:var(--display);font-weight:800;color:var(--amber-glow);font-size:clamp(24px,3.1vw,43px);line-height:1.5;margin-top:32px;letter-spacing:-.035em}
      .ask-priorities>h3{font-size:22px;line-height:1.4;margin-bottom:28px}.ask-priorities>div{display:flex;align-items:flex-start;gap:20px;border-top:1px solid #343a52;padding:22px 0}.ask-priorities>div>span{color:var(--amber-glow);font-weight:700;font-size:14px;padding-top:4px}.ask-priorities p{font-size:16px;color:var(--ask-ink-2)}.ask-priorities strong{color:var(--ask-ink)}
      .ask-priorities .ask-disclosure{font-size:12px;line-height:1.8;margin-top:16px}
      .progress-line{position:fixed;left:0;bottom:0;height:3px;width:100%;background:var(--amber-glow);transform:scaleX(0);transform-origin:left;z-index:20;pointer-events:none}
      .presentation-hint{text-align:center;font-size:12px;color:var(--ink-2);padding:20px 24px 0}
      @media(min-width:1250px){.nav-in{padding-left:20px;padding-right:20px}.nav-actions{gap:5px}.nav-action{padding:8px 10px}}
      @media(max-width:1180px){.nav ul a{padding:8px 7px;font-size:12px}.nav-in{gap:12px}.nav-action{padding:8px 10px;font-size:12px}}
      @media(max-width:1050px){.nav ul{display:none}.nav ul+.nav-actions{margin-left:auto}.film-grid{gap:16px}.film-card{padding:12px}.film-heading{font-size:10px}.film-card h3{font-size:16px}.business-card{padding:24px}.hero-meta{gap:22px}}
      @media(max-width:760px){.film-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.film-card.landscape{grid-column:1/-1}.film-detail{grid-template-columns:repeat(3,minmax(0,1fr));font-size:13px;gap:16px}.business-grid,.validation-row,.positioning{grid-template-columns:minmax(0,1fr)}.business-grid{gap:16px}.positioning{padding:28px;gap:24px}.business-card{gap:15px}.hero-meta{gap:20px}}
      @media(max-width:480px){.film-grid{grid-template-columns:minmax(0,1fr)}.film-card.portrait{max-width:360px;width:100%;margin:0 auto}.film-card.landscape{grid-column:auto}.film-card{padding:16px}.film-heading{font-size:12px}.film-card h3{font-size:19px}.film-detail{grid-template-columns:1fr;gap:10px;font-size:17px}.nav-in{padding:10px 16px;gap:8px}.nav-action{font-size:11px;padding:8px 10px}.hero h1{font-size:clamp(38px,10vw,52px)}.hero-meta div{min-width:130px}.hero-meta strong{font-size:15px}.hero-meta span{font-size:13px}.hero-fig{margin-top:24px;border-radius:22px}.hero-fig::after{right:10px;bottom:10px;font-size:10px}.ask-statement{font-size:clamp(23px,6.5vw,34px)}}
      @media print{.nav,.progress-line,.presentation-hint,.nav-actions{display:none!important}:root{--bg:#fff;--bg-2:#f5f6f8;--panel:#fff;--ink:#141834;--ink-2:#4a5070;--line:#cdd2e2}section{padding:40px 0;break-inside:avoid}body{font-size:12px}h1{font-size:48px!important}h2{font-size:32px}.film-grid{grid-template-columns:repeat(3,1fr)}.film-card{break-inside:avoid}.ask{print-color-adjust:exact}.hero-fig{box-shadow:none}a{color:inherit}}
    '''
    document = document.replace("</style>", extra_css + "\n</style>", 1)
    nav_actions = '''</ul><div class="nav-actions"><button class="nav-action" id="theme-toggle" type="button" aria-pressed="false">Koyu tema</button><button class="nav-action" id="fullscreen-toggle" type="button">Tam ekran</button></div>'''
    document = document.replace("</ul>", nav_actions, 1)
    document = document.replace("<main>", '<p class="presentation-hint">Bölümler arasında ← → tuşlarıyla gezinin · Videoları oynatmak için dokunun · İnternet gerektirmeyen gömülü medya</p><main>', 1)

    script = '''<div class="progress-line" aria-hidden="true"></div><script>
      (() => {
        const root = document.documentElement;
        const themeButton = document.querySelector('#theme-toggle');
        const fullscreenButton = document.querySelector('#fullscreen-toggle');
        const videos = [...document.querySelectorAll('video')];
        const sections = [...document.querySelectorAll('main > section')];
        const progress = document.querySelector('.progress-line');
        const applyTheme = theme => {
          root.dataset.theme = theme;
          themeButton.setAttribute('aria-pressed', String(theme === 'dark'));
          themeButton.textContent = theme === 'dark' ? 'Açık tema' : 'Koyu tema';
        };
        let initialTheme = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        try { initialTheme = localStorage.getItem('findy-theme') || initialTheme; } catch {}
        applyTheme(initialTheme === 'dark' ? 'dark' : 'light');
        themeButton.addEventListener('click', () => {
          const nextTheme = root.dataset.theme === 'dark' ? 'light' : 'dark';
          applyTheme(nextTheme);
          try { localStorage.setItem('findy-theme', nextTheme); } catch {}
        });
        fullscreenButton.addEventListener('click', async () => {
          try {
            if (document.fullscreenElement) await document.exitFullscreen();
            else await root.requestFullscreen();
          } catch { fullscreenButton.textContent = 'F11 ile tam ekran'; }
        });
        document.addEventListener('fullscreenchange', () => {
          fullscreenButton.textContent = document.fullscreenElement ? 'Tam ekrandan çık' : 'Tam ekran';
        });
        videos.forEach(video => video.addEventListener('play', () => {
          videos.forEach(other => { if (other !== video) other.pause(); });
        }));
        document.addEventListener('visibilitychange', () => {
          if (document.hidden) videos.forEach(video => video.pause());
        });
        document.addEventListener('keydown', event => {
          if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey || event.target.closest('video,button,a,input,textarea,select,[contenteditable]')) return;
          if (!['ArrowRight', 'ArrowLeft', 'PageDown', 'PageUp'].includes(event.key)) return;
          event.preventDefault();
          const current = sections.reduce((selected, section, index) => section.getBoundingClientRect().top <= innerHeight * .4 ? index : selected, 0);
          const direction = ['ArrowRight', 'PageDown'].includes(event.key) ? 1 : -1;
          const target = sections[Math.max(0, Math.min(sections.length - 1, current + direction))];
          target.scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'});
        });
        const navLinks = [...document.querySelectorAll('.nav ul a')];
        let queued = false;
        const updateProgress = () => {
          const available = root.scrollHeight - innerHeight;
          progress.style.transform = `scaleX(${available > 0 ? scrollY / available : 0})`;
          const active = sections.reduce((selected, section) => section.getBoundingClientRect().top <= innerHeight * .4 ? section : selected, sections[0]);
          navLinks.forEach(link => {
            if (link.hash === '#' + active.id) link.setAttribute('aria-current', 'location');
            else link.removeAttribute('aria-current');
          });
          queued = false;
        };
        addEventListener('scroll', () => { if (!queued) { queued = true; requestAnimationFrame(updateProgress); } }, {passive: true});
        addEventListener('resize', updateProgress);
        updateProgress();
      })();
    </script>'''
    document = document.replace("</body>", script + "\n</body>")
    unresolved = re.findall(r"\[(?:TARİH|FİYAT|MODEL|TAM|SAM|SOM|ÇEYREK|ETKİNLİK|AD SOYAD|ROL|GEÇMİŞ|TUTAR|HİSSE|KİLOMETRE|E-POSTA|HEDEF|SAAT|BOM|YIL|%)\b[^\]]*\]", document)
    if unresolved:
        raise ValueError(f"Unresolved placeholders: {unresolved}")
    if len(re.findall(r"<video\b", document)) != 3:
        raise ValueError("The presentation must contain all three videos")
    if "https://fonts." in document:
        raise ValueError("External font dependencies remain")
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(document, encoding="utf-8")
    print(json.dumps({"output": str(arguments.output), "bytes": arguments.output.stat().st_size, "video_count": 3, "source_reference_unchanged": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()

# Panel Projesi — AI Agent Kuralları

## BMAD Story Döngüsü Kuralları

Bu kurallar her yeni conversation'da geçerlidir. BMAD workflow'u (DS → CR → DS döngüsü) sırasında aşağıdaki adımları otomatik uygula.

### Ajan Başlangıcında Her Zaman Kontrol Et

Bir story ile çalışmaya başlamadan önce şunları kontrol et:

1. `git branch --show-current` → doğru branch'te mi? (`story/{story-id}` formatında olmalı)
2. Story dosyasındaki `Code Review Findings` başlık sayısını say → kaçıncı CR turundayım?
3. `_bmad-output/implementation-artifacts/sprint-status.yaml` → story'nin mevcut durumu ne?

---

### DS (Dev Story) Başladığında

1. **Git durumunu kontrol et ve gerekirse merge yap:**
   - `git branch --show-current` → mevcut branch nedir?
   - `git log --oneline main | head -1` → main'in HEAD commit'i nedir?
   - `sprint-status.yaml`'da `done` olan ama main'de bulunmayan story var mı?
     - Varsa: `git checkout main && git merge story/{done-story-id} --ff-only`
     - Birden fazla `done` story varsa hepsini sırayla merge et.
   - Main güncel değilse yeni branch açma, önce merge tamamla.
2. `git checkout main && git checkout -b story/{story-id}` ile branch aç (her zaman güncel main'den)
3. `sprint-status.yaml`'da story'yi `in-progress` yap

---

### Code Review (CR) — Paralel Agent Zorunluluğu

CR işlemi sırasında **3 reviewer ajanı her zaman paralel olarak çalıştırılır**. Kullanıcıdan onay veya talimat bekleme; aşağıdaki adımları otomatik uygula:

1. Diff ve spec dosyalarını hazırla (gruplar halinde gerekiyorsa).
2. **Aynı anda** 3 bağımsız ajan başlat:
   - `blind-hunter` — kodu kör olarak inceler, spec'e bakmadan hata arar
   - `edge-case-hunter` — sınır koşulları ve edge case'leri tarar
   - `acceptance-auditor` — her AC'yi tek tek doğrular
3. 3 çıktı gelince triage yap: bulguları birleştir, severity'ye göre sırala, nihai raporu üret.

> **Kritik:** "Paralel agent çalıştırayım mı?" diye sormak yasaktır. Her CR'da bu akış varsayılan davranıştır.

---

### CR'a Göndermeden Önce (code-review çalıştırılmadan)

1. Story dosyasındaki mevcut `Code Review Findings` bölüm sayısını say → N
2. Tüm değişiklikleri commit et:
   ```
   git commit -m "feat: story {story-id} implementation [CR-{N+1}]"
   ```
3. `sprint-status.yaml`'da story'yi `review` yap

---

### CR Tamamlandığında — Bulgular Çıktıysa (patch veya intent_gap var)

> Bu projede turlar uzayabildiği için bulgu çıkması story'i bloklamaz.

1. Story dosyasına yeni bölüm ekle:
   ```
   ### Code Review Findings — Tur {N} ({tarih}) → Sonradan Uygulanacak
   ```
   Tüm patch ve intent_gap bulgularını bu bölüme yaz (severity, lokasyon, düzeltme önerisi ile birlikte).
2. `sprint-status.yaml`'da story'yi `done` yap.
3. Final commit:
   ```
   git commit -m "feat: story {story-id} complete — CR logged (deferred fixes)"
   ```
4. **ZORUNLU — Main'e merge et (atlanamaz):**
   ```
   git checkout main && git merge story/{story-id} --ff-only && git checkout story/{story-id}
   ```
   - `git log --oneline main | head -1` ile merge'in başarılı olduğunu doğrula.
   - Merge başarısızsa (ff-only çalışmazsa) kullanıcıya bildir, elle müdahale gerekebilir.
5. Sonraki story'ye geç. Patch/intent_gap maddeleri daha sonra toplu düzeltme turunda uygulanır.

---

### CR Tamamlandığında — Temiz (0 patch, 0 intent_gap)

1. Story dosyasındaki son CR bölümünü `✅ Onaylandı` olarak işaretle.
2. `sprint-status.yaml`'da story'yi `done` yap.
3. Final commit:
   ```
   git commit -m "feat: story {story-id} complete — CR approved"
   ```
4. **ZORUNLU — Main'e merge et (atlanamaz):**
   ```
   git checkout main && git merge story/{story-id} --ff-only && git checkout story/{story-id}
   ```
   - `git log --oneline main | head -1` ile merge'in başarılı olduğunu doğrula.
   - Merge başarısızsa (ff-only çalışmazsa) kullanıcıya bildir, elle müdahale gerekebilir.

> **Not:** DS başlangıcındaki merge kontrolü yalnızca fallback'tir; asıl merge burada yapılır.

---

### Deferred Fix Politikası

- Review bulguları story dosyasında biriktirilir.
- Story akışı bekletilmez: `done` + `main` merge ile sprint devam eder.
- Biriken patch/intent_gap maddeleri ayrı bir sonradan-düzeltme turunda uygulanır.

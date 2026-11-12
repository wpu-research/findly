#include "slots.h"

namespace findy {

// ARAMA yayılımı (kendi kararım; spec "son bayraktan 60 sn" diyor ama kim bayrak koyar demiyor):
//  - Başlatıcı (tuş) 60 sn boyunca paketlerine bayrak koyar.
//  - BEKLEME'deyken bayraklı paket alan düğüm ARAMA'ya geçer ve o andan 60 sn boyunca bayrak koyar (röle,
//    süre uzatılmaz) — başlatıcıyı duymayan düğümler de haberdar olur ama sonsuz döngü oluşmaz.
//  - ARAMA'dan dönüş = bilinen SON bayraklı paketin (alınan ya da kendi) dilim başlangıcı + 60 sn.
//    Herkes aynı son paketi duyduğundan geri dönüş anı ortaktır; UTC yoksa BEKLEME faz
//    çapası bu anda yeniden kurulur (aksi halde 5 sn faz bilgisi 15 sn fazını belirsiz bırakır).

void SlotScheduler::set_utc(uint64_t utc_ms, ms_t local_ms) {
    uint64_t F = cfg_.standby_frame_ms;
    offset_ = (uint32_t)(((utc_ms % F) + F - (local_ms % F)) % F);
    src_ = SyncSource::Utc;
}

void SlotScheduler::enter_search(ms_t now) {
    mode_ = Mode::Search;
    have_anchor_ = false;
    search_until_ = now + cfg_.search_hold_ms;  // geçici; ilk bayrak çapası gelince yerini alır
}

void SlotScheduler::note_flag_anchor(ms_t anchor) {
    ms_t until = anchor + cfg_.search_hold_ms;
    if (!have_anchor_) { search_until_ = until; have_anchor_ = true; }
    else if (until > search_until_) search_until_ = until;
}

void SlotScheduler::request_search(ms_t now) {
    if (mode_ == Mode::Standby) enter_search(now);
    emit_until_ = now + cfg_.search_hold_ms;
    if (search_until_ < emit_until_ && !have_anchor_) search_until_ = emit_until_;
}

void SlotScheduler::on_tx(ms_t slot_start_ms, bool flagged) {
    if (flagged && mode_ == Mode::Search) note_flag_anchor(slot_start_ms);
}

void SlotScheduler::on_rx(uint8_t node, ms_t rx_start_ms, bool search_flag, ms_t now) {
    if (node == cfg_.node_id || node >= cfg_.nodes) return;
    if (search_flag) {
        if (mode_ == Mode::Standby) {
            enter_search(now);
            emit_until_ = now + cfg_.search_hold_ms;  // röle: bir kez, uzatılmaz
        }
        note_flag_anchor(rx_start_ms);
    }
    // Faz kilitleme: UTC varsa dokunma. Paket, bizim kipimizle tutarlıysa kullan.
    if (src_ == SyncSource::Utc) return;
    if (search_flag != (mode_ == Mode::Search)) return;
    uint64_t fl = frame_ms();
    uint64_t slot = fl / cfg_.nodes;
    uint64_t want = node * slot;                  // gönderenin dilim başlangıç fazı
    uint64_t have = rx_start_ms % fl;
    uint64_t off = (want + fl - have) % fl;       // fl'e göre; 15000'e genişletme: ilk fl kopyası
    offset_ = (uint32_t)off;
    src_ = SyncSource::Packet;
}

void SlotScheduler::update(ms_t now) {
    if (mode_ == Mode::Search && now >= search_until_) {
        mode_ = Mode::Standby;
        emit_until_ = 0;
        if (src_ != SyncSource::Utc) {
            // Ortak çapa: search_until_ anında BEKLEME çerçevesi başlar.
            uint64_t F = cfg_.standby_frame_ms;
            offset_ = (uint32_t)((F - (search_until_ % F)) % F);
        }
    }
}

ms_t SlotScheduler::next_tx_start(ms_t now) const {
    uint64_t fl = frame_ms(), slot = fl / cfg_.nodes;
    uint64_t n = net(now);
    uint64_t frame_start = n - (n % fl);
    uint64_t tx = frame_start + (uint64_t)cfg_.node_id * slot;
    if (tx < n) tx += fl;
    return now + (tx - n);
}

bool SlotScheduler::in_full_listen_frame(ms_t now) const {
    if (src_ != SyncSource::Free || cfg_.full_listen_every == 0) return false;
    uint64_t fl = frame_ms();
    return ((net(now) / fl) % cfg_.full_listen_every) == 0;
}

bool SlotScheduler::should_listen(ms_t now) const {
    uint64_t fl = frame_ms(), slot = fl / cfg_.nodes;
    int64_t pos = (int64_t)(net(now) % fl);
    int64_t own = (int64_t)cfg_.node_id * (int64_t)slot;
    int64_t half = (int64_t)fl / 2;
    // Kendi gönderim aralığı [own, own+air) içinde dinleme yok.
    int64_t d_own = ((pos - own + (int64_t)fl + half) % (int64_t)fl) - half;
    if (d_own >= 0 && d_own < (int64_t)cfg_.air_ms) return false;
    if (in_full_listen_frame(now)) return true;
    for (uint8_t n = 0; n < cfg_.nodes; n++) {
        if (n == cfg_.node_id) continue;
        int64_t ss = (int64_t)n * (int64_t)slot;
        int64_t d = ((pos - ss + (int64_t)fl + half) % (int64_t)fl) - half;
        if (d >= -(int64_t)cfg_.guard_ms && d < (int64_t)cfg_.guard_ms + (int64_t)cfg_.air_ms) return true;
    }
    return false;
}

ms_t SlotScheduler::next_event(ms_t now) const {
    uint64_t fl = frame_ms(), slot = fl / cfg_.nodes;
    uint64_t n = net(now);
    uint64_t base = n - (n % fl);
    uint64_t best = UINT64_MAX;
    auto cand = [&](int64_t t_in_frame, uint64_t frame_start) {
        int64_t t = (int64_t)frame_start + t_in_frame;
        if (t > (int64_t)n && (uint64_t)t < best) best = (uint64_t)t;
    };
    for (int f = -1; f <= 1; f++) {
        int64_t fs_signed = (int64_t)base + f * (int64_t)fl;
        if (fs_signed < 0) continue;
        uint64_t fs = (uint64_t)fs_signed;
        cand(0, fs);
        int64_t own = (int64_t)cfg_.node_id * (int64_t)slot;
        cand(own, fs);
        cand(own + cfg_.air_ms, fs);
        for (uint8_t k = 0; k < cfg_.nodes; k++) {
            if (k == cfg_.node_id) continue;
            int64_t ss = (int64_t)k * (int64_t)slot;
            cand(ss - (int64_t)cfg_.guard_ms, fs);
            cand(ss + (int64_t)cfg_.guard_ms + (int64_t)cfg_.air_ms, fs);
        }
    }
    return now + (best - n);
}

}  // namespace findy

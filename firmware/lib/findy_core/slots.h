// Findy çekirdek: çerçeve/dilim zamanlayıcı ve kip geçişleri (spec bölüm 4).
//
// Zaman modeli: yerel saat `now` (ms, 64 bit). Ağ fazı = (now + offset) mod 15000.
// BEKLEME çerçevesi (15 sn) ve ARAMA çerçevesi (5 sn) 15000'in bölenidir; tek `offset`
// iki kipte de geçerlidir. UTC kaynağında offset = utc_ms - yerel_ms (mod 15000), böylece
// `utc_ms mod çerçeve_süresi == 0` kuralı sağlanır.
#pragma once
#include <cstdint>
#include "group.h"

namespace findy {

enum class Mode : uint8_t { Standby = 0, Search = 1 };            // BEKLEME / ARAMA
enum class SyncSource : uint8_t { Free = 0, Packet = 1, Utc = 2 };  // öncelik: Utc > Packet > Free

struct SlotConfig {
    uint8_t node_id = 0;
    uint8_t nodes = MAX_NODES;
    uint32_t standby_frame_ms = 15000;
    uint32_t search_frame_ms = 5000;   // standby_frame_ms'in tam böleni olmalı
    uint32_t search_hold_ms = 60000;   // son ARAMA bayrağından sonra dönüş süresi
    uint32_t guard_ms = 120;           // ±GUARD_MS
    uint32_t air_ms = 124;             // tek paket havada kalma süresi (power_model::lora_airtime_ms)
    uint32_t full_listen_every = 4;    // senkronsuzken her N çerçevede bir tam çerçeve dinle
};

class SlotScheduler {
public:
    explicit SlotScheduler(const SlotConfig& cfg) : cfg_(cfg) {}

    Mode mode() const { return mode_; }
    SyncSource source() const { return src_; }
    uint32_t frame_ms() const { return mode_ == Mode::Search ? cfg_.search_frame_ms : cfg_.standby_frame_ms; }
    uint32_t slot_ms() const { return frame_ms() / cfg_.nodes; }
    uint32_t offset_ms() const { return offset_; }

    // Zaman kaynakları
    void set_utc(uint64_t utc_ms, ms_t local_ms);  // GNSS UTC (öncelik 1)
    void drop_utc() { if (src_ == SyncSource::Utc) src_ = SyncSource::Free; }

    // Yerel kullanıcı ARAMA başlattı (PING tuşu).
    void request_search(ms_t now);
    // Alınan geçerli paket: rx_start_ms = paketin havaya başladığı yerel an (rx_bitiş - air_ms).
    void on_rx(uint8_t node, ms_t rx_start_ms, bool search_flag, ms_t now);
    // Kendi paketimiz gönderildi (slot_start_ms = dilim başlangıcı).
    void on_tx(ms_t slot_start_ms, bool flagged);
    // Düzenli çağrılır; ARAMA süresi dolunca BEKLEME'ye döner.
    void update(ms_t now);

    // Paketimde ARAMA bayrağı olmalı mı? (yalnız başlatıcı/ilk-röle; bkz. .cpp açıklaması)
    bool emit_search_flag(ms_t now) const { return mode_ == Mode::Search && now < emit_until_; }

    // Kendi dilimimin sonraki başlangıcı (yerel ms, >= now).
    ms_t next_tx_start(ms_t now) const;
    // Radyo şu an dinlemede olmalı mı?
    bool should_listen(ms_t now) const;
    // should_listen / tx durumunun değişebileceği sonraki yerel an (> now).
    ms_t next_event(ms_t now) const;
    // Senkronsuzken tam çerçeve dinleme çerçevesinde miyiz?
    bool in_full_listen_frame(ms_t now) const;

private:
    uint64_t net(ms_t now) const { return now + offset_; }
    void enter_search(ms_t now);
    void note_flag_anchor(ms_t anchor);

    SlotConfig cfg_;
    Mode mode_ = Mode::Standby;
    SyncSource src_ = SyncSource::Free;
    uint32_t offset_ = 0;
    ms_t search_until_ = 0;
    ms_t emit_until_ = 0;
    bool have_anchor_ = false;
};

}  // namespace findy

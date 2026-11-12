// Findy P0 — ana döngü (RAK4631, Arduino/PlatformIO). DERLENMEDİ, DONANIMDA DENENMEDİ.
// Mantığın çoğu findy_core'dadır (PC'de birim testli); bu dosya yalnızca donanımı çekirdeğe bağlar.
#include <Arduino.h>
#include <stdio.h>
#include <string.h>
#include "board_pins.h"
#include "button.h"
#include "compass.h"
#include "geo.h"
#include "group.h"
#include "hw.h"
#include "packet.h"
#include "power_model.h"
#include "slots.h"

using namespace findy;

// ------------------------------------------------------------------ genel durum
static Settings cfg;
static Group group;
static SlotScheduler* sched = nullptr;
static TxCounter txc;
static Button btn;
static StillnessDetector still_det(0.05f, 60000);
static MagCalibrator calib;
static uint8_t avatar_buf[AVATAR_BYTES];

static HeadingResult g_heading{false, false, 0, 0};
static ImuSample g_imu{};
static bool g_log_on = false;

static uint64_t millis64() {
    static uint32_t last = 0, hi = 0;
    uint32_t m = millis();
    if (m < last) hi++;
    last = m;
    return ((uint64_t)hi << 32) | m;
}

static SlotConfig make_slot_config() {
    SlotConfig c;
    c.node_id = group.has_group() ? group.self_node() : 0;
    c.standby_frame_ms = (uint32_t)cfg.standby_s * 1000;
    c.search_frame_ms = (uint32_t)cfg.search_s * 1000;
    c.air_ms = radio_airtime_ms(PACKET_LEN);
    return c;
}
static void rebuild_sched() {
    static SlotScheduler holder(SlotConfig{});
    holder = SlotScheduler(make_slot_config());
    sched = &holder;
}
static RadioParams radio_params() { return RadioParams{cfg.sf, cfg.tx_power_dbm}; }

// ------------------------------------------------------------------ pil
static uint8_t read_batt_pct() {
    analogReference(AR_INTERNAL_3_0);
    analogReadResolution(12);
    uint32_t raw = analogRead(FINDY_PIN_BATT_ADC);
    // DOĞRULANACAK: RAK19007 bölücü katsayısı (hatırlanan: 1,73) ve 3,0 V iç referans.
    uint32_t mv = (uint32_t)((float)raw * (3000.0f / 4096.0f) * 1.73f);
    return battery_pct_from_mv((uint16_t)mv);
}

// ------------------------------------------------------------------ titreşim (bloklamayan)
static uint64_t vib_until = 0;
static void vibrate(uint64_t now, uint32_t ms) { digitalWrite(FINDY_PIN_VIBRA, HIGH); vib_until = now + ms; }

// ------------------------------------------------------------------ arayüz durumu
static Screen screen = Screen::Off;
static uint64_t screen_since = 0, last_interaction = 0, last_render = 0;
static int selected_node = -1;
static int ping_tx_left = 0;
static uint8_t ping_target_mask = 0;

static void wake(uint64_t now) {
    last_interaction = now;
    if (screen == Screen::Off) { screen = Screen::Avatar; screen_since = now; ui_backlight(true); }
}
static void set_screen(Screen s, uint64_t now) { screen = s; screen_since = now; last_interaction = now; ui_backlight(s != Screen::Off); }

// ------------------------------------------------------------------ eşleşme
struct Pairing {
    bool active = false;
    bool founder = false;
    bool probing = false;
    uint64_t start = 0, probe_until = 0, next_offer = 0;
    int pending_node = -1;
    const char* text = "";
} pair;

static void pair_start(uint64_t now) {
    pair = Pairing();
    pair.active = true;
    pair.start = now;
    set_screen(Screen::Pair, now);
    if (group.has_group()) { pair.founder = true; pair.text = "TEKLIF"; }
    else {
        // Grubu olmayan: önce kısa süre teklif dinle; gelmezse kurucu ol (rastgele gecikme çakışmayı azaltır)
        uint8_t r = 0; hw_random(&r, 1);
        pair.probing = true; pair.probe_until = now + 3000 + (uint32_t)r * 8;
        pair.text = "ARANIYOR";
    }
    radio_idle();
}

static void pair_end(uint64_t now) {
    pair.active = false;
    if (pair.founder && pair.pending_node >= 0) group.release_node_id((uint8_t)pair.pending_node);
    radio_apply(radio_params());   // normal güce dön
    rebuild_sched();
    set_screen(Screen::Radar, now);
}

static void pair_become_founder(uint64_t now) {
    uint8_t key[32];
    if (!hw_random(key, 32)) { pair.text = "RNG HATA"; return; }
    group.set_group(crypto(), key, 0);
    memcpy(cfg.key, key, 32); cfg.has_group = 1; cfg.node_id = 0; settings_save(cfg);
    pair.founder = true; pair.probing = false; pair.text = "TEKLIF";
    (void)now;
}

static void pair_loop(uint64_t now) {
    uint8_t buf[64]; size_t len; int rssi, snr;
    if (now - pair.start > 30000) { pair_end(now); return; }   // 30 sn
    if (pair.probing && now >= pair.probe_until) pair_become_founder(now);

    if (pair.founder) {
        if (pair.pending_node < 0) pair.pending_node = group.allocate_node_id();
        if (pair.pending_node < 0) { pair.text = "DOLU"; }
        else if (now >= pair.next_offer) {
            uint8_t off[PAIR_OFFER_LEN];
            encode_pair_offer(group.key(), (uint8_t)pair.pending_node, off);
            radio_transmit(off, sizeof(off), -9);   // en düşük güç (spec)
            pair.next_offer = now + 400;
            radio_listen();
        }
    } else {
        radio_listen();
    }
    if (radio_poll(buf, len, rssi, snr)) {
        if (!group.has_group() || pair.probing) {
            uint8_t key[32], node;
            if (len == PAIR_OFFER_LEN && decode_pair_offer(buf, len, key, node) && pair_rssi_ok(rssi)) {
                group.set_group(crypto(), key, node);
                memcpy(cfg.key, key, 32); cfg.has_group = 1; cfg.node_id = node; settings_save(cfg);
                uint8_t ack[PAIR_ACK_LEN];
                encode_pair_ack(group.group_id(), node, ack);
                for (int i = 0; i < 3; i++) { radio_transmit(ack, sizeof(ack), -9); delay(80); }
                pair.text = "TAMAM"; pair.probing = false;
                // atanan numara ekranda gösterilir; kısa bekleyip çık
                pair.start = now - 26000;
            }
        } else if (pair.founder && len == PAIR_ACK_LEN) {
            uint16_t gid; uint8_t node;
            if (decode_pair_ack(buf, len, gid, node) && gid == group.group_id() && (int)node == pair.pending_node) {
                pair.text = "BIRI KATILDI";
                pair.pending_node = -1;   // sıradaki katılımcı için yenisi atanır
            }
        }
        radio_listen();
    }
}

// ------------------------------------------------------------------ BLE kancaları
static bool cfg_set(const char* k, const char* v) {
    if (!strcmp(k, "sf")) { int x = atoi(v); if (x < 7 || x > 9) return false; cfg.sf = (uint8_t)x; }
    else if (!strcmp(k, "pwr")) { int x = atoi(v); if (x < -9 || x > 22) return false; cfg.tx_power_dbm = (int8_t)x; }
    else if (!strcmp(k, "standby")) { int x = atoi(v); if (x < 5 || x > 60 || x % cfg.search_s) return false; cfg.standby_s = (uint16_t)x; }
    else if (!strcmp(k, "search")) { int x = atoi(v); if (x < 1 || x > 15 || cfg.standby_s % x) return false; cfg.search_s = (uint16_t)x; }
    else if (!strcmp(k, "decl")) { cfg.declination_deg = (float)atof(v); }
    else if (!strcmp(k, "calib")) { calib.reset(); set_screen(Screen::Calibrate, millis64()); return true; }
    else return false;
    settings_save(cfg);
    radio_apply(radio_params());
    rebuild_sched();   // SF değişince hava süresi değişir; tüm cihazlarda aynı SF olmalı
    return true;
}
static void hk_set_name(const char* n) { strncpy(cfg.name, n, 8); cfg.name[8] = 0; settings_save(cfg); }
static bool hk_set_avatar(const uint8_t* d, size_t n) { if (!avatar_save(d, n)) return false; ui_set_avatar(d); return true; }
static void hk_status(char* out, size_t cap) {
    const GnssState& g = gnss_state();
    snprintf(out, cap, "{\"fw\":\"%s\",\"name\":\"%s\",\"batt\":%u,\"fix\":%d,\"members\":%d,\"node\":%d,\"mode\":\"%s\",\"sf\":%u,\"pwr\":%d,\"decl\":%.1f}",
             FINDY_FW_VERSION, cfg.name, read_batt_pct(), g.fix ? 1 : 0, group.member_count(), cfg.node_id,
             (sched && sched->mode() == Mode::Search) ? "SEARCH" : "STANDBY", cfg.sf, cfg.tx_power_dbm, cfg.declination_deg);
}
static void hk_set_log(bool on) {
    g_log_on = on;
    if (on) ble_send_line("LOGCOLS,ms,node,rssi,snr,counter,lat_e7,lon_e7,fix_age_s,hacc_m,batt,flags,own_lat_e7,own_lon_e7");
}
static bool hk_set_friend(int id, const char* name) {
    if (id < 1 || id > 5) return false;
    char* d = cfg.friend_names[id - 1];
    strncpy(d, name, 8); d[8] = 0;
    for (char* c = d; *c; c++) if (*c >= 'a' && *c <= 'z') *c -= 32;
    settings_save(cfg);
    return true;
}

// ------------------------------------------------------------------ gönderim
static void do_tx(uint64_t now, uint64_t slot_start) {
    if (!group.has_group()) return;
    const GnssState& g = gnss_state();
    Payload p{};
    bool have_pos = g.fix_ms != 0;
    if (have_pos) {
        p.lat_e7 = g.lat_e7; p.lon_e7 = g.lon_e7;
        uint64_t age = (now - g.fix_ms) / 1000;
        p.fix_age_s = (uint8_t)(age > 254 ? 254 : age);   // 255 yalnız "konum yok" için
        p.hacc_m = (uint8_t)(g.hacc_m > 254 ? HACC_UNKNOWN : g.hacc_m);
    } else { p.fix_age_s = FIX_AGE_NONE; p.hacc_m = HACC_UNKNOWN; }
    p.batt_pct = read_batt_pct();
    bool flagged = sched->emit_search_flag(now);
    if (flagged) p.flags |= FLAG_SEARCH;
    if (ping_tx_left > 0) { p.flags |= FLAG_PING; p.ping_target = ping_target_mask; ping_tx_left--; }
    if (still_det.still(now)) p.flags |= FLAG_STILL;

    Header h{group.group_id(), group.self_node(), PROTO_VERSION, txc.next()};
    uint8_t buf[PACKET_LEN];
    if (!encode_packet(crypto(), group.key(), h, p, buf)) return;
    radio_transmit(buf, sizeof(buf));
    sched->on_tx(slot_start, flagged);
    if (txc.should_persist()) { cfg.tx_counter = txc.persist_value(); settings_save(cfg); txc.mark_persisted(); }
}

// ------------------------------------------------------------------ alım
static void do_rx(uint64_t now, const uint8_t* buf, size_t len, int rssi, int snr) {
    Header h; Payload p;
    RxStatus st = group.on_packet(crypto(), buf, len, now, rssi, snr, &h, &p);
    if (st != RxStatus::Ok) return;
    uint64_t rx_start = now - radio_airtime_ms(PACKET_LEN);   // RxDone paket sonudur
    sched->on_rx(h.node_id, rx_start, (p.flags & FLAG_SEARCH) != 0, now);
    if ((p.flags & FLAG_PING) && (p.ping_target & (1u << group.self_node()))) {
        vibrate(now, 700);     // "arkadaşı titret"
        wake(now);
    }
    if (g_log_on && ble_connected()) {
        const GnssState& g = gnss_state();
        char line[128];
        snprintf(line, sizeof(line), "LOG,%lu,%u,%d,%d,%lu,%ld,%ld,%u,%u,%u,%u,%ld,%ld",
                 (unsigned long)now, h.node_id, rssi, snr, (unsigned long)h.counter, (long)p.lat_e7, (long)p.lon_e7,
                 p.fix_age_s, p.hacc_m, p.batt_pct, p.flags, (long)g.lat_e7, (long)g.lon_e7);
        ble_send_line(line);
    }
}

// ------------------------------------------------------------------ arayüz modeli
static void build_model(uint64_t now, UiModel& m) {
    memset(&m, 0, sizeof(m));
    m.screen = screen;
    m.selected = -1;
    m.batt_pct = read_batt_pct();
    const GnssState& g = gnss_state();
    m.gnss_fix = g.fix; m.gnss_powered = g.powered;
    m.members = (uint8_t)group.member_count();
    m.tilted = g_heading.too_tilted;
    m.search = sched && sched->mode() == Mode::Search;
    m.hold_stage = btn.hold_stage(now);
    m.self_name = cfg.name;
    m.pair_node = group.has_group() ? (int8_t)group.self_node() : -1;
    m.pair_text = pair.text;
    m.pair_progress = pair.active ? (float)(now - pair.start) / 30000.0f : 0;
    m.mag_progress = calib.ready() ? 1.0f : (float)calib.samples() / 300.0f;
    if (m.mag_progress > 1) m.mag_progress = 1;

    bool own_pos = g.fix_ms != 0;
    int shown = 0;
    for (uint8_t n = 0; n < MAX_NODES && shown < 4; n++) {
        const Member* mem = group.member(n);
        if (!mem || !mem->seen || n == group.self_node()) continue;
        UiFriend& f = m.f[shown];
        f.valid = true; f.node = n;
        if (cfg.friend_names[n][0]) strncpy(f.name, cfg.friend_names[n], 8); else { f.name[0] = (char)('1' + n); f.name[1] = 0; }
        f.st = group.staleness(n, now);
        f.dist_m = -1;
        if (own_pos && group.has_position(n)) {
            double la = e7_to_deg(g.lat_e7), lo = e7_to_deg(g.lon_e7);
            double fl = e7_to_deg(mem->p.lat_e7), fo = e7_to_deg(mem->p.lon_e7);
            f.dist_m = (float)haversine_m(la, lo, fl, fo);
            double brg = bearing_deg(la, lo, fl, fo);
            f.arrow_ok = g_heading.valid;
            if (g_heading.valid) f.arrow_deg = (float)arrow_angle_deg(brg, g_heading.heading_deg);
            // güven göstergesi: doğruluk toplamı mesafenin yarısından büyükse yalnız mesafe halkası (eşik deneyle ayarlanacak)
            float own_h = g.hacc_m > 254 ? 254.f : (float)g.hacc_m, fr_h = mem->p.hacc_m == HACC_UNKNOWN ? 254.f : (float)mem->p.hacc_m;
            if ((own_h + fr_h) > f.dist_m * 0.5f) { f.ring_only = true; f.arrow_ok = false; }
        }
        if (f.dist_m < 0) f.dist_m = 9999;
        if ((int)n == selected_node) m.selected = shown;
        shown++;
    }
    if (m.selected < 0 && shown > 0) { m.selected = 0; selected_node = m.f[0].node; }
}

// ------------------------------------------------------------------ setup / loop
void setup() {
    Serial.begin(115200);
    pinMode(FINDY_PIN_BUTTON, INPUT_PULLUP);
    pinMode(FINDY_PIN_VIBRA, OUTPUT);
    digitalWrite(FINDY_PIN_VIBRA, LOW);

    storage_begin();
    bool had = settings_load(cfg);
    (void)had;

    BleHooks hooks{hk_set_name, hk_set_avatar, hk_status, hk_set_log, cfg_set, hk_set_friend};
    char adv[16]; snprintf(adv, sizeof(adv), "Findy-%s", cfg.name);
    ble_begin(adv, hooks);            // SoftDevice'i de başlatır (RNG için gerekli)

    imu_begin();
    gnss_begin();
    radio_begin(radio_params());
    ui_begin();
    if (avatar_load(avatar_buf, AVATAR_BYTES)) ui_set_avatar(avatar_buf);

    if (cfg.has_group) group.set_group(crypto(), cfg.key, cfg.node_id);
    // Tekrar saldırısı/nonce güvenliği: sayaç açılışta +1000 atlanır ve HEMEN kalıcılaştırılır (spec).
    txc.init(cfg.tx_counter);
    cfg.tx_counter = txc.persist_value();
    settings_save(cfg);
    txc.mark_persisted();
    rebuild_sched();

    // Pusula ofseti hiç yoksa açılışta "8 çiz" kalibrasyonu
    if (cfg.mag_off[0] == 0 && cfg.mag_off[1] == 0 && cfg.mag_off[2] == 0) { calib.reset(); set_screen(Screen::Calibrate, millis64()); }
    else wake(millis64());
}

void loop() {
    static uint64_t last_imu = 0, last_gnss = 0, tx_at = 0;
    static Mode snap_mode = Mode::Standby; static uint32_t snap_off = 0; static SyncSource snap_src = SyncSource::Free;
    static uint64_t utc_applied = 0;
    uint64_t now = millis64();

    ble_poll();
    if (vib_until && now >= vib_until) { digitalWrite(FINDY_PIN_VIBRA, LOW); vib_until = 0; }

    // ---- tuş
    ButtonEvent ev = btn.update(digitalRead(FINDY_PIN_BUTTON) == LOW, now);
    if (btn.is_down()) last_interaction = now;
    switch (ev) {
        case ButtonEvent::Short:
            if (screen == Screen::Off) wake(now);
            else if (screen == Screen::Radar) { selected_node = group.next_friend(selected_node); last_interaction = now; }
            else set_screen(Screen::Radar, now);
            break;
        case ButtonEvent::Double: wake(now); set_screen(Screen::Status, now); break;
        case ButtonEvent::Hold1500:
            if (selected_node >= 0 && group.has_group()) {
                ping_target_mask = (uint8_t)(1u << selected_node); ping_tx_left = 3;
                sched->request_search(now);
                vibrate(now, 150);
            }
            wake(now);
            break;
        case ButtonEvent::Hold5000: wake(now); pair_start(now); break;
        case ButtonEvent::Hold10000:
            group.leave(); cfg.has_group = 0; memset(cfg.key, 0, 32); settings_save(cfg);
            selected_node = -1; rebuild_sched(); vibrate(now, 400); wake(now);
            break;
        default: break;
    }

    // ---- IMU (20 Hz)
    if (now - last_imu >= 50) {
        last_imu = now;
        if (imu_read(g_imu)) {
            Vec3 off{cfg.mag_off[0], cfg.mag_off[1], cfg.mag_off[2]};
            g_heading = compute_heading(g_imu.acc_g, apply_offset(g_imu.mag_ut, off), cfg.declination_deg);
            still_det.update(g_imu.acc_g.x, g_imu.acc_g.y, g_imu.acc_g.z, now);
            if (screen == Screen::Calibrate) {
                calib.add(g_imu.mag_ut);
                if ((calib.ready() && now - screen_since > 8000) || now - screen_since > 30000) {
                    if (calib.ready()) {
                        Vec3 o = calib.offset();
                        cfg.mag_off[0] = o.x; cfg.mag_off[1] = o.y; cfg.mag_off[2] = o.z; settings_save(cfg);
                    }
                    set_screen(Screen::Radar, now);
                }
            }
        }
    }

    // ---- GNSS (1 Hz) + hareketsizlikte kapat / harekette aç
    if (now - last_gnss >= 1000) {
        last_gnss = now;
        // 3V3_S (WB_IO2) ÇALIŞIRKEN KESİLMEZ: RAK12500'de V_BCKP yok, besleme kesilince ephemeris silinir ve
        // her açılış soğuk başlangıç olur (tipik ~26 sn; bkz. hardware/dogrulama-notlari.md H1). Ayrıca WB_IO2
        // GNSS RESET hattıdır. v0'da GNSS sürekli 1 Hz açık kalır; güç tasarrufu (UBX-RXM-PMREQ yazılım yedek
        // kipi veya u-blox güç tasarruf kipi) Faz 4 ölçümünden sonra eklenecek.
        (void)still_det.still(now);   // "hareketsiz" bayrağı için durum güncel kalsın
        gnss_poll(now);
        const GnssState& g = gnss_state();
        if (g.utc_valid && g.utc_local_ms != utc_applied) {
            utc_applied = g.utc_local_ms;
            sched->set_utc(g.utc_ms, g.utc_local_ms);
        }
        // Görev döngüsü (spec 6): konum alındıktan sonra GNSS'i uyut. DOĞRULANACAK/DENENMEDİ; v0'da kapalı.
        // if (g.fix && sched->mode() == Mode::Standby) gnss_sleep_for(28000);
    }

    // ---- radyo
    sched->update(now);
    if (pair.active) {
        pair_loop(now);
    } else if (group.has_group()) {
        if (sched->mode() != snap_mode || sched->offset_ms() != snap_off || sched->source() != snap_src) {
            snap_mode = sched->mode(); snap_off = sched->offset_ms(); snap_src = sched->source();
            tx_at = sched->next_tx_start(now);
        }
        if (tx_at == 0) tx_at = sched->next_tx_start(now);
        if (now >= tx_at) {
            uint64_t slot_start = tx_at;
            if (now - tx_at < sched->slot_ms() / 2) do_tx(now, slot_start);   // gecikmişse bu dilimi atla
            tx_at = sched->next_tx_start(now + 1);
        } else if (sched->should_listen(now)) {
            radio_listen();
        } else {
            radio_idle();
        }
        uint8_t buf[64]; size_t len; int rssi, snr;
        if (radio_poll(buf, len, rssi, snr)) do_rx(now, buf, len, rssi, snr);
    } else {
        radio_idle();
    }

    // ---- arayüz (5 Hz çizim)
    if (screen == Screen::Avatar && now - screen_since > 3000) set_screen(Screen::Radar, now);
    if (screen != Screen::Off && screen != Screen::Pair && screen != Screen::Calibrate && now - last_interaction > 10000)
        set_screen(Screen::Off, now);
    if (now - last_render >= 200) {
        last_render = now;
        UiModel m;
        build_model(now, m);
        ui_render(m);
    }
    delay(2);
}

// Findy P0 — donanım katmanı iç arayüzleri (main.cpp ile modüller arası).
#pragma once
#include <Arduino.h>
#include "compass.h"
#include "crypto_ref.h"
#include "group.h"
#include "packet.h"

#define FINDY_FW_VERSION "p0-0.1"

// ---- crypto_port.cpp
const findy::ICrypto& crypto();
bool hw_random(uint8_t* out, size_t n);   // 32 baytlık grup anahtarı için

// ---- storage.cpp
struct Settings {
    uint32_t magic;          // 'FNDY'
    uint16_t version;
    uint8_t has_group;
    uint8_t node_id;
    uint8_t key[32];
    char name[9];
    char friend_names[5][9];
    uint8_t sf;              // 7..9
    int8_t tx_power_dbm;
    uint16_t standby_s;      // BEKLEME çerçeve süresi (sn)
    uint16_t search_s;       // ARAMA çerçeve süresi (sn)
    float declination_deg;
    float mag_off[3];
    uint32_t tx_counter;
    uint32_t crc;            // yukarıdaki baytların CRC32'si
};
constexpr size_t AVATAR_W = 96, AVATAR_BYTES = AVATAR_W * AVATAR_W * 2;  // 18432
void settings_defaults(Settings& s);
bool storage_begin();
bool settings_load(Settings& s);   // false: dosya yok/bozuk -> varsayılanlar yüklenir
bool settings_save(const Settings& s);
bool avatar_save(const uint8_t* data, size_t n);
bool avatar_load(uint8_t* data, size_t n);   // little-endian RGB565, 96x96

// ---- radio_sx1262.cpp
struct RadioParams { uint8_t sf; int8_t power_dbm; };
bool radio_begin(const RadioParams& p);
void radio_apply(const RadioParams& p);      // SF/güç değişimi
void radio_listen();                         // alıma geç (zaten alımdaysa dokunmaz)
void radio_idle();                           // alımı bırak (standby)
bool radio_transmit(const uint8_t* buf, size_t len, int8_t power_dbm_override = 127);  // bloklayıcı
bool radio_poll(uint8_t* buf, size_t& len, int& rssi, int& snr);  // paket varsa true
uint32_t radio_airtime_ms(size_t len);

// ---- gnss_ublox.cpp
struct GnssState {
    bool powered;
    bool fix;               // geçerli 2D/3D konum
    int32_t lat_e7, lon_e7;
    uint16_t hacc_m;        // 65535: bilinmiyor
    uint32_t fix_ms;        // son konumun yerel zamanı (millis64)
    bool utc_valid;
    uint64_t utc_ms;        // UTC (Unix ms), son okuma anına ait
    uint64_t utc_local_ms;  // utc_ms'nin okunduğu yerel zaman (millis64)
};
bool gnss_begin();
void gnss_power(bool on);
void gnss_poll(uint64_t now_ms);   // ~1 Hz çağır
const GnssState& gnss_state();
void gnss_sleep_for(uint32_t ms);  // UBX yazılım yedek kipi (DOĞRULANACAK)

// ---- imu_lsm303agr.cpp
struct ImuSample { findy::Vec3 acc_g; findy::Vec3 mag_ut; bool ok; };
bool imu_begin();
bool imu_read(ImuSample& s);       // aygıt eksen düzenine eşlenmiş

// ---- display_ui.cpp
enum class Screen : uint8_t { Off, Avatar, Radar, Pair, Status, Calibrate };
struct UiFriend {
    bool valid;
    uint8_t node;
    char name[9];
    float dist_m;
    float arrow_deg;                 // (-180,180], 0 = ekranın üstü
    bool arrow_ok;                   // false: ok gizli
    bool ring_only;                  // güven göstergesi: yalnızca mesafe halkası
    findy::Staleness st;
};
struct UiModel {
    Screen screen;
    UiFriend f[4];
    int selected;                    // f[] indeksi
    bool tilted;                     // "düz tut" simgesi
    uint8_t batt_pct;
    bool gnss_fix;
    bool gnss_powered;
    uint8_t members;
    float pair_progress;             // 0..1
    int8_t pair_node;                // atanan numara, -1 yok
    const char* pair_text;
    int hold_stage;
    bool search;
    float mag_progress;              // kalibrasyon ilerleme 0..1
    const char* self_name;
};
void ui_begin();
void ui_set_avatar(const uint8_t* rgb565_le);   // 18432 bayt; nullptr = avatar yok
void ui_render(const UiModel& m);
void ui_backlight(bool on);

// ---- ble_link.cpp
struct BleHooks {
    void (*set_name)(const char* name);
    bool (*set_avatar)(const uint8_t* data, size_t n);
    void (*status_json)(char* out, size_t cap);
    void (*set_log)(bool on);
    bool (*set_cfg)(const char* key, const char* value);
    bool (*set_friend)(int id, const char* name);
};
bool ble_begin(const char* adv_name, const BleHooks& hooks);
void ble_poll();
void ble_send_line(const char* line);
bool ble_connected();

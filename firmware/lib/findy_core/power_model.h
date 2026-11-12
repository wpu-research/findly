// Findy çekirdek: güç modeli — kip başına görev oranı -> TAHMİNİ ortalama akım (spec bölüm 6).
// UYARI: Girdi akımları veri sayfası tipik değerlerine dayalı tahmindir; ÖLÇÜLMEMİŞTİR (Faz 4'te ölçülecek).
#pragma once
#include <cstdint>
#include "slots.h"

namespace findy {

// LoRa havada kalma süresi (ms) — Semtech AN1200.13 formülü. ldro: -1 = otomatik (sembol > 16 ms ise açık).
double lora_airtime_ms(unsigned payload_len, unsigned sf, double bw_hz, unsigned cr_denom /*5..8*/,
                       unsigned preamble_syms = 8, bool crc = true, bool implicit_header = false, int ldro = -1);

struct PowerParams {           // mA, veri sayfası tipik tahminleri (ölçülmedi)
    double mcu_sleep_ma = 0.01;
    double rx_ma = 5.0;
    double tx_ma = 45.0;       // +14 dBm
    double gnss_ma = 22.5;     // 20-25 mA izleme ortası
    double display_ma = 30.0;  // 20-40 mA ortası
    double imu_ma = 0.05;
};

struct PowerScenario {
    double rx_duty = 0, tx_duty = 0, gnss_duty = 0, display_duty = 0;
};

// Dilim yapılandırmasından RX/TX görev oranları. gnss_duty ve display_duty politika girdisidir.
PowerScenario scenario_for_mode(const SlotConfig& cfg, Mode mode, double gnss_duty, double display_duty);

double average_current_ma(const PowerParams& p, const PowerScenario& s);
// Ortalama akımdan pil ömrü tahmini (saat). Kullanılabilir kapasite %80 varsayılır.
double battery_life_h(double capacity_mah, double avg_ma, double usable_fraction = 0.8);

// LiPo gerilimi -> yüzde (kaba tablo; kapasiteye/sıcaklığa/yüke bağlı, ölçümle ayarlanmalı).
uint8_t battery_pct_from_mv(uint16_t mv);

// Hareketsizlik algılama: ivme vektörü değişimi eşiğin altında kalırsa N ms sonra "hareketsiz".
class StillnessDetector {
public:
    explicit StillnessDetector(float thresh_g = 0.05f, uint32_t still_after_ms = 60000)
        : thresh_(thresh_g), after_(still_after_ms) {}
    void update(float ax_g, float ay_g, float az_g, ms_t now);
    bool still(ms_t now) const { return started_ && (now - last_motion_) >= after_; }
private:
    float thresh_;
    uint32_t after_;
    bool started_ = false;
    float px_ = 0, py_ = 0, pz_ = 0;
    ms_t last_motion_ = 0;
};

}  // namespace findy

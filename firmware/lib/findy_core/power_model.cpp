#include "power_model.h"
#include <cmath>

namespace findy {

double lora_airtime_ms(unsigned pl, unsigned sf, double bw, unsigned cr, unsigned pre, bool crc, bool impl, int ldro) {
    double tsym = std::pow(2.0, (double)sf) / bw * 1000.0;
    int de = ldro >= 0 ? ldro : (tsym > 16.0 ? 1 : 0);
    double num = 8.0 * pl - 4.0 * sf + 28.0 + (crc ? 16.0 : 0.0) - (impl ? 20.0 : 0.0);
    double den = 4.0 * (sf - 2.0 * de);
    double n = std::ceil(num / den) * (double)cr;
    if (n < 0) n = 0;
    double payload_syms = 8.0 + n;
    double t_pre = ((double)pre + 4.25) * tsym;
    return t_pre + payload_syms * tsym;
}

PowerScenario scenario_for_mode(const SlotConfig& cfg, Mode mode, double gnss, double disp) {
    double fl = (mode == Mode::Search) ? cfg.search_frame_ms : cfg.standby_frame_ms;
    PowerScenario s;
    s.rx_duty = (cfg.nodes - 1) * (2.0 * cfg.guard_ms + cfg.air_ms) / fl;
    s.tx_duty = (double)cfg.air_ms / fl;
    s.gnss_duty = gnss;
    s.display_duty = disp;
    return s;
}

double average_current_ma(const PowerParams& p, const PowerScenario& s) {
    return p.mcu_sleep_ma + p.imu_ma + p.rx_ma * s.rx_duty + p.tx_ma * s.tx_duty +
           p.gnss_ma * s.gnss_duty + p.display_ma * s.display_duty;
}

double battery_life_h(double cap, double ma, double frac) { return ma > 0 ? cap * frac / ma : 0.0; }

uint8_t battery_pct_from_mv(uint16_t mv) {
    static const struct { uint16_t mv; uint8_t pct; } T[] = {
        {3300, 0}, {3500, 5}, {3600, 15}, {3700, 35}, {3800, 55}, {3900, 70}, {4000, 82}, {4100, 92}, {4200, 100}};
    const int N = (int)(sizeof(T) / sizeof(T[0]));
    if (mv <= T[0].mv) return 0;
    if (mv >= T[N - 1].mv) return 100;
    for (int i = 1; i < N; i++) {
        if (mv <= T[i].mv) {
            double f = (double)(mv - T[i - 1].mv) / (double)(T[i].mv - T[i - 1].mv);
            return (uint8_t)std::lround(T[i - 1].pct + f * (T[i].pct - T[i - 1].pct));
        }
    }
    return 100;
}

void StillnessDetector::update(float x, float y, float z, ms_t now) {
    if (!started_) { started_ = true; px_ = x; py_ = y; pz_ = z; last_motion_ = now; return; }
    float dx = x - px_, dy = y - py_, dz = z - pz_;
    if (std::sqrt(dx * dx + dy * dy + dz * dz) > thresh_) last_motion_ = now;
    px_ = x; py_ = y; pz_ = z;
}

}  // namespace findy

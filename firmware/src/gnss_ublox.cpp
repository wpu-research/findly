// Findy P0 — u-blox GNSS (RAK12500, ZOE-M8Q) SparkFun u-blox GNSS Arduino Library ile, I2C 0x42.
// Derlendi (12 Kasım 2026), donanımda denenmedi. Kütüphane işlev adları derlemede doğrulandı; davranışları değil (v3 API: SFE_UBLOX_GNSS). Emin olunmayanlar işaretli.
#include <SparkFun_u-blox_GNSS_Arduino_Library.h>
#include <Wire.h>
#include "board_pins.h"
#include "hw.h"

static SFE_UBLOX_GNSS g_gnss;
static GnssState g_st;
static bool g_ok = false;

// UTC -> Unix ms (Howard Hinnant "days from civil")
static uint64_t unix_ms(int y, int m, int d, int hh, int mm, int ss, int ms) {
    y -= m <= 2;
    int era = (y >= 0 ? y : y - 399) / 400;
    unsigned yoe = (unsigned)(y - era * 400);
    unsigned doy = (153 * (m + (m > 2 ? -3 : 9)) + 2) / 5 + d - 1;
    unsigned doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    int64_t days = (int64_t)era * 146097 + (int64_t)doe - 719468;
    return (uint64_t)(((days * 24 + hh) * 60 + mm) * 60 + ss) * 1000ULL + (uint64_t)ms;
}

void gnss_power(bool on) {
    pinMode(FINDY_PIN_GNSS_PWR, OUTPUT);
    digitalWrite(FINDY_PIN_GNSS_PWR, on ? HIGH : LOW);   // 3V3_S anahtarı; mantık seviyesi DOĞRULANACAK
    g_st.powered = on;
    if (!on) { g_ok = false; g_st.fix = false; }
}

bool gnss_begin() {
    gnss_power(true);
    delay(500);   // modül açılış süresi (ölçülmedi)
    FINDY_I2C.begin();
    FINDY_I2C.setClock(400000);
    if (!g_gnss.begin(FINDY_I2C, FINDY_I2C_ADDR_GNSS)) { g_ok = false; return false; }
    g_gnss.setI2COutput(COM_TYPE_UBX);
    g_gnss.setNavigationFrequency(1);
    g_gnss.setAutoPVT(true);   // PVT'yi modül kendisi üretsin; getPVT() hızlı döner
    g_ok = true;
    return true;
}

void gnss_poll(uint64_t now_ms) {
    if (!g_st.powered) return;
    if (!g_ok) { gnss_begin(); return; }
    if (!g_gnss.getPVT()) return;
    uint8_t fixType = g_gnss.getFixType();
    g_st.fix = fixType >= 2;
    if (g_st.fix) {
        g_st.lat_e7 = g_gnss.getLatitude();    // derece x 1e-7
        g_st.lon_e7 = g_gnss.getLongitude();
        uint32_t h_mm = g_gnss.getHorizontalAccEst();   // mm (DOĞRULANACAK: ad)
        g_st.hacc_m = (uint16_t)(h_mm / 1000 > 65534 ? 65535 : h_mm / 1000);
        g_st.fix_ms = now_ms;
    }
    // UTC: PPS/TIMEPULSE P0'da bağlı DEĞİL; I2C ile okunan zaman damgası gecikmeli (onlarca-yüzlerce ms)
    // olabilir. Bu hata ±GUARD_MS (120 ms) ile kıyaslanıp ölçülmeli.
    if (g_gnss.getTimeValid() && g_gnss.getDateValid()) {   // DOĞRULANACAK: adlar
        uint16_t ms = (uint16_t)g_gnss.getMillisecond();
        g_st.utc_ms = unix_ms(g_gnss.getYear(), g_gnss.getMonth(), g_gnss.getDay(), g_gnss.getHour(),
                              g_gnss.getMinute(), g_gnss.getSecond(), ms);
        g_st.utc_local_ms = now_ms;
        g_st.utc_valid = true;
    }
}

const GnssState& gnss_state() { return g_st; }

void gnss_sleep_for(uint32_t ms) {
    // UBX-RXM-PMREQ ile yazılım yedek kipi: 3V3_S'yi kesmekten farkı, V_BCKP varsa ephemeris korunur
    // (sıcak başlangıç). DOĞRULANACAK: powerOff imzası ve RAK12500'de V_BCKP bağlantısı.
    if (g_ok) { g_gnss.powerOff(ms); g_ok = false; }
}

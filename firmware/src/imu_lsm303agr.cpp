// Findy P0 — LSM303AGR doğrudan I2C register erişimi (kütüphane sürümü riskini azaltmak için).
// İvme 0x19, manyeto 0x1E. Register adresleri ST LSM303AGR veri sayfasından hatırlanan değerlerdir;
// Derlendi (12 Kasım 2026), DONANIMDA DENENMEDİ -> WHO_AM_I okuması (0x33 / 0x40) ilk doğrulama adımıdır.
#include <Wire.h>
#include "board_pins.h"
#include "hw.h"

static const uint8_t ACC_WHO_AM_I = 0x0F, ACC_CTRL1 = 0x20, ACC_CTRL4 = 0x23, ACC_OUT_X_L = 0x28;
static const uint8_t MAG_WHO_AM_I = 0x4F, MAG_CFG_A = 0x60, MAG_CFG_B = 0x61, MAG_CFG_C = 0x62, MAG_OUT_X_L = 0x68;

struct AxisMap { int8_t src; int8_t sign; };
static const AxisMap ACC_MAP[3] = {FINDY_ACC_MAP_X, FINDY_ACC_MAP_Y, FINDY_ACC_MAP_Z};
static const AxisMap MAG_MAP[3] = {FINDY_MAG_MAP_X, FINDY_MAG_MAP_Y, FINDY_MAG_MAP_Z};

static bool wr(uint8_t addr, uint8_t reg, uint8_t val) {
    FINDY_I2C.beginTransmission(addr);
    FINDY_I2C.write(reg); FINDY_I2C.write(val);
    return FINDY_I2C.endTransmission() == 0;
}
static bool rd(uint8_t addr, uint8_t reg, uint8_t* buf, uint8_t n) {
    FINDY_I2C.beginTransmission(addr);
    FINDY_I2C.write(reg);
    if (FINDY_I2C.endTransmission(false) != 0) return false;
    if (FINDY_I2C.requestFrom((int)addr, (int)n) != n) return false;
    for (uint8_t i = 0; i < n; i++) buf[i] = FINDY_I2C.read();
    return true;
}

bool imu_begin() {
    FINDY_I2C.begin();
    uint8_t w = 0;
    if (!rd(FINDY_I2C_ADDR_ACC, ACC_WHO_AM_I, &w, 1) || w != 0x33) return false;
    if (!rd(FINDY_I2C_ADDR_MAG, MAG_WHO_AM_I, &w, 1) || w != 0x40) return false;
    // İvme: 25 Hz, normal/HR, XYZ açık (CTRL1 = 0b0011_0111), BDU + +-2 g + yüksek çözünürlük (CTRL4 = 0x88)
    bool ok = wr(FINDY_I2C_ADDR_ACC, ACC_CTRL1, 0x37);
    ok &= wr(FINDY_I2C_ADDR_ACC, ACC_CTRL4, 0x88);
    // Manyeto: sıcaklık telafisi + 50 Hz + sürekli mod (CFG_A = 0x88), ofset iptali (CFG_B = 0x02), BDU (CFG_C = 0x10)
    ok &= wr(FINDY_I2C_ADDR_MAG, MAG_CFG_A, 0x88);
    ok &= wr(FINDY_I2C_ADDR_MAG, MAG_CFG_B, 0x02);
    ok &= wr(FINDY_I2C_ADDR_MAG, MAG_CFG_C, 0x10);
    return ok;
}

bool imu_read(ImuSample& s) {
    uint8_t b[6];
    float a[3], m[3];
    // 0x80 biti: çok baytlı okumada adres otomatik artışı (ivme).  DOĞRULANACAK
    if (!rd(FINDY_I2C_ADDR_ACC, ACC_OUT_X_L | 0x80, b, 6)) { s.ok = false; return false; }
    for (int i = 0; i < 3; i++) {
        int16_t raw = (int16_t)(b[2 * i] | (b[2 * i + 1] << 8));
        a[i] = (float)(raw >> 4) * 0.001f;   // HR 12 bit, +-2 g: ~1 mg/LSB (veri sayfası tipik) -> g
    }
    if (!rd(FINDY_I2C_ADDR_MAG, MAG_OUT_X_L, b, 6)) { s.ok = false; return false; }
    for (int i = 0; i < 3; i++) {
        int16_t raw = (int16_t)(b[2 * i] | (b[2 * i + 1] << 8));
        m[i] = (float)raw * 0.15f;           // 1,5 mgauss/LSB = 0,15 µT/LSB
    }
    float* ao = &s.acc_g.x; float* mo = &s.mag_ut.x;
    for (int i = 0; i < 3; i++) {
        ao[i] = ACC_MAP[i].sign * a[ACC_MAP[i].src];
        mo[i] = MAG_MAP[i].sign * m[MAG_MAP[i].src];
    }
    s.ok = true;
    return true;
}

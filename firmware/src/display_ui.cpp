// Findy P0 — 240x240 yuvarlak GC9A01 arayüzü (spec bölüm 7). Adafruit GFX + Adafruit GC9A01A.
// Derlendi (12 Kasım 2026), donanımda denenmedi. Tam kare GFXcanvas16 (240*240*2 = 115 200 bayt RAM) kullanılır: nRF52840'ın 256 KB RAM'inde
// yer var ama BLE + LittleFS ile birlikte yığın/heap payı DOĞRULANACAK; sığmazsa doğrudan çizime geçilmeli.
#include <Adafruit_GC9A01A.h>
#include <Adafruit_GFX.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
#include "board_pins.h"
#include "hw.h"

static Adafruit_GC9A01A tft(FINDY_PIN_TFT_CS, FINDY_PIN_TFT_DC, FINDY_PIN_TFT_RST);
static GFXcanvas16 canvas(240, 240);
static uint16_t g_avatar[AVATAR_W * AVATAR_W];
static bool g_has_avatar = false;

static constexpr uint16_t rgb(uint8_t r, uint8_t g, uint8_t b) { return (uint16_t)(((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)); }
static const uint16_t C_BG = rgb(0, 0, 0);
static const uint16_t C_LIME = rgb(0xC6, 0xFF, 0x3D);   // #C6FF3D
static const uint16_t C_WHITE = rgb(255, 255, 255);
static const uint16_t C_GRAY = rgb(0x5A, 0x5F, 0x66);   // #5A5F66
static const int CX = 120, CY = 120;
static const float DEG2RAD = 0.017453292519943295f;

void ui_begin() {
    pinMode(FINDY_PIN_TFT_BL, OUTPUT);
    analogWrite(FINDY_PIN_TFT_BL, 0);
    tft.begin();
    tft.fillScreen(C_BG);
    canvas.fillScreen(C_BG);
}

void ui_backlight(bool on) { analogWrite(FINDY_PIN_TFT_BL, on ? 200 : 0); }   // %78 PWM (parlaklık ayarı ölçülmedi)

void ui_set_avatar(const uint8_t* p) {
    if (!p) { g_has_avatar = false; return; }
    for (size_t i = 0; i < AVATAR_W * AVATAR_W; i++) g_avatar[i] = (uint16_t)(p[2 * i] | (p[2 * i + 1] << 8));
    g_has_avatar = true;
}

// Ekran açısı (0 = yukarı, saat yönü) -> piksel
static void polar(float ang_deg, float r, int& x, int& y) {
    float a = ang_deg * DEG2RAD;
    x = CX + (int)lroundf(r * sinf(a));
    y = CY - (int)lroundf(r * cosf(a));
}

static void centered(const char* s, int y, uint8_t size, uint16_t col) {
    int16_t x1, y1; uint16_t w, h;
    canvas.setTextSize(size);
    canvas.getTextBounds(s, 0, 0, &x1, &y1, &w, &h);
    canvas.setCursor(CX - (int)w / 2, y);
    canvas.setTextColor(col);
    canvas.print(s);
}

static void draw_arrow(float ang_deg, float len, uint16_t col) {
    int tx, ty, lx, ly, rx, ry, bx, by;
    polar(ang_deg, len, tx, ty);
    polar(ang_deg + 150, len * 0.55f, lx, ly);
    polar(ang_deg - 150, len * 0.55f, rx, ry);
    polar(ang_deg + 180, len * 0.2f, bx, by);
    canvas.fillTriangle(tx, ty, lx, ly, bx, by, col);
    canvas.fillTriangle(tx, ty, rx, ry, bx, by, col);
}

static void draw_avatar() {
    canvas.fillScreen(C_BG);
    canvas.drawCircle(CX, CY, 118, C_LIME);
    canvas.drawCircle(CX, CY, 117, C_LIME);
    canvas.drawCircle(CX, CY, 116, C_LIME);
    if (!g_has_avatar) { centered("FINDY", 108, 3, C_LIME); return; }
    // 96x96, 2x büyütülmüş (192x192), dairesel maske
    for (int y = 0; y < (int)AVATAR_W; y++)
        for (int x = 0; x < (int)AVATAR_W; x++) {
            int dx = x - 48, dy = y - 48;
            if (dx * dx + dy * dy > 48 * 48) continue;
            canvas.fillRect(24 + 2 * x, 24 + 2 * y, 2, 2, g_avatar[y * AVATAR_W + x]);
        }
}

static void fmt_dist(float m, char* out, size_t n) {
    if (m < 1000) snprintf(out, n, "%d m", (int)lroundf(m));
    else snprintf(out, n, "%d.%d km", (int)(m / 1000), (int)((m - 1000 * (int)(m / 1000)) / 100));
}

static void draw_radar(const UiModel& m) {
    canvas.fillScreen(C_BG);
    // 3 mesafe halkası: <=50 m, <=200 m, >200 m
    const int R[3] = {40, 75, 108};
    for (int i = 0; i < 3; i++) canvas.drawCircle(CX, CY, R[i], C_GRAY);
    canvas.fillCircle(CX, CY, 3, C_LIME);   // merkez = ben

    for (int i = 0; i < 4; i++) {
        const UiFriend& f = m.f[i];
        if (!f.valid) continue;
        int ring = f.dist_m <= 50 ? 0 : (f.dist_m <= 200 ? 1 : 2);
        uint16_t col = (f.st == findy::Staleness::Fresh) ? C_LIME : C_GRAY;   // soluk çizim
        int x, y;
        if (f.arrow_ok) polar(f.arrow_deg, R[ring], x, y);
        else { x = CX; y = CY - R[ring]; }   // yön yoksa halkanın tepesinde (yön bilinmiyor)
        canvas.fillCircle(x, y, (i == m.selected) ? 7 : 5, col);
        if (i == m.selected) canvas.drawCircle(x, y, 10, C_WHITE);
    }

    if (m.selected >= 0 && m.selected < 4 && m.f[m.selected].valid) {
        const UiFriend& f = m.f[m.selected];
        char d[16], line[24];
        fmt_dist(f.dist_m, d, sizeof(d));
        if (m.tilted) {
            centered("DUZ TUT", 96, 2, C_WHITE);          // eğim > 60°: ok gizli, "düz tut"
        } else if (f.ring_only) {
            centered("YAKININDA", 96, 2, C_LIME);          // güven göstergesi: yalnız mesafe halkası
        } else if (f.arrow_ok) {
            draw_arrow(f.arrow_deg, 50, (f.st == findy::Staleness::Fresh) ? C_LIME : C_GRAY);
        }
        snprintf(line, sizeof(line), "%s %s", f.name[0] ? f.name : "?", d);
        centered(line, 168, 2, C_WHITE);
        if (f.st == findy::Staleness::LastSeen) centered("SON GORULME", 192, 1, C_GRAY);
    } else {
        centered("ARKADAS YOK", 108, 2, C_GRAY);
    }
    if (m.search) canvas.drawCircle(CX, CY, 119, C_LIME);   // ARAMA kipi halkası
    if (m.hold_stage > 0) {                                   // tuş basılı geri bildirimi
        const char* t = m.hold_stage == 1 ? "PING" : (m.hold_stage == 2 ? "ESLESME" : "CIK");
        centered(t, 12, 2, C_LIME);
    }
}

static void draw_pair(const UiModel& m) {
    canvas.fillScreen(C_BG);
    // ilerleme halkası: 0..1 -> yay (çizgilerle)
    int steps = (int)(m.pair_progress * 120.0f);
    for (int i = 0; i < steps; i++) {
        int x1, y1, x2, y2;
        polar(i * 3.0f, 112, x1, y1); polar(i * 3.0f, 118, x2, y2);
        canvas.drawLine(x1, y1, x2, y2, C_LIME);
    }
    centered("ESLESME", 70, 2, C_WHITE);
    if (m.pair_node >= 0) { char b[8]; snprintf(b, sizeof(b), "%d", m.pair_node + 1); centered(b, 100, 6, C_LIME); }
    if (m.pair_text) centered(m.pair_text, 170, 2, C_GRAY);
}

static void draw_status(const UiModel& m) {
    canvas.fillScreen(C_BG);
    char b[32];
    centered("DURUM", 30, 2, C_LIME);
    snprintf(b, sizeof(b), "PIL %%%d", m.batt_pct);  centered(b, 70, 2, C_WHITE);
    centered(m.gnss_fix ? "GNSS: KONUM VAR" : (m.gnss_powered ? "GNSS: ARANIYOR" : "GNSS: KAPALI"), 100, 2, m.gnss_fix ? C_LIME : C_GRAY);
    snprintf(b, sizeof(b), "GRUP: %d UYE", m.members); centered(b, 130, 2, C_WHITE);
    centered(FINDY_FW_VERSION, 170, 2, C_GRAY);
}

static void draw_calibrate(const UiModel& m) {
    canvas.fillScreen(C_BG);
    centered("PUSULA", 70, 2, C_WHITE);
    centered("8 CIZ", 100, 3, C_LIME);
    canvas.drawRect(40, 160, 160, 12, C_GRAY);
    canvas.fillRect(41, 161, (int)(158 * m.mag_progress), 10, C_LIME);
}

void ui_render(const UiModel& m) {
    if (m.screen == Screen::Off) { tft.fillScreen(C_BG); ui_backlight(false); return; }
    switch (m.screen) {
        case Screen::Avatar: draw_avatar(); break;
        case Screen::Radar: draw_radar(m); break;
        case Screen::Pair: draw_pair(m); break;
        case Screen::Status: draw_status(m); break;
        case Screen::Calibrate: draw_calibrate(m); break;
        default: break;
    }
    tft.drawRGBBitmap(0, 0, canvas.getBuffer(), 240, 240);
}

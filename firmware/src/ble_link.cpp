// Findy P0 — BLE Nordic UART Service (Bluefruit, nRF52 BSP içinde), satır tabanlı komutlar (spec bölüm 8).
// Derlendi (12 Kasım 2026), donanımda denenmedi. Bluefruit API adları (BLEUart, Bluefruit.Periph, Advertising) Adafruit nRF52 örneklerinden hatırlanıyor.
//
// Protokol (bu sürümde kendi kararım; spec yalnızca komut adlarını verir):
//   Telefon -> cihaz (satır sonu '\n'):  NAME <ad> | STATUS | LOG ON|OFF | CFG <k> <v> | FRIEND <id> <ad>
//   AVATAR BEGIN <bayt>  -> cihaz "OK" der; ardından tam <bayt> ham veri (satır ayrıştırılmaz);
//   AVATAR END <crc32 hex>  -> CRC32 (zlib) doğrulanır; cihaz "OK" ya da "ERR ..." der.
//   Cihaz -> telefon: "OK", "ERR <neden>", STATUS için tek satır JSON, LOG için CSV satırları.
#include <bluefruit.h>
#include <stdlib.h>
#include <string.h>
#include "hw.h"

static BLEUart bleuart;
static BleHooks g_h;
static char g_line[96];
static size_t g_line_n = 0;
static bool g_bin = false;
static size_t g_bin_need = 0, g_bin_got = 0;
static uint8_t g_avatar_buf[AVATAR_BYTES];
static bool g_avatar_ready = false;

static void reply(const char* s) { bleuart.print(s); bleuart.print("\n"); }

void ble_send_line(const char* line) { if (bleuart.notifyEnabled()) reply(line); }
bool ble_connected() { return Bluefruit.connected(); }

static void upper_ascii(char* s) { for (; *s; s++) if (*s >= 'a' && *s <= 'z') *s -= 32; }

static void handle_line(char* line) {
    // baştaki/sondaki boşluk ve \r temizle
    while (*line == ' ') line++;
    size_t n = strlen(line);
    while (n && (line[n - 1] == '\r' || line[n - 1] == ' ')) line[--n] = 0;
    if (!n) return;

    char* sp = strchr(line, ' ');
    char* arg = nullptr;
    if (sp) { *sp = 0; arg = sp + 1; }
    char cmd[12]; strncpy(cmd, line, sizeof(cmd) - 1); cmd[sizeof(cmd) - 1] = 0;
    upper_ascii(cmd);

    if (!strcmp(cmd, "NAME")) {
        if (!arg || !*arg) { reply("ERR ad bos"); return; }
        char nm[9]; strncpy(nm, arg, 8); nm[8] = 0; upper_ascii(nm);
        for (char* c = nm; *c; c++) if (*c < 'A' || *c > 'Z') if (*c < '0' || *c > '9') { reply("ERR yalniz A-Z 0-9"); return; }
        g_h.set_name(nm); reply("OK");
    } else if (!strcmp(cmd, "STATUS")) {
        char buf[200]; g_h.status_json(buf, sizeof(buf)); reply(buf);
    } else if (!strcmp(cmd, "LOG")) {
        if (arg && !strncasecmp(arg, "ON", 2)) { g_h.set_log(true); reply("OK"); }
        else if (arg && !strncasecmp(arg, "OFF", 3)) { g_h.set_log(false); reply("OK"); }
        else reply("ERR LOG ON|OFF");
    } else if (!strcmp(cmd, "CFG")) {
        char* v = arg ? strchr(arg, ' ') : nullptr;
        if (!v) { reply("ERR CFG <anahtar> <deger>"); return; }
        *v++ = 0;
        reply(g_h.set_cfg(arg, v) ? "OK" : "ERR bilinmeyen anahtar/deger");
    } else if (!strcmp(cmd, "FRIEND")) {
        char* v = arg ? strchr(arg, ' ') : nullptr;
        if (!v) { reply("ERR FRIEND <1-5> <ad>"); return; }
        *v++ = 0;
        int id = atoi(arg);
        reply(g_h.set_friend(id, v) ? "OK" : "ERR");
    } else if (!strcmp(cmd, "AVATAR")) {
        if (arg && !strncasecmp(arg, "BEGIN", 5)) {
            size_t need = (size_t)atoi(arg + 5);
            if (need != AVATAR_BYTES) { reply("ERR 18432 bayt bekleniyor"); return; }
            g_bin = true; g_bin_need = need; g_bin_got = 0; g_avatar_ready = false;
            reply("OK");
        } else if (arg && !strncasecmp(arg, "END", 3)) {
            uint32_t crc = (uint32_t)strtoul(arg + 3, nullptr, 16);
            if (!g_avatar_ready) { reply("ERR veri eksik"); return; }
            if (findy::crc32_ieee(g_avatar_buf, AVATAR_BYTES) != crc) { reply("ERR crc"); g_avatar_ready = false; return; }
            reply(g_h.set_avatar(g_avatar_buf, AVATAR_BYTES) ? "OK" : "ERR kayit");
            g_avatar_ready = false;
        } else reply("ERR AVATAR BEGIN|END");
    } else {
        reply("ERR bilinmeyen komut");
    }
}

bool ble_begin(const char* adv_name, const BleHooks& hooks) {
    g_h = hooks;
    // El sıkışma büyük MTU: 18 KB avatar için hız iyileştirmesi (zorunlu değil). DOĞRULANACAK: configPrphConn imzası.
    Bluefruit.configPrphConn(247, BLE_GAP_EVENT_LENGTH_DEFAULT, 16, 16);
    Bluefruit.begin();
    Bluefruit.setTxPower(0);
    Bluefruit.setName(adv_name);
    bleuart.begin();

    Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
    Bluefruit.Advertising.addTxPower();
    Bluefruit.Advertising.addService(bleuart);
    Bluefruit.ScanResponse.addName();
    Bluefruit.Advertising.restartOnDisconnect(true);
    Bluefruit.Advertising.setInterval(1600, 3200);   // 1 s - 2 s (birim 0,625 ms): düşük güç; bağlanma gecikmesi ölçülmedi
    Bluefruit.Advertising.setFastTimeout(30);
    Bluefruit.Advertising.start(0);
    return true;
}

void ble_poll() {
    while (bleuart.available()) {
        int c = bleuart.read();
        if (c < 0) break;
        if (g_bin) {
            g_avatar_buf[g_bin_got++] = (uint8_t)c;
            if (g_bin_got >= g_bin_need) { g_bin = false; g_avatar_ready = true; }
            continue;
        }
        if (c == '\n') { g_line[g_line_n] = 0; g_line_n = 0; handle_line(g_line); }
        else if (g_line_n < sizeof(g_line) - 1) g_line[g_line_n++] = (char)c;
    }
}

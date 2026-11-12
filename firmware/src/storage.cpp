// Findy P0 — kalıcı saklama (InternalFS = Adafruit LittleFS, nRF52 dahili flaş).
// DOĞRULANACAK: Adafruit_LittleFS dosya API'si (File, FILE_O_READ/WRITE, InternalFS.begin) örnek kodlardan hatırlanıyor.
#include <Adafruit_LittleFS.h>
#include <InternalFileSystem.h>
#include <string.h>
#include "hw.h"

using namespace Adafruit_LittleFS_Namespace;

static const char* CFG_PATH = "/findy_cfg.bin";
static const char* AVATAR_PATH = "/findy_avatar.rgb";
static const uint32_t MAGIC = 0x59444E46;  // 'FNDY'

void settings_defaults(Settings& s) {
    memset(&s, 0, sizeof(s));
    s.magic = MAGIC; s.version = 1;
    strcpy(s.name, "FINDY");
    s.sf = 8; s.tx_power_dbm = 14;
    s.standby_s = 15; s.search_s = 5;
    s.declination_deg = 0.0f;   // v0: ayar sabiti (spec bölüm 5)
}

bool storage_begin() { return InternalFS.begin(); }

static uint32_t cfg_crc(const Settings& s) { return findy::crc32_ieee((const uint8_t*)&s, offsetof(Settings, crc)); }

bool settings_load(Settings& s) {
    File f(InternalFS);
    if (f.open(CFG_PATH, FILE_O_READ)) {
        Settings t;
        int n = f.read((uint8_t*)&t, sizeof(t));
        f.close();
        if (n == (int)sizeof(t) && t.magic == MAGIC && t.version == 1 && t.crc == cfg_crc(t)) { s = t; return true; }
    }
    settings_defaults(s);
    return false;
}

bool settings_save(const Settings& in) {
    Settings s = in;
    s.magic = MAGIC; s.version = 1; s.crc = cfg_crc(s);
    InternalFS.remove(CFG_PATH);   // LittleFS'te üzerine yazmak yerine sil+yaz (basit; güç kesintisi riski DOĞRULANACAK)
    File f(InternalFS);
    if (!f.open(CFG_PATH, FILE_O_WRITE)) return false;
    size_t n = f.write((const uint8_t*)&s, sizeof(s));
    f.close();
    return n == sizeof(s);
}

bool avatar_save(const uint8_t* data, size_t n) {
    if (n != AVATAR_BYTES) return false;
    InternalFS.remove(AVATAR_PATH);
    File f(InternalFS);
    if (!f.open(AVATAR_PATH, FILE_O_WRITE)) return false;
    size_t w = f.write(data, n);
    f.close();
    return w == n;
}

bool avatar_load(uint8_t* data, size_t n) {
    File f(InternalFS);
    if (!f.open(AVATAR_PATH, FILE_O_READ)) return false;
    int r = f.read(data, n);
    f.close();
    return r == (int)n;
}

// Findy P0 — SX1262 (RadioLib). FindyLink fiziksel katmanı (spec bölüm 4): 869,525 MHz, BW125, SF8, CR4/5,
// önek 8, CRC açık, sync word 0x46. Derlendi (12 Kasım 2026, RadioLib 6.6.0), donanımda denenmedi.
#include <RadioLib.h>
#include <SPI.h>
#include "board_pins.h"
#include "hw.h"

// LoRa, WisBlock SPI'ından AYRI bir SPI bloğunda (SX1262 modül içi). Ekran BSP `SPI`yı kullanır.
// DOĞRULANACAK: SPIClass kurucu imzası ve boş bir SPIM bloğu (NRF_SPIM2) seçimi; BSP zaten
// `SPI1` tanımlıyorsa onu kullan.
static SPIClass loraSPI(NRF_SPIM2, PIN_LORA_MISO, PIN_LORA_SCLK, PIN_LORA_MOSI);
static SX1262 radio = new Module(PIN_LORA_NSS, PIN_LORA_DIO_1, PIN_LORA_RESET, PIN_LORA_BUSY, loraSPI);

static const float FREQ_MHZ = 869.525f;
static const float BW_KHZ = 125.0f;
static const uint8_t CR_DENOM = 5;
static const uint8_t SYNC_WORD = 0x46;   // DOĞRULANACAK: RadioLib 1 baytlık syncWord'ü SX126x için (0x46 -> 0x4464) genişletir
static const uint16_t PREAMBLE = 8;

static volatile bool g_rx_flag = false;
static bool g_listening = false;
static uint8_t g_sf = 8;

static void on_dio1() { g_rx_flag = true; }

bool radio_begin(const RadioParams& p) {
    loraSPI.begin();
    g_sf = p.sf;
    int st = radio.begin(FREQ_MHZ, BW_KHZ, p.sf, CR_DENOM, SYNC_WORD, p.power_dbm, PREAMBLE, FINDY_LORA_TCXO_V, false);
    if (st != RADIOLIB_ERR_NONE) return false;
    // RF anahtarı DIO2'den (spec). DOĞRULANACAK: RAK4631'de gerekli mi / ek RXEN-TXEN pini var mı.
    if (FINDY_LORA_DIO2_RFSW) radio.setDio2AsRfSwitch(true);
    radio.setCRC(true);
    radio.setPacketReceivedAction(on_dio1);
    g_listening = false;
    return true;
}

void radio_apply(const RadioParams& p) {
    g_sf = p.sf;
    radio.setSpreadingFactor(p.sf);
    radio.setOutputPower(p.power_dbm);
    g_listening = false;
}

void radio_listen() {
    if (g_listening) return;
    g_rx_flag = false;
    if (radio.startReceive() == RADIOLIB_ERR_NONE) g_listening = true;
}

void radio_idle() {
    if (!g_listening) return;
    radio.standby();
    g_listening = false;
}

bool radio_transmit(const uint8_t* buf, size_t len, int8_t power_override) {
    radio_idle();
    int8_t prev = 0; bool changed = false;
    if (power_override != 127) { radio.setOutputPower(power_override); changed = true; (void)prev; }
    int st = radio.transmit((uint8_t*)buf, len);   // bloklayıcı; SF8'de 30 bayt ~123 ms
    (void)changed;
    return st == RADIOLIB_ERR_NONE;
    // NOT: eşleşme gücü (-9 dBm) sonrası normal güce dönüş main.cpp'de radio_apply() ile yapılır.
}

bool radio_poll(uint8_t* buf, size_t& len, int& rssi, int& snr) {
    if (!g_rx_flag) return false;
    g_rx_flag = false;
    size_t n = radio.getPacketLength();
    if (n == 0 || n > 64) { g_listening = false; return false; }
    int st = radio.readData(buf, n);
    g_listening = false;   // readData sonrası yeniden startReceive gerekir
    if (st != RADIOLIB_ERR_NONE) return false;   // CRC hatası dahil
    len = n;
    rssi = (int)radio.getRSSI();
    snr = (int)radio.getSNR();
    return true;
}

uint32_t radio_airtime_ms(size_t len) {
    return (uint32_t)(radio.getTimeOnAir(len) / 1000);   // µs -> ms (DOĞRULANACAK: getTimeOnAir µs döner)
}

// Findy çekirdek: FindyLink v0 paket kodlama/çözme (spec bölüm 4).
#pragma once
#include <cstddef>
#include <cstdint>
#include "crypto_iface.h"

namespace findy {

constexpr uint8_t MAGIC_DATA = 0xF1;
constexpr uint8_t MAGIC_PAIR_OFFER = 0xF2;
constexpr uint8_t MAGIC_PAIR_ACK = 0xF3;  // spec biçim vermiyor; bu sürümde kendi kararım (aşağıda)

constexpr size_t HEADER_LEN = 8;
constexpr size_t PAYLOAD_LEN = 14;
constexpr size_t TAG_LEN = 8;
constexpr size_t PACKET_LEN = HEADER_LEN + PAYLOAD_LEN + TAG_LEN;  // 30
constexpr uint8_t PROTO_VERSION = 0;
constexpr uint8_t MAX_NODES = 5;
constexpr uint8_t FIX_AGE_NONE = 255;
constexpr uint8_t HACC_UNKNOWN = 255;

enum : uint8_t {
    FLAG_SEARCH = 1 << 0,  // ARAMA kipi
    FLAG_PING = 1 << 1,    // arkadaşı titret
    FLAG_STILL = 1 << 2,   // hareketsiz
};

struct Header {
    uint16_t group_id;
    uint8_t node_id;  // 0..4 (bit 0-2)
    uint8_t version;  // bit 3-7
    uint32_t counter;
};

struct Payload {
    int32_t lat_e7;
    int32_t lon_e7;
    uint8_t fix_age_s;  // 255 = konum yok
    uint8_t hacc_m;     // 255 = bilinmiyor
    uint8_t batt_pct;
    uint8_t flags;
    uint8_t ping_target;  // bit i = node i
    uint8_t rsv;
};

enum class DecodeResult : uint8_t {
    Ok = 0,
    BadLength,
    BadMagic,
    BadVersion,
    WrongGroup,
    BadTag,
};

// group_id = BLAKE2s(anahtar)'ın ilk 2 baytı (little-endian uint16 olarak okunur).
uint16_t group_id_from_key(const ICrypto& c, const uint8_t key[32]);

// out en az PACKET_LEN bayt. Başlık geçersizse (node_id>=MAX_NODES) false.
bool encode_packet(const ICrypto& c, const uint8_t key[32], const Header& h, const Payload& p,
                   uint8_t out[PACKET_LEN]);

// Tekrar (replay) denetimi BURADA yapılmaz; group.cpp'de etiket doğrulandıktan sonra yapılır.
DecodeResult decode_packet(const ICrypto& c, const uint8_t key[32], uint16_t expected_group_id,
                           const uint8_t* buf, size_t len, Header& h, Payload& p);

// ---- Eşleşme mesajları (spec 4: PAIR_OFFER; PAIR_ACK biçimi bu sürümde bana ait karar)
constexpr size_t PAIR_OFFER_LEN = 1 + 32 + 1 + 2;  // magic, anahtar, node_id, CRC16
constexpr size_t PAIR_ACK_LEN = 1 + 2 + 1 + 2;     // magic, group_id, node_id, CRC16
constexpr int PAIR_RSSI_MIN_DBM = -45;             // bundan GÜÇLÜ (>) olmalı: temas mesafesi

uint16_t crc16_ccitt(const uint8_t* data, size_t len);  // poly 0x1021, init 0xFFFF
uint32_t crc32_ieee(const uint8_t* data, size_t len);   // zlib uyumlu (avatar doğrulaması)

void encode_pair_offer(const uint8_t key[32], uint8_t assigned_node, uint8_t out[PAIR_OFFER_LEN]);
bool decode_pair_offer(const uint8_t* buf, size_t len, uint8_t key_out[32], uint8_t& assigned_node);
void encode_pair_ack(uint16_t group_id, uint8_t node_id, uint8_t out[PAIR_ACK_LEN]);
bool decode_pair_ack(const uint8_t* buf, size_t len, uint16_t& group_id, uint8_t& node_id);

inline bool pair_rssi_ok(int rssi_dbm) { return rssi_dbm > PAIR_RSSI_MIN_DBM; }

}  // namespace findy

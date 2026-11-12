#include "packet.h"
#include <cstring>

namespace findy {

static inline void put32(uint8_t* p, uint32_t v) {
    p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8); p[2] = (uint8_t)(v >> 16); p[3] = (uint8_t)(v >> 24);
}
static inline uint32_t get32(const uint8_t* p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

uint16_t group_id_from_key(const ICrypto& c, const uint8_t key[32]) {
    uint8_t h[32];
    c.hash256(key, 32, h);
    return (uint16_t)(h[0] | (h[1] << 8));
}

// Nonce (12) = node_id(1) || 0x00 x7 || counter(4, LE)
static void make_nonce(uint8_t node, uint32_t counter, uint8_t nonce[12]) {
    memset(nonce, 0, 12);
    nonce[0] = node;
    put32(nonce + 8, counter);
}

bool encode_packet(const ICrypto& c, const uint8_t key[32], const Header& h, const Payload& p,
                   uint8_t out[PACKET_LEN]) {
    if (h.node_id >= MAX_NODES) return false;
    out[0] = MAGIC_DATA;
    out[1] = (uint8_t)h.group_id;
    out[2] = (uint8_t)(h.group_id >> 8);
    out[3] = (uint8_t)((h.node_id & 0x07) | ((h.version & 0x1F) << 3));
    put32(out + 4, h.counter);

    uint8_t pt[PAYLOAD_LEN];
    put32(pt + 0, (uint32_t)p.lat_e7);
    put32(pt + 4, (uint32_t)p.lon_e7);
    pt[8] = p.fix_age_s; pt[9] = p.hacc_m; pt[10] = p.batt_pct;
    pt[11] = p.flags; pt[12] = p.ping_target; pt[13] = p.rsv;

    uint8_t nonce[12], tag[16];
    make_nonce(h.node_id, h.counter, nonce);
    c.aead_seal(key, nonce, out, HEADER_LEN, pt, PAYLOAD_LEN, out + HEADER_LEN, tag);
    memcpy(out + HEADER_LEN + PAYLOAD_LEN, tag, TAG_LEN);
    return true;
}

DecodeResult decode_packet(const ICrypto& c, const uint8_t key[32], uint16_t expected_group_id,
                           const uint8_t* buf, size_t len, Header& h, Payload& p) {
    if (len != PACKET_LEN) return DecodeResult::BadLength;
    if (buf[0] != MAGIC_DATA) return DecodeResult::BadMagic;
    uint16_t gid = (uint16_t)(buf[1] | (buf[2] << 8));
    if (gid != expected_group_id) return DecodeResult::WrongGroup;
    uint8_t ver = buf[3] >> 3;
    if (ver != PROTO_VERSION) return DecodeResult::BadVersion;
    uint8_t node = buf[3] & 0x07;
    if (node >= MAX_NODES) return DecodeResult::BadVersion;  // geçersiz başlık; ayrı kod gerekmedi
    uint32_t counter = get32(buf + 4);

    uint8_t nonce[12], pt[PAYLOAD_LEN];
    make_nonce(node, counter, nonce);
    if (!c.aead_open(key, nonce, buf, HEADER_LEN, buf + HEADER_LEN, PAYLOAD_LEN,
                     buf + HEADER_LEN + PAYLOAD_LEN, TAG_LEN, pt))
        return DecodeResult::BadTag;

    h.group_id = gid; h.node_id = node; h.version = ver; h.counter = counter;
    p.lat_e7 = (int32_t)get32(pt + 0);
    p.lon_e7 = (int32_t)get32(pt + 4);
    p.fix_age_s = pt[8]; p.hacc_m = pt[9]; p.batt_pct = pt[10];
    p.flags = pt[11]; p.ping_target = pt[12]; p.rsv = pt[13];
    return DecodeResult::Ok;
}

uint16_t crc16_ccitt(const uint8_t* d, size_t n) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < n; i++) {
        crc ^= (uint16_t)d[i] << 8;
        for (int b = 0; b < 8; b++) crc = (crc & 0x8000) ? (uint16_t)((crc << 1) ^ 0x1021) : (uint16_t)(crc << 1);
    }
    return crc;
}

uint32_t crc32_ieee(const uint8_t* d, size_t n) {
    uint32_t crc = 0xFFFFFFFFu;
    for (size_t i = 0; i < n; i++) {
        crc ^= d[i];
        for (int b = 0; b < 8; b++) crc = (crc & 1) ? (crc >> 1) ^ 0xEDB88320u : (crc >> 1);
    }
    return ~crc;
}

void encode_pair_offer(const uint8_t key[32], uint8_t assigned_node, uint8_t out[PAIR_OFFER_LEN]) {
    out[0] = MAGIC_PAIR_OFFER;
    memcpy(out + 1, key, 32);
    out[33] = assigned_node;
    uint16_t crc = crc16_ccitt(out, 34);
    out[34] = (uint8_t)crc; out[35] = (uint8_t)(crc >> 8);
}

bool decode_pair_offer(const uint8_t* buf, size_t len, uint8_t key_out[32], uint8_t& assigned_node) {
    if (len != PAIR_OFFER_LEN || buf[0] != MAGIC_PAIR_OFFER) return false;
    uint16_t crc = (uint16_t)(buf[34] | (buf[35] << 8));
    if (crc != crc16_ccitt(buf, 34)) return false;
    if (buf[33] >= MAX_NODES) return false;
    memcpy(key_out, buf + 1, 32);
    assigned_node = buf[33];
    return true;
}

void encode_pair_ack(uint16_t group_id, uint8_t node_id, uint8_t out[PAIR_ACK_LEN]) {
    out[0] = MAGIC_PAIR_ACK;
    out[1] = (uint8_t)group_id; out[2] = (uint8_t)(group_id >> 8);
    out[3] = node_id;
    uint16_t crc = crc16_ccitt(out, 4);
    out[4] = (uint8_t)crc; out[5] = (uint8_t)(crc >> 8);
}

bool decode_pair_ack(const uint8_t* buf, size_t len, uint16_t& group_id, uint8_t& node_id) {
    if (len != PAIR_ACK_LEN || buf[0] != MAGIC_PAIR_ACK) return false;
    uint16_t crc = (uint16_t)(buf[4] | (buf[5] << 8));
    if (crc != crc16_ccitt(buf, 4)) return false;
    group_id = (uint16_t)(buf[1] | (buf[2] << 8));
    node_id = buf[3];
    return true;
}

}  // namespace findy

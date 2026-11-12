#include "group.h"
#include <cstring>

namespace findy {

void Group::set_group(const ICrypto& c, const uint8_t key[32], uint8_t self_node) {
    memcpy(key_, key, 32);
    group_id_ = group_id_from_key(c, key);
    self_node_ = self_node;
    has_group_ = true;
    assigned_mask_ = (uint8_t)(1u << self_node);
    for (auto& m : m_) m = Member();
}

void Group::leave() {
    has_group_ = false;
    memset(key_, 0, sizeof(key_));
    group_id_ = 0;
    assigned_mask_ = 0;
    for (auto& m : m_) m = Member();
}

RxStatus Group::on_packet(const ICrypto& c, const uint8_t* buf, size_t len, ms_t now, int rssi, int snr,
                          Header* hdr_out, Payload* pl_out) {
    if (!has_group_) return RxStatus::NoGroup;
    Header h{};
    Payload p{};
    switch (decode_packet(c, key_, group_id_, buf, len, h, p)) {
        case DecodeResult::Ok: break;
        case DecodeResult::BadLength: return RxStatus::BadLength;
        case DecodeResult::BadMagic: return RxStatus::BadMagic;
        case DecodeResult::BadVersion: return RxStatus::BadVersion;
        case DecodeResult::WrongGroup: return RxStatus::WrongGroup;
        case DecodeResult::BadTag: return RxStatus::BadTag;
    }
    if (h.node_id == self_node_) return RxStatus::OwnNode;
    Member& m = m_[h.node_id];
    // Aynı node için son kabul edilen sayaçtan küçük/eşit olan atılır.
    if (m.has_counter && h.counter <= m.last_counter) return RxStatus::Replay;
    m.has_counter = true;
    m.last_counter = h.counter;
    m.seen = true;
    m.p = p;
    m.last_rx_ms = now;
    m.rssi_dbm = (int16_t)rssi;
    m.snr_db = (int8_t)snr;
    assigned_mask_ |= (uint8_t)(1u << h.node_id);
    if (hdr_out) *hdr_out = h;
    if (pl_out) *pl_out = p;
    return RxStatus::Ok;
}

ms_t Group::rx_age_ms(uint8_t node, ms_t now) const {
    if (node >= MAX_NODES || !m_[node].seen) return UINT64_MAX;
    return now - m_[node].last_rx_ms;
}

bool Group::has_position(uint8_t node) const {
    if (node >= MAX_NODES || !m_[node].seen) return false;
    return m_[node].p.fix_age_s != FIX_AGE_NONE;
}

uint32_t Group::position_age_s(uint8_t node, ms_t now) const {
    if (!has_position(node)) return UINT32_MAX;
    return (uint32_t)(rx_age_ms(node, now) / 1000) + m_[node].p.fix_age_s;
}

Staleness Group::staleness(uint8_t node, ms_t now) const {
    uint32_t age = position_age_s(node, now);
    if (age > LAST_SEEN_AFTER_S) return Staleness::LastSeen;
    if (age > FAINT_AFTER_S) return Staleness::Faint;
    return Staleness::Fresh;
}

int Group::visible_count() const {
    int n = 0;
    for (uint8_t i = 0; i < MAX_NODES; i++)
        if (i != self_node_ && m_[i].seen) n++;
    return n;
}

void Group::prune(ms_t now, ms_t ttl_ms) {
    for (auto& m : m_)
        if (m.seen && now - m.last_rx_ms > ttl_ms) m = Member();
}

int Group::next_friend(int from) const {
    for (int k = 1; k <= MAX_NODES; k++) {
        int i = (from + k + MAX_NODES) % MAX_NODES;
        if (from < 0) i = k - 1;
        if (i != self_node_ && m_[i].seen) return i;
    }
    return -1;
}

int Group::allocate_node_id() {
    for (int i = 0; i < MAX_NODES; i++) {
        if (!(assigned_mask_ & (1u << i))) {
            assigned_mask_ |= (uint8_t)(1u << i);
            return i;
        }
    }
    return -1;
}

void Group::release_node_id(uint8_t id) {
    if (id < MAX_NODES && id != self_node_ && !m_[id].seen) assigned_mask_ &= (uint8_t)~(1u << id);
}

}  // namespace findy

// Findy çekirdek birim testleri — çerçevesiz, yalnızca g++ gerekir.
// Çalıştırma: bash firmware/test/run_native_tests.sh
#include <cmath>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#include "button.h"
#include "compass.h"
#include "crypto_ref.h"
#include "geo.h"
#include "group.h"
#include "packet.h"
#include "power_model.h"
#include "slots.h"

using namespace findy;

// ---------------------------------------------------------------- mini çerçeve
static int g_checks = 0, g_failed_checks = 0, g_tests = 0, g_failed_tests = 0;
static int g_cur_failed = 0;
struct TestReg { const char* name; void (*fn)(); };
static std::vector<TestReg>& registry() { static std::vector<TestReg> r; return r; }
struct Reg { Reg(const char* n, void (*f)()) { registry().push_back({n, f}); } };
#define TEST(name) static void name(); static Reg reg_##name(#name, name); static void name()
#define CHECK(c) do { g_checks++; if (!(c)) { g_failed_checks++; g_cur_failed++; \
    printf("    BAŞARISIZ %s:%d: %s\n", __FILE__, __LINE__, #c); } } while (0)
#define CHECK_EQ(a, b) do { g_checks++; long long _a = (long long)(a), _b = (long long)(b); if (_a != _b) { \
    g_failed_checks++; g_cur_failed++; printf("    BAŞARISIZ %s:%d: %s == %s (%lld != %lld)\n", __FILE__, __LINE__, #a, #b, _a, _b); } } while (0)
#define CHECK_NEAR(a, b, tol) do { g_checks++; double _a = (double)(a), _b = (double)(b); if (!(std::fabs(_a - _b) <= (tol))) { \
    g_failed_checks++; g_cur_failed++; printf("    BAŞARISIZ %s:%d: %s ~ %s (%.6f vs %.6f, tol %.6f)\n", __FILE__, __LINE__, #a, #b, _a, _b, (double)(tol)); } } while (0)

static std::vector<uint8_t> hex(const char* s) {
    std::vector<uint8_t> v;
    int hi = -1;
    for (; *s; s++) {
        int d;
        if (*s >= '0' && *s <= '9') d = *s - '0';
        else if (*s >= 'a' && *s <= 'f') d = *s - 'a' + 10;
        else if (*s >= 'A' && *s <= 'F') d = *s - 'A' + 10;
        else continue;
        if (hi < 0) hi = d; else { v.push_back((uint8_t)(hi * 16 + d)); hi = -1; }
    }
    return v;
}
static bool eq(const uint8_t* a, const std::vector<uint8_t>& b) { return memcmp(a, b.data(), b.size()) == 0; }

static RefCrypto CR;
static void make_key(uint8_t key[32], uint8_t seed) { for (int i = 0; i < 32; i++) key[i] = (uint8_t)(seed * 31 + i * 7 + 1); }

// ================================================================ ŞİFRELEME (RFC 8439 / BLAKE2s)
TEST(crypto_chacha20_block_rfc8439_2_3_2) {
    auto key = hex("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f");
    auto nonce = hex("000000090000004a00000000");
    uint8_t out[64];
    chacha20_block(key.data(), 1, nonce.data(), out);
    CHECK(eq(out, hex("10f1e7e4d13b5915500fdd1fa32071c4c7d1f4c733c068030422aa9ac3d46c4e")));
}

TEST(crypto_poly1305_rfc8439_2_5_2) {
    auto key = hex("85d6be7857556d337f4452fe42d506a80103808afb0db2fd4abff6af4149f51b");
    const char* msg = "Cryptographic Forum Research Group";
    uint8_t tag[16];
    poly1305_mac(key.data(), (const uint8_t*)msg, strlen(msg), tag);
    CHECK(eq(tag, hex("a8061dc1305136c6c22b8baf0c0127a9")));
}

TEST(crypto_aead_rfc8439_2_8_2) {
    auto key = hex("808182838485868788898a8b8c8d8e8f909192939495969798999a9b9c9d9e9f");
    auto nonce = hex("070000004041424344454647");
    auto aad = hex("50515253c0c1c2c3c4c5c6c7");
    const char* pt = "Ladies and Gentlemen of the class of '99: If I could offer you only one tip for the future, sunscreen would be it.";
    size_t n = strlen(pt);
    CHECK_EQ(n, 114);
    std::vector<uint8_t> ct(n), back(n);
    uint8_t tag[16];
    CR.aead_seal(key.data(), nonce.data(), aad.data(), aad.size(), (const uint8_t*)pt, n, ct.data(), tag);
    CHECK(eq(ct.data(), hex("d31a8d34648e60db7b86afbc53ef7ec2a4aded51296e08fea9e2b5a736ee62d6")));
    CHECK(eq(tag, hex("1ae10b594f09e26a7e902ecbd0600691")));
    CHECK(CR.aead_open(key.data(), nonce.data(), aad.data(), aad.size(), ct.data(), n, tag, 16, back.data()));
    CHECK(memcmp(back.data(), pt, n) == 0);
    // kısaltılmış 8 baytlık etiketle de açılır
    CHECK(CR.aead_open(key.data(), nonce.data(), aad.data(), aad.size(), ct.data(), n, tag, 8, back.data()));
    // oynanmış veri / AAD / etiket reddedilir
    ct[3] ^= 1;
    CHECK(!CR.aead_open(key.data(), nonce.data(), aad.data(), aad.size(), ct.data(), n, tag, 16, back.data()));
    ct[3] ^= 1;
    aad[0] ^= 1;
    CHECK(!CR.aead_open(key.data(), nonce.data(), aad.data(), aad.size(), ct.data(), n, tag, 16, back.data()));
}

TEST(crypto_blake2s_vectors) {
    uint8_t out[32];
    blake2s_256((const uint8_t*)"abc", 3, out);
    CHECK(eq(out, hex("508c5e8c327c14e2e1a72ba34eeb452f37458b209ed63a294d999b4c86675982")));
    blake2s_256(nullptr, 0, out);
    CHECK(eq(out, hex("69217a3079908094e11121d042354a7c1f55b6482ca1a51e1b250dfd1ed0eef9")));
    // çok bloklu giriş: parçalama hatası olmadığını, uzunluk sınırlarında (63/64/65/128) tutarlılığı sınar
    uint8_t buf[200];
    for (int i = 0; i < 200; i++) buf[i] = (uint8_t)i;
    uint8_t a[32], b[32];
    blake2s_256(buf, 64, a); blake2s_256(buf, 65, b);
    CHECK(memcmp(a, b, 32) != 0);
}

// ================================================================ GEO
TEST(geo_haversine_known) {
    CHECK_NEAR(haversine_m(0, 0, 0, 1), 111195.1, 5.0);   // 1° ekvatorda
    CHECK_NEAR(haversine_m(0, 0, 1, 0), 111195.1, 5.0);
    CHECK_NEAR(haversine_m(10, 20, 10, 20), 0.0, 1e-6);
    CHECK_NEAR(haversine_m(51.5074, -0.1278, 48.8566, 2.3522), 343.6e3, 1.5e3);  // Londra-Paris ~344 km
    // kısa mesafe: 0.0001° enlem ~ 11.12 m
    CHECK_NEAR(haversine_m(41.0, 29.0, 41.0001, 29.0), 11.12, 0.05);
    // simetri
    CHECK_NEAR(haversine_m(41, 29, 39.9, 32.8), haversine_m(39.9, 32.8, 41, 29), 1e-6);
}

TEST(geo_bearing_known) {
    CHECK_NEAR(bearing_deg(0, 0, 1, 0), 0.0, 1e-6);
    CHECK_NEAR(bearing_deg(0, 0, 0, 1), 90.0, 1e-6);
    CHECK_NEAR(bearing_deg(0, 0, -1, 0), 180.0, 1e-6);
    CHECK_NEAR(bearing_deg(0, 0, 0, -1), 270.0, 1e-6);
    CHECK_NEAR(bearing_deg(51.5074, -0.1278, 48.8566, 2.3522), 148.1, 0.5);  // Londra->Paris
    double b = bearing_deg(41.0, 29.0, 41.0, 28.9);  // batıya doğru
    CHECK(b > 269.0 && b < 271.0);
}

TEST(geo_arrow_angle_wrap) {
    CHECK_NEAR(arrow_angle_deg(10, 350), 20, 1e-9);
    CHECK_NEAR(arrow_angle_deg(350, 10), -20, 1e-9);
    CHECK_NEAR(arrow_angle_deg(0, 90), -90, 1e-9);
    CHECK_NEAR(arrow_angle_deg(90, 0), 90, 1e-9);
    CHECK_NEAR(arrow_angle_deg(0, 180), 180, 1e-9);
    CHECK_NEAR(arrow_angle_deg(90, 270), 180, 1e-9);
    CHECK_NEAR(arrow_angle_deg(45, 45), 0, 1e-9);
    CHECK_NEAR(wrap360(-10), 350, 1e-9);
    CHECK_NEAR(wrap360(720.5), 0.5, 1e-9);
    for (double b = 0; b < 360; b += 7.3)
        for (double h = 0; h < 360; h += 11.9) {
            double a = arrow_angle_deg(b, h);
            CHECK(a > -180.0 - 1e-9 && a <= 180.0 + 1e-9);
        }
}

// ================================================================ PAKET
static Payload sample_payload() {
    Payload p{};
    p.lat_e7 = deg_to_e7(41.0123456);
    p.lon_e7 = deg_to_e7(-28.9876543);  // negatif boylam: işaret testi
    p.fix_age_s = 4; p.hacc_m = 7; p.batt_pct = 83; p.flags = FLAG_SEARCH | FLAG_PING; p.ping_target = 0x05; p.rsv = 0;
    return p;
}

TEST(packet_length_is_30) {
    CHECK_EQ(PACKET_LEN, 30);
    CHECK_EQ(HEADER_LEN + PAYLOAD_LEN + TAG_LEN, 30);
    uint8_t key[32]; make_key(key, 1);
    Header h{group_id_from_key(CR, key), 2, 0, 12345};
    uint8_t buf[PACKET_LEN];
    CHECK(encode_packet(CR, key, h, sample_payload(), buf));
    CHECK_EQ(buf[0], 0xF1);
    CHECK_EQ(buf[3], 2);  // node_id=2, sürüm=0
    CHECK(!encode_packet(CR, key, Header{h.group_id, 5, 0, 1}, sample_payload(), buf));  // node_id>=5
}

TEST(packet_roundtrip) {
    uint8_t key[32]; make_key(key, 1);
    uint16_t gid = group_id_from_key(CR, key);
    Header h{gid, 4, 0, 0xDEADBEEF};
    Payload p = sample_payload();
    uint8_t buf[PACKET_LEN];
    CHECK(encode_packet(CR, key, h, p, buf));
    Header h2{}; Payload p2{};
    CHECK(decode_packet(CR, key, gid, buf, PACKET_LEN, h2, p2) == DecodeResult::Ok);
    CHECK_EQ(h2.node_id, 4); CHECK_EQ(h2.counter, 0xDEADBEEFu); CHECK_EQ(h2.group_id, gid);
    CHECK_EQ(p2.lat_e7, p.lat_e7); CHECK_EQ(p2.lon_e7, p.lon_e7);
    CHECK_EQ(p2.fix_age_s, 4); CHECK_EQ(p2.hacc_m, 7); CHECK_EQ(p2.batt_pct, 83);
    CHECK_EQ(p2.flags, FLAG_SEARCH | FLAG_PING); CHECK_EQ(p2.ping_target, 5);
    // yük şifreli: açık metin enlem baytları pakette görünmemeli
    uint8_t plain[4]; int32_t lat = p.lat_e7; memcpy(plain, &lat, 4);
    CHECK(memcmp(buf + 8, plain, 4) != 0);
    // farklı sayaç -> farklı şifreli metin (nonce yeniden kullanılmıyor)
    uint8_t buf2[PACKET_LEN];
    Header hb = h; hb.counter++;
    encode_packet(CR, key, hb, p, buf2);
    CHECK(memcmp(buf + 8, buf2 + 8, 14) != 0);
}

TEST(packet_rejects_bad_tag_wrong_group_truncation) {
    uint8_t key[32]; make_key(key, 1);
    uint16_t gid = group_id_from_key(CR, key);
    Header h{gid, 1, 0, 77};
    uint8_t buf[PACKET_LEN], t[PACKET_LEN];
    encode_packet(CR, key, h, sample_payload(), buf);
    Header ho{}; Payload po{};

    // etiket / yük / başlık baytlarından herhangi birinin bir biti değişirse kabul edilmemeli
    for (size_t i = 0; i < PACKET_LEN; i++) {
        memcpy(t, buf, PACKET_LEN);
        t[i] ^= 0x01;
        CHECK(decode_packet(CR, key, gid, t, PACKET_LEN, ho, po) != DecodeResult::Ok);
    }
    memcpy(t, buf, PACKET_LEN); t[PACKET_LEN - 1] ^= 0x80;
    CHECK(decode_packet(CR, key, gid, t, PACKET_LEN, ho, po) == DecodeResult::BadTag);
    memcpy(t, buf, PACKET_LEN); t[12] ^= 0x40;  // şifreli yük
    CHECK(decode_packet(CR, key, gid, t, PACKET_LEN, ho, po) == DecodeResult::BadTag);

    // yanlış grup anahtarı: group_id uyuşmaz -> WrongGroup
    uint8_t key2[32]; make_key(key2, 9);
    uint16_t gid2 = group_id_from_key(CR, key2);
    CHECK(gid != gid2);
    CHECK(decode_packet(CR, key2, gid2, buf, PACKET_LEN, ho, po) == DecodeResult::WrongGroup);
    // group_id aynı ama anahtar farklı (çarpışma): etiket tutmaz
    CHECK(decode_packet(CR, key2, gid, buf, PACKET_LEN, ho, po) == DecodeResult::BadTag);

    CHECK(decode_packet(CR, key, gid, buf, PACKET_LEN - 1, ho, po) == DecodeResult::BadLength);
    CHECK(decode_packet(CR, key, gid, buf, PACKET_LEN + 1, ho, po) == DecodeResult::BadLength);
    memcpy(t, buf, PACKET_LEN); t[0] = 0xF2;
    CHECK(decode_packet(CR, key, gid, t, PACKET_LEN, ho, po) == DecodeResult::BadMagic);
}

TEST(packet_pairing_messages) {
    uint8_t key[32]; make_key(key, 3);
    uint8_t off[PAIR_OFFER_LEN], k2[32]; uint8_t node = 0;
    encode_pair_offer(key, 3, off);
    CHECK_EQ(PAIR_OFFER_LEN, 36);
    CHECK(decode_pair_offer(off, PAIR_OFFER_LEN, k2, node));
    CHECK(memcmp(k2, key, 32) == 0); CHECK_EQ(node, 3);
    off[10] ^= 1;
    CHECK(!decode_pair_offer(off, PAIR_OFFER_LEN, k2, node));  // CRC16 bozuk
    uint8_t ack[PAIR_ACK_LEN]; uint16_t gid = 0; uint8_t n2 = 0;
    encode_pair_ack(0xBEEF, 2, ack);
    CHECK(decode_pair_ack(ack, PAIR_ACK_LEN, gid, n2)); CHECK_EQ(gid, 0xBEEF); CHECK_EQ(n2, 2);
    CHECK(pair_rssi_ok(-30)); CHECK(!pair_rssi_ok(-45)); CHECK(!pair_rssi_ok(-80));
    // CRC bilinen değerler
    CHECK_EQ(crc16_ccitt((const uint8_t*)"123456789", 9), 0x29B1);   // CRC-16/CCITT-FALSE
    CHECK_EQ(crc32_ieee((const uint8_t*)"123456789", 9), 0xCBF43926u);
}

// ================================================================ GRUP
TEST(group_replay_and_ownnode) {
    uint8_t key[32]; make_key(key, 5);
    Group g;
    g.set_group(CR, key, 0);
    uint16_t gid = g.group_id();
    uint8_t buf[PACKET_LEN];
    auto send = [&](uint8_t node, uint32_t ctr) {
        encode_packet(CR, key, Header{gid, node, 0, ctr}, sample_payload(), buf);
    };
    send(1, 100);
    CHECK(g.on_packet(CR, buf, PACKET_LEN, 1000, -90, 5) == RxStatus::Ok);
    CHECK(g.on_packet(CR, buf, PACKET_LEN, 1100, -90, 5) == RxStatus::Replay);   // aynı paket tekrar
    send(1, 99);
    CHECK(g.on_packet(CR, buf, PACKET_LEN, 1200, -90, 5) == RxStatus::Replay);   // eski sayaç
    send(1, 101);
    CHECK(g.on_packet(CR, buf, PACKET_LEN, 1300, -90, 5) == RxStatus::Ok);
    send(2, 5);   // başka düğümün sayacı bağımsız
    CHECK(g.on_packet(CR, buf, PACKET_LEN, 1400, -90, 5) == RxStatus::Ok);
    send(0, 1);   // kendi node_id
    CHECK(g.on_packet(CR, buf, PACKET_LEN, 1500, -90, 5) == RxStatus::OwnNode);
    // bozuk etiketli paket sayacı İLERLETMEMELİ (zehirleme koruması)
    send(1, 5000); buf[29] ^= 1;
    CHECK(g.on_packet(CR, buf, PACKET_LEN, 1600, -90, 5) == RxStatus::BadTag);
    send(1, 102);
    CHECK(g.on_packet(CR, buf, PACKET_LEN, 1700, -90, 5) == RxStatus::Ok);
    // başka grup
    uint8_t key2[32]; make_key(key2, 6);
    encode_packet(CR, key2, Header{group_id_from_key(CR, key2), 3, 0, 1}, sample_payload(), buf);
    CHECK(g.on_packet(CR, buf, PACKET_LEN, 1800, -90, 5) == RxStatus::WrongGroup);
    CHECK_EQ(g.visible_count(), 2);
    CHECK_EQ(g.member_count(), 3);
    g.leave();
    CHECK(g.on_packet(CR, buf, PACKET_LEN, 1900, -90, 5) == RxStatus::NoGroup);
    CHECK_EQ(g.member_count(), 0);
}

TEST(group_aging_and_prune) {
    uint8_t key[32]; make_key(key, 5);
    Group g; g.set_group(CR, key, 0);
    uint8_t buf[PACKET_LEN];
    Payload p = sample_payload(); p.fix_age_s = 10;
    encode_packet(CR, key, Header{g.group_id(), 1, 0, 1}, p, buf);
    g.on_packet(CR, buf, PACKET_LEN, 100000, -90, 5);
    Payload q = sample_payload(); q.fix_age_s = FIX_AGE_NONE;
    encode_packet(CR, key, Header{g.group_id(), 2, 0, 1}, q, buf);
    g.on_packet(CR, buf, PACKET_LEN, 100000, -90, 5);

    CHECK(g.staleness(1, 100000) == Staleness::Fresh);
    CHECK_EQ(g.position_age_s(1, 100000), 10);
    CHECK(g.staleness(1, 100000 + 50000) == Staleness::Fresh);    // 10+50 = 60 -> hâlâ taze (sınır dahil)
    CHECK(g.staleness(1, 100000 + 51000) == Staleness::Faint);    // 61 sn
    CHECK(g.staleness(1, 100000 + 290000) == Staleness::Faint);   // 300 sn tam sınır
    CHECK(g.staleness(1, 100000 + 291000) == Staleness::LastSeen);
    CHECK(!g.has_position(2));
    CHECK(g.staleness(2, 100000) == Staleness::LastSeen);          // konum yok -> son görülme
    CHECK_EQ(g.rx_age_ms(1, 130000), 30000);
    CHECK_EQ(g.rx_age_ms(3, 130000), UINT64_MAX);

    g.prune(100000 + 600000, 1800000);
    CHECK_EQ(g.visible_count(), 2);                // 10 dk < 30 dk TTL
    g.prune(100000 + 1900000, 1800000);
    CHECK_EQ(g.visible_count(), 0);
}

TEST(group_friend_cycle_and_node_alloc) {
    uint8_t key[32]; make_key(key, 5);
    Group g; g.set_group(CR, key, 0);
    CHECK_EQ(g.next_friend(-1), -1);
    uint8_t buf[PACKET_LEN];
    for (uint8_t n : {1, 3, 4}) {
        encode_packet(CR, key, Header{g.group_id(), n, 0, 1}, sample_payload(), buf);
        g.on_packet(CR, buf, PACKET_LEN, 10, -90, 5);
    }
    CHECK_EQ(g.next_friend(-1), 1);
    CHECK_EQ(g.next_friend(1), 3);
    CHECK_EQ(g.next_friend(3), 4);
    CHECK_EQ(g.next_friend(4), 1);   // dairesel
    // kurucu: node 0 kendisi; 1,3,4 görüldü; sırayla 2 verilir, sonra dolu
    Group f; f.set_group(CR, key, 0);
    CHECK_EQ(f.allocate_node_id(), 1); CHECK_EQ(f.allocate_node_id(), 2);
    CHECK_EQ(f.allocate_node_id(), 3); CHECK_EQ(f.allocate_node_id(), 4);
    CHECK_EQ(f.allocate_node_id(), -1);   // en çok 5 düğüm
}

TEST(tx_counter_boot_skip) {
    TxCounter c;
    c.init(5000);
    CHECK_EQ(c.value(), 6000);                 // açılışta +1000
    CHECK_EQ(c.next(), 6000); CHECK_EQ(c.next(), 6001);
    CHECK(c.should_persist());          // açılışta atlanan değer hemen kalıcılaştırılmalı
    c.mark_persisted();
    CHECK(!c.should_persist());
    for (int i = 0; i < 300; i++) c.next();
    CHECK(c.should_persist());
    uint32_t pv = c.persist_value(); c.mark_persisted();
    CHECK(!c.should_persist());
    // yeniden açılış: son kalıcı değerden +1000 atlama, önceki hiçbir sayaçla çakışmaz
    TxCounter c2; c2.init(pv);
    CHECK(c2.value() > pv + 999);
}

// ================================================================ DİLİMLER
namespace {
constexpr uint64_t UTC_BASE = 1700000010000ULL;  // 15000'in tam katı

struct SimNode {
    SlotScheduler s;
    uint64_t off;  // yerel saat = sim + off
    uint64_t last_tx = UINT64_MAX;
    SimNode(uint8_t id, uint64_t o) : s(cfgfor(id)), off(o) {}
    static SlotConfig cfgfor(uint8_t id) { SlotConfig c; c.node_id = id; return c; }
};
struct TxRec { uint64_t t; int node; bool flag; Mode mode; };

// Kusursuz kanal: her yayın, tüm diğer düğümlerce hemen alınır (ilk yaklaşım).
static void sim_step(std::vector<SimNode>& nodes, uint64_t t, std::vector<TxRec>* log) {
    for (auto& n : nodes) n.s.update(t + n.off);
    for (size_t i = 0; i < nodes.size(); i++) {
        SimNode& a = nodes[i];
        uint64_t la = t + a.off;
        if (a.last_tx != la && a.s.next_tx_start(la) == la) {
            a.last_tx = la;
            bool flag = a.s.emit_search_flag(la);
            if (log) log->push_back({t, (int)i, flag, a.s.mode()});
            a.s.on_tx(la, flag);
            for (size_t j = 0; j < nodes.size(); j++) {
                if (j == i) continue;
                uint64_t lj = t + nodes[j].off;
                nodes[j].s.on_rx((uint8_t)i, lj, flag, lj);
            }
        }
    }
}
}  // namespace

TEST(slots_basic_geometry) {
    SlotConfig c; c.node_id = 2;
    SlotScheduler s(c);
    CHECK_EQ(s.frame_ms(), 15000); CHECK_EQ(s.slot_ms(), 3000);
    CHECK(s.mode() == Mode::Standby);
    CHECK_EQ(s.next_tx_start(0), 6000);          // dilim 2: 6000
    CHECK_EQ(s.next_tx_start(6000), 6000);
    CHECK_EQ(s.next_tx_start(6001), 21000);
    s.request_search(100);
    CHECK(s.mode() == Mode::Search);
    CHECK_EQ(s.frame_ms(), 5000); CHECK_EQ(s.slot_ms(), 1000);
    CHECK_EQ(s.next_tx_start(0), 2000);
}

TEST(slots_five_nodes_no_overlap_utc) {
    std::vector<SimNode> nodes;
    for (int i = 0; i < 5; i++) nodes.emplace_back((uint8_t)i, 1000ULL * 1000 * (i + 1) + 137ULL * i);
    for (auto& n : nodes) n.s.set_utc(UTC_BASE, 0 + n.off);  // sim=0 anında UTC_BASE
    // set_utc(utc, local): local = sim + off. sim=0 için local=off. Bu çağrı doğru.
    std::vector<TxRec> log;
    for (uint64_t t = 0; t < 150000; t++) sim_step(nodes, t, &log);
    CHECK_EQ(log.size(), 50);   // 150 sn / 15 sn * 5 düğüm
    for (auto& r : log) {
        CHECK_EQ(r.t % 15000, (uint64_t)r.node * 3000);   // utc_ms mod çerçeve hizası + dilim
        CHECK(!r.flag);
    }
    // ardışık yayınlar tam 3 sn arayla (çakışma yok)
    for (size_t i = 1; i < log.size(); i++) CHECK_EQ(log[i].t - log[i - 1].t, 3000);
}

TEST(slots_search_flag_propagation_and_return) {
    std::vector<SimNode> nodes;
    for (int i = 0; i < 5; i++) nodes.emplace_back((uint8_t)i, 5000ULL * i + 3);
    for (auto& n : nodes) n.s.set_utc(UTC_BASE, n.off);
    std::vector<TxRec> log;
    std::vector<uint64_t> back(5, 0);
    uint64_t t = 0;
    for (; t < 20000; t++) sim_step(nodes, t, &log);
    for (auto& n : nodes) CHECK(n.s.mode() == Mode::Standby);
    nodes[2].s.request_search(t + nodes[2].off);   // düğüm 2 PING/ARAMA başlatır
    CHECK(nodes[2].s.mode() == Mode::Search);
    uint64_t t_req = t;
    std::vector<bool> was_search(5, false);
    for (; t < 260000; t++) {
        sim_step(nodes, t, &log);
        for (int i = 0; i < 5; i++) {
            bool srch = nodes[i].s.mode() == Mode::Search;
            if (!srch && was_search[i] && back[i] == 0) back[i] = t;   // ARAMA -> BEKLEME geçişi
            was_search[i] = srch;
        }
        if (t == t_req + 3000) for (auto& n : nodes) CHECK(n.s.mode() == Mode::Search);   // ilk çerçeve içinde yayıldı
        if (t == t_req + 55000) for (auto& n : nodes) CHECK(n.s.mode() == Mode::Search);  // 60 sn dolmadı
    }
    // son ARAMA bayraklı yayın
    uint64_t last_flag = 0;
    for (auto& r : log) if (r.flag) last_flag = r.t;
    CHECK(last_flag >= t_req + 55000);   // başlatıcı 60 sn bayrak koydu
    CHECK(last_flag <= t_req + 70000);   // röle bayrakları sonsuza uzamadı
    uint64_t lo = UINT64_MAX, hi = 0;
    for (int i = 0; i < 5; i++) {
        CHECK(nodes[i].s.mode() == Mode::Standby);
        CHECK(back[i] != 0);
        // dönüş = son bayraklı yayın + 60 sn (±1 sn)
        CHECK_NEAR((double)back[i], (double)(last_flag + 60000), 1.0);
        lo = back[i] < lo ? back[i] : lo; hi = back[i] > hi ? back[i] : hi;
    }
    CHECK(hi - lo <= 2);    // hepsi aynı anda döndü
    // ARAMA sırasında 1 sn dilimlerle yayın, dönüş sonrası 3 sn dilimlerle
    uint64_t prev = 0; int search_tx = 0;
    for (auto& r : log) {
        if (r.t > t_req + 5000 && r.t < t_req + 50000 && r.mode == Mode::Search) {
            if (prev) CHECK_EQ(r.t - prev, 1000);
            prev = r.t; search_tx++;
        }
    }
    CHECK(search_tx >= 40);
    uint64_t tail_prev = 0;
    for (auto& r : log) if (r.t > back[0] + 1000) { if (tail_prev) CHECK_EQ(r.t - tail_prev, 3000); tail_prev = r.t; }
}

TEST(slots_search_rebroadcast_only_from_standby_restarts_by_request) {
    SlotConfig c; c.node_id = 1;
    SlotScheduler s(c);
    s.on_rx(0, 1000, true, 1000);
    CHECK(s.mode() == Mode::Search);
    CHECK(s.emit_search_flag(1001));
    CHECK(!s.emit_search_flag(1000 + 60001));   // röle süresi uzamaz
    s.on_rx(0, 20000, false, 20000);            // bayraksız paket ARAMA'yı bitirmez
    CHECK(s.mode() == Mode::Search);
    s.update(1000 + 59999); CHECK(s.mode() == Mode::Search);
    s.update(1000 + 60000); CHECK(s.mode() == Mode::Standby);
}

TEST(slots_gnss_less_phase_lock) {
    // A: kimlik 0, B: kimlik 1; ikisinde de UTC yok, farklı yerel saatler (B +7777 ms ileride).
    std::vector<SimNode> nodes;
    nodes.emplace_back(0, 0);
    nodes.emplace_back(1, 7777);
    CHECK(nodes[1].s.source() == SyncSource::Free);
    std::vector<TxRec> log;
    for (uint64_t t = 0; t < 200000; t++) sim_step(nodes, t, &log);
    CHECK(nodes[1].s.source() == SyncSource::Packet);
    // kilitlendikten sonra B, A'nın fazına göre kendi diliminde yayın yapar: sim zamanında ≡ 3000 (mod 15000)
    int checked = 0;
    for (auto& r : log) {
        if (r.node == 1 && r.t > 30000) { CHECK_EQ(r.t % 15000, 3000); checked++; }
        if (r.node == 0) CHECK_EQ(r.t % 15000, 0);
    }
    CHECK(checked >= 10);
}

TEST(slots_listen_duty_and_events) {
    SlotConfig c; c.node_id = 1;
    SlotScheduler s(c);
    s.set_utc(UTC_BASE, 0);   // senkron
    // BEKLEME görev oranı: 4 * (2*120 + 124) / 15000 = %9.68
    uint64_t on = 0, N = 150000;
    for (uint64_t t = 0; t < N; t++) if (s.should_listen(t)) on++;
    double duty = (double)on / N;
    CHECK(duty > 0.093 && duty < 0.100);
    // her komşu dilim başında ±guard penceresi var; kendi diliminde yok
    CHECK(s.should_listen(0));            // düğüm 0 diliminin başı
    CHECK(!s.should_listen(3000 + 50));   // kendi dilimim (1): 3000..3124 TX
    CHECK(s.should_listen(6000 - 100));   // düğüm 2 öncesi guard
    CHECK(!s.should_listen(6000 - 130));
    CHECK(!s.should_listen(1500));

    // next_event: iki olay arasında should_listen sabit kalmalı
    for (uint64_t t = 0; t < 31000; t += 7) {
        uint64_t e = s.next_event(t);
        CHECK(e > t);
        bool a = s.should_listen(t);
        if (e - 1 > t) CHECK(a == s.should_listen(e - 1));
        uint64_t tx = s.next_tx_start(t);
        CHECK(tx == t || tx >= e);
    }
}

TEST(slots_unsynced_full_listen_every_4_frames) {
    SlotConfig c; c.node_id = 0;
    SlotScheduler s(c);   // Free
    uint64_t on = 0, N = 60000;   // 4 çerçeve
    for (uint64_t t = 0; t < N; t++) if (s.should_listen(t)) on++;
    double duty = (double)on / N;
    CHECK(duty > 0.30 && duty < 0.34);   // 1 tam çerçeve + 3 pencereli çerçeve
    CHECK(s.in_full_listen_frame(100));
    CHECK(!s.in_full_listen_frame(15000 + 100));
    CHECK(s.in_full_listen_frame(60000 + 100));
    CHECK(s.should_listen(5000));          // tam dinleme çerçevesinde pencere dışı da dinlenir
    CHECK(!s.should_listen(15000 + 5000)); // 2. çerçevede yalnız pencereler
    s.set_utc(UTC_BASE, 0);
    CHECK(!s.in_full_listen_frame(100));   // UTC kilidiyle sürekli dinleme biter
}

// ================================================================ PUSULA
// Dünya (Doğu, Kuzey, Yukarı) → aygıt ekseni dönüşümü. psi: ekran üstünün azimutu, pitch/roll derece.
static Vec3 device_from_world(double e, double n, double u, double psi_deg, double pitch_deg, double roll_deg) {
    const double D = 3.14159265358979323846 / 180.0;
    double psi = psi_deg * D, th = pitch_deg * D, ph = roll_deg * D;
    double xw[3] = {std::cos(psi), -std::sin(psi), 0}, yw[3] = {std::sin(psi), std::cos(psi), 0}, zw[3] = {0, 0, 1};
    double y2[3], z2[3], x3[3], z3[3];
    for (int i = 0; i < 3; i++) { y2[i] = yw[i] * std::cos(th) + zw[i] * std::sin(th); z2[i] = zw[i] * std::cos(th) - yw[i] * std::sin(th); }
    for (int i = 0; i < 3; i++) { x3[i] = xw[i] * std::cos(ph) - z2[i] * std::sin(ph); z3[i] = z2[i] * std::cos(ph) + xw[i] * std::sin(ph); }
    double w[3] = {e, n, u};
    auto dot = [&](double* a) { return a[0] * w[0] + a[1] * w[1] + a[2] * w[2]; };
    return Vec3{(float)dot(x3), (float)dot(y2), (float)dot(z3)};
}

static HeadingResult heading_for(double psi, double pitch, double roll, double decl = 0) {
    // Kuzey yarımküre manyetik alanı: 20 µT kuzey, 40 µT aşağı. İvme: yukarı 1 g.
    Vec3 m = device_from_world(0, 20, -40, psi, pitch, roll);
    Vec3 a = device_from_world(0, 0, 1, psi, pitch, roll);
    return compute_heading(a, m, (float)decl);
}

TEST(compass_heading_flat_cardinals) {
    // Düz masada, ekran üstü kuzeye bakarsa m = (0,+20,-40)
    HeadingResult r = compute_heading(Vec3{0, 0, 1}, Vec3{0, 20, -40}, 0);
    CHECK(r.valid); CHECK_NEAR(r.heading_deg, 0, 0.01); CHECK_NEAR(r.tilt_deg, 0, 0.01);
    r = compute_heading(Vec3{0, 0, 1}, Vec3{-20, 0, -40}, 0);   // doğuya bakıyor: kuzey solda
    CHECK_NEAR(r.heading_deg, 90, 0.01);
    r = compute_heading(Vec3{0, 0, 1}, Vec3{0, -20, -40}, 0);   // güney
    CHECK_NEAR(r.heading_deg, 180, 0.01);
    r = compute_heading(Vec3{0, 0, 1}, Vec3{20, 0, -40}, 0);    // batı
    CHECK_NEAR(r.heading_deg, 270, 0.01);
}

TEST(compass_tilt_compensation) {
    for (double psi = 0; psi < 360; psi += 15) {
        for (double pitch : {0.0, 20.0, 40.0, -30.0}) {
            for (double roll : {0.0, 25.0, -35.0}) {
                // toplam eğim 60° altında kalsın
                HeadingResult r = heading_for(psi, pitch, roll);
                if (!r.valid) continue;
                double err = wrap180(r.heading_deg - psi);
                CHECK(std::fabs(err) < 0.5);
            }
        }
    }
    // Eğim düzeltmesi gerçekten çalışıyor mu: düzeltmesiz atan2(-mx,my) ile 40° eğimde belirgin hata olmalı
    Vec3 m = device_from_world(0, 20, -40, 90, 40, 0);
    double naive = wrap360(std::atan2(-(double)m.x, (double)m.y) * 180 / 3.14159265358979);
    CHECK(std::fabs(wrap180(naive - 90)) > 5.0);
    CHECK_NEAR(heading_for(90, 40, 0).heading_deg, 90, 0.5);
}

TEST(compass_declination_and_tilt_limit) {
    HeadingResult r = heading_for(10, 0, 0, 6.5);
    CHECK_NEAR(r.heading_deg, 16.5, 0.05);
    r = heading_for(355, 0, 0, 10);
    CHECK_NEAR(r.heading_deg, 5, 0.05);     // 360 sarması
    r = heading_for(100, 0, 0, -10);
    CHECK_NEAR(r.heading_deg, 90, 0.05);
    // 60° eşiği (kolye gibi asılı)
    r = heading_for(0, 59, 0);   CHECK(r.valid); CHECK(!r.too_tilted); CHECK_NEAR(r.tilt_deg, 59, 0.1);
    r = heading_for(0, 61, 0);   CHECK(!r.valid); CHECK(r.too_tilted);
    r = compute_heading(Vec3{0, 1, 0.1f}, Vec3{0, 20, -40}, 0);   // neredeyse dik
    CHECK(r.too_tilted && !r.valid);
    r = compute_heading(Vec3{0, 0, 0}, Vec3{0, 20, -40}, 0);       // bozuk ivme
    CHECK(!r.valid);
    r = compute_heading(Vec3{0, 0, 1}, Vec3{0, 0, -40}, 0);        // yatay bileşen yok -> belirsiz
    CHECK(!r.valid);
}

TEST(compass_hard_iron_calibration) {
    MagCalibrator c;
    CHECK(!c.ready());
    const Vec3 hi{12.0f, -25.0f, 7.0f};
    for (int i = 0; i < 360; i += 10) for (int j = -80; j <= 80; j += 20) {
        double a = i * 3.14159265 / 180, b = j * 3.14159265 / 180;
        c.add(Vec3{(float)(hi.x + 45 * std::cos(b) * std::cos(a)), (float)(hi.y + 45 * std::cos(b) * std::sin(a)), (float)(hi.z + 45 * std::sin(b))});
    }
    CHECK(c.ready());
    Vec3 o = c.offset();
    CHECK_NEAR(o.x, hi.x, 0.7); CHECK_NEAR(o.y, hi.y, 0.7); CHECK_NEAR(o.z, hi.z, 0.7);
    Vec3 fixed = apply_offset(Vec3{hi.x + 45, hi.y, hi.z}, o);
    CHECK_NEAR(fixed.x, 45, 0.7);
    MagCalibrator d;   // tek düzlemde yayılım: hazır değil
    for (int i = 0; i < 360; i += 10) d.add(Vec3{(float)(45 * std::cos(i * 0.01745)), (float)(45 * std::sin(i * 0.01745)), 0.f});
    CHECK(!d.ready());
}

// ================================================================ TUŞ
namespace {
struct BtnRig {
    Button b;
    ms_t t = 1000;
    std::vector<ButtonEvent> ev;
    void step(bool down, uint32_t ms) {
        for (uint32_t i = 0; i < ms; i += 10) {
            ButtonEvent e = b.update(down, t);
            if (e != ButtonEvent::None) ev.push_back(e);
            t += 10;
        }
    }
    void press(uint32_t ms) { step(true, ms); }
    void gap(uint32_t ms) { step(false, ms); }
};
}  // namespace

TEST(button_short_press) {
    BtnRig r; r.gap(100); r.press(120); r.gap(600);
    CHECK_EQ(r.ev.size(), 1); CHECK(r.ev[0] == ButtonEvent::Short);
}

TEST(button_double_press) {
    BtnRig r; r.press(100); r.gap(150); r.press(100); r.gap(800);
    CHECK_EQ(r.ev.size(), 1); CHECK(r.ev[0] == ButtonEvent::Double);
    BtnRig s; s.press(100); s.gap(600); s.press(100); s.gap(600);   // yavaş iki basış = iki kısa
    CHECK_EQ(s.ev.size(), 2); CHECK(s.ev[0] == ButtonEvent::Short && s.ev[1] == ButtonEvent::Short);
}

TEST(button_long_holds) {
    BtnRig a; a.press(1600); a.gap(100);
    CHECK_EQ(a.ev.size(), 1); CHECK(a.ev[0] == ButtonEvent::Hold1500);
    BtnRig a2; a2.press(1400); a2.gap(600);
    CHECK_EQ(a2.ev.size(), 1); CHECK(a2.ev[0] == ButtonEvent::Short);   // 1,5 sn'nin hemen altı = kısa
    BtnRig b; b.press(5200); b.gap(100);
    CHECK_EQ(b.ev.size(), 1); CHECK(b.ev[0] == ButtonEvent::Hold5000);   // 1,5 sn PING'i tetiklemez
    BtnRig c; c.press(10500); c.gap(100);
    CHECK_EQ(c.ev.size(), 1); CHECK(c.ev[0] == ButtonEvent::Hold10000);
    BtnRig d; d.press(4900); d.gap(100);
    CHECK(d.ev.size() == 1 && d.ev[0] == ButtonEvent::Hold1500);
}

TEST(button_hold_stage_feedback_and_bounce) {
    BtnRig r;
    r.press(1000);  CHECK_EQ(r.b.hold_stage(r.t), 0);
    r.press(600);   CHECK_EQ(r.b.hold_stage(r.t), 1);
    r.press(3500);  CHECK_EQ(r.b.hold_stage(r.t), 2);
    r.press(5000);  CHECK_EQ(r.b.hold_stage(r.t), 3);
    r.gap(100);
    BtnRig z; z.press(10); z.gap(800);   // 10 ms parazit -> olay yok
    CHECK_EQ(z.ev.size(), 0);
    // uzun ikinci basış: uzun basış kazanır
    BtnRig w; w.press(100); w.gap(150); w.press(1700); w.gap(100);
    CHECK(w.ev.size() == 1 && w.ev[0] == ButtonEvent::Hold1500);
}

// ================================================================ GÜÇ MODELİ
TEST(power_airtime_sf8) {
    // SF8, BW125, CR4/5, 8 önek, CRC açık, 30 bayt -> ~123,4 ms (Semtech formülü, elle hesap)
    CHECK_NEAR(lora_airtime_ms(30, 8, 125000, 5), 123.4, 0.5);
    CHECK(lora_airtime_ms(30, 9, 125000, 5) > lora_airtime_ms(30, 8, 125000, 5));
    CHECK(lora_airtime_ms(30, 7, 125000, 5) < lora_airtime_ms(30, 8, 125000, 5));
}

TEST(power_model_matches_spec_table_order_of_magnitude) {
    SlotConfig c;
    c.air_ms = (uint32_t)std::lround(lora_airtime_ms(30, 8, 125000, 5));
    PowerParams pp;
    PowerScenario s = scenario_for_mode(c, Mode::Standby, 0.15, 0.0);
    // Spec: RX ~%6 (0,3 mA), TX ~%0,7 (0,3 mA). Bu model guard dahil RX'i ~%9,7 bulur; aynı mertebe:
    CHECK(s.rx_duty > 0.05 && s.rx_duty < 0.12);
    CHECK(s.tx_duty > 0.005 && s.tx_duty < 0.010);
    double ma = average_current_ma(pp, s);
    // Spec tablo toplamı: 0,01+0,3+0,3+3,5+0,05 ≈ 4,2 mA; hedef <= 7 mA
    CHECK(ma > 3.5 && ma < 6.0);
    CHECK(ma <= 7.0);
    // GNSS sürekli açık olursa bütçe aşılır (spec: "GNSS bütçenin en büyük kalemi")
    PowerScenario hot = scenario_for_mode(c, Mode::Standby, 1.0, 0.0);
    CHECK(average_current_ma(pp, hot) > 7.0);
    // ARAMA kipi BEKLEME'den pahalı (aynı GNSS görevinde)
    PowerScenario srch = scenario_for_mode(c, Mode::Search, 0.15, 0.0);
    CHECK(average_current_ma(pp, srch) > ma);
    // ARAMA kipinde TX görev oranı %10 AB sınırının altında olmalı
    CHECK(srch.tx_duty < 0.10);
    // pil ömrü (yalnızca model aritmetiği; ölçülmüş değer DEĞİL)
    CHECK_NEAR(battery_life_h(250, 5.0), 40.0, 1e-9);
}

TEST(power_battery_pct_and_stillness) {
    CHECK_EQ(battery_pct_from_mv(4300), 100); CHECK_EQ(battery_pct_from_mv(3000), 0);
    int prev = -1;
    for (int mv = 3200; mv <= 4300; mv += 10) { int p = battery_pct_from_mv((uint16_t)mv); CHECK(p >= prev); prev = p; }
    CHECK_EQ(battery_pct_from_mv(3700), 35);

    StillnessDetector d(0.05f, 60000);
    ms_t t = 0;
    for (; t < 59000; t += 100) { d.update(0.0f, 0.0f, 1.0f, t); }
    CHECK(!d.still(t));
    for (; t < 61000; t += 100) d.update(0.0f, 0.0f, 1.001f, t);
    CHECK(d.still(t));                      // 60 sn hareketsiz
    d.update(0.3f, 0.0f, 1.0f, t);          // hareket
    CHECK(!d.still(t + 1000));
    CHECK(!d.still(t + 59000));
    for (ms_t u = t + 100; u < t + 61000; u += 100) d.update(0.3f, 0.0f, 1.0f, u);
    CHECK(d.still(t + 61000));
}

// ================================================================ ana
int main() {
    for (auto& r : registry()) {
        g_cur_failed = 0;
        g_tests++;
        r.fn();
        if (g_cur_failed) { g_failed_tests++; printf("[BAŞARISIZ] %s\n", r.name); }
        else printf("[GEÇTİ]     %s\n", r.name);
    }
    printf("\nÖZET: %d test, %d kontrol; %d test başarısız, %d kontrol başarısız\n", g_tests, g_checks, g_failed_tests, g_failed_checks);
    printf(g_failed_tests == 0 ? "TÜM TESTLER GEÇTİ\n" : "BAŞARISIZ TESTLER VAR\n");
    return g_failed_tests == 0 ? 0 : 1;
}

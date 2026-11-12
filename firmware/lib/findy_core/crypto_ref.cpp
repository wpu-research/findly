#include "crypto_ref.h"
#include <cstring>

namespace findy {

static inline uint32_t rotl32(uint32_t v, int c) { return (v << c) | (v >> (32 - c)); }
static inline uint32_t rotr32(uint32_t v, int c) { return (v >> c) | (v << (32 - c)); }
static inline uint32_t ld32(const uint8_t* p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}
static inline void st32(uint8_t* p, uint32_t v) {
    p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8); p[2] = (uint8_t)(v >> 16); p[3] = (uint8_t)(v >> 24);
}
static inline void st64(uint8_t* p, uint64_t v) { st32(p, (uint32_t)v); st32(p + 4, (uint32_t)(v >> 32)); }

// ---------------------------------------------------------------- ChaCha20
#define QR(a, b, c, d)                       \
    a += b; d ^= a; d = rotl32(d, 16);       \
    c += d; b ^= c; b = rotl32(b, 12);       \
    a += b; d ^= a; d = rotl32(d, 8);        \
    c += d; b ^= c; b = rotl32(b, 7);

void chacha20_block(const uint8_t key[32], uint32_t counter, const uint8_t nonce[12], uint8_t out[64]) {
    uint32_t s[16], x[16];
    s[0] = 0x61707865; s[1] = 0x3320646e; s[2] = 0x79622d32; s[3] = 0x6b206574;
    for (int i = 0; i < 8; i++) s[4 + i] = ld32(key + 4 * i);
    s[12] = counter;
    for (int i = 0; i < 3; i++) s[13 + i] = ld32(nonce + 4 * i);
    memcpy(x, s, sizeof(s));
    for (int i = 0; i < 10; i++) {
        QR(x[0], x[4], x[8], x[12]) QR(x[1], x[5], x[9], x[13])
        QR(x[2], x[6], x[10], x[14]) QR(x[3], x[7], x[11], x[15])
        QR(x[0], x[5], x[10], x[15]) QR(x[1], x[6], x[11], x[12])
        QR(x[2], x[7], x[8], x[13]) QR(x[3], x[4], x[9], x[14])
    }
    for (int i = 0; i < 16; i++) st32(out + 4 * i, x[i] + s[i]);
}

static void chacha20_xor(const uint8_t key[32], uint32_t counter, const uint8_t nonce[12],
                         const uint8_t* in, size_t len, uint8_t* out) {
    uint8_t block[64];
    while (len > 0) {
        chacha20_block(key, counter++, nonce, block);
        size_t n = len < 64 ? len : 64;
        for (size_t i = 0; i < n; i++) out[i] = in[i] ^ block[i];
        in += n; out += n; len -= n;
    }
}

// ---------------------------------------------------------------- Poly1305 (donna-32 tarzı, 26 bit uzuvlar)
struct Poly {
    uint32_t r[5], h[5], pad[4];
    uint8_t buf[16];
    size_t leftover;
};

static void poly_init(Poly& c, const uint8_t key[32]) {
    c.r[0] = (ld32(key + 0)) & 0x3ffffff;
    c.r[1] = (ld32(key + 3) >> 2) & 0x3ffff03;
    c.r[2] = (ld32(key + 6) >> 4) & 0x3ffc0ff;
    c.r[3] = (ld32(key + 9) >> 6) & 0x3f03fff;
    c.r[4] = (ld32(key + 12) >> 8) & 0x00fffff;
    for (int i = 0; i < 5; i++) c.h[i] = 0;
    for (int i = 0; i < 4; i++) c.pad[i] = ld32(key + 16 + 4 * i);
    c.leftover = 0;
}

static void poly_blocks(Poly& c, const uint8_t* m, size_t bytes, uint32_t hibit) {
    const uint32_t r0 = c.r[0], r1 = c.r[1], r2 = c.r[2], r3 = c.r[3], r4 = c.r[4];
    const uint32_t s1 = r1 * 5, s2 = r2 * 5, s3 = r3 * 5, s4 = r4 * 5;
    uint32_t h0 = c.h[0], h1 = c.h[1], h2 = c.h[2], h3 = c.h[3], h4 = c.h[4];
    while (bytes >= 16) {
        h0 += (ld32(m + 0)) & 0x3ffffff;
        h1 += (ld32(m + 3) >> 2) & 0x3ffffff;
        h2 += (ld32(m + 6) >> 4) & 0x3ffffff;
        h3 += (ld32(m + 9) >> 6) & 0x3ffffff;
        h4 += (ld32(m + 12) >> 8) | hibit;
        uint64_t d0 = (uint64_t)h0 * r0 + (uint64_t)h1 * s4 + (uint64_t)h2 * s3 + (uint64_t)h3 * s2 + (uint64_t)h4 * s1;
        uint64_t d1 = (uint64_t)h0 * r1 + (uint64_t)h1 * r0 + (uint64_t)h2 * s4 + (uint64_t)h3 * s3 + (uint64_t)h4 * s2;
        uint64_t d2 = (uint64_t)h0 * r2 + (uint64_t)h1 * r1 + (uint64_t)h2 * r0 + (uint64_t)h3 * s4 + (uint64_t)h4 * s3;
        uint64_t d3 = (uint64_t)h0 * r3 + (uint64_t)h1 * r2 + (uint64_t)h2 * r1 + (uint64_t)h3 * r0 + (uint64_t)h4 * s4;
        uint64_t d4 = (uint64_t)h0 * r4 + (uint64_t)h1 * r3 + (uint64_t)h2 * r2 + (uint64_t)h3 * r1 + (uint64_t)h4 * r0;
        uint32_t cc;
        cc = (uint32_t)(d0 >> 26); h0 = (uint32_t)d0 & 0x3ffffff;
        d1 += cc; cc = (uint32_t)(d1 >> 26); h1 = (uint32_t)d1 & 0x3ffffff;
        d2 += cc; cc = (uint32_t)(d2 >> 26); h2 = (uint32_t)d2 & 0x3ffffff;
        d3 += cc; cc = (uint32_t)(d3 >> 26); h3 = (uint32_t)d3 & 0x3ffffff;
        d4 += cc; cc = (uint32_t)(d4 >> 26); h4 = (uint32_t)d4 & 0x3ffffff;
        h0 += cc * 5; cc = h0 >> 26; h0 &= 0x3ffffff;
        h1 += cc;
        m += 16; bytes -= 16;
    }
    c.h[0] = h0; c.h[1] = h1; c.h[2] = h2; c.h[3] = h3; c.h[4] = h4;
}

static void poly_update(Poly& c, const uint8_t* m, size_t bytes) {
    if (c.leftover) {
        size_t want = 16 - c.leftover;
        if (want > bytes) want = bytes;
        memcpy(c.buf + c.leftover, m, want);
        m += want; bytes -= want; c.leftover += want;
        if (c.leftover < 16) return;
        poly_blocks(c, c.buf, 16, 1u << 24);
        c.leftover = 0;
    }
    if (bytes >= 16) {
        size_t full = bytes & ~(size_t)15;
        poly_blocks(c, m, full, 1u << 24);
        m += full; bytes -= full;
    }
    if (bytes) { memcpy(c.buf, m, bytes); c.leftover = bytes; }
}

static void poly_finish(Poly& c, uint8_t mac[16]) {
    if (c.leftover) {
        c.buf[c.leftover] = 1;
        for (size_t i = c.leftover + 1; i < 16; i++) c.buf[i] = 0;
        poly_blocks(c, c.buf, 16, 0);
    }
    uint32_t h0 = c.h[0], h1 = c.h[1], h2 = c.h[2], h3 = c.h[3], h4 = c.h[4], cc;
    cc = h1 >> 26; h1 &= 0x3ffffff;
    h2 += cc; cc = h2 >> 26; h2 &= 0x3ffffff;
    h3 += cc; cc = h3 >> 26; h3 &= 0x3ffffff;
    h4 += cc; cc = h4 >> 26; h4 &= 0x3ffffff;
    h0 += cc * 5; cc = h0 >> 26; h0 &= 0x3ffffff;
    h1 += cc;
    uint32_t g0 = h0 + 5; cc = g0 >> 26; g0 &= 0x3ffffff;
    uint32_t g1 = h1 + cc; cc = g1 >> 26; g1 &= 0x3ffffff;
    uint32_t g2 = h2 + cc; cc = g2 >> 26; g2 &= 0x3ffffff;
    uint32_t g3 = h3 + cc; cc = g3 >> 26; g3 &= 0x3ffffff;
    uint32_t g4 = h4 + cc - (1u << 26);
    uint32_t mask = (g4 >> 31) - 1;
    g0 &= mask; g1 &= mask; g2 &= mask; g3 &= mask; g4 &= mask;
    mask = ~mask;
    h0 = (h0 & mask) | g0; h1 = (h1 & mask) | g1; h2 = (h2 & mask) | g2;
    h3 = (h3 & mask) | g3; h4 = (h4 & mask) | g4;
    h0 = (h0 | (h1 << 26));
    h1 = ((h1 >> 6) | (h2 << 20));
    h2 = ((h2 >> 12) | (h3 << 14));
    h3 = ((h3 >> 18) | (h4 << 8));
    uint64_t f;
    f = (uint64_t)h0 + c.pad[0]; h0 = (uint32_t)f;
    f = (uint64_t)h1 + c.pad[1] + (f >> 32); h1 = (uint32_t)f;
    f = (uint64_t)h2 + c.pad[2] + (f >> 32); h2 = (uint32_t)f;
    f = (uint64_t)h3 + c.pad[3] + (f >> 32); h3 = (uint32_t)f;
    st32(mac, h0); st32(mac + 4, h1); st32(mac + 8, h2); st32(mac + 12, h3);
}

void poly1305_mac(const uint8_t key[32], const uint8_t* msg, size_t len, uint8_t tag[16]) {
    Poly c;
    poly_init(c, key);
    poly_update(c, msg, len);
    poly_finish(c, tag);
}

// ---------------------------------------------------------------- AEAD (RFC 8439 bölüm 2.8)
static void aead_tag(const uint8_t key[32], const uint8_t nonce[12],
                     const uint8_t* aad, size_t aad_len,
                     const uint8_t* ct, size_t len, uint8_t tag[16]) {
    uint8_t block[64];
    chacha20_block(key, 0, nonce, block);  // ilk 32 bayt = tek kullanımlık Poly1305 anahtarı
    Poly c;
    poly_init(c, block);
    static const uint8_t zeros[16] = {0};
    poly_update(c, aad, aad_len);
    if (aad_len % 16) poly_update(c, zeros, 16 - (aad_len % 16));
    poly_update(c, ct, len);
    if (len % 16) poly_update(c, zeros, 16 - (len % 16));
    uint8_t lens[16];
    st64(lens, (uint64_t)aad_len);
    st64(lens + 8, (uint64_t)len);
    poly_update(c, lens, 16);
    poly_finish(c, tag);
}

void RefCrypto::aead_seal(const uint8_t key[32], const uint8_t nonce[12],
                          const uint8_t* aad, size_t aad_len,
                          const uint8_t* pt, size_t len, uint8_t* ct, uint8_t tag[16]) const {
    chacha20_xor(key, 1, nonce, pt, len, ct);
    aead_tag(key, nonce, aad, aad_len, ct, len, tag);
}

bool RefCrypto::aead_open(const uint8_t key[32], const uint8_t nonce[12],
                          const uint8_t* aad, size_t aad_len,
                          const uint8_t* ct, size_t len,
                          const uint8_t* tag, size_t tag_len, uint8_t* pt) const {
    if (tag_len == 0 || tag_len > 16) return false;
    uint8_t full[16];
    aead_tag(key, nonce, aad, aad_len, ct, len, full);
    uint8_t diff = 0;
    for (size_t i = 0; i < tag_len; i++) diff |= (uint8_t)(full[i] ^ tag[i]);
    if (diff != 0) return false;
    chacha20_xor(key, 1, nonce, ct, len, pt);
    return true;
}

// ---------------------------------------------------------------- BLAKE2s-256
static const uint32_t B2S_IV[8] = {0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
                                   0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19};
static const uint8_t B2S_SIGMA[10][16] = {
    {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15},
    {14, 10, 4, 8, 9, 15, 13, 6, 1, 12, 0, 2, 11, 7, 5, 3},
    {11, 8, 12, 0, 5, 2, 15, 13, 10, 14, 3, 6, 7, 1, 9, 4},
    {7, 9, 3, 1, 13, 12, 11, 14, 2, 6, 5, 10, 4, 0, 15, 8},
    {9, 0, 5, 7, 2, 4, 10, 15, 14, 1, 11, 12, 6, 8, 3, 13},
    {2, 12, 6, 10, 0, 11, 8, 3, 4, 13, 7, 5, 15, 14, 1, 9},
    {12, 5, 1, 15, 14, 13, 4, 10, 0, 7, 6, 3, 9, 2, 8, 11},
    {13, 11, 7, 14, 12, 1, 3, 9, 5, 0, 15, 4, 8, 6, 2, 10},
    {6, 15, 14, 9, 11, 3, 0, 8, 12, 2, 13, 7, 1, 4, 10, 5},
    {10, 2, 8, 4, 7, 6, 1, 5, 15, 11, 9, 14, 3, 12, 13, 0}};

static void b2s_compress(uint32_t h[8], const uint8_t block[64], uint64_t t, bool last) {
    uint32_t m[16], v[16];
    for (int i = 0; i < 16; i++) m[i] = ld32(block + 4 * i);
    for (int i = 0; i < 8; i++) { v[i] = h[i]; v[i + 8] = B2S_IV[i]; }
    v[12] ^= (uint32_t)t;
    v[13] ^= (uint32_t)(t >> 32);
    if (last) v[14] = ~v[14];
#define G(a, b, c, d, x, y)                                  \
    v[a] = v[a] + v[b] + (x); v[d] = rotr32(v[d] ^ v[a], 16); \
    v[c] = v[c] + v[d];       v[b] = rotr32(v[b] ^ v[c], 12); \
    v[a] = v[a] + v[b] + (y); v[d] = rotr32(v[d] ^ v[a], 8);  \
    v[c] = v[c] + v[d];       v[b] = rotr32(v[b] ^ v[c], 7);
    for (int r = 0; r < 10; r++) {
        const uint8_t* s = B2S_SIGMA[r];
        G(0, 4, 8, 12, m[s[0]], m[s[1]]) G(1, 5, 9, 13, m[s[2]], m[s[3]])
        G(2, 6, 10, 14, m[s[4]], m[s[5]]) G(3, 7, 11, 15, m[s[6]], m[s[7]])
        G(0, 5, 10, 15, m[s[8]], m[s[9]]) G(1, 6, 11, 12, m[s[10]], m[s[11]])
        G(2, 7, 8, 13, m[s[12]], m[s[13]]) G(3, 4, 9, 14, m[s[14]], m[s[15]])
    }
#undef G
    for (int i = 0; i < 8; i++) h[i] ^= v[i] ^ v[i + 8];
}

void blake2s_256(const uint8_t* data, size_t len, uint8_t out[32]) {
    uint32_t h[8];
    for (int i = 0; i < 8; i++) h[i] = B2S_IV[i];
    h[0] ^= 0x01010020;  // özet uzunluğu 32, anahtarsız, fanout=depth=1
    uint64_t t = 0;
    while (len > 64) {
        t += 64;
        b2s_compress(h, data, t, false);
        data += 64; len -= 64;
    }
    uint8_t last[64];
    memset(last, 0, sizeof(last));
    if (len) memcpy(last, data, len);
    t += len;
    b2s_compress(h, last, t, true);
    for (int i = 0; i < 8; i++) st32(out + 4 * i, h[i]);
}

void RefCrypto::hash256(const uint8_t* data, size_t len, uint8_t out[32]) const {
    blake2s_256(data, len, out);
}

}  // namespace findy

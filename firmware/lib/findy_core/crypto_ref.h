// Findy çekirdek: bağımsız ChaCha20-Poly1305 (RFC 8439) ve BLAKE2s-256 referans uygulaması.
// Harici kütüphane gerektirmez; hem PC testlerinde hem hedefte kullanılabilir.
// NOT: Yan kanal (zamanlama) dayanıklılığı için özel çaba gösterilmedi, yalnızca
// etiket karşılaştırması sabit zamanlıdır. Üretim öncesi inceleme gerekir.
#pragma once
#include "crypto_iface.h"

namespace findy {

class RefCrypto : public ICrypto {
public:
    void aead_seal(const uint8_t key[32], const uint8_t nonce[12],
                   const uint8_t* aad, size_t aad_len,
                   const uint8_t* pt, size_t len,
                   uint8_t* ct, uint8_t tag[16]) const override;
    bool aead_open(const uint8_t key[32], const uint8_t nonce[12],
                   const uint8_t* aad, size_t aad_len,
                   const uint8_t* ct, size_t len,
                   const uint8_t* tag, size_t tag_len,
                   uint8_t* pt) const override;
    void hash256(const uint8_t* data, size_t len, uint8_t out[32]) const override;
};

// Test amaçlı alt işlevler (RFC 8439 vektörleriyle doğrulanır).
void chacha20_block(const uint8_t key[32], uint32_t counter, const uint8_t nonce[12], uint8_t out[64]);
void poly1305_mac(const uint8_t key[32], const uint8_t* msg, size_t len, uint8_t tag[16]);
void blake2s_256(const uint8_t* data, size_t len, uint8_t out[32]);

}  // namespace findy

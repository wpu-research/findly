// Findy çekirdek: soyut şifreleme arayüzü.
// Taşınabilir C++17; Arduino başlığı İÇERMEZ.
#pragma once
#include <cstddef>
#include <cstdint>

namespace findy {

// AEAD (ChaCha20-Poly1305, RFC 8439) + 256 bit özet (BLAKE2s-256) arayüzü.
// Hedefte crypto_port.cpp, testte RefCrypto (crypto_ref.h) bu arayüzü uygular.
class ICrypto {
public:
    virtual ~ICrypto() {}

    // ct (pt ile aynı uzunlukta) ve tam 16 baytlık etiket üretir.
    // ct == pt (yerinde şifreleme) desteklenir.
    virtual void aead_seal(const uint8_t key[32], const uint8_t nonce[12],
                           const uint8_t* aad, size_t aad_len,
                           const uint8_t* pt, size_t len,
                           uint8_t* ct, uint8_t tag[16]) const = 0;

    // Etiketin ilk tag_len baytını (<=16) sabit zamanlı karşılaştırır.
    // Doğrulama başarısızsa false döner ve pt'ye veri YAZMAZ.
    virtual bool aead_open(const uint8_t key[32], const uint8_t nonce[12],
                           const uint8_t* aad, size_t aad_len,
                           const uint8_t* ct, size_t len,
                           const uint8_t* tag, size_t tag_len,
                           uint8_t* pt) const = 0;

    virtual void hash256(const uint8_t* data, size_t len, uint8_t out[32]) const = 0;
};

}  // namespace findy

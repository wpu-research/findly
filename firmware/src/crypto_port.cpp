// Findy P0 — şifreleme bağlantı noktası. Hedefte ek kütüphane gerekmesin diye findy_core'un
// bağımsız referans uygulaması (RefCrypto) kullanılır. İleride donanım hızlandırmalı (nRF52840 CC310
// yok; nRF52840'ta CryptoCell-310 vardır ancak BSP erişimi ayrıca doğrulanmalı) bir uygulamaya geçilebilir.
#include "hw.h"
#include "nrf_soc.h"   // sd_rand_application_vector_get  (DOĞRULANACAK: Bluefruit BSP'de başlık yolu)

const findy::ICrypto& crypto() {
    static findy::RefCrypto inst;
    return inst;
}

// SoftDevice RNG'si. Bluefruit.begin() SONRASINDA çağrılmalı (SoftDevice etkin olmalı).
bool hw_random(uint8_t* out, size_t n) {
    size_t done = 0;
    while (done < n) {
        uint8_t avail = 0;
        sd_rand_application_bytes_available_get(&avail);
        if (avail == 0) { delay(1); continue; }   // havuz dolana kadar bekle
        uint8_t take = (uint8_t)((n - done) < avail ? (n - done) : avail);
        if (sd_rand_application_vector_get(out + done, take) != NRF_SUCCESS) return false;
        done += take;
    }
    return true;
}

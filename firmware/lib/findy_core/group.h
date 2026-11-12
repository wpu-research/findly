// Findy çekirdek: grup durumu — üye tablosu, tekrar (replay) koruması, yaşlandırma, sayaç.
#pragma once
#include <cstdint>
#include "crypto_iface.h"
#include "packet.h"

namespace findy {

using ms_t = uint64_t;  // donanım katmanı millis()'i 64 bite genişletir (49 gün sarmasını önler)

constexpr uint32_t COUNTER_BOOT_SKIP = 1000;   // her açılışta atlanan sayaç (spec)
constexpr uint32_t COUNTER_PERSIST_EVERY = 256;  // çalışırken bu kadar pakette bir kalıcı yaz (< 1000 olmalı)
constexpr uint32_t FAINT_AFTER_S = 60;           // konum yaşı > 60 sn → soluk
constexpr uint32_t LAST_SEEN_AFTER_S = 300;      // > 5 dk → "son görülme"

// Cihaz başına artan gönderim sayacı. Kalıcı değer + atlama ile tekrar saldırısı/nonce yeniden kullanımı önlenir.
class TxCounter {
public:
    // stored: flaşta saklı son değer. Açılışta +1000 atlanır; atlanmış değer hemen kalıcılaştırılmalı.
    void init(uint32_t stored) { value_ = stored + COUNTER_BOOT_SKIP; persisted_ = stored; }
    uint32_t value() const { return value_; }
    uint32_t next() { return value_++; }  // gönderilecek sayacı döndürür
    bool should_persist() const { return value_ - persisted_ >= COUNTER_PERSIST_EVERY; }
    uint32_t persist_value() const { return value_; }  // kalıcılaştırılacak değer
    void mark_persisted() { persisted_ = value_; }
private:
    uint32_t value_ = 0, persisted_ = 0;
};

enum class RxStatus : uint8_t {
    Ok = 0, BadLength, BadMagic, BadVersion, WrongGroup, BadTag, Replay, OwnNode, NoGroup,
};

enum class Staleness : uint8_t { Fresh, Faint, LastSeen };

struct Member {
    bool seen = false;
    bool has_counter = false;
    Payload p{};
    uint32_t last_counter = 0;
    ms_t last_rx_ms = 0;
    int16_t rssi_dbm = 0;
    int8_t snr_db = 0;
};

class Group {
public:
    bool has_group() const { return has_group_; }
    uint16_t group_id() const { return group_id_; }
    uint8_t self_node() const { return self_node_; }
    const uint8_t* key() const { return key_; }

    void set_group(const ICrypto& c, const uint8_t key[32], uint8_t self_node);
    void leave();  // gruptan çık (anahtar ve tablo silinir)

    // Paketi çöz + tekrar denetimi + tabloyu güncelle. Sayaç yalnızca ETİKET DOĞRULANDIKTAN sonra ilerler
    // (sahte paketle sayaç zehirlenemez). Kendi node_id'li paket OwnNode ile atılır.
    RxStatus on_packet(const ICrypto& c, const uint8_t* buf, size_t len, ms_t now, int rssi_dbm, int snr_db,
                       Header* hdr_out = nullptr, Payload* pl_out = nullptr);

    const Member* member(uint8_t node) const { return node < MAX_NODES ? &m_[node] : nullptr; }
    ms_t rx_age_ms(uint8_t node, ms_t now) const;
    // Konum yaşı (sn) = son alımdan beri geçen süre + paketteki fix_age_s (255 → konum yok = UINT32_MAX).
    uint32_t position_age_s(uint8_t node, ms_t now) const;
    bool has_position(uint8_t node) const;
    Staleness staleness(uint8_t node, ms_t now) const;

    int visible_count() const;       // görülen başka üye sayısı
    int member_count() const { return has_group_ ? visible_count() + 1 : 0; }  // kendimiz dahil
    void prune(ms_t now, ms_t ttl_ms);  // ttl'den eski üyeleri sil (ör. 30 dk)

    // "from"dan sonraki görülmüş üye (dairesel); from=-1 ilk üyeyi verir; yoksa -1.
    int next_friend(int from) const;
    // Kurucu için: boş node_id ata (kendimiz ve zaten atananlar hariç); dolu ise -1.
    int allocate_node_id();
    // Atanmış ama hiç görülmemiş (eşleşme zaman aşımı) node_id'yi geri ver.
    void release_node_id(uint8_t id);

private:
    bool has_group_ = false;
    uint8_t key_[32] = {0};
    uint16_t group_id_ = 0;
    uint8_t self_node_ = 0;
    uint8_t assigned_mask_ = 0;
    Member m_[MAX_NODES];
};

}  // namespace findy

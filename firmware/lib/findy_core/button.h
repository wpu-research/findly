// Findy çekirdek: tuş durum makinesi (spec bölüm 7).
// Olaylar BIRAKILIŞTA, basılı kalma süresine göre üretilir (1,5 sn'lik basış, 5 sn'lik basışın parçası
// olarak yanlışlıkla PING üretmesin diye). Basılıyken ilerleme halkası için hold_stage() kullanılır.
#pragma once
#include <cstdint>
#include "group.h"  // ms_t

namespace findy {

enum class ButtonEvent : uint8_t {
    None = 0,
    Short,      // kısa bas: uyandır / sonraki arkadaş
    Double,     // çift bas: DURUM
    Hold1500,   // 1,5-5 sn: PING
    Hold5000,   // 5-10 sn: EŞLEŞME
    Hold10000,  // >= 10 sn: gruptan çık
};

struct ButtonTimes {
    uint32_t debounce_ms = 30;
    uint32_t double_gap_ms = 400;  // ilk kısa basıştan sonra ikinciyi bekleme penceresi
    uint32_t t_ping_ms = 1500;
    uint32_t t_pair_ms = 5000;
    uint32_t t_leave_ms = 10000;
};

class Button {
public:
    explicit Button(const ButtonTimes& t = ButtonTimes()) : t_(t) {}
    // pressed: elektriksel seviye değil, mantıksal "basılı" (donanım aktif-düşük ters çevirir).
    // Her döngüde çağrılır; bir olay en fazla bir çağrıda döner.
    ButtonEvent update(bool pressed, ms_t now);
    // Basılıyken şu anki eşik (0: eşik yok, 1: PING, 2: EŞLEŞME, 3: ÇIK) — UI geri bildirimi için.
    int hold_stage(ms_t now) const;
    bool is_down() const { return st_ == State::Down || st_ == State::Down2; }

private:
    enum class State : uint8_t { Idle, Down, WaitSecond, Down2 };
    ButtonEvent classify(uint32_t dur) const;
    ButtonTimes t_;
    State st_ = State::Idle;
    ms_t t_press_ = 0, t_release_ = 0;
};

}  // namespace findy

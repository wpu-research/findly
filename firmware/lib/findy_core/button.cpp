#include "button.h"

namespace findy {

ButtonEvent Button::classify(uint32_t d) const {
    if (d >= t_.t_leave_ms) return ButtonEvent::Hold10000;
    if (d >= t_.t_pair_ms) return ButtonEvent::Hold5000;
    if (d >= t_.t_ping_ms) return ButtonEvent::Hold1500;
    return ButtonEvent::Short;
}

int Button::hold_stage(ms_t now) const {
    if (!is_down()) return 0;
    ms_t d = now - t_press_;
    if (d >= t_.t_leave_ms) return 3;
    if (d >= t_.t_pair_ms) return 2;
    if (d >= t_.t_ping_ms) return 1;
    return 0;
}

ButtonEvent Button::update(bool pressed, ms_t now) {
    switch (st_) {
        case State::Idle:
            if (pressed) { st_ = State::Down; t_press_ = now; }
            return ButtonEvent::None;

        case State::Down:
            if (pressed) return ButtonEvent::None;
            {
                uint32_t d = (uint32_t)(now - t_press_);
                if (d < t_.debounce_ms) { st_ = State::Idle; return ButtonEvent::None; }  // parazit
                if (d < t_.t_ping_ms) { st_ = State::WaitSecond; t_release_ = now; return ButtonEvent::None; }
                st_ = State::Idle;
                return classify(d);
            }

        case State::WaitSecond:
            if (pressed) { st_ = State::Down2; t_press_ = now; return ButtonEvent::None; }
            if ((uint32_t)(now - t_release_) >= t_.double_gap_ms) { st_ = State::Idle; return ButtonEvent::Short; }
            return ButtonEvent::None;

        case State::Down2:
            if (pressed) return ButtonEvent::None;
            {
                uint32_t d = (uint32_t)(now - t_press_);
                st_ = State::Idle;
                if (d < t_.debounce_ms) return ButtonEvent::Short;  // ikinci basış parazit: ilk kısa basış geçerli
                if (d < t_.t_ping_ms) return ButtonEvent::Double;
                return classify(d);  // ikinci basış uzunsa uzun basış kazanır
            }
    }
    return ButtonEvent::None;
}

}  // namespace findy

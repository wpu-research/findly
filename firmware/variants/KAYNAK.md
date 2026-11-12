# Kart tanımı dosyalarının kaynağı

PlatformIO `nordicnrf52` platformu (11.0.0) RAK4631 kartını içermez. Aşağıdaki dosyalar
12 Kasım 2026'da RAK'ın resmî GitHub depolarından değiştirilmeden alındı.

| Dosya | Kaynak | Sürüm (commit) |
|---|---|---|
| `variants/WisCore_RAK4631_Board/variant.h`, `variant.cpp` | `RAKWireless/RAK-nRF52-Arduino`, `variants/WisCore_RAK4631_Board/` | `cc4b1bf417541ae4e4b8afb96b4f4e7ff438f355` |
| `boards/wiscore_rak4631.json` | `RAKWireless/WisBlock`, `PlatformIO/RAK4630/` | `0a611f0cbfb9ce878a03e0e6fe5c03c0e08044b0` |

`variant.h` LGPL 2.1 lisanslıdır (dosya başlığına bakın). SX1262 pinleri (`PIN_LORA_*`) bu
dosyada tanımlı değildir; `src/board_pins.h` içindeki değerler hâlâ doğrulanmayı bekliyor.

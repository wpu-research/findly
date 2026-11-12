// Findy P0 — kart pin ataması. Pinler YALNIZCA burada tanımlanır (spec bölüm 3).
// RAK4631 Arduino BSP (WisCore_RAK4631_Board) variant.h sembolik adları kullanılır.
// DERLENMEDİ/DOĞRULANMADI: BSP'de bu adların varlığı ve değerleri donanım gelince kontrol edilecek.
#pragma once
#include <Arduino.h>

// ---- Ekran (GC9A01 yuvarlak TFT, WisBlock IO yuvası SPI'ı) ---------------------------------
// SCK/MOSI: BSP varsayılan `SPI` nesnesi (PIN_SPI_SCK / PIN_SPI_MOSI). MISO kullanılmaz.
// DOĞRULANACAK: BSP'de `SPI`nin WisBlock IO yuvası SPI'ına bağlı olduğu varsayılıyor.
#ifdef WB_SPI_CS
  #define FINDY_PIN_TFT_CS   WB_SPI_CS
#else
  #define FINDY_PIN_TFT_CS   PIN_SPI_SS   // DOĞRULANACAK: WB_SPI_CS adı BSP'de yoksa yedek
#endif
#define FINDY_PIN_TFT_DC     WB_IO3
#define FINDY_PIN_TFT_RST    WB_IO4
#define FINDY_PIN_TFT_BL     WB_IO5       // PWM; modülde sürücü transistör yoksa N-MOSFET gerekir

// ---- Titreşim motoru, tuş, güç -------------------------------------------------------------
#define FINDY_PIN_VIBRA      WB_IO6       // N-MOSFET + ters diyot
#define FINDY_PIN_BUTTON     WB_SW1       // aktif düşük, dahili pull-up (RAK4631'de WB_SW1 harici/çekirdek tuşu olabilir: DOĞRULANACAK)
#define FINDY_PIN_GNSS_PWR   WB_IO2       // 3V3_S anahtarı + GNSS RESET. Açılışta YÜKSEK sürülür ve çalışırken KESİLMEZ (H1/H3).
#define FINDY_PIN_GNSS_PPS   WB_IO1       // Yuva A'daki RAK12500'ün 1PPS çıkışı. v0'da okunmuyor; başka işe KULLANMA (H2).
// WB_IO5/WB_IO6 = P0.09/P0.10, nRF52840 NFC pinleri: GPIO olarak çalışması için NFC kapalı olmalı
// (platformio.ini'de CONFIG_NFCT_PINS_AS_GPIOS). İlk donanım testinde doğrulanacak (H5).
#define FINDY_PIN_BATT_ADC   WB_A0        // taban kartındaki bölücü üzerinden

// ---- I2C1 (`Wire`) -------------------------------------------------------------------------
// GNSS 0x42, LSM303AGR ivme 0x19 / manyeto 0x1E. Spec "I2C1" der; RAK BSP'de `Wire` = I2C1 varsayıldı (DOĞRULANACAK).
#define FINDY_I2C            Wire
#define FINDY_I2C_ADDR_GNSS  0x42
#define FINDY_I2C_ADDR_ACC   0x19
#define FINDY_I2C_ADDR_MAG   0x1E

// ---- SX1262 (RAK4631 modül içi) ------------------------------------------------------------
// DOĞRULANACAK: Aşağıdaki sayılar RAK4630/4631 için yayımlanmış SX126x örneklerinden HATIRLANAN
// değerlerdir; kesin kaynak RAK4631 variant.h / modül veri sayfasıdır. BSP bu makroları tanımlıyorsa
// onlar kullanılır.
#ifndef PIN_LORA_NSS
  #define PIN_LORA_NSS    42
#endif
#ifndef PIN_LORA_SCLK
  #define PIN_LORA_SCLK   43
#endif
#ifndef PIN_LORA_MOSI
  #define PIN_LORA_MOSI   44
#endif
#ifndef PIN_LORA_MISO
  #define PIN_LORA_MISO   45
#endif
#ifndef PIN_LORA_BUSY
  #define PIN_LORA_BUSY   46
#endif
#ifndef PIN_LORA_DIO_1
  #define PIN_LORA_DIO_1  47
#endif
#ifndef PIN_LORA_RESET
  #define PIN_LORA_RESET  38
#endif
// TCXO DIO3'ten 1,8 V, RF anahtarı DIO2'den (spec bölüm 3 notu). Gerilim DOĞRULANACAK.
#define FINDY_LORA_TCXO_V        1.8f
#define FINDY_LORA_DIO2_RFSW     true

// ---- Sensör eksen eşlemesi -----------------------------------------------------------------
// findy_core eksen düzeni: x = ekranın sağı, y = ekranın üstü, z = ekrandan kullanıcıya.
// Sensörün karta/kasaya montajı ve LSM303AGR'nin ivme/manyeto eksen farkları bilinmiyor.
// DOĞRULANACAK: Her eksen için {kaynak eksen 0..2, işaret ±1}. Tezgâhta kalibre edilecek.
#define FINDY_ACC_MAP_X  {0, +1}
#define FINDY_ACC_MAP_Y  {1, +1}
#define FINDY_ACC_MAP_Z  {2, +1}
#define FINDY_MAG_MAP_X  {0, +1}
#define FINDY_MAG_MAP_Y  {1, +1}
#define FINDY_MAG_MAP_Z  {2, +1}

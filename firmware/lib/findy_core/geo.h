// Findy çekirdek: coğrafi hesaplar (haversine, bearing, ok açısı).
#pragma once
#include <cstdint>

namespace findy {

constexpr double EARTH_RADIUS_M = 6371008.8;  // ortalama yarıçap (küre modeli; yüzlerce metrede hata ihmal edilebilir)

double wrap360(double deg);  // [0, 360)
double wrap180(double deg);  // (-180, 180]

// İki nokta arası büyük daire mesafesi (metre).
double haversine_m(double lat1_deg, double lon1_deg, double lat2_deg, double lon2_deg);

// (1)'den (2)'ye büyük daire başlangıç açısı, kuzeyden saat yönünde, [0,360).
double bearing_deg(double lat1_deg, double lon1_deg, double lat2_deg, double lon2_deg);

// Ekrandaki ok açısı = bearing - heading, (-180, 180]; 0 = ekranın üstü (12 yönü), + = saat yönü.
double arrow_angle_deg(double bearing_deg_v, double heading_deg_v);

inline double e7_to_deg(int32_t v) { return (double)v / 1e7; }
int32_t deg_to_e7(double deg);

}  // namespace findy

// Findy çekirdek: eğim düzeltmeli pusula başı ve hard-iron kalibrasyon matematiği.
//
// Aygıt eksen düzeni (donanım katmanı sensör eksenlerini BU düzene çevirir):
//   x = ekranın sağı, y = ekranın üstü (saat 12 yönü), z = ekrandan kullanıcıya doğru.
// İvmeölçer durağan haldeyken "yukarı" yönünü gösterir (düz masada yüzü yukarı: a = (0,0,+g)).
#pragma once
#include <cstdint>

namespace findy {

struct Vec3 { float x, y, z; };

constexpr float TILT_HIDE_DEG = 60.0f;  // eğim bundan büyükse ok gizlenir

struct HeadingResult {
    bool valid;        // false: ivme/manyeto bozuk ya da eğim eşiği aşıldı
    bool too_tilted;   // eğim > 60°
    float tilt_deg;    // z ekseni ile "yukarı" arasındaki açı
    float heading_deg; // ekran üstünün (y) gerçek kuzeyden saat yönü açısı [0,360); declination eklenmiş
};

// accel: ivmeölçer (herhangi ölçek), mag: kalibre edilmiş manyeto (µT), declination: doğu pozitif.
HeadingResult compute_heading(const Vec3& accel, const Vec3& mag, float declination_deg);

// Hard-iron: "8 çiz" sırasında min/max tutar, ofset = (min+max)/2.
class MagCalibrator {
public:
    void reset();
    void add(const Vec3& m);
    bool ready(float min_span_ut = 40.0f) const;  // her eksende yayılım >= min_span (yaklaşık, deneyle ayarlanacak)
    Vec3 offset() const;
    int samples() const { return n_; }
private:
    Vec3 mn_{0, 0, 0}, mx_{0, 0, 0};
    int n_ = 0;
};

inline Vec3 apply_offset(const Vec3& m, const Vec3& o) { return Vec3{m.x - o.x, m.y - o.y, m.z - o.z}; }

}  // namespace findy

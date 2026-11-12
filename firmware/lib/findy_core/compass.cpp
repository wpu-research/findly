#include "compass.h"
#include "geo.h"
#include <cmath>

namespace findy {

static Vec3 cross(const Vec3& a, const Vec3& b) {
    return Vec3{a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x};
}
static float norm(const Vec3& a) { return std::sqrt(a.x * a.x + a.y * a.y + a.z * a.z); }

HeadingResult compute_heading(const Vec3& a, const Vec3& m, float declination_deg) {
    HeadingResult r{false, false, 0.f, 0.f};
    float na = norm(a), nm = norm(m);
    if (na < 1e-6f || nm < 1e-6f) return r;
    r.tilt_deg = std::acos(std::fmax(-1.f, std::fmin(1.f, a.z / na))) * 180.f / 3.14159265f;
    if (r.tilt_deg > TILT_HIDE_DEG) { r.too_tilted = true; return r; }

    // Doğu = m × a ; Kuzey = a × Doğu (a ≈ yukarı). (Kuzey yarımkürede m'nin kuzey bileşeni pozitif.)
    Vec3 east = cross(m, a);
    float ne = norm(east);
    if (ne < 1e-6f) return r;  // manyeto ile ivme paralel: yön belirsiz
    east = Vec3{east.x / ne, east.y / ne, east.z / ne};
    Vec3 north = cross(a, east);
    float nn = norm(north);
    north = Vec3{north.x / nn, north.y / nn, north.z / nn};

    // Ekran üstü ekseni y = (0,1,0): kuzey/doğu bileşenleri
    double h = std::atan2((double)east.y, (double)north.y) * 180.0 / 3.14159265358979323846;
    r.heading_deg = (float)wrap360(h + declination_deg);
    r.valid = true;
    return r;
}

void MagCalibrator::reset() { n_ = 0; mn_ = mx_ = Vec3{0, 0, 0}; }

void MagCalibrator::add(const Vec3& m) {
    if (n_ == 0) { mn_ = mx_ = m; }
    else {
        mn_.x = std::fmin(mn_.x, m.x); mn_.y = std::fmin(mn_.y, m.y); mn_.z = std::fmin(mn_.z, m.z);
        mx_.x = std::fmax(mx_.x, m.x); mx_.y = std::fmax(mx_.y, m.y); mx_.z = std::fmax(mx_.z, m.z);
    }
    n_++;
}

bool MagCalibrator::ready(float s) const {
    return n_ > 0 && (mx_.x - mn_.x) >= s && (mx_.y - mn_.y) >= s && (mx_.z - mn_.z) >= s;
}

Vec3 MagCalibrator::offset() const {
    return Vec3{(mn_.x + mx_.x) * 0.5f, (mn_.y + mx_.y) * 0.5f, (mn_.z + mx_.z) * 0.5f};
}

}  // namespace findy

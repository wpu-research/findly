#include "geo.h"
#include <cmath>

namespace findy {

static const double DEG2RAD = 3.14159265358979323846 / 180.0;
static const double RAD2DEG = 180.0 / 3.14159265358979323846;

double wrap360(double d) {
    d = std::fmod(d, 360.0);
    if (d < 0) d += 360.0;
    if (d >= 360.0) d = 0.0;
    return d;
}

double wrap180(double d) {
    d = wrap360(d);
    if (d > 180.0) d -= 360.0;
    return d;
}

double haversine_m(double lat1, double lon1, double lat2, double lon2) {
    double p1 = lat1 * DEG2RAD, p2 = lat2 * DEG2RAD;
    double dp = (lat2 - lat1) * DEG2RAD, dl = (lon2 - lon1) * DEG2RAD;
    double a = std::sin(dp / 2) * std::sin(dp / 2) + std::cos(p1) * std::cos(p2) * std::sin(dl / 2) * std::sin(dl / 2);
    if (a > 1.0) a = 1.0;
    return 2.0 * EARTH_RADIUS_M * std::asin(std::sqrt(a));
}

double bearing_deg(double lat1, double lon1, double lat2, double lon2) {
    double p1 = lat1 * DEG2RAD, p2 = lat2 * DEG2RAD, dl = (lon2 - lon1) * DEG2RAD;
    double y = std::sin(dl) * std::cos(p2);
    double x = std::cos(p1) * std::sin(p2) - std::sin(p1) * std::cos(p2) * std::cos(dl);
    return wrap360(std::atan2(y, x) * RAD2DEG);
}

double arrow_angle_deg(double bearing, double heading) { return wrap180(bearing - heading); }

int32_t deg_to_e7(double deg) { return (int32_t)std::llround(deg * 1e7); }

}  // namespace findy

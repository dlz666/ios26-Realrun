"""Coordinate-system conversions to WGS-84 (the datum iOS location simulation
expects).

- WGS-84: true GPS coordinates (no conversion needed).
- GCJ-02: China "Mars" coordinates, used by Google/Gaode maps in mainland China.
- BD-09:  Baidu coordinates.
"""
import math

X_PI = 3.14159265358979324 * 3000.0 / 180.0
PI = 3.1415926535897932384626433832795
A = 6378245.0  # semi-major axis
EE = 0.00669342162296594323  # eccentricity squared


def _transform_lat(x, y):
    ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * PI) + 20.0 * math.sin(2.0 * x * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(y * PI) + 40.0 * math.sin(y / 3.0 * PI)) * 2.0 / 3.0
    ret += (160.0 * math.sin(y / 12.0 * PI) + 320 * math.sin(y * PI / 30.0)) * 2.0 / 3.0
    return ret


def _transform_lng(x, y):
    ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * PI) + 20.0 * math.sin(2.0 * x * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(x * PI) + 40.0 * math.sin(x / 3.0 * PI)) * 2.0 / 3.0
    ret += (150.0 * math.sin(x / 12.0 * PI) + 300.0 * math.sin(x / 30.0 * PI)) * 2.0 / 3.0
    return ret


def _out_of_china(lng, lat):
    return not (73.66 < lng < 135.05 and 3.86 < lat < 53.55)


def gcj02_to_wgs84(lng, lat):
    if _out_of_china(lng, lat):
        return lng, lat
    dlat = _transform_lat(lng - 105.0, lat - 35.0)
    dlng = _transform_lng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * PI
    magic = math.sin(radlat)
    magic = 1 - EE * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((A * (1 - EE)) / (magic * sqrtmagic) * PI)
    dlng = (dlng * 180.0) / (A / sqrtmagic * math.cos(radlat) * PI)
    mglat = lat + dlat
    mglng = lng + dlng
    return lng * 2 - mglng, lat * 2 - mglat


def bd09_to_gcj02(bd_lng, bd_lat):
    x = bd_lng - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * X_PI)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * X_PI)
    return z * math.cos(theta), z * math.sin(theta)


def bd09_to_wgs84(bd_lng, bd_lat):
    return gcj02_to_wgs84(*bd09_to_gcj02(bd_lng, bd_lat))


def to_wgs84(lng, lat, system):
    """Convert (lng, lat) in the given source `system` to WGS-84."""
    system = (system or "wgs84").lower()
    if system == "wgs84":
        return lng, lat
    if system == "gcj02":
        return gcj02_to_wgs84(lng, lat)
    if system == "bd09":
        return bd09_to_wgs84(lng, lat)
    raise ValueError(f"unknown coordSystem: {system!r} (expected wgs84/gcj02/bd09)")

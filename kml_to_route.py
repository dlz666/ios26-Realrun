"""Convert a KML LineString export (e.g. from Google My Maps) into the route
file format used by this project: a comma-separated list of
``{"lng": "...", "lat": "..."}`` objects (the same format as HNroute.txt).

The KML's coordinates are written verbatim. Tell the program which datum they
are in via ``coordSystem`` in config.yaml (gcj02 for points traced on a normal
Google/Gaode map in mainland China, wgs84 for satellite imagery).

Usage:
    python kml_to_route.py <input.kml> <output.txt>
"""
import re
import sys


def parse_kml(kml_text):
    m = re.search(r"<coordinates>(.*?)</coordinates>", kml_text, re.S)
    if not m:
        raise ValueError("no <coordinates> element found in KML")
    points = []
    for token in m.group(1).split():
        parts = token.split(",")
        if len(parts) < 2:
            continue
        points.append((float(parts[0]), float(parts[1])))  # (lng, lat)
    return points


def drop_closing_duplicate(points):
    # the route is treated as a loop (last point wraps back to the first), so a
    # trailing point equal to the first would create a zero-length segment
    if len(points) >= 2:
        (lng0, lat0), (lngn, latn) = points[0], points[-1]
        if abs(lng0 - lngn) < 1e-7 and abs(lat0 - latn) < 1e-7:
            return points[:-1]
    return points


def format_route(points):
    return ",".join('{{"lng":"{}","lat":"{}"}}'.format(lng, lat) for lng, lat in points)


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    in_path, out_path = sys.argv[1], sys.argv[2]
    with open(in_path, encoding="utf-8") as f:
        points = drop_closing_duplicate(parse_kml(f.read()))
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(format_route(points))
    print(f"converted {len(points)} points -> {out_path}")


if __name__ == "__main__":
    main()

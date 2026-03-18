# Pobieranie i formatowanie pozycji pojazdów do wyświetlenia na mapie

from data.realtime.client import fetch_vehicle_positions
from data.db import get_connection


def _get_route_info():
    """Pobiera informacje o trasach z bazy (short_name, color, type)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.route_id, r.route_short_name, r.route_color, rt.route_type
        FROM routes r
        LEFT JOIN route_type rt ON r.route_type = rt.route_type
    """)
    route_map = {}
    for route_id, short_name, color, route_type in cur.fetchall():
        route_map[route_id] = {
            "short_name": short_name,
            "color": f"#{color}" if color else "#888888",
            "route_type": route_type,
        }
    cur.close()
    conn.close()
    return route_map


# Cache route info — it doesn't change during runtime
_route_map = None


def _ensure_route_map():
    global _route_map
    if _route_map is None:
        _route_map = _get_route_info()
    return _route_map


def get_vehicles_geojson():
    """Pobiera pozycje pojazdów i zwraca jako GeoJSON FeatureCollection."""
    positions = fetch_vehicle_positions()
    route_map = _ensure_route_map()

    features = []
    for v in positions:
        route_info = route_map.get(v["route_id"], {})
        vehicle_type = "tram" if route_info.get("route_type") == 0 else "bus"

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [v["lon"], v["lat"]],
            },
            "properties": {
                "vehicle_id": v["vehicle_id"],
                "label": v["label"],
                "route_id": v["route_id"],
                "trip_id": v["trip_id"],
                "route_short_name": route_info.get("short_name", v["route_id"]),
                "route_color": route_info.get("color", "#888888"),
                "vehicle_type": vehicle_type,
                "speed": v.get("speed"),
                "bearing": v.get("bearing"),
                "tooltip": f"{route_info.get('short_name', '?')} ({vehicle_type})",
            },
        })

    return {"type": "FeatureCollection", "features": features}

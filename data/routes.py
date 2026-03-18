# Pobieranie danych o trasach z bazy danych

import json
from data.db import get_connection


def get_routes_geojson():
    """Pobiera trasy z bazy i zwraca jako GeoJSON FeatureCollection."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            r.route_id,
            r.route_short_name,
            r.route_long_name,
            r.route_color,
            r.route_text_color,
            rt.route_type_name,
            ST_AsGeoJSON(r.geom) AS geom
        FROM routes r
        LEFT JOIN route_type rt ON r.route_type = rt.route_type
        WHERE r.geom IS NOT NULL
        ORDER BY r.route_sort_order, r.route_short_name
    """)

    features = []
    for row in cur.fetchall():
        route_id, short_name, long_name, color, text_color, type_name, geom_json = row
        features.append({
            "type": "Feature",
            "geometry": json.loads(geom_json),
            "properties": {
                "route_id": route_id,
                "route_short_name": short_name,
                "route_long_name": long_name,
                "route_color": f"#{color}" if color else "#888888",
                "route_text_color": f"#{text_color}" if text_color else "#FFFFFF",
                "route_type_name": type_name or "",
                "tooltip": f"{short_name} – {long_name}",
            },
        })

    cur.close()
    conn.close()

    return {"type": "FeatureCollection", "features": features}

# Pobieranie danych o przystankach z bazy danych

import json
from data.db import get_connection


def get_stops_geojson():
    """Pobiera przystanki z bazy i zwraca jako GeoJSON FeatureCollection."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            s.stop_id, 
            s.stop_name, 
            ST_AsGeoJSON(s.geom) as geom, 
            MIN(r.route_type) as route_type 
        FROM stops s 
        JOIN route_stops rs ON s.stop_id = rs.stop_id 
        JOIN routes r ON rs.route_id = r.route_id 
        GROUP BY s.stop_id, s.stop_name, s.geom
        HAVING s.geom IS NOT NULL
    """)

    features = []
    for row in cur.fetchall():
        stop_id, stop_name, geom_json, route_type = row
        features.append({
            "type": "Feature",
            "geometry": json.loads(geom_json),
            "properties": {
                "stop_id": stop_id,
                "stop_name": stop_name,
                "route_type": route_type,
                "tooltip": stop_name,
            },
        })

    cur.close()
    conn.close()

    return {"type": "FeatureCollection", "features": features}

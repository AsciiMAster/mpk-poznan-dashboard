# Pobieranie danych o przystankach z bazy danych

import json
from data.db import get_connection


def get_stops():
    """Pobiera przystanki z bazy danych wraz z typem transportu (bus/tram)."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            s.stop_id,
            s.stop_code,
            s.stop_name,
            s.zone_id,
            ST_Y(s.geom) AS lat,
            ST_X(s.geom) AS lon,
            CASE
                WHEN EXISTS (
                    SELECT 1 FROM route_stops rs
                    JOIN routes r ON rs.route_id = r.route_id
                    JOIN route_type rt ON r.route_type = rt.route_type
                    WHERE rs.stop_id = s.stop_id AND rt.route_type = 0
                ) THEN 'tram'
                ELSE 'bus'
            END AS stop_type
        FROM stops s
        WHERE s.geom IS NOT NULL
        ORDER BY s.stop_name
    """)

    stops = []
    for row in cur.fetchall():
        stop_id, stop_code, stop_name, zone_id, lat, lon, stop_type = row
        stops.append({
            "stop_id": str(stop_id),
            "stop_code": stop_code,
            "stop_name": stop_name,
            "zone_id": zone_id,
            "lat": float(lat),
            "lon": float(lon),
            "stop_type": stop_type,
        })

    cur.close()
    conn.close()
    return stops


def get_stop_routes(stop_id):
    """Pobiera trasy przejeżdżające przez dany przystanek."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            r.route_id,
            r.route_short_name,
            COALESCE(dir.headsign, r.route_long_name) AS route_long_name,
            r.route_color,
            rt.route_type_name
        FROM (
            SELECT DISTINCT rs.route_id
            FROM route_stops rs
            WHERE rs.stop_id = %s
        ) srs
        JOIN routes r ON srs.route_id = r.route_id
        LEFT JOIN route_type rt ON r.route_type = rt.route_type
        LEFT JOIN LATERAL (
            SELECT COALESCE(
                NULLIF(st.stop_headsign, ''),
                NULLIF(t.trip_headsign, '')
            ) AS headsign
            FROM stop_times st
            JOIN trips t ON st.trip_id = t.trip_id
            JOIN universal_calendar uc ON t.service_id = uc.service_id
            WHERE st.stop_id = %s
              AND t.route_id = r.route_id
              AND uc.date = (
                  SELECT COALESCE(
                      MAX(date) FILTER (WHERE date <= CURRENT_DATE),
                      MAX(date)
                  )
                  FROM universal_calendar
              )
            ORDER BY st.departure_time
            LIMIT 1
        ) dir ON TRUE
        ORDER BY rt.route_type_name, r.route_short_name
    """, (stop_id, stop_id))

    routes = []
    for row in cur.fetchall():
        route_id, short_name, long_name, color, type_name = row
        routes.append({
            "route_id": route_id,
            "route_short_name": short_name,
            "route_long_name": long_name,
            "route_color": f"#{color}" if color else "#888888",
            "route_type_name": type_name or "",
        })

    cur.close()
    conn.close()
    return routes

# Pobieranie rozkładu jazdy z bazy danych

from datetime import datetime
from data.db import get_connection


def get_upcoming_departures(stop_id, limit=20):
    """Pobiera nadchodzące odjazdy z danego przystanku na dziś."""
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            st.departure_time,
            st.stop_headsign,
            t.trip_id,
            t.trip_headsign,
            r.route_short_name,
            r.route_color,
            r.route_id
        FROM stop_times st
        JOIN trips t ON st.trip_id = t.trip_id
        JOIN routes r ON t.route_id = r.route_id
        JOIN universal_calendar uc ON t.service_id = uc.service_id
        WHERE st.stop_id = %s
                    AND uc.date = (
                            SELECT COALESCE(
                                    MAX(date) FILTER (WHERE date <= CURRENT_DATE),
                                    MAX(date)
                            )
                            FROM universal_calendar
                    )
          AND st.departure_time >= %s
        ORDER BY st.departure_time
        LIMIT %s
    """, (stop_id, current_time, limit))

    departures = []
    for row in cur.fetchall():
        dep_time, stop_headsign, trip_id, trip_headsign, short_name, color, route_id = row
        departures.append({
            "departure_time": str(dep_time),
            "headsign": stop_headsign or trip_headsign or "",
            "trip_id": trip_id,
            "route_short_name": short_name,
            "route_color": f"#{color}" if color else "#888888",
            "route_id": route_id,
        })

    cur.close()
    conn.close()
    return departures

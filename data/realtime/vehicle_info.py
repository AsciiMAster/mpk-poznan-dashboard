# Informacje o pojeździe — cechy z vehicle_dictionary + opóźnienie z trip_updates

from data.realtime.client import fetch_vehicle_dictionary, fetch_trip_updates

_vehicle_dict_cache = None


def _ensure_vehicle_dict():
    global _vehicle_dict_cache
    if _vehicle_dict_cache is None:
        rows = fetch_vehicle_dictionary()
        _vehicle_dict_cache = {row["vehicle"]: row for row in rows}
    return _vehicle_dict_cache


def get_vehicle_amenities(label):
    """Zwraca cechy pojazdu na podstawie numeru taborowego (label).

    Label z GTFS-RT ma format '401/2' — numer taborowy to część przed '/'.
    """
    vd = _ensure_vehicle_dict()
    key = str(label)
    if "/" in key:
        key = key.split("/")[0]
    return vd.get(key)


def get_vehicle_delay(trip_id):
    """Zwraca opóźnienie w sekundach dla danego trip_id (None jeśli brak danych)."""
    if not trip_id:
        return None
    updates = fetch_trip_updates()
    for tu in updates:
        if tu["trip_id"] == trip_id:
            for stu in tu["stop_time_updates"]:
                delay = stu["arrival_delay"] or stu["departure_delay"]
                if delay is not None:
                    return delay
    return None

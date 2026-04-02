# Callback odświeżający pozycje pojazdów na mapie

from dash import callback, Output, Input, State
from data.realtime.vehicles import get_vehicles_geojson_split


def _viewport_to_bounds(viewport, margin=1.5):
    """Przelicza viewport mapy (center+zoom) na przybliżony prostokąt geograficzny.

    margin=1.5 daje 50% zapas względem nominalnego rozmiaru widoku (ok. 1400x900px),
    żeby pojazdy nie znikały przy przewijaniu przed kolejnym odświeżeniem.
    Zwraca (south, west, north, east) lub None jeśli brak danych.
    """
    if not viewport:
        return None
    center = viewport.get("center") or []
    zoom = viewport.get("zoom", 13)
    if len(center) < 2:
        return None
    lat, lon = center[0], center[1]
    deg_per_px = 360.0 / (256 * (2 ** zoom))
    half_lon = deg_per_px * 700 * margin
    half_lat = deg_per_px * 450 * margin
    return (lat - half_lat, lon - half_lon, lat + half_lat, lon + half_lon)


@callback(
    Output("buses-layer", "data"),
    Output("trams-layer", "data"),
    Input("vehicle-interval", "n_intervals"),
    State("map", "viewport"),
)
def update_vehicles(_n, viewport):
    """Co interwał pobiera nowe pozycje pojazdów z API, filtrując do widocznego obszaru."""
    bounds = _viewport_to_bounds(viewport)
    return get_vehicles_geojson_split(bounds)

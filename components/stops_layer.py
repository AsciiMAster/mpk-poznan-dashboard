# Warstwa mapy z przystankami

import dash_leaflet as dl


def create_stops_layer(stops_geojson):
    """Tworzy klasterowaną warstwę GeoJSON z przystankami."""
    return dl.GeoJSON(
        data=stops_geojson,
        id="stops",
        cluster=True,
    )

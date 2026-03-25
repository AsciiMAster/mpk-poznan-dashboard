# Callback odświeżający pozycje pojazdów na mapie

from dash import callback, Output, Input
from data.realtime.vehicles import get_vehicles_geojson_split


@callback(
    Output("buses-layer", "data"),
    Output("trams-layer", "data"),
    Input("vehicle-interval", "n_intervals"),
)
def update_vehicles(_n):
    """Co interwał pobiera nowe pozycje pojazdów z API."""
    return get_vehicles_geojson_split()

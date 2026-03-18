# Główny layout aplikacji

from dash import html
import dash_leaflet as dl
from config import MAP_CENTER, MAP_ZOOM
from components.routes_layer import create_routes_layer
from components.stops_layer import create_stops_layer


def create_layout(stops_geojson, routes_geojson):
    """Buduje główny layout z mapą, przystankami i trasami."""
    return html.Div([
        html.H1("MPK Poznań Dashboard"),
        html.Div(
            dl.Map(
                [
                    dl.TileLayer(),
                    create_routes_layer(routes_geojson),
                    create_stops_layer(stops_geojson),
                ],
                style={
                    "width": "100%",
                    "height": "80vh",
                    "border-radius": "12px",
                    "border": "2px solid #2c2e33",
                },
                center=MAP_CENTER,
                zoom=MAP_ZOOM,
            ),
            className="map-container",
        ),
    ])

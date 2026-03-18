# Główny layout aplikacji

from dash import html, dcc
import dash_leaflet as dl
from config import MAP_CENTER, MAP_ZOOM
from components.routes_layer import create_routes_layer
from components.stops_layer import create_stops_layer
from components.vehicles_layer import create_vehicles_layer


def create_layout(stops, routes_geojson):
    """Buduje główny layout z mapą, przystankami, pojazdami i panelem info."""
    return html.Div([
        html.H1("MPK Poznań Dashboard"),
        # Interwał odświeżania pojazdów co 10 sekund
        dcc.Interval(id="vehicle-interval", interval=10_000, n_intervals=0),
        html.Div(
            [
                html.Div(
                    dl.Map(
                        [
                            dl.TileLayer(),
                            create_routes_layer(routes_geojson),
                            create_stops_layer(stops),
                            create_vehicles_layer(),
                        ],
                        style={
                            "width": "100%",
                            "height": "80vh",
                            "border-radius": "12px",
                            "border": "2px solid #2c2e33",
                        },
                        center=MAP_CENTER,
                        zoom=MAP_ZOOM,
                        id="map",
                    ),
                    className="map-wrapper",
                ),
                html.Div(
                    id="stop-info-panel",
                    className="stop-info-panel",
                ),
            ],
            className="map-container",
        ),
    ])

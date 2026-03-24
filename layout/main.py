# Główny layout aplikacji

from dash import html, dcc
import dash_leaflet as dl
from config import MAP_CENTER, MAP_ZOOM
from components.routes_layer import create_routes_layer
from components.stops_layer import create_stops_layer
from components.vehicles_layer import create_vehicles_layer

TILE_LIGHT = "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
TILE_DARK = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"


def create_layout(stops, routes_geojson):
    """Buduje główny layout z mapą, przystankami, pojazdami i panelem info."""
    return html.Div([
        # Stan motywu
        dcc.Store(id="theme-store", data="light", storage_type="local"),
        # Interwał odświeżania pojazdów co 10 sekund
        dcc.Interval(id="vehicle-interval", interval=10_000, n_intervals=0),
        # Kompaktowy nagłówek
        html.Div([
            html.H1([
                html.Span("MPK", className="accent"),
                " Poznań",
            ]),
            html.Span("Mapa komunikacji miejskiej", className="header-subtitle"),
            html.Button(
                id="theme-toggle",
                className="theme-toggle",
                n_clicks=0,
            ),
        ], className="app-header"),
        html.Div(
            [
                html.Div(
                    dl.Map(
                        [
                            dl.TileLayer(
                                id="tile-layer",
                                url=TILE_LIGHT,
                                attribution='&copy; <a href="https://carto.com/">CARTO</a>',
                            ),
                            create_routes_layer(routes_geojson),
                            create_stops_layer(stops),
                            create_vehicles_layer(),
                        ],
                        style={
                            "width": "100%",
                            "height": "100%",
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
    ], id="app-root", **{"data-theme": "light"})

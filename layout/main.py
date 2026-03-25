# Główny layout aplikacji

from dash import html, dcc
import dash_leaflet as dl
from config import MAP_CENTER, MAP_ZOOM
from components.routes_layer import create_routes_layer
from components.stops_layer import create_stops_layer
from components.vehicles_layer import create_vehicles_layers

TILE_LIGHT = "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
TILE_DARK = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"


def create_layout(stops, routes_geojson):
    """Buduje główny layout z mapą, przystankami, pojazdami i panelem info."""
    stop_options = [
        {
            "label": f"{s['stop_name']} ({s['stop_code']})" if s.get("stop_code") else s["stop_name"],
            "value": s["stop_id"],
        }
        for s in stops
    ]

    stop_coords = {
        s["stop_id"]: [s["lat"], s["lon"]]
        for s in stops
    }

    buses_layer, trams_layer = create_vehicles_layers()

    return html.Div([
        # Stan motywu
        dcc.Store(id="theme-store", data="light", storage_type="local"),
        # Zapamietany przystanek do odswiezania odjazdow w czasie rzeczywistym
        dcc.Store(id="selected-stop-store", data=None),
        # Slownik wspolrzednych przystankow do wyszukiwarki
        dcc.Store(id="stops-coords-store", data=stop_coords),
        # Interwał odświeżania pojazdów co 10 sekund
        dcc.Interval(id="vehicle-interval", interval=10_000, n_intervals=0),
        # Kompaktowy nagłówek
        html.Div([
            html.H1([
                html.Span("MPK", className="accent"),
                " Poznań",
            ]),
            html.Span("Mapa komunikacji miejskiej", className="header-subtitle"),
            dcc.Dropdown(
                id="stop-search",
                options=stop_options,
                placeholder="Szukaj przystanku...",
                clearable=True,
                className="stop-search",
            ),
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
                            dl.LayersControl(
                                [
                                    dl.Overlay(create_routes_layer(routes_geojson), name="Trasy", checked=False),
                                    dl.Overlay(create_stops_layer(stops), name="Przystanki", checked=True),
                                    dl.Overlay(buses_layer, name="Autobusy", checked=True),
                                    dl.Overlay(trams_layer, name="Tramwaje", checked=True),
                                ],
                                position="bottomleft",
                            ),
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

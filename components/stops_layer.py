# Warstwa mapy z przystankami — markery divIcon stylowane w CSS

import dash_leaflet as dl


def create_stops_layer(stops):
    """Tworzy warstwę z markerami przystanków (bez klastrowania)."""
    markers = []
    for stop in stops:
        glyph_class = (
            "stop-icon__glyph--rail-light"
            if stop["stop_type"] == "tram"
            else "stop-icon__glyph--bus"
        )
        icon_class = (
            "stop-icon stop-icon--tram"
            if stop["stop_type"] == "tram"
            else "stop-icon stop-icon--bus"
        )
        markers.append(
            dl.DivMarker(
                position=[stop["lat"], stop["lon"]],
                iconOptions={
                    "className": "stop-marker-wrapper",
                    "html": f'<div class="{icon_class}"><span class="stop-icon__glyph {glyph_class}"></span></div>',
                    "iconSize": [14, 14],
                    "iconAnchor": [9, 9],
                    "popupAnchor": [0, -9],
                },
                children=[dl.Tooltip(stop["stop_name"])],
                id={"type": "stop-marker", "stop_id": stop["stop_id"]},
                n_clicks=0,
            )
        )

    return dl.LayerGroup(markers, id="stops-layer")

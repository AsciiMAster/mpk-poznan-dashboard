# Warstwa mapy z przystankami — indywidualne markery z ikonami SVG

import dash_leaflet as dl


def create_stops_layer(stops):
    """Tworzy warstwę z markerami przystanków (bez klastrowania)."""
    markers = []
    for stop in stops:
        icon_url = (
            "/assets/icons/tram.svg"
            if stop["stop_type"] == "tram"
            else "/assets/icons/bus.svg"
        )
        markers.append(
            dl.Marker(
                position=[stop["lat"], stop["lon"]],
                icon={
                    "iconUrl": icon_url,
                    "iconSize": [24, 24],
                    "iconAnchor": [12, 12],
                },
                children=[dl.Tooltip(stop["stop_name"])],
                id={"type": "stop-marker", "stop_id": stop["stop_id"]},
                n_clicks=0,
            )
        )

    return dl.LayerGroup(markers, id="stops-layer")

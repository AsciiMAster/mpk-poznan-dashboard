# Warstwa mapy z trasami komunikacji miejskiej

import dash_leaflet as dl
from dash_extensions.javascript import assign

# Styl linii trasy — kolor pobierany z właściwości obiektu GeoJSON
_style_handle = assign("""function(feature) {
    return {
        color: feature.properties.route_color || "#888888",
        weight: 3,
        opacity: 0.8
    };
}""")


def create_routes_layer(routes_geojson):
    """Tworzy warstwę GeoJSON z trasami na mapie."""
    return dl.GeoJSON(
        data=routes_geojson,
        id="routes",
        style=_style_handle,
    )

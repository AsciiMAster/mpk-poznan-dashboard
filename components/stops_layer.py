# Warstwa mapy z przystankami

import dash_leaflet as dl
from dash_extensions.javascript import assign

_point_to_layer = assign("""function(feature, latlng, context) {
    const isTram = feature.properties.route_type === 0;
    const iconUrl = isTram ? '/assets/icons/tram.svg' : '/assets/icons/bus.svg';
    
    const icon = L.icon({
        iconUrl: iconUrl,
        iconSize: [24, 24],
        iconAnchor: [12, 12]
    });
    return L.marker(latlng, {icon: icon});
}""")

def create_stops_layer(stops_geojson):
    """Tworzy klasterowaną warstwę GeoJSON z przystankami."""
    return dl.GeoJSON(
        data=stops_geojson,
        id="stops",
        cluster=True,
        pointToLayer=_point_to_layer,
    )

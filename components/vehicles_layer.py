# Warstwa mapy z pojazdami w czasie rzeczywistym

import dash_leaflet as dl
from dash_extensions.javascript import assign

# Renderowanie markerów pojazdów — kolor z route_color, kółko z numerem linii
_point_to_layer = assign("""function(feature, latlng) {
    var props = feature.properties;
    var color = props.route_color || "#888";
    var border = "#fff";
    var delay = props.delay_sec;
    if (delay !== null && delay !== undefined) {
        if (delay > 60) {
            border = "#ef5350";
        } else if (delay < -30) {
            border = "#81d4fa";
        }
    }
    var icon = L.divIcon({
        className: "vehicle-icon",
        html: '<div style="background:' + color + ';color:#fff;font-weight:700;' +
              'font-size:11px;width:26px;height:26px;border-radius:50%;' +
              'display:flex;align-items:center;justify-content:center;' +
              'border:2px solid ' + border + ';box-shadow:0 0 4px rgba(0,0,0,0.5);">' +
              props.route_short_name + '</div>',
        iconSize: [26, 26],
        iconAnchor: [13, 13]
    });
    return L.marker(latlng, {icon: icon, zIndexOffset: 1000});
}""")

# Po kliknięciu w pojazd — zapisz properties do hideout, aby callback Dash mógł je odczytać
_on_each_feature = assign("""function(feature, layer, context) {
    var props = feature.properties;
    layer.bindTooltip(props.tooltip);
    layer.on("click", function() {
        context.setProps({hideout: feature.properties});
    });
}""")


def create_vehicle_layer(layer_id):
    """Tworzy warstwę GeoJSON dla pojazdów (dane ładowane przez callback)."""
    return dl.GeoJSON(
        id=layer_id,
        data={"type": "FeatureCollection", "features": []},
        pointToLayer=_point_to_layer,
        onEachFeature=_on_each_feature,
        hideout={},
    )


def create_vehicles_layers():
    """Tworzy osobne warstwy autobusów i tramwajów."""
    return (
        create_vehicle_layer("buses-layer"),
        create_vehicle_layer("trams-layer"),
    )

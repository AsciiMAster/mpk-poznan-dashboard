window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature) {
            return {
                color: feature.properties.route_color || "#888888",
                weight: 3,
                opacity: 0.8
            };
        },
        function1: function(feature, latlng) {
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
            return L.marker(latlng, {
                icon: icon,
                zIndexOffset: 1000
            });
        },
        function2: function(feature, layer, context) {
            var props = feature.properties;
            layer.bindTooltip(props.tooltip);
            layer.on("click", function() {
                context.setProps({
                    hideout: feature.properties
                });
            });
        }
    }
});
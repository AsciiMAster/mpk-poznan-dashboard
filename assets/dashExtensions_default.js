window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature) {
            return {
                color: feature.properties.route_color || "#888888",
                weight: 3,
                opacity: 0.8
            };
        },
        function1: function(feature, latlng, context) {
            const isTram = feature.properties.route_type === 0;
            const iconUrl = isTram ? '/assets/icons/tram.svg' : '/assets/icons/bus.svg';

            const icon = L.icon({
                iconUrl: iconUrl,
                iconSize: [24, 24],
                iconAnchor: [12, 12]
            });
            return L.marker(latlng, {
                icon: icon
            });
        }
    }
});
window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature) {
            return {
                color: feature.properties.route_color || "#888888",
                weight: 3,
                opacity: 0.8
            };
        }
    }
});
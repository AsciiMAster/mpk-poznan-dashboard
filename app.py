from dash import Dash, html
import dash_leaflet as dl
import json

app = Dash(__name__)

with open('data/stops.geojson', 'r', encoding='utf-8') as f:
    stops_geojson = json.load(f)

# dodanie tooltipów do przystanków
for feature in stops_geojson.get('features', []):
    if 'stop_name' in feature.get('properties', {}):
        feature['properties']['tooltip'] = feature['properties']['stop_name']

app.layout = html.Div([
    html.H1("MPK Poznań Dashboard"),
    html.Div(
        dl.Map(
            [
                dl.TileLayer(),
                dl.GeoJSON(
                    data=stops_geojson,
                    id="stops",
                    cluster=True
                )
            ],
            style={'width': '100%', 'height': '80vh', 'border-radius': '12px', 'border': '2px solid #2c2e33'},
            center=[52.40, 16.92],
            zoom=11
        ),
        className="map-container"
    )
])

if __name__ == '__main__':
    app.run(debug=True)

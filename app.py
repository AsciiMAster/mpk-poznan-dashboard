# Punkt wejścia aplikacji MPK Poznań Dashboard

from dash import Dash
from data.stops import get_stops_geojson
from data.routes import get_routes_geojson
from layout.main import create_layout

app = Dash(__name__)

# Pobranie danych
stops_geojson = get_stops_geojson()
routes_geojson = get_routes_geojson()

app.layout = create_layout(stops_geojson, routes_geojson)

if __name__ == "__main__":
    app.run(debug=True)

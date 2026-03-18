# Punkt wejścia aplikacji MPK Poznań Dashboard

from dash import Dash
from data.stops import get_stops
from data.routes import get_routes_geojson
from layout.main import create_layout

app = Dash(__name__)

# Pobranie danych
stops = get_stops()
routes_geojson = get_routes_geojson()

app.layout = create_layout(stops, routes_geojson)

# Rejestracja callbacków (importy wystarczą, Dash je wykryje)
import callbacks.stops  # noqa: F401, E402
import callbacks.vehicles  # noqa: F401, E402

if __name__ == "__main__":
    app.run(debug=True)

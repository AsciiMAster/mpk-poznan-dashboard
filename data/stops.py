# Pobieranie danych o przystankach z pliku GeoJSON

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent


def get_stops_geojson():
    """Wczytuje przystanki z pliku GeoJSON i dodaje tooltipy."""
    with open(DATA_DIR / "stops.geojson", "r", encoding="utf-8") as f:
        stops = json.load(f)

    for feature in stops.get("features", []):
        props = feature.get("properties", {})
        if "stop_name" in props:
            props["tooltip"] = props["stop_name"]

    return stops

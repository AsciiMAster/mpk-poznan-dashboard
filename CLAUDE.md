# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MPK Poznan Dashboard — interactive Dash (Plotly) web app visualizing public transit data for Poznan, Poland. Displays stops, routes, vehicles, and delays on a Leaflet map via `dash-leaflet`.

## Commands

```bash
# Install dependencies (uses uv, not pip)
uv sync

# Run the app (dev server with hot reload)
uv run python app.py
# App serves at http://127.0.0.1:8050

# Activate venv manually if needed
source .venv/Scripts/activate   # Windows/Git Bash
```

## Architecture

- **app.py** — Entry point. Creates the Dash app, loads GeoJSON data, defines layout with a Leaflet map.
- **config.py** — Loads `.env`, defines constants (map center, zoom, EPSG).
- **layout/** — Dash layout components (placeholder, to be built out).
- **components/** — Reusable UI components (placeholder, to be built out).
- **callbacks/** — Dash callbacks for interactivity (placeholder, to be built out).
- **data/** — Static data files. `stops.geojson` contains transit stop features. Subdirectories `data/static/` (GTFS feed, parquet) and `data/realtime/` are gitignored.
- **assets/** — Auto-served by Dash. Contains `style.css` (dark theme, Rajdhani font) and SVG icons (`bus.svg`, `tram.svg`).

## Key Details

- Python 3.14, managed with `uv` (not pip). Dependencies in `pyproject.toml`.
- Uses `dash-leaflet` for map rendering (not folium, despite it being a dependency).
- Map centered on Poznan: `[52.4064, 16.9252]`, EPSG:2180 for local projections.
- External data from ZTM Poznan API: GTFS-RT feeds (trip updates, vehicle positions) and vehicle dictionary CSV. URLs configured in `.env`.
- PostgreSQL database connection configured in `.env` (host, port, name, user, password).
- `scheme.sql` contains the database schema.
- Dark UI theme with green (#4e9040) accent color.

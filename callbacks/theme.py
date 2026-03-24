# Callback przełączania motywu jasny/ciemny

from dash import callback, Output, Input, State

TILE_LIGHT = "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
TILE_DARK = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"


@callback(
    Output("theme-store", "data"),
    Output("app-root", "data-theme"),
    Output("tile-layer", "url"),
    Output("theme-toggle", "children"),
    Input("theme-toggle", "n_clicks"),
    State("theme-store", "data"),
)
def toggle_theme(n_clicks, current_theme):
    """Przełącza motyw jasny/ciemny."""
    if n_clicks == 0 or n_clicks is None:
        # Początkowy stan — jasny
        return "light", "light", TILE_LIGHT, "\u2600\ufe0f Jasny"

    if current_theme == "light":
        return "dark", "dark", TILE_DARK, "\U0001f319 Ciemny"
    else:
        return "light", "light", TILE_LIGHT, "\u2600\ufe0f Jasny"

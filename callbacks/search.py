from dash import callback, Output, Input, State, no_update


@callback(
    Output("map", "center"),
    Output("map", "zoom"),
    Input("stop-search", "value"),
    State("stops-coords-store", "data"),
    prevent_initial_call=True,
)
def zoom_to_stop(stop_id, stop_coords):
    """Po wybraniu przystanku w wyszukiwarce centruje i przybliza mape."""
    if not stop_id or not stop_coords:
        return no_update, no_update

    coords = stop_coords.get(stop_id)
    if not coords:
        return no_update, no_update

    return coords, 16

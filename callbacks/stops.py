# Callback obsługujący panel informacyjny — kliknięcie w przystanek lub pojazd

from dash import callback, Output, Input, ALL, html, no_update, ctx
from data.stops import get_stop_routes
from data.timetable import get_upcoming_departures
from data.realtime.client import fetch_trip_updates
from data.realtime.vehicle_info import get_vehicle_amenities, get_vehicle_delay


def _format_delay(delay_sec):
    """Formatuje opóźnienie w sekundach jako element HTML."""
    if delay_sec is None:
        return []
    abs_delay = abs(delay_sec)
    minutes = abs_delay // 60
    seconds = abs_delay % 60
    if delay_sec > 0:
        text = f"+{minutes}m {seconds}s"
        cls = "delay-late"
    elif delay_sec < 0:
        text = f"-{minutes}m {seconds}s"
        cls = "delay-early"
    else:
        text = "OK"
        cls = "delay-ok"
    return [html.Span(f" {text}", className=f"delay-badge {cls}")]


def _get_delays_for_stop(stop_id):
    """Pobiera opóźnienia z trip_updates dla danego przystanku."""
    trip_updates = fetch_trip_updates()
    delays = {}
    for tu in trip_updates:
        for stu in tu["stop_time_updates"]:
            if stu["stop_id"] == str(stop_id):
                delay_sec = stu["arrival_delay"] or stu["departure_delay"] or 0
                if tu["route_id"] not in delays:
                    delays[tu["route_id"]] = delay_sec
                if tu["trip_id"] not in delays:
                    delays[tu["trip_id"]] = delay_sec
    return delays



def _build_stop_panel(stop_id):
    """Buduje panel informacyjny przystanku z trasami i rozkładem jazdy."""
    routes = get_stop_routes(stop_id)
    delays = _get_delays_for_stop(stop_id)
    departures = get_upcoming_departures(stop_id, limit=15)

    if not routes and not departures:
        return html.Div("Brak danych dla tego przystanku.", className="stop-info-empty")

    children = []

    # Sekcja tras
    if routes:
        route_items = []
        for r in routes:
            delay = delays.get(r.get("route_id"))
            route_items.append(
                html.Div(
                    [
                        html.Span(
                            r["route_short_name"],
                            className="route-badge",
                            style={"backgroundColor": r["route_color"]},
                        ),
                        html.Span(f" {r['route_long_name']}", className="route-name"),
                    ] + _format_delay(delay),
                    className="route-item",
                )
            )
        children.append(html.H3("Trasy", className="stop-info-title"))
        children.append(html.Div(route_items, className="route-list"))

    # Sekcja rozkładu jazdy
    if departures:
        dep_items = []
        for dep in departures:
            dep_time = dep["departure_time"]
            if dep_time.count(":") == 2:
                dep_time = dep_time[:5]

            trip_delay = delays.get(dep["trip_id"])

            dep_items.append(
                html.Div(
                    [
                        html.Span(dep_time, className="dep-time"),
                        html.Span(
                            dep["route_short_name"],
                            className="route-badge",
                            style={"backgroundColor": dep["route_color"]},
                        ),
                        html.Span(f" {dep['headsign']}", className="dep-headsign"),
                    ] + _format_delay(trip_delay),
                    className="dep-item",
                )
            )
        children.append(html.H3("Nadchodzące odjazdy", className="stop-info-title timetable-title"))
        children.append(html.Div(dep_items, className="timetable-list"))

    return html.Div(children)


_AMENITY_LABELS = {
    "ramp": "Rampa",
    "air_conditioner": "Klimatyzacja",
    "place_for_transp_bicycles": "Miejsce na rowery",
    "voice_announcement_sys": "Zapowiedzi głosowe",
    "ticket_machine": "Biletomat",
    "ticket_sales_by_the_driver": "Sprzedaż u kierowcy",
    "usb_charger": "Ładowarka USB",
}


def _build_vehicle_panel(feature):
    """Buduje panel informacyjny pojazdu."""
    if not feature:
        return no_update
    props = feature["properties"]

    vehicle_type = props.get("vehicle_type", "bus")
    type_label = "Tramwaj" if vehicle_type == "tram" else "Autobus"

    children = [
        html.H3(
            [
                html.Span(
                    props.get("route_short_name", "?"),
                    className="route-badge",
                    style={"backgroundColor": props.get("route_color", "#888")},
                ),
                f" {type_label}",
            ],
            className="stop-info-title",
        ),
        html.Div(f"Nr taborowy: {props.get('label', '—')}", className="vehicle-detail"),
    ]

    # Prędkość
    speed = props.get("speed")
    if speed is not None:
        children.append(
            html.Div(f"Prędkość: {speed:.0f} km/h", className="vehicle-detail")
        )

    # Opóźnienie
    delay = get_vehicle_delay(props.get("trip_id"))
    if delay is not None:
        children.append(
            html.Div(
                ["Opóźnienie: "] + _format_delay(delay),
                className="vehicle-detail",
            )
        )

    # Cechy pojazdu z vehicle_dictionary
    amenities = get_vehicle_amenities(props.get("label"))
    if amenities:
        amenity_items = []
        for key, label in _AMENITY_LABELS.items():
            val = amenities.get(key, "0")
            has_it = val == "1"
            amenity_items.append(
                html.Div(
                    [
                        html.Span(
                            "✓ " if has_it else "✗ ",
                            className="amenity-icon amenity-yes" if has_it else "amenity-icon amenity-no",
                        ),
                        label,
                    ],
                    className="amenity-item",
                )
            )
        children.append(html.H3("Wyposażenie", className="stop-info-title amenity-title"))
        children.append(html.Div(amenity_items, className="amenity-list"))

    return html.Div(children)


@callback(
    Output("stop-info-panel", "children"),
    Input({"type": "stop-marker", "stop_id": ALL}, "n_clicks"),
    Input("vehicles-layer", "hideout"),
    prevent_initial_call=True,
)
def show_info_panel(n_clicks_list, vehicle_props):
    """Panel informacyjny — reaguje na kliknięcie w przystanek lub pojazd."""
    triggered = ctx.triggered_id

    if triggered == "vehicles-layer":
        if vehicle_props:
            return _build_vehicle_panel({"properties": vehicle_props})
        return no_update

    if isinstance(triggered, dict) and triggered.get("type") == "stop-marker":
        if not any(n for n in n_clicks_list if n):
            return no_update
        return _build_stop_panel(triggered["stop_id"])

    return no_update

# Callback obsługujący panel informacyjny — kliknięcie w przystanek lub pojazd

from datetime import datetime, timedelta

from dash import callback, Output, Input, State, ALL, html, no_update, ctx
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


def _normalize_trip_id(trip_id):
    """Normalizuje trip_id (np. 1_123 -> 123), aby zwiekszyc szanse dopasowania RT."""
    if not trip_id:
        return None
    if "_" in trip_id:
        return trip_id.split("_", 1)[1]
    return trip_id


def _get_delays_for_stop(stop_id):
    """Pobiera opóźnienia RT. Preferuje dopasowanie po stop_id, a fallback po trip/route."""
    trip_updates = fetch_trip_updates()
    trip_delays = {}

    for tu in trip_updates:
        fallback_delay = None
        matched_stop_delay = None

        for stu in tu["stop_time_updates"]:
            delay_sec = stu.get("arrival_delay")
            if delay_sec is None:
                delay_sec = stu.get("departure_delay")

            if delay_sec is None:
                continue

            if fallback_delay is None:
                fallback_delay = delay_sec

            if stu.get("stop_id") == str(stop_id):
                matched_stop_delay = delay_sec
                break

        chosen_delay = matched_stop_delay if matched_stop_delay is not None else fallback_delay
        if chosen_delay is None:
            continue

        trip_id = tu.get("trip_id")
        if trip_id and trip_id not in trip_delays:
            trip_delays[trip_id] = chosen_delay
            normalized = _normalize_trip_id(trip_id)
            if normalized:
                trip_delays[normalized] = chosen_delay

    return trip_delays



def _build_stop_panel(stop_id):
    """Buduje panel informacyjny przystanku z trasami i rozkładem jazdy."""
    routes = get_stop_routes(stop_id)
    trip_delays = _get_delays_for_stop(stop_id)
    departures = get_upcoming_departures(stop_id, limit=15)

    if not routes and not departures:
        return html.Div("Brak danych dla tego przystanku.", className="stop-info-empty")

    children = []

    # Sekcja tras
    if routes:
        route_items = []
        for r in routes:
            route_items.append(
                html.Div(
                    [
                        html.Span(
                            r["route_short_name"],
                            className="route-badge",
                            style={"backgroundColor": r["route_color"]},
                        ),
                        html.Span(f" {r['route_long_name']}", className="route-name"),
                    ],
                    className="route-item",
                )
            )
        children.append(html.H3("Trasy", className="stop-info-title"))
        children.append(html.Div(route_items, className="route-list"))

    # Sekcja rozkładu jazdy
    if departures:
        dep_rows = []
        now = datetime.now()

        for dep in departures:
            dep_time_raw = dep["departure_time"]
            hh, mm, ss = [int(x) for x in dep_time_raw.split(":")[:3]]
            dep_dt = now.replace(hour=hh % 24, minute=mm, second=ss, microsecond=0)
            if hh >= 24:
                dep_dt += timedelta(days=1)

            trip_id = dep["trip_id"]
            normalized_trip = _normalize_trip_id(trip_id)
            delay_sec = None
            is_live_match = False

            if trip_id in trip_delays:
                delay_sec = trip_delays[trip_id]
                is_live_match = True
            elif normalized_trip and normalized_trip in trip_delays:
                delay_sec = trip_delays[normalized_trip]
                is_live_match = True

            effective_dt = dep_dt + timedelta(seconds=delay_sec or 0)
            eta_seconds = (effective_dt - now).total_seconds()
            if eta_seconds < -60:
                continue

            eta_minutes = max(0, int(eta_seconds // 60))
            eta_label = "zaraz" if eta_minutes == 0 else f"{eta_minutes} min"

            dep_classes = "dep-item"
            if delay_sec is not None and delay_sec >= 60:
                dep_classes += " dep-item-delayed"
            elif delay_sec is not None and delay_sec <= -60:
                dep_classes += " dep-item-early"

            dep_rows.append({
                "eta_seconds": eta_seconds,
                "route_short_name": dep["route_short_name"],
                "route_color": dep["route_color"],
                "headsign": dep["headsign"],
                "eta_label": eta_label,
                "delay_sec": delay_sec,
                "is_live_match": is_live_match,
                "classes": dep_classes,
            })

        dep_rows.sort(key=lambda row: row["eta_seconds"])

        dep_items = [
            html.Div(
                [
                    html.Span(
                        row["route_short_name"],
                        className="route-badge",
                        style={"backgroundColor": row["route_color"]},
                    ),
                    html.Span(f" {row['headsign']}", className="dep-headsign"),
                    html.Span("LIVE", className="dep-live-label") if row["is_live_match"] else None,
                    html.Span(row["eta_label"], className="dep-time-eta"),
                ] + _format_delay(row["delay_sec"]),
                className=row["classes"],
            )
            for row in dep_rows
        ]

        if dep_items:
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
    Output("selected-stop-store", "data"),
    Input({"type": "stop-marker", "stop_id": ALL}, "n_clicks"),
    Input("buses-layer", "hideout"),
    Input("trams-layer", "hideout"),
    Input("vehicle-interval", "n_intervals"),
    Input("stop-search", "value"),
    State("selected-stop-store", "data"),
    prevent_initial_call=True,
)
def show_info_panel(n_clicks_list, bus_props, tram_props, _n, searched_stop_id, selected_stop_id):
    """Panel info — klik przystanku/pojazdu + odswiezanie RT co interwal."""
    triggered = ctx.triggered_id

    if triggered in ("buses-layer", "trams-layer"):
        vehicle_props = bus_props if triggered == "buses-layer" else tram_props
        if vehicle_props:
            return _build_vehicle_panel({"properties": vehicle_props}), None
        return no_update, no_update

    if isinstance(triggered, dict) and triggered.get("type") == "stop-marker":
        if not any(n for n in n_clicks_list if n):
            return no_update, no_update
        stop_id = triggered["stop_id"]
        return _build_stop_panel(stop_id), stop_id

    if triggered == "stop-search":
        if searched_stop_id:
            return _build_stop_panel(searched_stop_id), searched_stop_id
        return no_update, no_update

    if triggered == "vehicle-interval":
        if selected_stop_id:
            return _build_stop_panel(selected_stop_id), selected_stop_id
        return no_update, no_update

    return no_update, no_update

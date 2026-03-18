# Klient do pobierania danych czasu rzeczywistego z ZTM Poznań API

import csv
import io
import logging
from datetime import datetime, timezone

import requests
from google.transit import gtfs_realtime_pb2

from config import ZTM_RT_BASE_URL

logger = logging.getLogger(__name__)

BASE_URL = ZTM_RT_BASE_URL
TIMEOUT = 10


def _fetch_protobuf(filename):
    """Pobiera plik protobuf z API i zwraca sparsowany FeedMessage."""
    try:
        resp = requests.get(BASE_URL, params={"file": filename}, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.warning("Nie udało się pobrać %s: %s", filename, e)
        return None
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(resp.content)
    return feed


def fetch_trip_updates():
    """Pobiera aktualizacje podróży (opóźnienia, odwołania).

    Zwraca listę słowników z kluczami:
        trip_id, route_id, direction_id, start_date, start_time,
        schedule_relationship, stop_time_updates (lista)
    """
    feed = _fetch_protobuf("trip_updates.pb")
    if feed is None:
        return []
    results = []

    for entity in feed.entity:
        if not entity.HasField("trip_update"):
            continue

        tu = entity.trip_update
        trip = tu.trip

        stop_updates = []
        for stu in tu.stop_time_update:
            stop_updates.append({
                "stop_sequence": stu.stop_sequence,
                "stop_id": stu.stop_id,
                "arrival_delay": stu.arrival.delay if stu.HasField("arrival") else None,
                "arrival_time": stu.arrival.time if stu.HasField("arrival") else None,
                "departure_delay": stu.departure.delay if stu.HasField("departure") else None,
                "departure_time": stu.departure.time if stu.HasField("departure") else None,
            })

        results.append({
            "trip_id": trip.trip_id,
            "route_id": trip.route_id,
            "direction_id": trip.direction_id,
            "start_date": trip.start_date,
            "start_time": trip.start_time,
            "schedule_relationship": trip.schedule_relationship,
            "stop_time_updates": stop_updates,
        })

    logger.info("Pobrano %d trip updates", len(results))
    return results


def fetch_vehicle_positions():
    """Pobiera pozycje pojazdów.

    Zwraca listę słowników z kluczami:
        vehicle_id, label, route_id, trip_id, lat, lon,
        bearing, speed, timestamp, current_stop_sequence
    """
    feed = _fetch_protobuf("vehicle_positions.pb")
    if feed is None:
        return []
    results = []

    for entity in feed.entity:
        if not entity.HasField("vehicle"):
            continue

        v = entity.vehicle
        results.append({
            "vehicle_id": v.vehicle.id,
            "label": v.vehicle.label,
            "route_id": v.trip.route_id if v.HasField("trip") else None,
            "trip_id": v.trip.trip_id if v.HasField("trip") else None,
            "lat": v.position.latitude,
            "lon": v.position.longitude,
            "bearing": v.position.bearing if v.position.bearing else None,
            "speed": v.position.speed if v.position.speed else None,
            "timestamp": v.timestamp,
            "current_stop_sequence": v.current_stop_sequence,
        })

    logger.info("Pobrano %d vehicle positions", len(results))
    return results


def fetch_feeds():
    """Pobiera feed pojazdów (feeds.pb — alternatywne źródło pozycji).

    Zwraca listę słowników w tym samym formacie co fetch_vehicle_positions.
    """
    feed = _fetch_protobuf("feeds.pb")
    if feed is None:
        return []
    results = []

    for entity in feed.entity:
        if not entity.HasField("vehicle"):
            continue

        v = entity.vehicle
        results.append({
            "vehicle_id": v.vehicle.id,
            "label": v.vehicle.label,
            "route_id": v.trip.route_id if v.HasField("trip") else None,
            "trip_id": v.trip.trip_id if v.HasField("trip") else None,
            "lat": v.position.latitude,
            "lon": v.position.longitude,
            "bearing": v.position.bearing if v.position.bearing else None,
            "speed": v.position.speed if v.position.speed else None,
            "timestamp": v.timestamp,
            "current_stop_sequence": v.current_stop_sequence,
        })

    logger.info("Pobrano %d feed vehicle entries", len(results))
    return results


def fetch_vehicle_dictionary():
    """Pobiera słownik pojazdów (CSV).

    Zwraca listę słowników — klucze zależą od kolumn w pliku CSV.
    """
    try:
        resp = requests.get(
            BASE_URL, params={"file": "vehicle_dictionary.csv"}, timeout=TIMEOUT
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.warning("Nie udało się pobrać vehicle_dictionary.csv: %s", e)
        return []

    text = resp.text
    reader = csv.DictReader(io.StringIO(text))
    results = [row for row in reader]

    logger.info("Pobrano %d wpisów ze słownika pojazdów", len(results))
    return results

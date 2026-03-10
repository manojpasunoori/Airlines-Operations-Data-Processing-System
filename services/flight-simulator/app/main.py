from __future__ import annotations

import logging
import os
import random
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

import requests
from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer
from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel


KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://schema-registry:8081")
KAFKA_TOPIC = os.getenv("SIMULATOR_TOPIC", "flight-events")
SCHEMA_PATH = os.getenv("FLIGHT_EVENT_SCHEMA_PATH", "/schemas/flight-event.avsc")
PUBLISH_INTERVAL_SECONDS = float(os.getenv("SIMULATOR_INTERVAL_SECONDS", "15.0"))
OPENSKY_API_URL = os.getenv("OPENSKY_API_URL", "https://opensky-network.org/api/states/all")
OPENSKY_TIMEOUT_SECONDS = float(os.getenv("OPENSKY_TIMEOUT_SECONDS", "15.0"))
OPENSKY_RETRIES = int(os.getenv("OPENSKY_RETRIES", "3"))
OPENSKY_RETRY_BACKOFF_SECONDS = float(os.getenv("OPENSKY_RETRY_BACKOFF_SECONDS", "2.0"))
MAX_EVENTS_PER_POLL = int(os.getenv("MAX_EVENTS_PER_POLL", "25"))


FLIGHT_EVENTS_PROCESSED = Counter("flight_events_processed", "Count of flight events generated from OpenSky")
CONSUMER_LAG = Gauge("consumer_lag", "Synthetic consumer lag gauge")
SERVICE_LATENCY = Histogram("service_latency", "Latency of simulator event publication", buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5))
CONSUMER_LAG.set(0)


app = FastAPI(title="AeroStream Flight Data Connector", version="2.1.0")
LOGGER = logging.getLogger(__name__)

_running = False
_lock = threading.Lock()
_scenario: Literal["normal", "storm"] = "normal"


class SimulationStartRequest(BaseModel):
    scenario: Literal["normal", "storm"] = "normal"


def _load_schema(schema_path: str) -> str:
    return Path(schema_path).read_text(encoding="utf-8")


def _producer() -> SerializingProducer:
    schema_registry_client = SchemaRegistryClient({"url": SCHEMA_REGISTRY_URL})
    schema_str = _load_schema(SCHEMA_PATH)

    avro_serializer = AvroSerializer(
        schema_registry_client=schema_registry_client,
        schema_str=schema_str,
        to_dict=lambda obj, ctx: obj,
    )

    producer_config = {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "key.serializer": StringSerializer("utf_8"),
        "value.serializer": avro_serializer,
    }
    return SerializingProducer(producer_config)


def _fetch_opensky_states_with_retry() -> list[list]:
    delay = OPENSKY_RETRY_BACKOFF_SECONDS
    last_exception: Optional[Exception] = None

    for attempt in range(1, OPENSKY_RETRIES + 1):
        try:
            response = requests.get(OPENSKY_API_URL, timeout=OPENSKY_TIMEOUT_SECONDS)
            response.raise_for_status()
            payload = response.json()
            states = payload.get("states")
            if isinstance(states, list):
                return states
            return []
        except Exception as ex:
            last_exception = ex
            LOGGER.warning("OpenSky fetch attempt %s/%s failed", attempt, OPENSKY_RETRIES, exc_info=ex)
            if attempt < OPENSKY_RETRIES:
                time.sleep(delay)
                delay *= 2

    raise RuntimeError("Failed to fetch OpenSky data after retries") from last_exception


def _storm_delay_minutes() -> int:
    base = random.randint(20, 80)
    # Inject occasional severe delays so the demo clearly shows propagation pressure.
    if random.random() < 0.25:
        base += random.randint(20, 60)
    return base


def _transform_to_flight_event(state: list, scenario: Literal["normal", "storm"]) -> Optional[dict]:
    if not isinstance(state, list) or len(state) < 9:
        return None

    icao24 = (state[0] or "").strip() if state[0] is not None else ""
    callsign = (state[1] or "").strip() if len(state) > 1 and state[1] is not None else ""
    origin_country = (state[2] or "").strip() if len(state) > 2 and state[2] is not None else "UNKNOWN"
    last_contact = state[4] if len(state) > 4 else None
    on_ground = bool(state[8]) if len(state) > 8 and state[8] is not None else False

    if not icao24 and not callsign:
        return None

    timestamp_epoch = int(last_contact) if isinstance(last_contact, (int, float)) else int(time.time())
    iso_timestamp = datetime.fromtimestamp(timestamp_epoch, tz=timezone.utc).isoformat()

    if scenario == "storm":
        delay_minutes = _storm_delay_minutes()
        status = "DELAYED"
    else:
        delay_minutes = 0
        status = "ON_GROUND" if on_ground else "EN_ROUTE"

    return {
        "flightId": callsign or icao24,
        "airline": origin_country,
        "origin": "UNKNOWN",
        "destination": "UNKNOWN",
        "timestamp": iso_timestamp,
        "delayMinutes": delay_minutes,
        "status": status,
    }


def _publish_loop() -> None:
    producer: Optional[SerializingProducer] = None

    while True:
        with _lock:
            if not _running:
                break
            current_scenario = _scenario

        try:
            if producer is None:
                producer = _producer()

            start = time.perf_counter()
            states = _fetch_opensky_states_with_retry()

            published = 0
            for state in states:
                event = _transform_to_flight_event(state, current_scenario)
                if event is None:
                    continue

                producer.produce(topic=KAFKA_TOPIC, key=event["flightId"], value=event)
                producer.poll(0)
                published += 1

                if published >= MAX_EVENTS_PER_POLL:
                    break

            if published > 0:
                FLIGHT_EVENTS_PROCESSED.inc(published)
            SERVICE_LATENCY.observe(time.perf_counter() - start)
        except Exception as ex:
            LOGGER.error("OpenSky publishing cycle failed", exc_info=ex)
            time.sleep(OPENSKY_RETRY_BACKOFF_SECONDS)

        time.sleep(PUBLISH_INTERVAL_SECONDS)

    if producer is not None:
        producer.flush(5)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "running": _running,
        "scenario": _scenario,
        "topic": KAFKA_TOPIC,
        "openskyApi": OPENSKY_API_URL,
    }


@app.get("/metrics")
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/simulation/start")
def start_simulation(request: Optional[SimulationStartRequest] = None) -> dict:
    global _running, _scenario

    with _lock:
        _scenario = request.scenario if request is not None else "normal"
        if _running:
            return {"status": "running", "source": "opensky", "scenario": _scenario}
        _running = True

    thread = threading.Thread(target=_publish_loop, daemon=True)
    thread.start()
    return {"status": "started", "source": "opensky", "scenario": _scenario}


@app.post("/simulation/stop")
def stop_simulation() -> dict:
    global _running
    with _lock:
        _running = False
    return {"status": "stopped"}

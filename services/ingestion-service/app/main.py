from __future__ import annotations

import json
import os
import time

from confluent_kafka import Producer
from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, Field


KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC = os.getenv("INGESTION_TOPIC", "flight-events")


FLIGHT_EVENTS_PROCESSED = Counter("flight_events_processed", "Count of flight events processed by ingestion service")
CONSUMER_LAG = Gauge("consumer_lag", "Synthetic consumer lag gauge")
SERVICE_LATENCY = Histogram("service_latency", "Latency of ingestion endpoint", buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5))
CONSUMER_LAG.set(0)


class FlightEvent(BaseModel):
    event_version: str = Field(default="1.0.0")
    event_id: str
    event_time: str
    flight_id: str
    carrier: str
    origin: str
    destination: str
    delay_minutes: int
    event_type: str
    metadata: dict[str, str]


app = FastAPI(title="AeroStream Ingestion Service", version="1.1.0")


def _producer() -> Producer:
    return Producer({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})


producer = _producer()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "topic": KAFKA_TOPIC}


@app.get("/metrics")
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/ingest/flight-events")
def ingest_flight_event(event: FlightEvent) -> dict:
    start = time.perf_counter()
    payload = event.model_dump()
    producer.produce(
        topic=KAFKA_TOPIC,
        key=payload["flight_id"],
        value=json.dumps(payload),
    )
    producer.poll(0)
    producer.flush(5)
    FLIGHT_EVENTS_PROCESSED.inc()
    SERVICE_LATENCY.observe(time.perf_counter() - start)
    return {"status": "accepted", "flight_id": payload["flight_id"], "topic": KAFKA_TOPIC}

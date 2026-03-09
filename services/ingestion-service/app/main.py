from __future__ import annotations

import os
import time
from pathlib import Path

from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer
from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, Field


KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://schema-registry:8081")
KAFKA_TOPIC = os.getenv("INGESTION_TOPIC", "flight.events.v1")
SCHEMA_PATH = os.getenv("FLIGHT_EVENT_SCHEMA_PATH", "/schemas/flight_event.avsc")


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


def _producer() -> SerializingProducer:
    schema_registry_client = SchemaRegistryClient({"url": SCHEMA_REGISTRY_URL})
    schema_str = Path(SCHEMA_PATH).read_text(encoding="utf-8")
    avro_serializer = AvroSerializer(
        schema_registry_client=schema_registry_client,
        schema_str=schema_str,
        to_dict=lambda obj, ctx: obj,
    )
    return SerializingProducer(
        {
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
            "key.serializer": StringSerializer("utf_8"),
            "value.serializer": avro_serializer,
        }
    )


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
    producer.produce(topic=KAFKA_TOPIC, key=payload["flight_id"], value=payload)
    producer.flush(5)
    FLIGHT_EVENTS_PROCESSED.inc()
    SERVICE_LATENCY.observe(time.perf_counter() - start)
    return {"status": "accepted", "flight_id": payload["flight_id"], "topic": KAFKA_TOPIC}

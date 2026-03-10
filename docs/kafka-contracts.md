# Kafka Contracts and Avro Schema

AeroStream uses Avro-encoded events on Kafka with Confluent Schema Registry.

## Topic and Registry

- Kafka topic: `flight-events`
- Registry URL (inside Docker network): `http://schema-registry:8081`
- Registry URL (host machine): `http://localhost:8085`
- Subject naming: `flight-events-value` (topic-value strategy)

## Active Schema

- Active schema file: `schemas/flight-event.avsc`

```json
{
  "type": "record",
  "name": "FlightEvent",
  "namespace": "com.aerostream.events",
  "fields": [
    { "name": "flightId", "type": "string" },
    { "name": "airline", "type": "string" },
    { "name": "origin", "type": "string" },
    { "name": "destination", "type": "string" },
    { "name": "timestamp", "type": "string" },
    { "name": "delayMinutes", "type": "int" },
    { "name": "status", "type": "string" }
  ]
}
```

## Sample Event Payload

```json
{
  "flightId": "DL430",
  "airline": "Delta Air Lines",
  "origin": "ATL",
  "destination": "JFK",
  "timestamp": "2026-03-10T16:20:45Z",
  "delayMinutes": 28,
  "status": "DELAYED"
}
```

## Producer and Consumer Mapping

### Producers

- `services/ingestion-service`
- `services/flight-simulator`

Both producers:

- read `schemas/flight-event.avsc`
- serialize with `AvroSerializer`
- publish to `flight-events`

### Consumer

- `services/streaming-analytics`

Consumer behavior:

- uses `KafkaAvroDeserializer`
- reads generic Avro records
- maps key fields (`origin`, `destination`, `delayMinutes`) into reliability calculations

## Schema Evolution Policy

Use this policy for safe evolution:

1. Prefer backward-compatible changes.
2. For new fields, provide a default value or nullable union type.
3. Never remove or rename required fields in-place.
4. For breaking changes, create a new major topic contract (for example `flight-events-v2`) and migrate consumers explicitly.

## Compatibility Modes (Recommended)

Set Schema Registry compatibility to `BACKWARD` (or `BACKWARD_TRANSITIVE` in stricter environments) for `flight-events-value`.

Example (host machine):

```bash
curl -X PUT http://localhost:8085/config/flight-events-value \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"compatibility":"BACKWARD"}'
```

## Useful Registry Checks

List subjects:

```bash
curl http://localhost:8085/subjects
```

Get latest schema for topic value subject:

```bash
curl http://localhost:8085/subjects/flight-events-value/versions/latest
```

## Legacy Schema Note

The repository also contains `schemas/flight_event.avsc` (underscore naming) from an earlier event format. Current runtime services are configured to use `schemas/flight-event.avsc`.

If you decide to remove the legacy file, do so in a dedicated cleanup commit with changelog notes.

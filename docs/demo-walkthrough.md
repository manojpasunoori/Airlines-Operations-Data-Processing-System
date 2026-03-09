# Demo Walkthrough (2 Minutes)

## Goal

Show real-time delay propagation and reliability scoring end-to-end.

## Steps

1. Start platform:
   - `docker compose up -d --build`
2. Trigger simulator storm scenario:
   - `curl -X POST http://localhost:8091/simulation/start -H "Content-Type: application/json" -d "{\"scenario\":\"storm\"}"`
3. Open dashboard:
   - `http://localhost:5173`
4. Open Grafana dashboard:
   - `http://localhost:3000`
5. Show analytics API output:
   - `http://localhost:8080/api/analytics/routes/reliability`

## Talking Points

- Event ingestion into Kafka (`flight.events.v1`)
- Streaming window aggregations in Spring Kafka Streams
- Live UI updates over SSE
- Operational metrics (`flight_events_processed`, `consumer_lag`, `service_latency`)
- GitOps deployment path through Helm + ArgoCD

## Optional Video Slot

Add your demo recording URL here after capture:

- `https://your-demo-video-link`

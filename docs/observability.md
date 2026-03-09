# Observability

AeroStream observability stack includes:

- Prometheus metrics scraping for Java and Python services
- Grafana provisioning with preloaded dashboards
- OpenTelemetry Collector for trace ingestion

## Key Metrics

- `flight_events_processed`
- `consumer_lag`
- `service_latency`

## Access

- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`
- OTel HTTP receiver: `http://localhost:4318`

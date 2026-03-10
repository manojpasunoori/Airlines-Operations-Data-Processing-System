# AeroStream Demo Walkthrough

This walkthrough demonstrates the full event pipeline:

OpenSky API -> Flight Simulator -> Kafka (`flight-events`) -> Streaming Analytics -> Dashboard + Grafana

## Demo Objective

In 3-5 minutes, show:

1. stack startup
2. storm-mode event generation
3. live dashboard changes
4. metrics and traces visibility

## Prerequisites

- Docker Desktop running
- Ports available: `3000`, `5173`, `8080`, `8085`, `8086`, `8090`, `8091`, `9090`

## Step 1: Start the platform

```bash
docker compose up -d --build
```

Verify containers:

```bash
docker compose ps
```

Expected key services in `Up` state:

- `kafka`
- `schema-registry`
- `streaming-analytics`
- `gateway`
- `dashboard`
- `prometheus`
- `grafana`

## Step 2: Trigger delay storm mode

Start simulator with storm scenario:

```bash
curl -X POST http://localhost:8091/simulation/start \
  -H "Content-Type: application/json" \
  -d '{"scenario":"storm"}'
```

Expected response:

```json
{"status":"started","source":"opensky","scenario":"storm"}
```

Confirm simulator health:

```bash
curl http://localhost:8091/health
```

Look for:

- `"running": true`
- `"scenario": "storm"`

## Step 3: Observe live dashboard updates

Open:

- Dashboard: `http://localhost:5173`

What to highlight:

- Live Flight Table fills with new events
- Delay propagation bars increase
- Route reliability rankings change over time

## Step 4: Validate analytics API output

Query current reliability aggregates:

```bash
curl http://localhost:8086/api/analytics/routes/reliability
```

Expected behavior:

- Routes appear as keys (for example `"UNKNOWN->UNKNOWN"`)
- `averageDelay` and `reliabilityScore` change continuously while storm mode runs

## Step 5: Show Grafana and Prometheus metrics

Open:

- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000` (default `admin/admin` unless overridden)

Prometheus quick checks:

- `flight_events_processed`
- `service_latency_seconds_count` (or related histogram series)
- `jvm_memory_used_bytes` (Spring services)

Grafana walkthrough:

1. Open provisioned AeroStream dashboard
2. Show ingestion/processing activity rising
3. Show latency and event throughput panels during storm mode

## Step 6: Optional JWT gateway check

Get token:

```bash
curl -s -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

Use token on gateway analytics route:

```bash
curl http://localhost:8080/api/analytics/routes/reliability \
  -H "Authorization: Bearer <accessToken>"
```

## Step 7: Stop the simulator

```bash
curl -X POST http://localhost:8091/simulation/stop
```

Expected response:

```json
{"status":"stopped"}
```

## Recording Tips (Optional)

- Keep the demo under 90 seconds for README embedding
- Capture one terminal + dashboard + Grafana sequence
- Store final media in `docs/images/` and `docs/videos/`


Airline Operations Data Processing System

A fully containerized, production-style distributed backend system simulating airline operational analytics using Spring Boot microservices, API Gateway, MySQL, Docker, and observability tooling.

 High-Level Architecture
Client
   ↓
API Gateway (8080)
   ↓
-------------------------------------------------
| flight-service  (8081) → flights table       |
| crew-service    (8082) → crew table          |
| delay-service   (8083) → delays table        |
| kpi-service     (8084) → kpi_metrics table   |
-------------------------------------------------
                    ↓
                 MySQL (3306)
System Overview

This system simulates airline operational workflows including:

Flight registration and lookup

Crew assignment per flight

Delay tracking and categorization

KPI storage and analytics

Operational KPI snapshot endpoint (on-time %, delayed flights, avg delay)

Distributed routing via API Gateway

Observability via Prometheus & Grafana

Correlation ID tracing across services

Centralized error handling

API documentation with Swagger

The architecture follows microservices best practices including:

Service isolation

Environment-based configuration

Docker container networking

Persistent storage via volumes

Health monitoring via Actuator

Metrics exposure via Prometheus

Structured logging with correlation IDs

 Technology Stack
Backend

Java 17

Spring Boot 3.2.x

Spring Data JPA (Hibernate)

Spring Cloud Gateway

Spring Validation

Springdoc OpenAPI (Swagger)

Database

MySQL 8

Foreign key constraints

Persistent volume storage

Infrastructure

Docker & Docker Compose

WSL2 (Ubuntu 22.04)

Multi-stage Docker builds

Observability

Spring Boot Actuator

Prometheus

Grafana

Micrometer metrics

Correlation ID logging

Project Structure
airline-ops-system/
├── docker-compose.yml
├── .env
├── gateway/
├── services/
│   ├── flight-service/
│   ├── crew-service/
│   ├── delay-service/
│   └── kpi-service/
├── infra/
│   ├── mysql/
│   ├── k8s/
│   └── observability/
├── load-test/
│   └── jmeter/
└── .github/workflows/
Getting Started
1)Clone Repository
git clone <your-repo-url>
cd airline-ops-system
2)Configure Environment

Create .env file:

MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=airline_ops
MYSQL_USER=airline_user
MYSQL_PASSWORD=airline_password
API_KEY=dev_key_change_me_1234567890
3) Build and Run
docker compose up -d --build
Service Endpoints
API Gateway

Base URL:

http://localhost:8080

All traffic flows through Gateway.

Example:

curl -H "X-API-KEY: <your_key>" \
     http://localhost:8080/api/flights
Individual Services
Service	Port
Gateway	8080
Flight Service	8081
Crew Service	8082
Delay Service	8083
KPI Service	8084
MySQL	3306
Prometheus	9090
Grafana	3000
Observability
Actuator Health
curl http://localhost:8081/actuator/health
Prometheus Metrics
curl http://localhost:8081/actuator/prometheus

Prometheus UI:

http://localhost:9090
Grafana Dashboard
http://localhost:3000

(Default login: admin/admin)

API Documentation (Swagger)

Each service exposes Swagger UI:

http://localhost:8081/swagger-ui/index.html
http://localhost:8082/swagger-ui/index.html
http://localhost:8083/swagger-ui/index.html
http://localhost:8084/swagger-ui/index.html

Operational snapshot example:

curl -H "X-API-KEY: <your_key>" \
     "http://localhost:8080/api/kpis/operational-snapshot?onTimeThresholdMinutes=15"

Threshold rules: `onTimeThresholdMinutes` must be between `0` and `300` (default `15`).

OpenAPI spec:

http://localhost:8081/v3/api-docs
Logging & Tracing

Correlation ID injected at Gateway

Propagated across all services

Included in log pattern

Enables request-level tracing across distributed system

Example log pattern:

INFO [cid=3b21d8f2-...] Flight created successfully
Security

API key enforced at Gateway layer

Header required:

X-API-KEY: <value_from_env>

Unauthorized requests return 401.

Load Testing

JMeter test plan available in:

load-test/jmeter/

Simulates concurrent API calls and system throughput.

Kubernetes (Optional Deployment)

K8s manifests located under:

infra/k8s/

Includes:

Namespace

Deployments

Services

Ingress

MySQL config

Deploy via:

kubectl apply -f infra/k8s/
Engineering Concepts Applied

Distributed system architecture

API Gateway routing pattern

Container orchestration via Docker

Environment-based configuration

Structured error handling

Correlation ID tracing

Prometheus-based monitoring

Health endpoints

Persistent storage volumes

GitHub CI pipeline

Clean repo structure

Future Enhancements

DTO separation layer

Inter-service communication via WebClient

Resilience4j (Circuit Breaker / Retry)

KPI aggregation logic

Redis caching

Distributed tracing (OpenTelemetry)

Authentication with JWT

Why This Project Matters

This system demonstrates:

Real-world microservices architecture

Production-grade containerization

Observability implementation

Clean API contracts

Infrastructure awareness

Backend engineering maturity

It is designed to simulate high-reliability airline backend systems where data consistency, fault tolerance, and traceability are critical.

Author

Manoj Pasunoori
MS Information Systems – University of Texas at Arlington
Backend & Distributed Systems Engineer
=======
# AeroStream: Real-Time Airline Operations Intelligence Platform

AeroStream is a production-style, event-driven distributed systems portfolio project focused on airline operations intelligence. The platform ingests flight events, analyzes delay propagation in near-real time, and publishes route reliability metrics to APIs and live dashboards.

## System Architecture

```mermaid
flowchart LR
    FAA["FAA/OpenSky Feeds"] --> ING["FastAPI Ingestion Service"]
    SIM["Flight Simulator"] --> ING
    ING --> KAFKA["Kafka + Schema Registry"]
    KAFKA --> STREAM["Spring Kafka Streams Analytics"]
    STREAM --> PG[(PostgreSQL Analytics)]
    STREAM --> SSE["SSE Endpoint"]
    MONGO[(MongoDB Route Config)] --> STREAM
    SSE --> UI["React + TypeScript Dashboard"]
    STREAM --> PROM["Prometheus"]
    ING --> PROM
    UI --> GW["API Gateway"]
    PROM --> GRAF["Grafana"]
```

## Event Flow

1. Flight events are produced by FAA/OpenSky connectors or the simulator.
2. Ingestion validates and publishes Avro events to topic `flight.events.v1`.
3. Streaming analytics computes 5-minute route delay windows.
4. Reliability scores are persisted to PostgreSQL and pushed via SSE.
5. Dashboard renders live route metrics.
6. Prometheus and Grafana expose operational health and performance.

## Infrastructure Design

- Runtime: Docker Compose for local multi-service environment.
- Event Backbone: Kafka + Zookeeper + Schema Registry.
- Data: PostgreSQL (analytics), MongoDB (route config), MySQL (legacy domain services).
- Observability: Prometheus, Grafana provisioning, OpenTelemetry collector.
- Deployment: Helm chart + env values + Kustomize overlays + ArgoCD app.
- CI/CD: GitHub Actions with test/build/image scan/publish flow.

## Tech Stack

- Python FastAPI (`services/ingestion-service`, `services/flight-simulator`)
- Apache Kafka + Avro schema contracts (`schemas/flight_event.avsc`)
- Java Spring Boot + Kafka Streams (`services/streaming-analytics`)
- React + TypeScript dashboard (`dashboard`)
- Docker + Kubernetes/Helm + ArgoCD GitOps

## Local Setup

1. Copy env template:
   - `cp .env.example .env`
2. Start platform:
   - `docker compose up -d --build`
3. Open services:
   - Gateway: `http://localhost:8080`
   - Ingestion: `http://localhost:8090`
   - Simulator: `http://localhost:8091`
   - Streaming Analytics: `http://localhost:8086`
   - Dashboard: `http://localhost:5173`
   - Prometheus: `http://localhost:9090`
   - Grafana: `http://localhost:3000`

Detailed docs:

- `docs/local-development.md`
- `docs/kafka-contracts.md`
- `docs/streaming-analytics.md`
- `docs/observability.md`
- `docs/kubernetes-deployment.md`
- `docs/realtime-dashboard.md`

## Demo Instructions

- Quick demo script (PowerShell): `demo/scripts/run_demo.ps1`
- Quick demo script (bash): `demo/scripts/run_demo.sh`
- Walkthrough: `docs/demo-walkthrough.md`
- Example dataset: `demo/datasets/sample_flights.jsonl`

2-minute demo strategy:

1. `docker compose up -d --build`
2. start simulator storm scenario
3. show dashboard live route updates
4. show Grafana metrics and reliability API

## Engineering Decisions

- Kafka + Avro contracts to decouple producers/consumers and support schema evolution.
- Spring Kafka Streams for deterministic, windowed delay propagation analytics.
- SSE for low-overhead live updates without websocket broker complexity.
- Split operational data stores by workload: PostgreSQL analytics + Mongo config.
- OTel + Prometheus metrics first-class for production debugging and SLO tracking.
- Helm + ArgoCD for repeatable environment promotion (dev/staging/prod).

## Repository Structure

- `gateway/`
- `services/`
- `dashboard/`
- `infra/`
- `schemas/`
- `docs/`
- `demo/`

## Current Status

The project now includes:

- local distributed stack bootstrapping
- schema-governed Kafka eventing
- synthetic delay scenario simulation
- streaming analytics with route reliability scoring
- real-time dashboard updates
- production-style observability and CI/CD assets
- Kubernetes Helm + GitOps deployment scaffolding

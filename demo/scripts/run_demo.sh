#!/usr/bin/env bash
set -euo pipefail

echo "[1/5] Starting platform"
docker compose up -d --build

echo "[2/5] Waiting for simulator"
sleep 8

echo "[3/5] Starting storm scenario"
curl -s -X POST http://localhost:8091/simulation/start -H "Content-Type: application/json" -d '{"scenario":"storm"}'

echo "[4/5] Open dashboard and Grafana"
echo "Dashboard: http://localhost:5173"
echo "Grafana:   http://localhost:3000"

echo "[5/5] Fetch current reliability snapshot"
curl -s http://localhost:8080/api/analytics/routes/reliability

echo "Demo running. Stop simulator with:"
echo "curl -X POST http://localhost:8091/simulation/stop"

$ErrorActionPreference = "Stop"

Write-Host "[1/5] Starting platform"
docker compose up -d --build

Write-Host "[2/5] Waiting for simulator"
Start-Sleep -Seconds 8

Write-Host "[3/5] Starting storm scenario"
Invoke-RestMethod -Method Post -Uri "http://localhost:8091/simulation/start" -ContentType "application/json" -Body '{"scenario":"storm"}' | Out-Host

Write-Host "[4/5] Open dashboard and Grafana"
Write-Host "Dashboard: http://localhost:5173"
Write-Host "Grafana:   http://localhost:3000"

Write-Host "[5/5] Fetch reliability snapshot"
Invoke-RestMethod -Method Get -Uri "http://localhost:8080/api/analytics/routes/reliability" | ConvertTo-Json -Depth 5

Write-Host "Demo running. Stop simulator with:"
Write-Host "Invoke-RestMethod -Method Post -Uri http://localhost:8091/simulation/stop"

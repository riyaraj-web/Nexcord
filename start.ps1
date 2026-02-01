# Quick start script for Nexcord
Write-Host "Starting Nexcord..." -ForegroundColor Cyan

# Check Docker
docker info 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Start services
docker compose up -d

Write-Host ""
Write-Host "Nexcord is starting!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host ""

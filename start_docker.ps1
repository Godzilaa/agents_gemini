# Docker Multi-Agent System Startup Script (PowerShell)
Write-Host "🐳 Starting Multi-Agent System with Docker Compose" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

# Check if docker-compose is available
try {
    docker-compose --version | Out-Null
    Write-Host "✅ Docker Compose is available" -ForegroundColor Green
} catch {
    Write-Host "❌ docker-compose not found. Please install Docker Compose." -ForegroundColor Red
    exit 1
}

# Check for .env file
if (!(Test-Path .env)) {
    Write-Host "⚠️  No .env file found. Creating from template..." -ForegroundColor Yellow
    Copy-Item .env.template .env
    Write-Host "📝 Please edit .env file with your API keys and configuration" -ForegroundColor Yellow
    Write-Host "   Default Google Maps API key is provided but you should use your own" -ForegroundColor Yellow
}

# Build and start all services
Write-Host ""
Write-Host "🔨 Building Docker images..." -ForegroundColor Blue
docker-compose build

Write-Host ""
Write-Host "🚀 Starting all agent services..." -ForegroundColor Green
docker-compose up -d

Write-Host ""
Write-Host "⏳ Waiting for services to become healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check service health
Write-Host ""
Write-Host "🔍 Checking service health..." -ForegroundColor Cyan

$services = @(
    @{name="food-agent"; port=8000},
    @{name="regulatory-agent"; port=8001},
    @{name="transport-agent"; port=8002},
    @{name="festival-agent"; port=8003},
    @{name="decision-agent"; port=8004}
)

foreach ($service in $services) {
    $status = docker-compose ps $service.name
    if ($status -like "*Up (healthy)*") {
        Write-Host "✅ $($service.name) is healthy (port $($service.port))" -ForegroundColor Green
    } else {
        Write-Host "❌ $($service.name) is not healthy" -ForegroundColor Red
        Write-Host "📋 Last 5 lines of $($service.name) logs:" -ForegroundColor Yellow
        docker-compose logs --tail=5 $service.name
        Write-Host ""
    }
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "🎉 Multi-Agent System is ready!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Service Status:" -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "🌐 Available Endpoints:" -ForegroundColor Cyan
Write-Host "   Food Agent:      http://localhost:8000 (http://localhost:8000/docs)" -ForegroundColor White
Write-Host "   Regulatory:      http://localhost:8001 (http://localhost:8001/docs)" -ForegroundColor White
Write-Host "   Transport:       http://localhost:8002 (http://localhost:8002/docs)" -ForegroundColor White
Write-Host "   Festival:        http://localhost:8003 (http://localhost:8003/docs)" -ForegroundColor White
Write-Host "   Decision:        http://localhost:8004 (http://localhost:8004/docs)" -ForegroundColor White
Write-Host ""
Write-Host "🧪 Quick Test Commands:" -ForegroundColor Yellow
Write-Host '   Invoke-RestMethod -Uri "http://localhost:8004/health"' -ForegroundColor Gray
Write-Host '   Invoke-RestMethod -Uri "http://localhost:8004/quick-analysis?latitude=19.0760&longitude=72.8777&vehicle_type=car"' -ForegroundColor Gray
Write-Host ""
Write-Host "📋 Useful Docker Commands:" -ForegroundColor Yellow
Write-Host "   View logs:       docker-compose logs -f [service-name]" -ForegroundColor Gray
Write-Host "   Stop all:        docker-compose down" -ForegroundColor Gray
Write-Host "   Restart:         docker-compose restart [service-name]" -ForegroundColor Gray
Write-Host "   Rebuild:         docker-compose build --no-cache" -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  To stop all services: docker-compose down" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan
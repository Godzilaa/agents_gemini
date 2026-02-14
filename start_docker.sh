#!/bin/bash

# Docker Multi-Agent System Startup Script
echo "🐳 Starting Multi-Agent System with Docker Compose"
echo "=================================================="

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install Docker Compose."
    exit 1
fi

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.template .env
    echo "📝 Please edit .env file with your API keys and configuration"
    echo "   Default Google Maps API key is provided but you should use your own"
fi

# Build and start all services
echo "🔨 Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting all agent services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to become healthy..."
sleep 30

# Check service health
echo ""
echo "🔍 Checking service health..."

services=("food-agent" "regulatory-agent" "transport-agent" "festival-agent" "decision-agent")
ports=(8000 8001 8002 8003 8004)

for i in "${!services[@]}"; do
    service="${services[i]}"
    port="${ports[i]}"
    
    if docker-compose ps | grep "$service" | grep -q "Up (healthy)"; then
        echo "✅ $service is healthy (port $port)"
    else
        echo "❌ $service is not healthy"
        # Show logs for debugging
        echo "📋 Last 5 lines of $service logs:"
        docker-compose logs --tail=5 "$service"
        echo ""
    fi
done

echo ""
echo "=================================================="
echo "🎉 Multi-Agent System is ready!"
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🌐 Available Endpoints:"
echo "   Food Agent:      http://localhost:8000 (http://localhost:8000/docs)"
echo "   Regulatory:      http://localhost:8001 (http://localhost:8001/docs)"
echo "   Transport:       http://localhost:8002 (http://localhost:8002/docs)"
echo "   Festival:        http://localhost:8003 (http://localhost:8003/docs)"
echo "   Decision:        http://localhost:8004 (http://localhost:8004/docs)"
echo ""
echo "🧪 Quick Test Commands:"
echo "   curl http://localhost:8004/health"
echo "   curl \"http://localhost:8004/quick-analysis?latitude=19.0760&longitude=72.8777&vehicle_type=car\""
echo ""
echo "📋 Useful Docker Commands:"
echo "   View logs:       docker-compose logs -f [service-name]"
echo "   Stop all:        docker-compose down"
echo "   Restart:         docker-compose restart [service-name]"
echo "   Rebuild:         docker-compose build --no-cache"
echo ""
echo "⚠️  To stop all services: docker-compose down"
echo "=================================================="
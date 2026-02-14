# 🐳 Docker Deployment Guide

## Quick Start

### 1. **Prerequisites**
- Docker Desktop installed and running
- Docker Compose available

### 2. **Launch All Agents**

#### Windows (PowerShell):
```powershell
.\start_docker.ps1
```

#### Linux/MacOS (Bash):
```bash
chmod +x start_docker.sh
./start_docker.sh
```

#### Manual Docker Compose:
```bash
# Build and start all services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network                          │
│                  (multi-agents-network)                    │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │food-agent   │  │regulatory   │  │transport    │        │
│  │:8000        │  │-agent:8001  │  │-agent:8002  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
│  ┌─────────────┐  ┌──────────────────────────────┐        │
│  │festival     │  │      decision-agent          │        │
│  │-agent:8003  │  │         :8004                │        │
│  └─────────────┘  └──────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Docker Files Structure

```
agents_gemini/
├── docker-compose.yml           # Main orchestration
├── Dockerfile.decision          # Decision agent
├── Dockerfile.festival          # Festival agent
├── .dockerignore               # Build optimization
├── .env.template               # Environment template
├── start_docker.ps1            # Windows startup
├── start_docker.sh             # Linux/Mac startup
├── foodagent/
│   └── Dockerfile              # Food agent
├── regulatoryagent/
│   └── Dockerfile              # Regulatory agent
└── transportagent/
    └── Dockerfile              # Transport agent
```

## 🚀 Available Services

| Service | Container | Port | Health Check |
|---------|-----------|------|--------------|
| **Food Agent** | food-agent | 8000 | ✅ |
| **Regulatory Agent** | regulatory-agent | 8001 | ✅ |
| **Transport Agent** | transport-agent | 8002 | ✅ |
| **Festival Agent** | festival-agent | 8003 | ✅ |
| **Decision Agent** | decision-agent | 8004 | ✅ |

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# Required for Food & Regulatory agents
GOOGLE_MAPS_API_KEY=your_api_key_here

# Optional configurations
AGENT_TIMEOUT=30
MAX_RETRIES=3
```

### Docker Compose Features
- **Health Checks**: All containers have health monitoring
- **Service Dependencies**: Decision agent waits for other agents
- **Auto-restart**: Containers restart automatically on failure
- **Custom Network**: Isolated network for agent communication
- **Volume Management**: Persistent data storage

## 🛠️ Management Commands

### **Startup**
```bash
# Start all services
docker-compose up -d

# Start with rebuild
docker-compose up -d --build

# Start specific service
docker-compose up -d food-agent
```

### **Monitoring**
```bash
# Check service status
docker-compose ps

# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f decision-agent

# Check health status
docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
```

### **Troubleshooting**
```bash
# Restart specific service
docker-compose restart food-agent

# Rebuild and restart
docker-compose up -d --build food-agent

# Execute command in container
docker-compose exec decision-agent bash

# View container resource usage
docker stats
```

### **Cleanup**
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Complete cleanup
docker system prune -a
```

## 🧪 Testing Dockerized System

### **Health Check All Services**
```bash
# Using curl (Linux/Mac)
curl http://localhost:8004/health

# Using PowerShell (Windows)
Invoke-RestMethod -Uri 'http://localhost:8004/health'
```

### **Quick System Test**
```bash
# Test coordination
curl "http://localhost:8004/quick-analysis?latitude=19.0760&longitude=72.8777&vehicle_type=car"

# Test dining recommendations
curl "http://localhost:8004/dining-recommendation?latitude=19.0760&longitude=72.8777&vehicle_type=bike"
```

### **Container Health Verification**
```bash
# Check all container health
docker-compose ps

# Expected output should show all services as "Up (healthy)"
```

## 🔧 Development Mode

### **Live Development with Volume Mounting**
```yaml
# Add to docker-compose.override.yml
services:
  decision-agent:
    volumes:
      - ./decision_agent.py:/app/decision_agent.py
      - ./a2a_models.py:/app/a2a_models.py
      - ./a2a_communication.py:/app/a2a_communication.py
```

### **Debug Mode**
```bash
# Run with debug logging
docker-compose up -d
docker-compose logs -f decision-agent

# Interactive shell access
docker-compose exec decision-agent bash
```

## 📊 Monitoring & Logs

### **Container Metrics**
```bash
# Resource usage
docker stats

# System-wide info
docker system df
```

### **Log Analysis**
```bash
# Follow logs from all services
docker-compose logs -f

# Filter logs by service
docker-compose logs -f decision-agent | grep ERROR

# Export logs
docker-compose logs --no-color > system_logs.txt
```

## 🚨 Troubleshooting

### **Common Issues**

#### **Service won't start**
```bash
# Check logs
docker-compose logs service-name

# Check port conflicts
netstat -tulpn | grep 8000

# Rebuild container
docker-compose build --no-cache service-name
```

#### **Health check failures**
```bash
# Check container status
docker-compose ps

# Manual health check
docker-compose exec service-name curl -f http://localhost:8000/health
```

#### **A2A Communication Issues**
```bash
# Test network connectivity
docker-compose exec decision-agent ping food-agent

# Check network configuration
docker network ls
docker network inspect multi-agents-network
```

#### **Memory/CPU Issues**
```bash
# Monitor resource usage
docker stats

# Increase resource limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
```

## 🔄 Production Deployment

### **Production docker-compose.prod.yml**
```yaml
version: '3.8'
services:
  decision-agent:
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### **Load Balancing**
```yaml
services:
  decision-agent:
    deploy:
      replicas: 3
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

## 🎯 Benefits of Docker Deployment

✅ **Isolated Environment** - Each agent runs in its own container  
✅ **Easy Scaling** - Scale individual agents independently  
✅ **Dependency Management** - No version conflicts  
✅ **Health Monitoring** - Automatic health checks and restarts  
✅ **Port Management** - Clean port mapping and networking  
✅ **Easy Deployment** - Single command deployment  
✅ **Development Consistency** - Same environment everywhere  

---

## 📞 Support Commands

```bash
# Quick system status
docker-compose ps && echo "System Status: $(docker-compose ps --quiet | wc -l) containers running"

# Full system health
for service in food-agent regulatory-agent transport-agent festival-agent decision-agent; do
  echo -n "$service: "
  docker-compose exec $service curl -s http://localhost:8000/health >/dev/null && echo "✅" || echo "❌"
done

# Performance snapshot
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

**Your multi-agent system is now fully containerized and ready for local hosting!** 🚀
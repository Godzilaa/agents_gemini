# Multi-Agent System with A2A Communication

## 🌟 Overview

A sophisticated multi-agent system that coordinates **Food**, **Regulatory**, **Transport**, and **Festival** agents through a **Master Decision Agent** using Agent-to-Agent (A2A) communication protocol.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Master Decision Agent                   │
│                     (Port 8004)                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            A2A Communication Hub                    │   │
│  │         - Message Routing                          │   │
│  │         - Response Coordination                    │   │
│  │         - Decision Synthesis                       │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────┬───────────────┬───────────────┬──────────────┘
              │               │               │
    ┌─────────▼────┐  ┌───────▼────┐  ┌──────▼─────┐  ┌──────────▼───┐
    │ Food Agent   │  │ Regulatory │  │ Transport  │  │ Festival     │
    │ (Port 8000)  │  │ Agent      │  │ Agent      │  │ Agent        │
    │              │  │ (Port 8001)│  │ (Port 8002)│  │ (Port 8003)  │
    │ • Restaurant │  │ • Traffic  │  │ • Traffic  │  │ • Event      │
    │   Recommendations│  • Enforcement│  • Analysis│  │   Detection  │
    │ • Hygiene    │  │ • Risk     │  │ • Route    │  │ • Road       │
    │   Analysis   │  │   Assessment│  │   Planning │  │   Closures   │
    │ • Hidden Gems│  │ • Zone     │  │ • Congestion│  │ • Festival   │
    │              │  │   Detection│  │   Prediction│  │   Impact     │
    └──────────────┘  └────────────┘  └────────────┘  └──────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- All agents' dependencies installed

### 🪟 Windows (PowerShell)
```powershell
# Start all agents
./start_agents.ps1
```

### 🐧 Linux/MacOS (Bash)
```bash
# Make script executable
chmod +x start_agents.sh

# Start all agents
./start_agents.sh
```

### Manual Start
```bash
# Terminal 1 - Food Agent
cd foodagent && python main.py

# Terminal 2 - Regulatory Agent  
cd regulatoryagent && python main.py

# Terminal 3 - Transport Agent
cd transportagent && python main.py

# Terminal 4 - Festival Agent
python festival_agent.py

# Terminal 5 - Master Decision Agent
python decision_agent.py
```

## 📡 A2A Communication Protocol

### Message Format
```json
{
  "message_id": "unique_id",
  "sender_agent": "decision",
  "receiver_agent": "food", 
  "message_type": "request",
  "priority": "medium",
  "timestamp": "2026-02-14T10:00:00",
  "payload": {
    "latitude": 19.0760,
    "longitude": 72.8777,
    "radius": 2000
  }
}
```

### Communication Flow
1. **Request Initiation**: Master Decision Agent receives user request
2. **Agent Coordination**: Parallel queries to relevant agents via A2A protocol
3. **Data Synthesis**: Combine responses from multiple agents
4. **Decision Making**: Generate unified recommendation with confidence scoring
5. **Response Delivery**: Return comprehensive decision to user

## 🎯 Key Endpoints

### Master Decision Agent (`localhost:8004`)

#### Quick Analysis
```bash
GET /quick-analysis?latitude=19.0760&longitude=72.8777&vehicle_type=car
```

#### Dining Recommendations
```bash
GET /dining-recommendation?latitude=19.0760&longitude=72.8777&vehicle_type=bike&radius=2000
```

#### Route Safety
```bash
GET /route-safety?origin_lat=19.0760&origin_lng=72.8777&dest_lat=19.0800&dest_lng=72.8800&vehicle_type=bike
```

#### Master Decision
```bash
POST /decide
Content-Type: application/json

{
  "user_context": {
    "location": {"latitude": 19.0760, "longitude": 72.8777},
    "vehicle_type": "bike",
    "preferences": {"radius": 2000}
  },
  "query_type": "dining_recommendation"
}
```

## 🧪 Testing

### Health Check All Agents
```bash
curl http://localhost:8000/health  # Food
curl http://localhost:8001/health  # Regulatory  
curl http://localhost:8002/health  # Transport
curl http://localhost:8003/health  # Festival
curl http://localhost:8004/health  # Decision
```

### Complete Test Suite
```bash
# Load test data
curl -X POST "http://localhost:8004/decide" \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

### PowerShell Testing
```powershell
# Health checks
Invoke-RestMethod -Uri 'http://localhost:8004/health'

# Quick analysis
Invoke-RestMethod -Uri 'http://localhost:8004/quick-analysis?latitude=19.0760&longitude=72.8777&vehicle_type=car'

# Master decision
$body = Get-Content 'test_request.json' | ConvertFrom-Json | ConvertTo-Json
Invoke-RestMethod -Uri 'http://localhost:8004/decide' -Method Post -Body $body -ContentType 'application/json'
```

## 📊 Agent Capabilities

| Agent | Port | Primary Function | Key Features |
|-------|------|------------------|--------------|
| **Food** | 8000 | Restaurant recommendations | Hidden gems, hygiene analysis, night spots |
| **Regulatory** | 8001 | Traffic enforcement detection | Risk assessment, zone analysis, violations |
| **Transport** | 8002 | Traffic & mobility analysis | Congestion prediction, route planning |
| **Festival** | 8003 | Event & road closure detection | Festival impact, alternate routes |
| **Decision** | 8004 | Master coordination | A2A orchestration, unified decisions |

## 🔄 Use Case Examples

### 1. Smart Dining Recommendation
**Input**: Location + Vehicle type  
**Process**: Food Agent finds restaurants → Regulatory Agent checks enforcement zones → Festival Agent checks events  
**Output**: Restaurant recommendations with safety warnings and event alerts

### 2. Route Safety Analysis  
**Input**: Origin + Destination + Vehicle type  
**Process**: Regulatory checks both locations → Transport analyzes traffic → Festival checks closures  
**Output**: Comprehensive route safety assessment

### 3. Area Analysis
**Input**: Location  
**Process**: All agents analyze the area simultaneously  
**Output**: Complete area profile with food, safety, traffic, and event information

## 📈 Decision Engine

### Confidence Scoring
- **Food Agent**: 30% weight (based on result count and ratings)
- **Regulatory Agent**: 40% weight (based on risk assessment completeness)  
- **Transport Agent**: 20% weight (based on traffic data availability)
- **Festival Agent**: 10% weight (based on event impact level)

### Recommendation Synthesis
1. Extract top recommendations from each agent
2. Apply priority-based filtering (safety warnings first)
3. Combine complementary insights
4. Generate unified action items

## 🛠️ Development

### Adding New Agents
1. Create agent with `/a2a/receive` endpoint
2. Register in `AGENT_REGISTRY` (a2a_models.py)
3. Add endpoint to `A2ACommunicationHandler`
4. Update decision engine logic

### Extending Communication
1. Add new `MessageType` to enum
2. Implement handler in target agent
3. Update orchestrator methods
4. Add test cases

## 📁 File Structure
```
agents_gemini/
├── a2a_models.py           # A2A protocol definitions
├── a2a_communication.py    # Communication handler
├── decision_agent.py       # Master decision agent
├── festival_agent.py       # Festival/event agent
├── start_agents.ps1        # Windows startup script
├── start_agents.sh         # Linux/Mac startup script
├── test_request.json       # Sample test data
├── multi_agent_tests.json  # Test suite
├── foodagent/             # Food recommendation agent
├── regulatoryagent/       # Traffic regulation agent
└── transportagent/        # Transport analysis agent
```

## 🌐 API Documentation

Once all agents are running:

- **Food Agent**: http://localhost:8000/docs
- **Regulatory Agent**: http://localhost:8001/docs  
- **Transport Agent**: http://localhost:8002/docs
- **Festival Agent**: http://localhost:8003/docs
- **Decision Agent**: http://localhost:8004/docs

## 🚨 Troubleshooting

### Agent Not Starting
1. Check port availability: `netstat -tulpn | grep :8000`
2. Verify dependencies: `pip install -r requirements.txt`
3. Check Python path for A2A imports

### A2A Communication Issues
1. Verify all agents are running: `curl http://localhost:800X/health`
2. Check network connectivity between agents
3. Review agent logs for A2A message handling

### Decision Quality Issues
1. Check agent response data quality
2. Verify confidence scoring weights
3. Review decision engine logic

## 🔮 Future Enhancements

- **Real-time WebSocket communication** between agents
- **Agent learning and adaptation** based on user feedback
- **Dynamic agent discovery** and registration
- **Load balancing** for high-traffic scenarios
- **Distributed deployment** across multiple servers
- **Advanced conflict resolution** between agent recommendations

---

## 🏆 System Highlights

✅ **Scalable Architecture** - Easy to add new agents  
✅ **Fault Tolerant** - Graceful degradation when agents fail  
✅ **Real-time Coordination** - Parallel agent processing  
✅ **Unified Interface** - Single decision endpoint  
✅ **Comprehensive Testing** - Full test suite included  
✅ **Cross-platform** - Windows & Linux support  

**Ready to revolutionize decision making with coordinated AI agents!** 🚀
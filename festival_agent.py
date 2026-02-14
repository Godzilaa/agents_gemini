from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Add parent directory to path for A2A imports
sys.path.append(str(Path(__file__).parent.parent))

from a2a_models import AgentMessage, AgentType, MessageType
from pydantic import BaseModel

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Festival Agent API",
    description="AI-powered event and road closure detection system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EventRequest(BaseModel):
    location: str  # "lat,lng" or address
    radius_km: int = 5
    date_range: List[str] = []  # ["YYYY-MM-DD", "YYYY-MM-DD"]


class EventInfo(BaseModel):
    name: str
    location: str
    start_date: Optional[str]
    end_date: Optional[str]
    impact_level: str  # "low", "medium", "high"
    description: str
    road_closures: List[str]
    alternate_routes: List[str]


class EventResponse(BaseModel):
    query_location: str
    search_radius_km: int
    events_found: int
    events: List[EventInfo]
    overall_impact: str
    recommendations: List[str]


# Mock festival/event data for demonstration
MOCK_EVENTS = [
    {
        "name": "Ganesh Chaturthi Festival",
        "location": "Lalbaugcha Raja, Mumbai",
        "coordinates": (19.0176, 72.8562),
        "start_date": "2026-08-29",
        "end_date": "2026-09-07",
        "impact_level": "high",
        "description": "Major religious festival causing significant traffic disruption",
        "road_closures": [
            "Dr. Baba Saheb Ambedkar Road (partial)",
            "Tulsi Pipe Road",
            "N.M. Joshi Marg (diversions)"
        ],
        "alternate_routes": [
            "Use Western Express Highway",
            "Take Sion-Panvel Highway", 
            "Avoid Lalbaug area between 6 PM - 11 PM"
        ]
    },
    {
        "name": "Navratri Celebrations",
        "location": "Borivali West, Mumbai",
        "coordinates": (19.2300, 72.8500),
        "start_date": "2026-10-15",
        "end_date": "2026-10-23",
        "impact_level": "medium",
        "description": "Local cultural festival with moderate traffic impact",
        "road_closures": [
            "S.V. Road (evening hours)",
            "Chandavarkar Road"
        ],
        "alternate_routes": [
            "Use Link Road",
            "Take Western Express Highway"
        ]
    },
    {
        "name": "Mumbai Marathon",
        "location": "Marine Drive to Bandra, Mumbai",
        "coordinates": (18.9220, 72.8347),
        "start_date": "2026-01-15",
        "end_date": "2026-01-15",
        "impact_level": "high",
        "description": "Annual marathon event causing major road closures",
        "road_closures": [
            "Marine Drive (complete closure)",
            "Bandra-Worli Sea Link",
            "Annie Besant Road",
            "Worli Sea Face"
        ],
        "alternate_routes": [
            "Use Eastern Express Highway",
            "Take Harbour Line route",
            "Avoid South Mumbai 5 AM - 1 PM"
        ]
    }
]


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate approximate distance in kilometers"""
    # Simple distance calculation (not accurate for large distances)
    lat_diff = abs(lat1 - lat2) * 111  # 1 degree lat ≈ 111 km
    lng_diff = abs(lng1 - lng2) * 111 * 0.855  # Approximate for Mumbai latitude
    return (lat_diff**2 + lng_diff**2)**0.5


def parse_location(location_str: str) -> tuple:
    """Parse location string to coordinates"""
    try:
        if "," in location_str:
            lat, lng = location_str.split(",")
            return float(lat.strip()), float(lng.strip())
    except:
        pass
    
    # Default to Mumbai center if parsing fails
    return 19.0760, 72.8777


def filter_events_by_location(events: List[Dict], location: tuple, radius_km: int) -> List[Dict]:
    """Filter events by location and radius"""
    filtered = []
    target_lat, target_lng = location
    
    for event in events:
        event_lat, event_lng = event["coordinates"]
        distance = calculate_distance(target_lat, target_lng, event_lat, event_lng)
        
        if distance <= radius_km:
            event_copy = event.copy()
            event_copy["distance_km"] = round(distance, 2)
            filtered.append(event_copy)
    
    return filtered


def filter_events_by_date(events: List[Dict], date_range: List[str]) -> List[Dict]:
    """Filter events by date range"""
    if not date_range:
        return events
    
    try:
        start_filter = datetime.strptime(date_range[0], "%Y-%m-%d")
        end_filter = datetime.strptime(date_range[1], "%Y-%m-%d") if len(date_range) > 1 else start_filter
    except:
        return events
    
    filtered = []
    for event in events:
        try:
            event_start = datetime.strptime(event["start_date"], "%Y-%m-%d")
            event_end = datetime.strptime(event.get("end_date", event["start_date"]), "%Y-%m-%d")
            
            # Check if event overlaps with filter range
            if event_start <= end_filter and event_end >= start_filter:
                filtered.append(event)
        except:
            # Include event if date parsing fails
            filtered.append(event)
    
    return filtered


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Festival Agent API is running",
        "events_database": len(MOCK_EVENTS)
    }


@app.post("/scan-events", response_model=EventResponse)
async def scan_events(request: EventRequest):
    """Scan for festivals and events in the specified area"""
    
    # Parse location
    coordinates = parse_location(request.location)
    
    # Filter events by location
    nearby_events = filter_events_by_location(MOCK_EVENTS, coordinates, request.radius_km)
    
    # Filter events by date if specified
    if request.date_range:
        nearby_events = filter_events_by_date(nearby_events, request.date_range)
    
    # Convert to response format
    events = []
    overall_impact = "low"
    
    for event_data in nearby_events:
        event_info = EventInfo(
            name=event_data["name"],
            location=event_data["location"],
            start_date=event_data.get("start_date"),
            end_date=event_data.get("end_date"),
            impact_level=event_data["impact_level"],
            description=event_data["description"],
            road_closures=event_data["road_closures"],
            alternate_routes=event_data["alternate_routes"]
        )
        events.append(event_info)
        
        # Update overall impact
        if event_data["impact_level"] == "high":
            overall_impact = "high"
        elif event_data["impact_level"] == "medium" and overall_impact == "low":
            overall_impact = "medium"
    
    # Generate recommendations
    recommendations = []
    if not events:
        recommendations = ["No major events detected in the area", "Normal traffic conditions expected"]
    else:
        if overall_impact == "high":
            recommendations = [
                "High impact events detected - Plan alternate routes",
                "Allow extra travel time",
                "Check real-time traffic updates",
                "Consider public transportation"
            ]
        elif overall_impact == "medium":
            recommendations = [
                "Moderate event activity in the area",
                "Minor delays possible",
                "Monitor traffic conditions"
            ]
        else:
            recommendations = [
                "Low impact events detected",
                "Minimal traffic disruption expected"
            ]
    
    return EventResponse(
        query_location=request.location,
        search_radius_km=request.radius_km,
        events_found=len(events),
        events=events,
        overall_impact=overall_impact,
        recommendations=recommendations
    )


@app.get("/road-closures")
async def get_road_closures(location: str, radius_km: int = 5):
    """Get active road closures in the area"""
    
    coordinates = parse_location(location)
    nearby_events = filter_events_by_location(MOCK_EVENTS, coordinates, radius_km)
    
    all_closures = []
    for event in nearby_events:
        for closure in event["road_closures"]:
            all_closures.append({
                "road": closure,
                "cause": event["name"],
                "impact": event["impact_level"],
                "start_date": event.get("start_date"),
                "end_date": event.get("end_date")
            })
    
    return {
        "location": location,
        "active_closures": len(all_closures),
        "closures": all_closures
    }


@app.get("/event-impact")
async def get_event_impact(location: str, date: str = None):
    """Get event impact analysis for a specific location and date"""
    
    coordinates = parse_location(location)
    
    # Filter by date if provided
    events_to_check = MOCK_EVENTS
    if date:
        events_to_check = filter_events_by_date(MOCK_EVENTS, [date, date])
    
    nearby_events = filter_events_by_location(events_to_check, coordinates, 10)  # 10km radius
    
    impact_score = 0
    for event in nearby_events:
        if event["impact_level"] == "high":
            impact_score += 3
        elif event["impact_level"] == "medium":
            impact_score += 2
        else:
            impact_score += 1
    
    return {
        "location": location,
        "date": date or "current",
        "impact_score": impact_score,
        "impact_level": "high" if impact_score >= 5 else "medium" if impact_score >= 2 else "low",
        "affecting_events": len(nearby_events),
        "recommendations": [
            "High traffic disruption expected" if impact_score >= 5 else
            "Moderate disruption possible" if impact_score >= 2 else
            "Normal conditions expected"
        ]
    }


@app.post("/a2a/receive")
async def receive_a2a_message(message: AgentMessage):
    """Receive A2A messages from other agents"""
    print(f"Festival Agent received message from {message.sender_agent}: {message.message_type}")
    
    # Process festival/event requests from other agents
    if message.message_type == MessageType.REQUEST:
        payload = message.payload
        
        # Handle event scanning requests
        if "location" in payload:
            try:
                request = EventRequest(
                    location=payload["location"],
                    radius_km=payload.get("radius_km", 5),
                    date_range=payload.get("date_range", [])
                )
                
                # Reuse the existing event scanning logic
                result = await scan_events(request)
                
                return {
                    "status": "success",
                    "agent_type": "festival",
                    "message_id": message.message_id,
                    "data": result.model_dump()
                }
                
            except Exception as e:
                return {
                    "status": "error",
                    "agent_type": "festival",
                    "message_id": message.message_id,
                    "error": str(e)
                }
    
    return {"status": "received", "message_id": message.message_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
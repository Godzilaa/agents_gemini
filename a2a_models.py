from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class AgentType(str, Enum):
    FOOD = "food"
    REGULATORY = "regulatory" 
    TRANSPORT = "transport"
    FESTIVAL = "festival"
    DECISION = "decision"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MessageType(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    QUERY = "query"
    STATUS = "status"


class Location(BaseModel):
    latitude: float
    longitude: float
    address: Optional[str] = None


class AgentMessage(BaseModel):
    """Standard message format for A2A communication"""
    message_id: str
    sender_agent: AgentType
    receiver_agent: AgentType
    message_type: MessageType
    priority: Priority
    timestamp: datetime
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None  # For request-response correlation


class AgentCapability(BaseModel):
    """Describes what an agent can do"""
    agent_type: AgentType
    capabilities: List[str]
    endpoints: List[str]
    data_provided: List[str]
    data_required: List[str]


class UserContext(BaseModel):
    """User's current context and preferences"""
    location: Location
    vehicle_type: Optional[str] = None
    preferences: Dict[str, Any] = {}
    urgency_level: Priority = Priority.MEDIUM
    destination: Optional[Location] = None
    activity_type: Optional[str] = None  # dining, commute, event, etc.


class AgentResponse(BaseModel):
    """Standard response from any agent"""
    agent_type: AgentType
    success: bool
    data: Dict[str, Any]
    confidence_score: float
    processing_time: float
    warnings: List[str] = []
    recommendations: List[str] = []


class DecisionRequest(BaseModel):
    """Request to the master decision agent"""
    user_context: UserContext
    query_type: str  # "dining_recommendation", "route_planning", "area_analysis", etc.
    additional_params: Dict[str, Any] = {}


class FinalDecision(BaseModel):
    """Final coordinated decision from master agent"""
    decision_id: str
    user_query: str
    location: Location
    primary_recommendation: str
    confidence_score: float
    agent_contributions: Dict[str, AgentResponse]
    combined_recommendations: List[str]
    warnings: List[str]
    additional_info: Dict[str, Any]
    timestamp: datetime


class A2AProtocol(BaseModel):
    """Protocol definition for agent-to-agent communication"""
    protocol_version: str = "1.0"
    supported_message_types: List[MessageType]
    max_retry_attempts: int = 3
    timeout_seconds: int = 30
    authentication_required: bool = False


# Agent Registry - defines all available agents and their capabilities
AGENT_REGISTRY = {
    AgentType.FOOD: AgentCapability(
        agent_type=AgentType.FOOD,
        capabilities=[
            "restaurant_recommendations",
            "hidden_gem_detection", 
            "hygiene_analysis",
            "vegetarian_detection",
            "night_dining_spots"
        ],
        endpoints=[
            "/recommendations",
            "/place/{place_id}",
            "/health"
        ],
        data_provided=[
            "restaurant_list",
            "ratings_scores",
            "location_data",
            "opening_hours",
            "cuisine_types"
        ],
        data_required=[
            "user_location",
            "radius",
            "preferences"
        ]
    ),
    
    AgentType.REGULATORY: AgentCapability(
        agent_type=AgentType.REGULATORY,
        capabilities=[
            "traffic_enforcement_detection",
            "regulation_zone_analysis",
            "police_density_scoring",
            "risk_assessment",
            "parking_violation_alerts"
        ],
        endpoints=[
            "/regulatory-analysis",
            "/nearby-police",
            "/nearby-toll-booths", 
            "/nearby-parking",
            "/zones"
        ],
        data_provided=[
            "risk_scores",
            "enforcement_zones",
            "police_locations",
            "parking_info",
            "violation_warnings"
        ],
        data_required=[
            "user_location",
            "vehicle_type",
            "route_info"
        ]
    ),
    
    AgentType.TRANSPORT: AgentCapability(
        agent_type=AgentType.TRANSPORT,
        capabilities=[
            "traffic_analysis",
            "congestion_prediction",
            "travel_mode_detection",
            "arrival_time_estimation",
            "parking_difficulty_assessment"
        ],
        endpoints=[
            "/transport-analysis",
            "/traffic-conditions",
            "/route-optimization"
        ],
        data_provided=[
            "congestion_scores",
            "travel_times",
            "traffic_conditions",
            "parking_availability",
            "route_suggestions"
        ],
        data_required=[
            "origin_location",
            "destination_location",
            "travel_mode",
            "time_of_day"
        ]
    ),
    
    AgentType.FESTIVAL: AgentCapability(
        agent_type=AgentType.FESTIVAL,
        capabilities=[
            "event_detection",
            "road_closure_alerts",
            "festival_impact_analysis",
            "crowd_density_prediction"
        ],
        endpoints=[
            "/scan-events",
            "/road-closures",
            "/event-impact"
        ],
        data_provided=[
            "event_list",
            "road_closures",
            "crowd_predictions",
            "alternate_routes"
        ],
        data_required=[
            "location",
            "date_range",
            "event_types"
        ]
    )
}


# Communication templates for different scenarios
class CommunicationTemplates:
    
    @staticmethod
    def create_food_request(user_location: Location, preferences: Dict[str, Any]) -> AgentMessage:
        return AgentMessage(
            message_id=f"food_req_{datetime.now().timestamp()}",
            sender_agent=AgentType.DECISION,
            receiver_agent=AgentType.FOOD,
            message_type=MessageType.REQUEST,
            priority=Priority.MEDIUM,
            timestamp=datetime.now(),
            payload={
                "latitude": user_location.latitude,
                "longitude": user_location.longitude,
                "radius": preferences.get("radius", 2000),
                "limit": preferences.get("limit", 10),
                "cuisine_type": preferences.get("cuisine_type"),
                "price_range": preferences.get("price_range")
            }
        )
    
    @staticmethod 
    def create_regulatory_request(user_location: Location, vehicle_type: str) -> AgentMessage:
        return AgentMessage(
            message_id=f"reg_req_{datetime.now().timestamp()}",
            sender_agent=AgentType.DECISION,
            receiver_agent=AgentType.REGULATORY,
            message_type=MessageType.REQUEST,
            priority=Priority.HIGH,
            timestamp=datetime.now(),
            payload={
                "latitude": user_location.latitude,
                "longitude": user_location.longitude,
                "vehicle_type": vehicle_type
            }
        )
    
    @staticmethod
    def create_transport_request(origin: Location, destination: Location, vehicle_type: str) -> AgentMessage:
        return AgentMessage(
            message_id=f"transport_req_{datetime.now().timestamp()}",
            sender_agent=AgentType.DECISION,
            receiver_agent=AgentType.TRANSPORT,
            message_type=MessageType.REQUEST,
            priority=Priority.MEDIUM,
            timestamp=datetime.now(),
            payload={
                "origin_latitude": origin.latitude,
                "origin_longitude": origin.longitude,
                "destination_latitude": destination.latitude,
                "destination_longitude": destination.longitude,
                "vehicle_type": vehicle_type,
                "current_time": datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def create_festival_request(location: Location, date_range: List[str]) -> AgentMessage:
        return AgentMessage(
            message_id=f"festival_req_{datetime.now().timestamp()}",
            sender_agent=AgentType.DECISION,
            receiver_agent=AgentType.FESTIVAL,
            message_type=MessageType.REQUEST,
            priority=Priority.MEDIUM,
            timestamp=datetime.now(),
            payload={
                "location": f"{location.latitude},{location.longitude}",
                "address": location.address,
                "date_range": date_range,
                "radius_km": 5
            }
        )
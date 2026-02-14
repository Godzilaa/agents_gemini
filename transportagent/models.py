from pydantic import BaseModel, Field
from typing import Optional

class TransportRequest(BaseModel):
    latitude: float
    longitude: float
    speed: float = Field(..., description="Current speed in km/h")
    time: str = Field(..., description="Current time in ISO 8601 format or HH:MM string")
    destination: Optional[str] = Field(None, description="Optional destination address or coordinates")
    language: str = Field("en", description="Language code for advisory (default: en)")

class TransportResponse(BaseModel):
    travel_mode: str
    zone_type: str
    forward_prediction: str
    congestion_score: float = Field(..., ge=0, le=10)
    risk_level: str
    advisory: str
    confidence_score: float = Field(..., ge=0, le=100)

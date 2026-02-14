from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class VehicleType(str, Enum):
    BIKE = "bike"
    CAR = "car"
    AUTO = "auto"


class ZoneType(str, Enum):
    HELMET_ENFORCEMENT = "helmet"
    PARKING = "parking"
    SIGNAL_CAMERA = "signal_camera"
    TOW_ZONE = "tow_zone"
    SCHOOL_ZONE = "school_zone"
    ONE_WAY_STRICT = "one_way_strict"
    HEAVY_TRAFFIC = "heavy_traffic"
    NO_HONK = "no_honk"


class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class Location(BaseModel):
    latitude: float
    longitude: float


class UserRequest(BaseModel):
    latitude: float
    longitude: float
    vehicle_type: VehicleType


class RoadSegment(BaseModel):
    latitude: float
    longitude: float
    placeId: Optional[str]
    snappedPosition: dict


class RegulationZone(BaseModel):
    id: str
    zone_type: ZoneType
    name: str
    description: str
    active_hours: Optional[dict]  # {"start": "07:00", "end": "22:00"}
    risk_weight: float
    geometry: dict  # GeoJSON polygon


class RegulatoryAdvice(BaseModel):
    risk_score: float
    risk_level: RiskLevel
    applicable_zones: List[RegulationZone]
    warnings: List[str]
    recommendations: List[str]
    current_location: Location
    snapped_location: Optional[Location]
    police_density_score: float
    government_area_risk: float


class TimeRange(BaseModel):
    start_time: str  # "HH:MM"
    end_time: str    # "HH:MM"


class PoliceStation(BaseModel):
    name: str
    latitude: float
    longitude: float
    distance_km: float

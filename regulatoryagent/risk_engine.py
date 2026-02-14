from typing import List, Dict, Tuple
from datetime import datetime
from models import ZoneType, VehicleType, RiskLevel, RegulationZone
from google_apis import calculate_distance
import math


# Zone weight mapping
ZONE_WEIGHTS = {
    ZoneType.SIGNAL_CAMERA: 3.0,
    ZoneType.TOW_ZONE: 4.0,
    ZoneType.HELMET_ENFORCEMENT: 2.0,
    ZoneType.SCHOOL_ZONE: 2.0,
    ZoneType.ONE_WAY_STRICT: 3.0,
    ZoneType.HEAVY_TRAFFIC: 2.5,
    ZoneType.NO_HONK: 1.5
}

MAX_POSSIBLE_SCORE = sum(ZONE_WEIGHTS.values())


def is_time_active(active_hours: Dict) -> bool:
    """
    STEP 5: Check if current time falls within zone's active hours
    """
    if not active_hours:
        return True  # Zone is always active

    try:
        current_time = datetime.now().time()
        start_time = datetime.strptime(active_hours.get("start", "00:00"), "%H:%M").time()
        end_time = datetime.strptime(active_hours.get("end", "23:59"), "%H:%M").time()

        return start_time <= current_time <= end_time

    except Exception as e:
        print(f"Error checking time: {e}")
        return True


def apply_vehicle_filter(zones: List[RegulationZone], vehicle_type: VehicleType) -> List[RegulationZone]:
    """
    STEP 6: Filter zones based on vehicle type
    """
    filtered_zones = []

    for zone in zones:
        zone_type = zone.zone_type

        # Bike-specific zones
        if vehicle_type == VehicleType.BIKE:
            if zone_type in [ZoneType.HELMET_ENFORCEMENT, ZoneType.NO_HONK]:
                filtered_zones.append(zone)
            elif zone_type in [ZoneType.SIGNAL_CAMERA, ZoneType.ONE_WAY_STRICT]:
                filtered_zones.append(zone)

        # Car-specific zones
        elif vehicle_type == VehicleType.CAR:
            if zone_type in [ZoneType.TOW_ZONE, ZoneType.PARKING]:
                filtered_zones.append(zone)
            elif zone_type in [ZoneType.SIGNAL_CAMERA, ZoneType.ONE_WAY_STRICT, ZoneType.HEAVY_TRAFFIC]:
                filtered_zones.append(zone)

        # Auto (3-wheeler) specific zones
        elif vehicle_type == VehicleType.AUTO:
            if zone_type in [ZoneType.ONE_WAY_STRICT, ZoneType.HEAVY_TRAFFIC]:
                filtered_zones.append(zone)
            elif zone_type in [ZoneType.SIGNAL_CAMERA]:
                filtered_zones.append(zone)

    return filtered_zones


def compute_risk_score(applicable_zones: List[RegulationZone], 
                      police_density_score: float,
                      government_area_risk: float) -> float:
    """
    STEP 4: Compute risk score from multiple factors
    
    Weights:
    - Zone-based: 50%
    - Police density: 30%
    - Government area: 20%
    """
    # Calculate zone-based score
    zone_score = 0
    for zone in applicable_zones:
        if is_time_active(zone.active_hours):
            zone_score += zone.risk_weight

    # Normalize zone score to 0-10
    if zone_score > 0:
        zone_score = min(10, (zone_score / MAX_POSSIBLE_SCORE) * 10)

    # Normalize police density score (0-5)
    normalized_police_score = min(5, police_density_score)

    # Normalize government area risk (0-5)
    normalized_govt_score = min(5, government_area_risk)

    # Weighted combination
    final_score = (zone_score * 0.5) + (normalized_police_score * 0.3) + (normalized_govt_score * 0.2)

    return round(min(10, final_score), 2)


def determine_risk_level(risk_score: float) -> RiskLevel:
    """
    STEP 7: Determine risk level from score
    """
    if risk_score >= 7:
        return RiskLevel.HIGH
    elif risk_score >= 4:
        return RiskLevel.MODERATE
    else:
        return RiskLevel.LOW


def compute_police_density_score(police_stations: List[Dict], latitude: float, longitude: float) -> float:
    """
    STEP 7: Heuristic - Police density detection
    
    If 3+ police stations within 1km: +3 risk
    If 2 police stations within 1km: +2 risk
    If 1 police station within 1km: +1 risk
    """
    score = 0

    # Check police stations within 1km
    nearby_police = [
        station for station in police_stations
        if calculate_distance(latitude, longitude, station["latitude"], station["longitude"]) <= 1
    ]

    if len(nearby_police) >= 3:
        score += 3
    elif len(nearby_police) == 2:
        score += 2
    elif len(nearby_police) == 1:
        score += 1

    # Check for traffic police offices (higher enforcement likelihood)
    traffic_police = [
        station for station in police_stations
        if "traffic" in str(station.get("types", [])).lower()
    ]

    if len(traffic_police) > 0:
        score += 1.5

    return score


def compute_government_area_risk(government_buildings: List[Dict], 
                                  latitude: float, longitude: float) -> float:
    """
    STEP 7: Heuristic - Government area detection
    
    Courts: +2.5
    Secretariat: +2.0
    Other govt offices: +1.0
    """
    score = 0

    for building in government_buildings:
        distance = calculate_distance(
            latitude, longitude,
            building["latitude"], building["longitude"]
        )

        if distance <= 0.5:  # Within 500m
            building_type = building.get("building_type", "").lower()

            if "courthouse" in building_type or "court" in building_type:
                score += 2.5
            elif "secretariat" in building_type:
                score += 2.0
            else:
                score += 1.0

    return score


def generate_warnings(applicable_zones: List[RegulationZone], 
                     risk_score: float,
                     vehicle_type: VehicleType) -> List[str]:
    """
    Generate warnings based on applicable zones and risk score
    """
    warnings = []

    for zone in applicable_zones:
        if not is_time_active(zone.active_hours):
            continue

        if zone.zone_type == ZoneType.HELMET_ENFORCEMENT:
            warnings.append("⚠️ Helmet enforcement active - Ensure helmet is worn properly")

        elif zone.zone_type == ZoneType.SIGNAL_CAMERA:
            warnings.append("📹 Traffic signal cameras active - Follow traffic rules strictly")

        elif zone.zone_type == ZoneType.TOW_ZONE:
            warnings.append("🚫 Tow zone active - Illegal parking will result in vehicle tow")

        elif zone.zone_type == ZoneType.SCHOOL_ZONE:
            warnings.append("👶 School zone - Reduce speed and be cautious")

        elif zone.zone_type == ZoneType.ONE_WAY_STRICT:
            warnings.append("🛑 One-way street with strict enforcement")

        elif zone.zone_type == ZoneType.HEAVY_TRAFFIC:
            warnings.append("🚗 Heavy traffic zone - Follow lane discipline")

        elif zone.zone_type == ZoneType.NO_HONK:
            warnings.append("🔇 No-honk zone - Avoid honking")

    if risk_score >= 7:
        warnings.append("🚨 HIGH ENFORCEMENT ZONE - Multiple active regulations")

    return warnings


def generate_recommendations(applicable_zones: List[RegulationZone],
                             risk_level: RiskLevel,
                             vehicle_type: VehicleType) -> List[str]:
    """
    Generate recommendations based on risk level and vehicle type
    """
    recommendations = []

    if risk_level == RiskLevel.HIGH:
        recommendations.append("Consider alternative route to avoid enforcement zones")
        recommendations.append("Ensure all vehicle documents and license are valid")

    if risk_level in [RiskLevel.HIGH, RiskLevel.MODERATE]:
        recommendations.append("Follow all traffic signs and road markings")
        recommendations.append("Maintain safe speed and distance from other vehicles")

    if vehicle_type == VehicleType.BIKE:
        recommendations.append("Wear helmet and safety gear")
        recommendations.append("Avoid double riding or triple riding")

    elif vehicle_type == VehicleType.CAR:
        recommendations.append("Park only in designated parking zones")
        recommendations.append("Check parking time restrictions")

    # General recommendations
    if risk_level == RiskLevel.LOW:
        recommendations.append("✅ Area has low enforcement activity - Drive normally but cautiously")
    else:
        recommendations.append("Stay vigilant and follow all traffic regulations")

    return recommendations

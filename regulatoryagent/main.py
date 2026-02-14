from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from models import UserRequest, RegulatoryAdvice, Location
from google_apis import (
    snap_to_road,
    find_nearby_police_stations,
    find_nearby_government_buildings,
    find_nearby_toll_booths,
    find_nearby_parking_lots,
    calculate_distance
)
from risk_engine import (
    apply_vehicle_filter,
    compute_risk_score,
    determine_risk_level,
    compute_police_density_score,
    compute_government_area_risk,
    generate_warnings,
    generate_recommendations
)

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Regulatory Agent API",
    description="AI-powered traffic and regulatory enforcement detection system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mock database for regulation zones (in production, use PostGIS)
MOCK_ZONES = [
    {
        "id": "zone_helmet_mg_road",
        "zone_type": "helmet",
        "name": "MG Road Helmet Enforcement",
        "description": "Strict helmet enforcement on MG Road stretch",
        "active_hours": {"start": "07:00", "end": "22:00"},
        "risk_weight": 2.0,
        "latitude_range": (19.0750, 19.0800),
        "longitude_range": (72.8750, 72.8800)
    },
    {
        "id": "zone_tow_central",
        "zone_type": "tow_zone",
        "name": "Central Business District Tow Zone",
        "description": "Illegal parking will result in vehicle tow",
        "active_hours": {"start": "06:00", "end": "23:00"},
        "risk_weight": 4.0,
        "latitude_range": (19.0700, 19.0900),
        "longitude_range": (72.8700, 72.8900)
    },
    {
        "id": "zone_camera_junction",
        "zone_type": "signal_camera",
        "name": "Traffic Signal Camera Junction",
        "description": "Red light camera active at all signals",
        "active_hours": {"start": "00:00", "end": "23:59"},
        "risk_weight": 3.0,
        "latitude_range": (19.0680, 19.0720),
        "longitude_range": (72.8680, 72.8720)
    },
    {
        "id": "zone_school",
        "zone_type": "school_zone",
        "name": "School Zone - 200m Radius",
        "description": "Reduced speed zone near school",
        "active_hours": {"start": "07:00", "end": "18:00"},
        "risk_weight": 2.0,
        "latitude_range": (19.0760, 19.0780),
        "longitude_range": (72.8770, 72.8790)
    }
]


def get_applicable_zones(latitude: float, longitude: float):
    """
    Get regulation zones that contain the user's location
    In production, use PostGIS: ST_Contains(geometry, user_location)
    """
    applicable = []

    for zone in MOCK_ZONES:
        lat_min, lat_max = zone["latitude_range"]
        lon_min, lon_max = zone["longitude_range"]

        if lat_min <= latitude <= lat_max and lon_min <= longitude <= lon_max:
            applicable.append({
                "id": zone["id"],
                "zone_type": zone["zone_type"],
                "name": zone["name"],
                "description": zone["description"],
                "active_hours": zone["active_hours"],
                "risk_weight": zone["risk_weight"],
                "geometry": {}
            })

    return applicable


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Regulatory Agent API is running",
        "version": "1.0.0"
    }


@app.post("/regulatory-analysis", response_model=RegulatoryAdvice)
async def analyze_regulatory_risk(request: UserRequest):
    """
    Main regulatory analysis endpoint
    
    STEP 1: Snap to road
    STEP 2: Detect regulatory anchors (police, government buildings)
    STEP 3: Find intersecting zones
    STEP 4: Compute risk score
    STEP 5: Generate advice
    """

    try:
        # STEP 1: Snap user location to road
        snapped = snap_to_road(request.latitude, request.longitude)
        snapped_location = None

        if snapped:
            snapped_location = Location(
                latitude=snapped["latitude"],
                longitude=snapped["longitude"]
            )
            working_lat, working_lon = snapped["latitude"], snapped["longitude"]
        else:
            working_lat, working_lon = request.latitude, request.longitude

        # STEP 2: Detect regulatory anchors
        police_stations = find_nearby_police_stations(working_lat, working_lon, radius=5000)
        government_buildings = find_nearby_government_buildings(working_lat, working_lon, radius=5000)
        toll_booths = find_nearby_toll_booths(working_lat, working_lon, radius=5000)
        parking_lots = find_nearby_parking_lots(working_lat, working_lon, radius=2000)

        # STEP 3: Find intersecting zones
        applicable_zones_raw = get_applicable_zones(working_lat, working_lon)

        # Convert to proper format
        applicable_zones = [
            {
                "id": z["id"],
                "zone_type": z["zone_type"],
                "name": z["name"],
                "description": z["description"],
                "active_hours": z["active_hours"],
                "risk_weight": z["risk_weight"],
                "geometry": {}
            }
            for z in applicable_zones_raw
        ]

        # STEP 6: Apply vehicle-specific filtering
        vehicle_filtered_zones = apply_vehicle_filter(applicable_zones, request.vehicle_type)

        # STEP 7: Compute heuristic scores
        police_density_score = compute_police_density_score(police_stations, working_lat, working_lon)
        government_area_risk = compute_government_area_risk(government_buildings, working_lat, working_lon)

        # STEP 4: Compute overall risk score
        risk_score = compute_risk_score(
            vehicle_filtered_zones,
            police_density_score,
            government_area_risk
        )

        # Determine risk level
        risk_level = determine_risk_level(risk_score)

        # STEP 8: Generate warnings and recommendations
        warnings = generate_warnings(vehicle_filtered_zones, risk_score, request.vehicle_type)
        recommendations = generate_recommendations(
            vehicle_filtered_zones,
            risk_level,
            request.vehicle_type
        )

        # Build response
        return RegulatoryAdvice(
            risk_score=risk_score,
            risk_level=risk_level,
            applicable_zones=vehicle_filtered_zones,
            warnings=warnings,
            recommendations=recommendations,
            current_location=Location(latitude=request.latitude, longitude=request.longitude),
            snapped_location=snapped_location,
            police_density_score=police_density_score,
            government_area_risk=government_area_risk
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing regulatory risk: {str(e)}")


@app.get("/nearby-police")
async def get_nearby_police(latitude: float, longitude: float, radius: int = 5000):
    """Get nearby police stations"""
    try:
        police_stations = find_nearby_police_stations(latitude, longitude, radius)
        return {
            "count": len(police_stations),
            "police_stations": police_stations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/nearby-toll-booths")
async def get_nearby_toll(latitude: float, longitude: float, radius: int = 5000):
    """Get nearby toll booths"""
    try:
        toll_booths = find_nearby_toll_booths(latitude, longitude, radius)
        return {
            "count": len(toll_booths),
            "toll_booths": toll_booths
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/nearby-parking")
async def get_nearby_parking(latitude: float, longitude: float, radius: int = 2000):
    """Get nearby parking lots"""
    try:
        parking_lots = find_nearby_parking_lots(latitude, longitude, radius)
        return {
            "count": len(parking_lots),
            "parking_lots": parking_lots
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/zones")
async def get_all_zones():
    """Get all available regulation zones"""
    return {
        "total_zones": len(MOCK_ZONES),
        "zones": MOCK_ZONES
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

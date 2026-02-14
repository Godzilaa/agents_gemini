from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from datetime import datetime

try:
    from .models import TransportRequest, TransportResponse
    from .prediction_engine import (
        detect_travel_mode,
        predict_mobility_condition,
        estimate_arrival_time,
        estimate_parking_difficulty,
        analyze_area_density
    )
    from .scoring_engine import (
        compute_congestion_score,
        compute_risk_level,
        compute_confidence_score
    )
    from .traffic_api import get_area_type, get_travel_time
    from .language_engine import translate_advisory
except ImportError:
    from models import TransportRequest, TransportResponse
    from prediction_engine import (
        detect_travel_mode,
        predict_mobility_condition,
        estimate_arrival_time,
        estimate_parking_difficulty,
        analyze_area_density
    )
    from scoring_engine import (
        compute_congestion_score,
        compute_risk_level,
        compute_confidence_score
    )
    from traffic_api import get_area_type, get_travel_time
    from language_engine import translate_advisory

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Transport Agent API",
    description="AI-powered mobility and congestion analysis engine",
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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Transport Agent API is running"}


@app.post("/analyze", response_model=TransportResponse)
async def analyze_transport(request: TransportRequest):
    """
    Analyze mobility context and provide predictions.
    """
    
    # Extract request data
    lat = request.latitude
    lon = request.longitude
    speed = request.speed
    time_str = request.time
    destination = request.destination
    language = request.language
    
    # Parse time (simplified)
    try:
        if ":" in time_str and len(time_str) <= 5:
            hour = int(time_str.split(":")[0])
        else:
            hour = datetime.now().hour
    except:
        hour = datetime.now().hour

    # 1. Detect Context & Mode
    mode = detect_travel_mode(speed)
    area_type = get_area_type(lat, lon)
    
    # 2. Compute Base Scores
    congestion_score = compute_congestion_score(speed, area_type, hour)
    risk_level = compute_risk_level(congestion_score)
    confidence_score = compute_confidence_score()
    
    forward_prediction = ""
    advisory = ""
    
    # 3. Logic based on Destination (Ambient vs Destination Mode)
    if not destination:
        # Ambient Mode
        condition = predict_mobility_condition(mode, congestion_score)
        forward_prediction = f"Next 15m: {condition}"
        advisory = f"Current zone is {area_type}. Traffic flow is {condition.lower()}."
        
    else:
        # Destination Mode
        # In real app, we would use traffic_api.get_travel_time(origin, dest) logic here
        
        # Estimate predictions
        parking_diff = estimate_parking_difficulty(area_type, hour) # Using current area for simplicity in mock
        density = analyze_area_density(area_type)
        
        forward_prediction = f"Arrival: {int(congestion_score * 10)}% Congestion Probability"
        advisory = f"Route to {destination} analyzed. Expect {density} area with {parking_diff} parking difficulty."

    # 4. Translate Advisory
    if language != "en":
        advisory = translate_advisory(advisory, language)

    # 5. Construct Response
    return TransportResponse(
        travel_mode=mode,
        zone_type=area_type,
        forward_prediction=forward_prediction,
        congestion_score=congestion_score,
        risk_level=risk_level,
        advisory=advisory,
        confidence_score=confidence_score
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

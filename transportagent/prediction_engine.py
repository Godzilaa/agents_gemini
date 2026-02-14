from datetime import datetime, timedelta

def detect_travel_mode(speed: float) -> str:
    """
    Detect travel mode based on speed (km/h).
    """
    if speed <= 6:
        return "Walking"
    elif speed <= 25:
        return "Bike"
    elif speed <= 60:
        return "Driving"
    else:
        return "Highway"

def predict_mobility_condition(mode: str, congestion_score: float) -> str:
    """
    Predict forward mobility condition based on mode and congestion.
    """
    if congestion_score > 7:
        return "Heavy Delays Expected"
    elif congestion_score > 4:
        return "Moderate Traffic"
    else:
        return "Smooth Flow"

def estimate_arrival_time(distance_km: float, speed: float) -> str:
    """
    Estimate arrival time.
    """
    if speed <= 0:
        return "Unknown"
    
    hours = distance_km / speed
    arrival_time = datetime.now() + timedelta(hours=hours)
    return arrival_time.strftime("%H:%M")

def estimate_parking_difficulty(area_type: str, time_hour: int) -> str:
    """
    Estimate parking difficulty.
    """
    if area_type == "Commercial" and (9 <= time_hour <= 18):
        return "High"
    elif area_type == "Residential" and (18 <= time_hour <= 8):
        return "Medium"
    return "Low"

def analyze_area_density(area_type: str) -> str:
    """
    Mock area density analysis.
    """
    if area_type == "Commercial":
        return "High Density"
    elif area_type == "Residential":
        return "Medium Density"
    return "Low Density"

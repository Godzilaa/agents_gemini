def compute_congestion_score(speed: float, area_type: str, time_hour: int) -> float:
    """
    Compute congestion score (0-10) based on speed, area, and time.
    """
    base_score = 0.0
    
    # Peak hours (8-10 AM, 5-7 PM)
    is_peak = (8 <= time_hour <= 10) or (17 <= time_hour <= 19)
    
    if is_peak:
        base_score += 4.0
    elif 11 <= time_hour <= 16:
        base_score += 2.0
    
    # Area type impact
    if area_type == "Commercial":
        base_score += 3.0
    elif area_type == "Residential":
        base_score += 1.0
        
    # Speed impact (lower speed = higher congestion)
    if speed < 10:
        base_score += 4.0
    elif speed < 25:
        base_score += 2.0
    elif speed > 50:
        base_score -= 1.0 # Free flow

    return round(max(0.0, min(10.0, base_score)), 1)

def compute_risk_level(congestion_score: float) -> str:
    """
    Determine risk level based on congestion score.
    """
    if congestion_score >= 8:
        return "Severe"
    elif congestion_score >= 6:
        return "High"
    elif congestion_score >= 4:
        return "Moderate"
    else:
        return "Low"

def compute_confidence_score(data_quality: str = "High") -> float:
    """
    Calculate confidence score based on data quality.
    """
    base_confidence = 85.0
    if data_quality == "Medium":
        base_confidence = 70.0
    elif data_quality == "Low":
        base_confidence = 50.0
        
    return base_confidence

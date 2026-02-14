from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from models import RestaurantRecommendation, NearbySearchRequest, PlaceScore
from places_api import fetch_nearby_restaurants, fetch_place_details
from scoring_engine import (
    compute_hidden_gem_score,
    compute_night_score,
    compute_hygiene_score,
    compute_veg_confidence,
    generate_label,
    generate_summary
)

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Food Agent API",
    description="AI-powered restaurant recommendation engine",
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
    return {"status": "ok", "message": "Food Agent API is running"}


@app.post("/recommendations", response_model=RestaurantRecommendation)
async def get_recommendations(request: NearbySearchRequest):
    """
    Get restaurant recommendations for a location
    
    Parameters:
    - latitude: Latitude of the search location
    - longitude: Longitude of the search location
    - radius: Search radius in meters (default: 2000)
    - limit: Number of top recommendations to return (default: 20)
    """

    # Fetch nearby restaurants
    nearby_places = fetch_nearby_restaurants(request.latitude, request.longitude, request.radius)

    if not nearby_places:
        raise HTTPException(status_code=404, detail="No restaurants found in this area")

    # Process top restaurants (limit to avoid API quota exhaustion)
    recommendations = []
    places_to_process = min(len(nearby_places), request.limit)

    for place in nearby_places[:places_to_process]:
        place_id = place.get("place_id")

        # Fetch detailed information
        place_details = fetch_place_details(place_id)

        if not place_details:
            continue

        # Compute scores
        hidden_gem_score = compute_hidden_gem_score(place_details)
        night_score = compute_night_score(place_details)
        reviews = place_details.get("reviews", [])
        hygiene_score = compute_hygiene_score(reviews)
        veg_confidence = compute_veg_confidence(place_details, reviews)

        # Generate label and summary
        label = generate_label(hidden_gem_score, night_score, hygiene_score, veg_confidence)
        summary = generate_summary(place_details, hidden_gem_score, night_score, hygiene_score)

        # Extract location
        geometry = place.get("geometry", {})
        location = geometry.get("location", {})

        # Create recommendation object
        recommendation = PlaceScore(
            name=place_details.get("name", place.get("name", "Unknown")),
            place_id=place_id,
            rating=place_details.get("rating", 0),
            user_ratings_total=place_details.get("user_ratings_total", 0),
            price_level=place_details.get("price_level"),
            hidden_gem_score=hidden_gem_score,
            night_score=night_score,
            hygiene_score=hygiene_score,
            veg_confidence=veg_confidence,
            label=label,
            summary=summary,
            latitude=location.get("lat", request.latitude),
            longitude=location.get("lng", request.longitude),
            types=place_details.get("types", [])
        )

        recommendations.append(recommendation)

    # Sort by combined score (weighted average)
    def calculate_total_score(rec: PlaceScore) -> float:
        weights = {
            "hidden_gem": 0.35,
            "night": 0.15,
            "hygiene": 0.35,
            "veg": 0.15
        }
        total = (
            rec.hidden_gem_score * weights["hidden_gem"] +
            rec.night_score * weights["night"] +
            rec.hygiene_score * weights["hygiene"] +
            (rec.veg_confidence / 10) * weights["veg"]  # Normalize veg_confidence
        )
        return total

    recommendations.sort(key=calculate_total_score, reverse=True)

    return RestaurantRecommendation(
        total_results=len(nearby_places),
        top_recommendations=recommendations[:request.limit],
        search_location={
            "latitude": request.latitude,
            "longitude": request.longitude,
            "radius_meters": request.radius
        }
    )


@app.get("/place/{place_id}")
async def get_place_details(place_id: str):
    """Get detailed information about a specific restaurant"""
    details = fetch_place_details(place_id)

    if not details:
        raise HTTPException(status_code=404, detail="Place not found")

    return details


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

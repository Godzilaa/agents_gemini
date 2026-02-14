from pydantic import BaseModel
from typing import Optional, List


class PlaceScore(BaseModel):
    name: str
    place_id: str
    rating: float
    user_ratings_total: int
    price_level: Optional[str]
    hidden_gem_score: float
    night_score: float
    hygiene_score: float
    veg_confidence: float
    label: str
    summary: str
    latitude: float
    longitude: float
    types: List[str]


class RestaurantRecommendation(BaseModel):
    total_results: int
    top_recommendations: List[PlaceScore]
    search_location: dict


class NearbySearchRequest(BaseModel):
    latitude: float
    longitude: float
    radius: int = 2000
    limit: int = 20

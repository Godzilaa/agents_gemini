import requests
from typing import List, Dict, Optional
import os

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY","AIzaSyCdlARRKdq2rTH1C0N4YEPpE6cgUjKZXg8")

NEARBY_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"


def fetch_nearby_restaurants(latitude: float, longitude: float, radius: int = 2000) -> List[Dict]:
    """
    Fetch nearby restaurants using Google Places Nearby Search API
    """
    params = {
        "location": f"{latitude},{longitude}",
        "radius": radius,
        "type": "restaurant",
        "key": API_KEY
    }

    try:
        response = requests.get(NEARBY_SEARCH_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "OK":
            print(f"API Error: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
            return []

        places = data.get("results", [])
        return places

    except requests.exceptions.RequestException as e:
        print(f"Error fetching nearby restaurants: {e}")
        return []


def fetch_place_details(place_id: str) -> Optional[Dict]:
    """
    Fetch detailed information for a specific place
    """
    params = {
        "place_id": place_id,
        "fields": "name,rating,user_ratings_total,reviews,opening_hours,price_level,types",
        "key": API_KEY
    }

    try:
        response = requests.get(PLACE_DETAILS_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "OK":
            print(f"API Error: {data.get('status')}")
            return None

        return data.get("result")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching place details: {e}")
        return None

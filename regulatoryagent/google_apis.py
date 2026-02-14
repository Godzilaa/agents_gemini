import requests
from typing import Dict, List, Optional, Tuple
import os

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "AIzaSyCdlARRKdq2rTH1C0N4YEPpE6cgUjKZXg8")

ROADS_API_URL = "https://roads.googleapis.com/v1/snapToRoads"
PLACES_API_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"


def snap_to_road(latitude: float, longitude: float) -> Optional[Dict]:
    """
    STEP 1: Snap user location to actual road segment using Roads API
    """
    params = {
        "points": f"{latitude},{longitude}",
        "key": API_KEY
    }

    try:
        response = requests.get(ROADS_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("snappedPoints"):
            snapped_point = data["snappedPoints"][0]
            return {
                "latitude": snapped_point["location"]["latitude"],
                "longitude": snapped_point["location"]["longitude"],
                "placeId": snapped_point.get("placeId"),
                "snappedPosition": snapped_point["location"]
            }

        return None

    except requests.exceptions.RequestException as e:
        print(f"Error snapping to road: {e}")
        return None


def find_nearby_police_stations(latitude: float, longitude: float, radius: int = 5000) -> List[Dict]:
    """
    STEP 2: Detect police stations as regulatory anchors
    """
    params = {
        "location": f"{latitude},{longitude}",
        "radius": radius,
        "type": "police",
        "key": API_KEY
    }

    try:
        response = requests.get(PLACES_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        police_stations = []
        for place in data.get("results", []):
            police_stations.append({
                "name": place.get("name"),
                "latitude": place["geometry"]["location"]["lat"],
                "longitude": place["geometry"]["location"]["lng"],
                "rating": place.get("rating"),
                "place_id": place.get("place_id"),
                "types": place.get("types", [])
            })

        return police_stations

    except requests.exceptions.RequestException as e:
        print(f"Error finding police stations: {e}")
        return []


def find_nearby_government_buildings(latitude: float, longitude: float, radius: int = 5000) -> List[Dict]:
    """
    STEP 3: Detect government buildings for risk heuristics
    """
    building_types = ["courthouse", "government_office", "local_government_office"]
    government_buildings = []

    for building_type in building_types:
        params = {
            "location": f"{latitude},{longitude}",
            "radius": radius,
            "keyword": building_type,
            "key": API_KEY
        }

        try:
            response = requests.get(PLACES_API_URL, params=params)
            response.raise_for_status()
            data = response.json()

            for place in data.get("results", []):
                government_buildings.append({
                    "name": place.get("name"),
                    "latitude": place["geometry"]["location"]["lat"],
                    "longitude": place["geometry"]["location"]["lng"],
                    "types": place.get("types", []),
                    "building_type": building_type
                })

        except requests.exceptions.RequestException as e:
            print(f"Error finding government buildings: {e}")

    return government_buildings


def find_nearby_toll_booths(latitude: float, longitude: float, radius: int = 5000) -> List[Dict]:
    """
    STEP 4: Detect toll booths as regulatory points
    """
    params = {
        "location": f"{latitude},{longitude}",
        "radius": radius,
        "keyword": "toll booth",
        "key": API_KEY
    }

    try:
        response = requests.get(PLACES_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        toll_booths = []
        for place in data.get("results", []):
            toll_booths.append({
                "name": place.get("name"),
                "latitude": place["geometry"]["location"]["lat"],
                "longitude": place["geometry"]["location"]["lng"],
                "place_id": place.get("place_id")
            })

        return toll_booths

    except requests.exceptions.RequestException as e:
        print(f"Error finding toll booths: {e}")
        return []


def find_nearby_parking_lots(latitude: float, longitude: float, radius: int = 2000) -> List[Dict]:
    """
    STEP 5: Detect parking areas for parking regulation checks
    """
    params = {
        "location": f"{latitude},{longitude}",
        "radius": radius,
        "keyword": "parking",
        "key": API_KEY
    }

    try:
        response = requests.get(PLACES_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        parking_lots = []
        for place in data.get("results", []):
            parking_lots.append({
                "name": place.get("name"),
                "latitude": place["geometry"]["location"]["lat"],
                "longitude": place["geometry"]["location"]["lng"],
                "opening_hours": place.get("opening_hours"),
                "place_id": place.get("place_id")
            })

        return parking_lots

    except requests.exceptions.RequestException as e:
        print(f"Error finding parking lots: {e}")
        return []


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates in kilometers
    Using Haversine formula
    """
    from math import radians, cos, sin, asin, sqrt

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km

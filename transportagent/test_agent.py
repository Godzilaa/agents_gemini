import requests
import json
import time

URL = "http://127.0.0.1:8001/analyze"

def test_analyze():
    # Test Case 1: Ambient Mode (Driving, English)
    payload_ambient = {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "speed": 35.0,
        "time": "18:00",
        "language": "en"
    }
    
    print(f"\n--- Testing Ambient Mode ---")
    send_request(payload_ambient)

    # Test Case 2: Destination Mode (Walking, Spanish)
    payload_dest = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "speed": 5.0,
        "time": "09:00",
        "destination": "Times Square",
        "language": "es"
    }
    
    print(f"\n--- Testing Destination Mode (Spanish) ---")
    send_request(payload_dest)

def send_request(payload):
    try:
        response = requests.post(URL, json=payload)
        response.raise_for_status()
        print("Status Code:", response.status_code)
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
             print(e.response.text)

if __name__ == "__main__":
    # Wait a bit for server to restart if needed (manual restart required by user usually, but for dev flow)
    test_analyze()

# Food Agent API

An AI-powered restaurant recommendation engine using Google Places API and intelligent scoring algorithms.

## Features

- **Nearby Restaurant Search**: Find restaurants within a specified radius
- **Hidden Gem Detection**: Identify underrated restaurants with high ratings but fewer reviews
- **Night Spot Scoring**: Detect restaurants that stay open late
- **Hygiene Analysis**: NLP-based hygiene scoring from user reviews
- **Vegetarian Detection**: Identify vegetarian/vegan restaurants
- **Smart Ranking**: Combined scoring system for intelligent recommendations

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

The `.env` file already contains your Google Maps API key:
```
GOOGLE_MAPS_API_KEY=AIzaSyCdlARRKdq2rTH1C0N4YEPpE6cgUjKZXg8
```

### 3. Run the Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### 1. Get Recommendations

**POST** `/recommendations`

Request body:
```json
{
  "latitude": 19.0760,
  "longitude": 72.8777,
  "radius": 2000,
  "limit": 20
}
```

Response:
```json
{
  "total_results": 45,
  "top_recommendations": [
    {
      "name": "Sharma Tiffins",
      "place_id": "ChIJrz...",
      "rating": 4.5,
      "user_ratings_total": 150,
      "price_level": "$",
      "hidden_gem_score": 8.5,
      "night_score": 6.0,
      "hygiene_score": 7.2,
      "veg_confidence": 82.0,
      "label": "Local Favorite",
      "summary": "Highly rated by locals, good hygiene standards, best after 9PM.",
      "latitude": 19.0760,
      "longitude": 72.8777,
      "types": ["restaurant", "point_of_interest"]
    }
  ],
  "search_location": {
    "latitude": 19.0760,
    "longitude": 72.8777,
    "radius_meters": 2000
  }
}
```

### 2. Health Check

**GET** `/health`

### 3. Get Place Details

**GET** `/place/{place_id}`

## Scoring Algorithms

### Hidden Gem Score (0-10)
```
Rating Score = Rating × 2
Review Factor:
  - < 200 reviews: +3
  - 200-500 reviews: +1
  - > 500 reviews: -2
```

### Night Score (0-10)
- 5 points if open now and closes after 11 PM
- 1 point if open now but closes earlier
- 0 points if closed

### Hygiene Score (0-10)
Analyzed from review text:
- Positive keywords: "clean", "hygienic", "fresh", "well maintained"
- Negative keywords: "dirty", "smell", "flies", "food poisoning"

### Veg Confidence (0-100%)
Detected from:
- Restaurant name
- Review keywords: "pure veg", "vegetarian", "vegan", "jain"

## Final Recommendation Score
```
Final Score = (Hidden Gem × 0.35) + (Night × 0.15) + (Hygiene × 0.35) + (Veg/10 × 0.15)
```

## Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

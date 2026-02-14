# Transport Agent

A FastAPI-based agent for mobility analysis and congestion prediction.

## Features
- **Travel Mode Detection**: Infers walking, driving, etc. from speed.
- **Congestion Scoring**: Estimates traffic congestion levels.
- **Mobility Prediction**: Forecasts movement conditions.
- **Risk Assessment**: Calculates travel risk based on conditions.

## API Endpoints

### `POST /analyze`
Analyzes transport context.

**Request Body:**
```json
{
  "latitude": 37.7749,
  "longitude": -122.4194,
  "speed": 45.0,
  "time": "18:30",
  "destination": {
    "lat": 37.7849,
    "lng": -122.4094
  }
}
```

**Response:**
```json
{
  "location": { ... },
  "prediction": {
    "mode": "Driving",
    "condition": "Moderate Traffic",
    ...
  },
  "scores": {
    "congestion_score": 6.0,
    ...
  },
  "summary": "Detected Driving in Commercial area..."
}
```

## Running the Agent
```bash
pip install -r requirements.txt
python main.py
```
Server runs on `http://0.0.0.0:8001`.

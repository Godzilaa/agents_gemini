from sqlalchemy import create_engine, Column, String, Float, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from shapely.geometry import Point, Polygon

# Use SQLite for simplicity (no external DB needed)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./regulatory_agent.db")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class RegulationZoneModel(Base):
    __tablename__ = "regulation_zones"

    id = Column(String, primary_key=True)
    zone_type = Column(String)  # helmet, parking, signal_camera, tow_zone
    name = Column(String)
    description = Column(String)
    active_hours = Column(JSON)  # {"start": "07:00", "end": "22:00"}
    risk_weight = Column(Float)
    # Store as JSON: {"type": "polygon", "coordinates": [[lat, lng], ...]}
    geometry = Column(JSON)


class PoliceStationModel(Base):
    __tablename__ = "police_stations"

    id = Column(String, primary_key=True)
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    station_type = Column(String)  # "police_station", "traffic_office"


class ParkingRegulationModel(Base):
    __tablename__ = "parking_regulations"

    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String)
    active_hours = Column(JSON)
    restricted_vehicles = Column(JSON)  # ["bike", "car", "auto"]
    geometry = Column(JSON)  # Store polygon coordinates as JSON


class TollBoothModel(Base):
    __tablename__ = "toll_booths"

    id = Column(String, primary_key=True)
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    toll_amount = Column(String)


class GovernmentBuildingModel(Base):
    __tablename__ = "government_buildings"

    id = Column(String, primary_key=True)
    name = Column(String)
    building_type = Column(String)  # "court", "secretariat", "police_hq"
    latitude = Column(Float)
    longitude = Column(Float)
    risk_multiplier = Column(Float)  # 1.5 for courts, 2.0 for secretariat


# Create tables
Base.metadata.create_all(bind=engine)


def init_sample_data(db_session):
    """Initialize sample regulation zones for testing"""
    try:
        # Clear existing data
        db_session.query(RegulationZoneModel).delete()
        db_session.query(PoliceStationModel).delete()
        db_session.query(GovernmentBuildingModel).delete()

        # Sample Helmet Enforcement Zone (MG Road, Mumbai)
        helmet_zone = RegulationZoneModel(
            id="zone_helmet_mg_road",
            zone_type="helmet",
            name="MG Road Helmet Enforcement",
            description="Strict helmet enforcement on MG Road stretch",
            active_hours={"start": "07:00", "end": "22:00"},
            risk_weight=2.0,
            geometry={
                "type": "polygon",
                "coordinates": [
                    [19.0750, 72.8750],
                    [19.0750, 72.8800],
                    [19.0800, 72.8800],
                    [19.0800, 72.8750],
                    [19.0750, 72.8750]
                ]
            }
        )

        # Sample Tow Zone
        tow_zone = RegulationZoneModel(
            id="zone_tow_central",
            zone_type="tow_zone",
            name="Central Business District Tow Zone",
            description="Illegal parking will result in vehicle tow",
            active_hours={"start": "06:00", "end": "23:00"},
            risk_weight=4.0,
            geometry={
                "type": "polygon",
                "coordinates": [
                    [19.0700, 72.8700],
                    [19.0700, 72.8900],
                    [19.0900, 72.8900],
                    [19.0900, 72.8700],
                    [19.0700, 72.8700]
                ]
            }
        )

        # Sample Signal Camera Zone
        camera_zone = RegulationZoneModel(
            id="zone_camera_junction",
            zone_type="signal_camera",
            name="Signal Camera Zone - Main Junction",
            description="Red light jumping detected by automated camera",
            active_hours={"start": "06:00", "end": "23:00"},
            risk_weight=3.0,
            geometry={
                "type": "polygon",
                "coordinates": [
                    [19.0760, 72.8770],
                    [19.0760, 72.8790],
                    [19.0780, 72.8790],
                    [19.0780, 72.8770],
                    [19.0760, 72.8770]
                ]
            }
        )

        # Sample Police Station
        police_station = PoliceStationModel(
            id="ps_001",
            name="Fort Police Station",
            latitude=19.0760,
            longitude=72.8777,
            station_type="police_station"
        )

        # Sample Government Building
        court = GovernmentBuildingModel(
            id="gov_court_001",
            name="High Court",
            building_type="court",
            latitude=19.0740,
            longitude=72.8850,
            risk_multiplier=1.5
        )

        db_session.add_all([helmet_zone, tow_zone, camera_zone, police_station, court])
        db_session.commit()
        print("Sample data initialized successfully")
    except Exception as e:
        print(f"Error initializing sample data: {e}")
        db_session.rollback()


def point_in_polygon(point: tuple, polygon_coords: list) -> bool:
    """
    Check if a point (lat, lng) is inside a polygon.
    Uses simple ray-casting algorithm.
    polygon_coords: list of [lat, lng] tuples
    """
    def is_point_inside_polygon(x, y, polygon):
        n = len(polygon)
        inside = False
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside
    
    try:
        # Convert [lat, lng] to (lng, lat) for polygon checking
        converted_polygon = [(coord[1], coord[0]) for coord in polygon_coords]
        return is_point_inside_polygon(point[1], point[0], converted_polygon)
    except Exception as e:
        print(f"Error in point_in_polygon: {e}")
    return False


# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully")

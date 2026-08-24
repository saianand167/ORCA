import math
from typing import Dict, List, Optional
from .models import LocationInfo, Coordinates

LOCATIONS: Dict[str, LocationInfo] = {
    "visakhapatnam": LocationInfo(
        id="visakhapatnam",
        name="Visakhapatnam",
        state="Andhra Pradesh",
        coordinates=Coordinates(latitude=17.6868, longitude=83.2185),
        coastal_body="Bay of Bengal",
        is_primary=True,
        description="Major port and primary operational marine zone on India's eastern seaboard."
    ),
    "kakinada": LocationInfo(
        id="kakinada",
        name="Kakinada",
        state="Andhra Pradesh",
        coordinates=Coordinates(latitude=16.9891, longitude=82.2475),
        coastal_body="Bay of Bengal",
        is_primary=False,
        description="Coringa mangrove estuary and deep-water anchorage zone."
    ),
    "chennai": LocationInfo(
        id="chennai",
        name="Chennai",
        state="Tamil Nadu",
        coordinates=Coordinates(latitude=13.0827, longitude=80.2707),
        coastal_body="Bay of Bengal / Coromandel Coast",
        is_primary=False,
        description="Coromandel Coast metropolitan hub and major commercial shipping corridor."
    ),
    "kochi": LocationInfo(
        id="kochi",
        name="Kochi",
        state="Kerala",
        coordinates=Coordinates(latitude=9.9312, longitude=76.2673),
        coastal_body="Arabian Sea / Malabar Coast",
        is_primary=False,
        description="Malabar Coast fishing harbour and Arabian Sea maritime nexus."
    ),
    "mumbai": LocationInfo(
        id="mumbai",
        name="Mumbai",
        state="Maharashtra",
        coordinates=Coordinates(latitude=18.9220, longitude=72.8347),
        coastal_body="Arabian Sea / Konkan Coast",
        is_primary=False,
        description="Western seaboard metropolitan port and offshore Bombay High basin."
    )
}

def get_location(loc_id: str) -> LocationInfo:
    loc_id_clean = loc_id.lower().replace(" ", "")
    for k, v in LOCATIONS.items():
        if k in loc_id_clean or v.name.lower() in loc_id_clean:
            return v
    # fallback to primary
    return LOCATIONS["visakhapatnam"]

def get_all_locations() -> List[LocationInfo]:
    return list(LOCATIONS.values())

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two points in km."""
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def calculate_bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate compass bearing in degrees from point 1 to point 2."""
    lat1_r, lon1_r = math.radians(lat1), math.radians(lon1)
    lat2_r, lon2_r = math.radians(lat2), math.radians(lon2)
    dlon = lon2_r - lon1_r
    y = math.sin(dlon) * math.cos(lat2_r)
    x = (math.cos(lat1_r) * math.sin(lat2_r) -
         math.sin(lat1_r) * math.cos(lat2_r) * math.cos(dlon))
    initial_bearing = math.atan2(y, x)
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    return round(compass_bearing, 1)

def bearing_to_cardinal(bearing: float) -> str:
    points = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
              "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    idx = int((bearing + 11.25) / 22.5) % 16
    return points[idx]

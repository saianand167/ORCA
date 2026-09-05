from datetime import datetime
from typing import Dict, Any, List
from ..core.models import AgentEvent
from ..core.location import haversine_distance_km, is_point_in_polygon

# Known Marine Protected Areas & Geofences along Indian Coastline
RESTRICTED_ZONES = [
    {
        "id": "MPA-CORINGA",
        "name": "Coringa Wildlife Sanctuary & Mangrove Reserve",
        "type": "Marine Protected Area",
        "center_lat": 16.8167,
        "center_lon": 82.2833,
        "radius_km": 18.0,
        "regulation": "No mechanized fishing or trawling without forest department permit."
    },
    {
        "id": "GEOFENCE-IMBL-SRILANKA",
        "name": "India - Sri Lanka International Maritime Boundary Line",
        "type": "International Maritime Boundary",
        "center_lat": 10.0500,
        "center_lon": 79.8600,
        "radius_km": 30.0,
        "regulation": "Strict border boundary; cross-border crossing strictly prohibited."
    },
    {
        "id": "MPA-GAHIRMATHA",
        "name": "Gahirmatha Marine Sanctuary (Olive Ridley Nesting)",
        "type": "Ecological Reserve",
        "center_lat": 20.7167,
        "center_lon": 87.0500,
        "radius_km": 20.0,
        "regulation": "Seasonal turtle breeding restriction zone."
    }
]

class GISAgent:
    """GIS Agent: Geospatial reasoning, geofencing checks, proximity to Marine Protected Areas and boundaries."""
    
    @staticmethod
    def execute(lat: float, lon: float, location_name: str) -> Dict[str, Any]:
        gis_alerts: List[Dict[str, Any]] = []
        
        for zone in RESTRICTED_ZONES:
            dist = haversine_distance_km(lat, lon, zone["center_lat"], zone["center_lon"])
            if dist <= zone["radius_km"] * 1.5:
                gis_alerts.append({
                    "zone_id": zone["id"],
                    "name": zone["name"],
                    "type": zone["type"],
                    "distance_km": dist,
                    "within_boundary": dist <= zone["radius_km"],
                    "regulation": zone["regulation"],
                    "alert_level": "WARNING" if dist <= zone["radius_km"] else "ADVISORY"
                })

        # Evaluate offshore deep-sea sector polygon
        deepsea_poly = [
            [lon + 0.35, lat - 0.15],
            [lon + 0.85, lat - 0.35],
            [lon + 0.95, lat + 0.45],
            [lon + 0.45, lat + 0.25],
            [lon + 0.35, lat - 0.15]
        ]
        if is_point_in_polygon(lat, lon, deepsea_poly):
            gis_alerts.append({
                "zone_id": "RISK-ZONE-DEEPSEA",
                "name": f"{location_name} Offshore Deep-Sea Sector",
                "type": "Maritime Operation Corridor",
                "distance_km": 0.0,
                "within_boundary": True,
                "regulation": "Deep-water navigation zone; monitor swell spectrum and surface currents.",
                "alert_level": "ADVISORY"
            })
                
        event = AgentEvent(
            agent="GIS Agent",
            action="Evaluated geospatial boundaries, maritime corridors & ecological zones",
            status="completed",
            details=f"Evaluated spatial layers around ({lat}°N, {lon}°E). Proximity alerts: {len(gis_alerts)}",
            timestamp=datetime.now().strftime("%H:%M:%S")
        )
        
        return {
            "gis_alerts": gis_alerts,
            "event": event
        }

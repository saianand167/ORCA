from typing import Dict, Any
from fastapi import APIRouter, Query
from ..core.location import get_location, LOCATIONS
from ..connectors.pfz import PFZProvider
from ..agents.gis_agent import RESTRICTED_ZONES

router = APIRouter(prefix="/map-data", tags=["Geospatial Layers"])

@router.get("")
async def get_map_layers(
    location: str = Query("visakhapatnam", description="Location identifier")
) -> Dict[str, Any]:
    loc_info = get_location(location)
    pfz_data = await PFZProvider.get_pfz_data(
        loc_info.coordinates.latitude,
        loc_info.coordinates.longitude,
        loc_info.name
    )
    
    # 1. Location Marker
    user_marker = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [loc_info.coordinates.longitude, loc_info.coordinates.latitude]
        },
        "properties": {
            "id": loc_info.id,
            "title": loc_info.name,
            "type": "user_location",
            "state": loc_info.state,
            "coastal_body": loc_info.coastal_body
        }
    }

    # 2. PFZ Points
    pfz_features = []
    for p in pfz_data.locations:
        pfz_features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [p.longitude, p.latitude]
            },
            "properties": {
                "id": p.id,
                "title": f"PFZ: {p.sector}",
                "type": "pfz",
                "distance_km": p.distance_km,
                "distance_nm": p.distance_nm,
                "depth_m": p.depth_m,
                "sst_range": p.sst_range_c,
                "species": p.fish_species_likely,
                "source": "INCOIS PFZ",
                "valid_until": pfz_data.valid_until
            }
        })

    # 3. Restricted & Ecological Zones
    zone_features = []
    for z in RESTRICTED_ZONES:
        zone_features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [z["center_lon"], z["center_lat"]]
            },
            "properties": {
                "id": z["id"],
                "title": z["name"],
                "type": "restricted_zone",
                "radius_km": z["radius_km"],
                "regulation": z["regulation"]
            }
        })

    # 4. Maritime Risk Zones (Polygons off coast)
    lat = loc_info.coordinates.latitude
    lon = loc_info.coordinates.longitude
    risk_polygons = [
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [lon, lat],
                    [lon + 0.35, lat - 0.15],
                    [lon + 0.45, lat + 0.25],
                    [lon + 0.1, lat + 0.35],
                    [lon, lat]
                ]]
            },
            "properties": {
                "id": "RISK-ZONE-COASTAL",
                "name": f"{loc_info.name} Coastal Corridor",
                "risk_level": "LOW",
                "color": "#10b981",
                "wave_range": "0.8 - 1.3 m",
                "wind_range": "3.5 - 5.2 m/s"
            }
        },
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [lon + 0.35, lat - 0.15],
                    [lon + 0.85, lat - 0.35],
                    [lon + 0.95, lat + 0.45],
                    [lon + 0.45, lat + 0.25],
                    [lon + 0.35, lat - 0.15]
                ]]
            },
            "properties": {
                "id": "RISK-ZONE-DEEPSEA",
                "name": f"{loc_info.name} Offshore Deep-Sea Sector",
                "risk_level": "MODERATE",
                "color": "#f59e0b",
                "wave_range": "1.5 - 2.2 m",
                "wind_range": "6.0 - 9.5 m/s"
            }
        }
    ]

    return {
        "location": loc_info.model_dump(),
        "user_marker": user_marker,
        "pfz_layer": {"type": "FeatureCollection", "features": pfz_features},
        "zones_layer": {"type": "FeatureCollection", "features": zone_features},
        "risk_zones": {"type": "FeatureCollection", "features": risk_polygons}
    }

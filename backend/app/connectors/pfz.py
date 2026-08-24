import json
from pathlib import Path
from typing import List, Optional
from ..core.models import PFZData, PFZLocation, Coordinates
from ..core.location import haversine_distance_km, calculate_bearing_deg, bearing_to_cardinal

SAMPLE_PATH = Path(__file__).resolve().parent.parent / "data" / "sample" / "pfz_visakhapatnam.json"

class PFZProvider:
    """INCOIS Potential Fishing Zones (PFZ) advisory provider with spatial proximity reasoning."""
    
    @staticmethod
    async def get_pfz_data(user_lat: float, user_lon: float, location_name: str = "Visakhapatnam") -> PFZData:
        if not SAMPLE_PATH.exists():
            return PFZData(
                available=False,
                locations=[],
                source="INCOIS PFZ Advisory",
                data_quality="DEMO SNAPSHOT"
            )
            
        try:
            with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            raw_locations = data.get("locations", [])
            calculated_locations: List[PFZLocation] = []
            
            for loc in raw_locations:
                pfz_lat = loc["latitude"]
                pfz_lon = loc["longitude"]
                
                # Dynamic distance and bearing from current user coordinates
                dist_km = haversine_distance_km(user_lat, user_lon, pfz_lat, pfz_lon)
                dist_nm = round(dist_km / 1.852, 1)
                bearing = calculate_bearing_deg(user_lat, user_lon, pfz_lat, pfz_lon)
                cardinal = bearing_to_cardinal(bearing)
                
                calculated_locations.append(PFZLocation(
                    id=loc["id"],
                    sector=f"{cardinal} ({bearing}°)",
                    direction_bearing_deg=bearing,
                    distance_km=dist_km,
                    distance_nm=dist_nm,
                    depth_m=loc.get("depth_m", "45 - 65"),
                    latitude=pfz_lat,
                    longitude=pfz_lon,
                    sst_range_c=loc.get("sst_range_c", "28.0 - 28.6"),
                    chlorophyll_gradient=loc.get("chlorophyll_gradient", "Optimal (0.8 - 1.4 mg/m³)"),
                    feature=loc.get("feature", "Satellite Thermal Front & Chlorophyll Bloom Boundary"),
                    fish_species_likely=loc.get("fish_species_likely", ["Tuna", "Mackerel", "Sardinella"]),
                    recommended_gear=loc.get("recommended_gear", "Gillnet / Ring Seine"),
                    safety_note=loc.get("safety_note", "Favorable within 20 nautical miles")
                ))

                
            # Sort by distance
            calculated_locations.sort(key=lambda x: x.distance_km)
            nearest = calculated_locations[0] if calculated_locations else None
            
            landing_c = data.get("landing_centre_coords", {})
            landing_coords = Coordinates(
                latitude=landing_c.get("latitude", 17.6974),
                longitude=landing_c.get("longitude", 83.3005)
            ) if landing_c else None
            
            return PFZData(
                available=True,
                locations=calculated_locations,
                nearest_pfz=nearest,
                advisory_date=data.get("advisory_date", "2026-08-24"),
                valid_until=data.get("valid_until", "2026-08-26"),
                source="INCOIS Marine Fisheries Advisory (PFZ)",
                data_quality="DEMO SNAPSHOT",
                landing_centre=data.get("landing_centre", "Visakhapatnam Fishing Harbour"),
                landing_centre_coords=landing_coords
            )
        except Exception:
            return PFZData(
                available=False,
                locations=[],
                source="INCOIS PFZ Provider (Unavailable)",
                data_quality="DEMO SNAPSHOT"
            )

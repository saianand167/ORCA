from datetime import datetime
from typing import Dict, Any
from ..core.models import AgentEvent, PFZData
from ..connectors.pfz import PFZProvider

class PFZAgent:
    """PFZ Agent: Filters Potential Fishing Zones and calculates spatial proximity and advisory."""
    
    @staticmethod
    async def execute(lat: float, lon: float, location_name: str) -> Dict[str, Any]:
        pfz_data = await PFZProvider.get_pfz_data(lat, lon, location_name)
        
        nearest_str = "None identified"
        if pfz_data.nearest_pfz:
            n = pfz_data.nearest_pfz
            nearest_str = f"{n.id} ({n.distance_km} km / {n.distance_nm} nm {n.sector})"
            
        event = AgentEvent(
            agent="PFZ Agent",
            action="Processed INCOIS Potential Fishing Zones & computed spatial bearings",
            status="completed" if pfz_data.available else "fallback",
            details=f"Active zones: {len(pfz_data.locations)}, Nearest: {nearest_str}, Advisory valid to: {pfz_data.valid_until}",
            timestamp=datetime.now().strftime("%H:%M:%S")
        )
        
        return {
            "pfz": pfz_data,
            "event": event
        }

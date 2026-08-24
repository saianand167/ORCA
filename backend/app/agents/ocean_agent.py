from datetime import datetime
from typing import Dict, Any
from ..core.models import AgentEvent, OceanData
from ..connectors.incois import OceanDataProvider

class OceanAgent:
    """Ocean Agent: Retrieves wave dynamics, swell, surface currents, SST, and chlorophyll."""
    
    @staticmethod
    async def execute(lat: float, lon: float, location_name: str) -> Dict[str, Any]:
        ocean = await OceanDataProvider.get_ocean_conditions(lat, lon, location_name)
        
        event = AgentEvent(
            agent="Ocean Agent",
            action="Retrieved INCOIS Ocean State Forecast telemetry",
            status="completed" if ocean.data_quality == "LIVE" else "fallback",
            details=f"Wave Height: {ocean.significant_wave_height_m}m, Swell: {ocean.swell_height_m}m @ {ocean.swell_period_s}s, Current: {ocean.surface_current_speed_ms}m/s, SST: {ocean.sea_surface_temperature_c}°C [{ocean.data_quality}]",
            timestamp=datetime.now().strftime("%H:%M:%S")
        )
        
        return {
            "ocean": ocean,
            "event": event
        }

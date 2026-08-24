from datetime import datetime
from typing import Dict, Any
from ..core.models import AgentEvent, WeatherData, MarineWarning
from ..connectors.weather import WeatherProvider
from ..connectors.imd import IMDProvider

class WeatherAgent:
    """Weather Agent: Discovers and normalizes atmospheric & marine weather data and alerts."""
    
    @staticmethod
    async def execute(lat: float, lon: float, location_name: str) -> Dict[str, Any]:
        weather = await WeatherProvider.get_weather(lat, lon, location_name)
        warnings = await IMDProvider.get_warnings(lat, lon, location_name)
        
        event = AgentEvent(
            agent="Weather Agent",
            action="Retrieved live atmospheric data and IMD coastal advisories",
            status="completed" if weather.data_quality == "LIVE" else "fallback",
            details=f"Condition: {weather.condition}, Temp: {weather.temperature_c}°C, Wind: {weather.wind_speed_ms} m/s ({weather.wind_direction_cardinal}), Active alerts: {len(warnings)} [{weather.data_quality}]",
            timestamp=datetime.now().strftime("%H:%M:%S")
        )
        
        return {
            "weather": weather,
            "warnings": warnings,
            "event": event
        }

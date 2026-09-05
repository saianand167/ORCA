from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Query
from ..core.models import WeatherData
from ..core.location import get_location
from ..connectors.weather import WeatherProvider

router = APIRouter(prefix="/weather", tags=["Weather Intelligence"])

@router.get("", response_model=WeatherData)
async def get_weather(
    location: str = Query("visakhapatnam", description="Location identifier or name"),
    lat: Optional[float] = Query(None, description="Custom latitude coordinate"),
    lon: Optional[float] = Query(None, description="Custom longitude coordinate"),
    demo_mode: bool = Query(False, description="Toggle simulated extreme squall condition for jury demonstration")
):
    valid_lat = lat if isinstance(lat, (int, float)) else None
    valid_lon = lon if isinstance(lon, (int, float)) else None
    is_demo = bool(demo_mode) if isinstance(demo_mode, bool) else False

    loc_info = get_location(location)
    target_lat = valid_lat if valid_lat is not None else loc_info.coordinates.latitude
    target_lon = valid_lon if valid_lon is not None else loc_info.coordinates.longitude
    display_name = f"{loc_info.name} ({target_lat:.2f}N, {target_lon:.2f}E)" if (valid_lat is not None or valid_lon is not None) else loc_info.name

    if is_demo:
        now_str = datetime.now().strftime("%d %b %Y, %H:%M IST")
        return WeatherData(
            location=f"{display_name} [DEMO SCENARIO]",
            temperature_c=24.8,
            humidity_percent=96.0,
            rainfall_mm=48.5,
            condition="Severe Coastal Squall & Rain",
            wind_speed_ms=18.5,
            wind_speed_knots=36.0,
            wind_direction_deg=185.0,
            wind_direction_cardinal="S",
            visibility_km=2.2,
            forecast_hourly=[
                {"time": f"{h:02d}:00", "temp_c": 24.5, "wind_ms": 18.0 + (h % 3) * 0.8}
                for h in range(12)
            ],
            source="DEMO / SIMULATED Coastal Squall Scenario",
            data_quality="DEMO / SIMULATED",
            timestamp=f"{now_str} (DEMO)",
            cache_age_seconds=0
        )

    return await WeatherProvider.get_weather(
        target_lat,
        target_lon,
        display_name
    )

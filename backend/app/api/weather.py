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
    lon: Optional[float] = Query(None, description="Custom longitude coordinate")
):
    loc_info = get_location(location)
    target_lat = lat if lat is not None else loc_info.coordinates.latitude
    target_lon = lon if lon is not None else loc_info.coordinates.longitude
    display_name = f"{loc_info.name} ({target_lat:.2f}N, {target_lon:.2f}E)" if (lat is not None or lon is not None) else loc_info.name
    return await WeatherProvider.get_weather(
        target_lat,
        target_lon,
        display_name
    )

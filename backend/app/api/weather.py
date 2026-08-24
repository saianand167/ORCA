from fastapi import APIRouter, Query
from ..core.models import WeatherData
from ..core.location import get_location
from ..connectors.weather import WeatherProvider

router = APIRouter(prefix="/weather", tags=["Weather Intelligence"])

@router.get("", response_model=WeatherData)
async def get_weather(
    location: str = Query("visakhapatnam", description="Location identifier or name")
):
    loc_info = get_location(location)
    return await WeatherProvider.get_weather(
        loc_info.coordinates.latitude,
        loc_info.coordinates.longitude,
        loc_info.name
    )

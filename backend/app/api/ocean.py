from fastapi import APIRouter, Query
from ..core.models import OceanData
from ..core.location import get_location
from ..connectors.incois import OceanDataProvider

router = APIRouter(prefix="/ocean", tags=["Ocean State Forecast"])

@router.get("", response_model=OceanData)
async def get_ocean_conditions(
    location: str = Query("visakhapatnam", description="Location identifier or name")
):
    loc_info = get_location(location)
    return await OceanDataProvider.get_ocean_conditions(
        loc_info.coordinates.latitude,
        loc_info.coordinates.longitude,
        loc_info.name
    )

from fastapi import APIRouter, Query
from ..core.models import PFZData
from ..core.location import get_location
from ..connectors.pfz import PFZProvider

router = APIRouter(prefix="/pfz", tags=["Potential Fishing Zones"])

@router.get("", response_model=PFZData)
async def get_pfz(
    location: str = Query("visakhapatnam", description="Location identifier or name"),
    lat: float = Query(None, description="Custom user latitude"),
    lon: float = Query(None, description="Custom user longitude")
):
    loc_info = get_location(location)
    user_lat = lat if lat is not None else loc_info.coordinates.latitude
    user_lon = lon if lon is not None else loc_info.coordinates.longitude
    return await PFZProvider.get_pfz_data(user_lat, user_lon, loc_info.name)

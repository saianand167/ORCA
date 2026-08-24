from typing import List
from fastapi import APIRouter, Query
from ..core.models import MarineWarning
from ..core.location import get_location
from ..connectors.imd import IMDProvider

router = APIRouter(prefix="/warnings", tags=["Marine & Weather Warnings"])

@router.get("", response_model=List[MarineWarning])
async def get_warnings(
    location: str = Query("visakhapatnam", description="Location identifier or name")
):
    loc_info = get_location(location)
    return await IMDProvider.get_warnings(
        loc_info.coordinates.latitude,
        loc_info.coordinates.longitude,
        loc_info.name
    )

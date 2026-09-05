from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Query
from ..core.models import MarineWarning
from ..core.location import get_location
from ..connectors.imd import IMDProvider

router = APIRouter(prefix="/warnings", tags=["Marine & Weather Warnings"])

@router.get("", response_model=List[MarineWarning])
async def get_warnings(
    location: str = Query("visakhapatnam", description="Location identifier or name"),
    demo_mode: bool = Query(False, description="Toggle simulated severe squall warnings for jury demonstration")
):
    is_demo = bool(demo_mode) if isinstance(demo_mode, bool) else False
    loc_info = get_location(location)

    if is_demo:
        now_str = datetime.now().strftime("%d %b %Y, %H:%M IST")
        valid_until_str = (datetime.now() + timedelta(hours=24)).strftime("%d %b %Y, %H:%M IST")
        return [
            MarineWarning(
                id=f"WARN-DEMO-{loc_info.id.upper()}-01",
                category="CYCLONE WARNING",
                severity="VERY HIGH",
                headline=f"RED ALERT: Severe Cyclonic Squall Advisory off {loc_info.name} Coast",
                description="Gale force surface winds reaching 65-75 kmph gusting to 85 kmph along with very rough sea conditions (wave heights 4.0-4.5m). Fishermen are strictly advised not to venture into deep sea and small motorized craft must return to harbor immediately.",
                affected_areas=[loc_info.name, loc_info.state, "Deep Bay of Bengal"],
                color_code="RED",
                issued_at=now_str,
                valid_until=valid_until_str,
                source="DEMO / SIMULATED IMD Cyclone Warning Centre"
            )
        ]

    return await IMDProvider.get_warnings(
        loc_info.coordinates.latitude,
        loc_info.coordinates.longitude,
        loc_info.name
    )

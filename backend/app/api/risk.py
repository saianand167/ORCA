from typing import Optional
from fastapi import APIRouter, Query
from ..core.models import RiskAssessment, RiskEvaluateRequest, UserType
from ..core.location import get_location
from ..connectors.weather import WeatherProvider
from ..connectors.incois import OceanDataProvider
from ..connectors.imd import IMDProvider
from ..core.risk_engine import evaluate_marine_risk, evaluate_risk_from_values

router = APIRouter(prefix="/risk", tags=["Deterministic Risk Engine"])

@router.get("", response_model=RiskAssessment)
async def get_location_risk(
    location: str = Query("visakhapatnam", description="Location identifier or name"),
    user_type: UserType = Query("fisherman", description="User operational role"),
    lat: Optional[float] = Query(None, description="Optional custom latitude"),
    lon: Optional[float] = Query(None, description="Optional custom longitude"),
    demo_mode: bool = Query(False, description="Toggle simulated extreme condition for jury demonstration")
):
    """
    Evaluates real-time deterministic marine risk by fetching live telemetry 
    (Wave, Wind, Currents, and Active Warnings) for the specified location or coordinates.
    """
    valid_lat = lat if isinstance(lat, (int, float)) else None
    valid_lon = lon if isinstance(lon, (int, float)) else None
    is_demo = bool(demo_mode) if isinstance(demo_mode, bool) else False
    role: UserType = user_type if isinstance(user_type, str) else "fisherman"

    if is_demo:
        return evaluate_risk_from_values(
            wave_height_m=4.2,
            wind_speed_ms=18.5,
            current_speed_ms=2.2,
            warning_severity="VERY HIGH",
            user_type=role
        )

    loc_info = get_location(location)
    target_lat = valid_lat if valid_lat is not None else loc_info.coordinates.latitude
    target_lon = valid_lon if valid_lon is not None else loc_info.coordinates.longitude
    loc_name = loc_info.name

    # Fetch live telemetry concurrently
    weather = await WeatherProvider.get_weather(target_lat, target_lon, loc_name)
    ocean = await OceanDataProvider.get_ocean_conditions(target_lat, target_lon, loc_name)
    warnings = await IMDProvider.get_warnings(target_lat, target_lon, loc_name)

    # Compute deterministic score
    return evaluate_marine_risk(weather, ocean, warnings, user_type)

@router.post("/evaluate", response_model=RiskAssessment)
async def evaluate_custom_risk(payload: RiskEvaluateRequest):
    """
    Evaluates deterministic marine risk based on direct custom sensor inputs or simulation parameters.
    Allows Member 1 (AI reasoning agents) and Member 3 (UI what-if simulation sliders) 
    to evaluate safety indices on demand without making external API calls.
    """
    return evaluate_risk_from_values(
        wave_height_m=payload.wave_height_m or 1.2,
        wind_speed_ms=payload.wind_speed_ms or 4.0,
        current_speed_ms=payload.current_speed_ms or 0.3,
        warning_severity=payload.warning_severity or "NONE",
        user_type=payload.user_type
    )

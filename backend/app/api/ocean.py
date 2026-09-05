from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Query
from ..core.models import OceanData
from ..core.location import get_location
from ..connectors.incois import OceanDataProvider

router = APIRouter(prefix="/ocean", tags=["Ocean State Forecast"])

@router.get("", response_model=OceanData)
async def get_ocean_conditions(
    location: str = Query("visakhapatnam", description="Location identifier or name"),
    lat: Optional[float] = Query(None, description="Custom latitude coordinate"),
    lon: Optional[float] = Query(None, description="Custom longitude coordinate"),
    demo_mode: bool = Query(False, description="Toggle simulated extreme rough sea condition for jury demonstration")
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
        return OceanData(
            location=f"{display_name} [DEMO SCENARIO]",
            significant_wave_height_m=4.20,
            wave_period_s=11.5,
            wave_direction_deg=175.0,
            swell_height_m=3.50,
            swell_period_s=9.8,
            swell_direction_deg=170.0,
            surface_current_speed_ms=2.20,
            surface_current_direction_deg=190.0,
            sea_surface_temperature_c=27.5,
            mixed_layer_depth_m=18.0,
            chlorophyll_mg_m3=2.40,
            chlorophyll_provenance="DERIVED (Empirical Proxy)",
            mld_provenance="DERIVED (Thermocline Model)",
            forecast_hourly=[
                {"time": f"{h:02d}:00", "wave_height_m": 4.2 + (h % 3) * 0.15, "swell_m": 3.5, "sst_c": 27.5, "current_ms": 2.2}
                for h in range(12)
            ],
            source="DEMO / SIMULATED High Sea Scenario",
            data_quality="DEMO / SIMULATED",
            timestamp=f"{now_str} (DEMO)",
            cache_age_seconds=0
        )

    return await OceanDataProvider.get_ocean_conditions(
        target_lat,
        target_lon,
        display_name
    )

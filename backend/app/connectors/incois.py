import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import httpx
from ..core.models import OceanData
from ..database.database import get_cached_data, get_any_cached_data, set_cached_data

logger = logging.getLogger(__name__)

SAMPLE_PATH = Path(__file__).resolve().parent.parent / "data" / "sample" / "incois_visakhapatnam.json"

def _safe_float(val: Any, default: Optional[float] = None) -> Optional[float]:
    """Safely converts a value to float, returning default if None or invalid."""
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

class OceanDataProvider:
    """
    Ocean data connector integrating live Marine State telemetry (Open-Meteo ECMWF / Copernicus Marine)
    calibrated for INCOIS Ocean State Forecast parameters, with a resilient 4-tier fallback architecture.
    """
    
    @staticmethod
    async def get_ocean_conditions(lat: float, lon: float, location_name: str = "Visakhapatnam") -> OceanData:
        cache_key = f"ocean_{round(lat, 2)}_{round(lon, 2)}"
        
        # Live-First Pipeline: Always attempt fresh live Marine API query on demand
        try:
            url = (
                f"https://marine-api.open-meteo.com/v1/marine"
                f"?latitude={lat}&longitude={lon}"
                f"&current=wave_height,wave_direction,wave_period,swell_wave_height,swell_wave_direction,swell_wave_period,ocean_current_velocity,ocean_current_direction,sea_surface_temperature"
                f"&hourly=wave_height,wave_period,swell_wave_height,ocean_current_velocity,sea_surface_temperature"
                f"&forecast_days=2&timezone=auto"
            )
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    current = data.get("current", {})
                    
                    wave_h = _safe_float(current.get("wave_height"))
                    wave_dir = _safe_float(current.get("wave_direction"), 0.0)
                    wave_p = _safe_float(current.get("wave_period"), 0.0)
                    swell_h = _safe_float(current.get("swell_wave_height"), 0.0)
                    swell_dir = _safe_float(current.get("swell_wave_direction"), 0.0)
                    swell_p = _safe_float(current.get("swell_wave_period"), 0.0)
                    curr_vel = _safe_float(current.get("ocean_current_velocity"), 0.0)
                    curr_dir = _safe_float(current.get("ocean_current_direction"), 0.0)
                    sst = _safe_float(current.get("sea_surface_temperature"))

                    # If shoreline or inland coordinates return null for marine parameters, fall back gracefully
                    if wave_h is not None and sst is not None:
                        # Dynamic proxy derivation for Chlorophyll & MLD based on live SST & Current Upwelling
                        # Transparently documented formula:
                        chlorophyll = round(max(0.2, min(3.0, 1.8 - (sst - 26.0) * 0.15 + (curr_vel * 0.2))), 2)
                        mld = round(max(12.0, min(45.0, 20.0 + (sst - 27.0) * 2.5)), 1)

                        # Hourly forecast mapping
                        hourly_raw = data.get("hourly", {})
                        forecast_hourly: List[Dict[str, Any]] = []
                        times = hourly_raw.get("time", [])[:12]
                        waves = hourly_raw.get("wave_height", [])[:12]
                        swells = hourly_raw.get("swell_wave_height", [])[:12]
                        ssts = hourly_raw.get("sea_surface_temperature", [])[:12]
                        currs = hourly_raw.get("ocean_current_velocity", [])[:12]
                        
                        for i in range(len(times)):
                            t_str = times[i].split("T")[-1] if "T" in times[i] else str(times[i])
                            wh = _safe_float(waves[i], wave_h) if i < len(waves) else wave_h
                            sh = _safe_float(swells[i], swell_h) if i < len(swells) else swell_h
                            st = _safe_float(ssts[i], sst) if i < len(ssts) else sst
                            cv = _safe_float(currs[i], curr_vel) if i < len(currs) else curr_vel
                            
                            forecast_hourly.append({
                                "time": t_str,
                                "wave_height_m": round(wh, 2) if wh is not None else 0.0,
                                "swell_m": round(sh, 2) if sh is not None else 0.0,
                                "sst_c": round(st, 1) if st is not None else 28.0,
                                "current_ms": round(cv, 2) if cv is not None else 0.0
                            })

                        now_str = datetime.now().strftime("%d %b %Y, %H:%M IST")
                        ocean_obj = OceanData(
                            location=location_name,
                            significant_wave_height_m=round(wave_h, 2),
                            wave_period_s=round(wave_p, 1),
                            wave_direction_deg=round(wave_dir, 1),
                            swell_height_m=round(swell_h, 2),
                            swell_period_s=round(swell_p, 1),
                            swell_direction_deg=round(swell_dir, 1),
                            surface_current_speed_ms=round(curr_vel, 2),
                            surface_current_direction_deg=round(curr_dir, 1),
                            sea_surface_temperature_c=round(sst, 1),
                            mixed_layer_depth_m=mld,
                            chlorophyll_mg_m3=chlorophyll,
                            chlorophyll_provenance="DERIVED (Empirical Proxy from Live SST & Current Upwelling)",
                            mld_provenance="DERIVED (Thermocline Boundary Layer Model)",
                            forecast_hourly=forecast_hourly,
                            source="Live Global Marine (ECMWF & Copernicus Models)",
                            data_quality="LIVE",
                            timestamp=now_str,
                            cache_age_seconds=0
                        )
                        # Write fresh telemetry to SQLite cache
                        set_cached_data(cache_key, ocean_obj.model_dump(), quality="LIVE")
                        return ocean_obj
        except Exception as err:
            logger.warning(f"Live marine API fetch failed for {lat}, {lon}: {err}. Initiating fallback sequence.")

        # Tier 2: Check for any existing cached data in SQLite (even if past normal TTL)
        cached_tuple = get_any_cached_data(cache_key)
        if cached_tuple:
            cached_data, age = cached_tuple
            cached_data["data_quality"] = "CACHED"
            cached_data["cache_age_seconds"] = age
            cached_data["source"] = f"{cached_data.get('source', 'Marine Telemetry')} (Cached {age // 60}m ago)"
            try:
                return OceanData(**cached_data)
            except Exception:
                pass

        # Tier 3: Fallback to verified local INCOIS sample snapshot
        fallback_obj = OceanDataProvider._get_sample_fallback(location_name)
        if fallback_obj:
            return fallback_obj

        # Tier 4: Graceful error response when both live API and snapshots are unreachable
        now_str = datetime.now().strftime("%d %b %Y, %H:%M IST")
        return OceanData(
            location=location_name,
            significant_wave_height_m=0.0,
            wave_period_s=0.0,
            wave_direction_deg=0.0,
            swell_height_m=0.0,
            swell_period_s=0.0,
            swell_direction_deg=0.0,
            surface_current_speed_ms=0.0,
            surface_current_direction_deg=0.0,
            sea_surface_temperature_c=0.0,
            source="Ocean Telemetry Temporarily Unavailable",
            data_quality="UNAVAILABLE",
            timestamp=now_str
        )

    @staticmethod
    def _get_sample_fallback(location_name: str) -> Optional[OceanData]:
        if SAMPLE_PATH.exists():
            try:
                with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    params = data.get("parameters", {})
                    return OceanData(
                        location=location_name,
                        significant_wave_height_m=_safe_float(params.get("significant_wave_height_m"), 1.4),
                        wave_period_s=_safe_float(params.get("wave_period_s"), 8.2),
                        wave_direction_deg=_safe_float(params.get("wave_direction_deg"), 140.0),
                        swell_height_m=_safe_float(params.get("swell_height_m"), 1.1),
                        swell_period_s=_safe_float(params.get("swell_period_s"), 11.5),
                        swell_direction_deg=_safe_float(params.get("swell_direction_deg"), 160.0),
                        surface_current_speed_ms=_safe_float(params.get("surface_current_speed_ms"), 0.42),
                        surface_current_direction_deg=_safe_float(params.get("surface_current_direction_deg"), 45.0),
                        sea_surface_temperature_c=_safe_float(params.get("sea_surface_temperature_c"), 29.4),
                        mixed_layer_depth_m=_safe_float(params.get("mixed_layer_depth_m"), 24.5),
                        chlorophyll_mg_m3=_safe_float(params.get("chlorophyll_mg_m3"), 0.85),
                        chlorophyll_provenance="DERIVED (Snapshot Empirical Model)",
                        mld_provenance="DERIVED (Snapshot Thermocline Model)",
                        forecast_hourly=data.get("forecast_24h", []),
                        source="INCOIS Ocean State Forecast (Verified Dataset Snapshot)",
                        data_quality="DEMO SNAPSHOT",
                        timestamp=data.get("timestamp", datetime.now().strftime("%d %b %Y, %H:%M IST"))
                    )
            except Exception as err:
                logger.error(f"Failed to parse sample snapshot from {SAMPLE_PATH}: {err}")
        return None

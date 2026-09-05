import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import httpx
from ..core.models import WeatherData
from ..core.location import bearing_to_cardinal
from ..database.database import get_cached_data, get_any_cached_data, set_cached_data

logger = logging.getLogger(__name__)

SAMPLE_PATH = Path(__file__).resolve().parent.parent / "data" / "sample" / "imd_visakhapatnam.json"

def _safe_float(val: Any, default: Optional[float] = None) -> Optional[float]:
    """Safely converts a value to float, returning default if None or invalid."""
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

class WeatherProvider:
    """
    Weather provider supporting live Open-Meteo Atmospheric Forecast API
    integrated with IMD coastal parameters and resilient 4-tier fallback architecture.
    """
    
    @staticmethod
    async def get_weather(lat: float, lon: float, location_name: str = "Visakhapatnam") -> WeatherData:
        cache_key = f"weather_{round(lat, 2)}_{round(lon, 2)}"
        
        # Live-First Pipeline: Always attempt fresh live Open-Meteo API query on demand
        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,wind_direction_10m,visibility"
                f"&hourly=temperature_2m,precipitation_probability,wind_speed_10m,wind_direction_10m"
                f"&forecast_days=2&timezone=auto"
            )
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    current = data.get("current", {})
                    
                    temp = _safe_float(current.get("temperature_2m"))
                    humidity = _safe_float(current.get("relative_humidity_2m"))
                    precip = _safe_float(current.get("precipitation"), 0.0)
                    wind_speed_kmh = _safe_float(current.get("wind_speed_10m"), 0.0)
                    wind_deg = _safe_float(current.get("wind_direction_10m"), 0.0)
                    raw_vis = _safe_float(current.get("visibility"))
                    
                    wind_speed_ms = round(wind_speed_kmh / 3.6, 2)
                    wind_speed_knots = round(wind_speed_kmh / 1.852, 1)
                    visibility_km = round(raw_vis / 1000.0, 1) if raw_vis is not None else 10.0
                    
                    code = current.get("weather_code", 0)
                    condition_map = {
                        0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
                        45: "Foggy", 51: "Light Drizzle", 61: "Slight Rain", 63: "Moderate Rain",
                        65: "Heavy Rain", 80: "Rain Showers", 95: "Thunderstorm"
                    }
                    condition = condition_map.get(code, "Partly Cloudy")
                    
                    # Hourly forecast items
                    hourly_raw = data.get("hourly", {})
                    forecast_hourly: List[Dict[str, Any]] = []
                    times = hourly_raw.get("time", [])[:12]
                    temps = hourly_raw.get("temperature_2m", [])[:12]
                    winds = hourly_raw.get("wind_speed_10m", [])[:12]
                    for i in range(len(times)):
                        t_str = times[i].split("T")[-1] if "T" in times[i] else str(times[i])
                        w_kmh = _safe_float(winds[i], wind_speed_kmh) if i < len(winds) else wind_speed_kmh
                        w_ms = round(w_kmh / 3.6, 1)
                        t_c = _safe_float(temps[i], temp) if i < len(temps) else temp
                        forecast_hourly.append({
                            "time": t_str,
                            "temp_c": round(t_c, 1) if t_c is not None else 30.0,
                            "wind_ms": w_ms
                        })
                    
                    now_str = datetime.now().strftime("%d %b %Y, %H:%M IST")
                    weather_obj = WeatherData(
                        location=location_name,
                        temperature_c=round(temp, 1) if temp is not None else None,
                        humidity_percent=round(humidity, 0) if humidity is not None else None,
                        rainfall_mm=round(precip, 1),
                        condition=condition,
                        wind_speed_ms=wind_speed_ms,
                        wind_speed_knots=wind_speed_knots,
                        wind_direction_deg=round(wind_deg, 1),
                        wind_direction_cardinal=bearing_to_cardinal(wind_deg),
                        visibility_km=visibility_km,
                        forecast_hourly=forecast_hourly,
                        source="Live Open-Meteo Weather API",
                        data_quality="LIVE",
                        timestamp=now_str,
                        cache_age_seconds=0
                    )
                    set_cached_data(cache_key, weather_obj.model_dump(), quality="LIVE")
                    return weather_obj
        except Exception as err:
            logger.warning(f"Live weather API fetch failed for {lat}, {lon}: {err}. Initiating fallback sequence.")

        # Tier 2: Check for any existing cached data in SQLite (even if past normal TTL)
        cached_tuple = get_any_cached_data(cache_key)
        if cached_tuple:
            cached_data, age = cached_tuple
            cached_data["data_quality"] = "CACHED"
            cached_data["cache_age_seconds"] = age
            cached_data["source"] = f"{cached_data.get('source', 'Weather Telemetry')} (Cached {age // 60}m ago)"
            try:
                return WeatherData(**cached_data)
            except Exception:
                pass

        # Tier 3: Fallback to verified local IMD snapshot
        fallback_obj = WeatherProvider._get_sample_fallback(location_name)
        if fallback_obj:
            return fallback_obj

        # Tier 4: Graceful error response when both live API and snapshots are unreachable
        now_str = datetime.now().strftime("%d %b %Y, %H:%M IST")
        return WeatherData(
            location=location_name,
            temperature_c=None,
            humidity_percent=None,
            rainfall_mm=0.0,
            condition="Telemetry Unavailable",
            wind_speed_ms=0.0,
            wind_speed_knots=0.0,
            wind_direction_deg=0.0,
            wind_direction_cardinal="N",
            visibility_km=None,
            source="Weather Telemetry Temporarily Unavailable",
            data_quality="UNAVAILABLE",
            timestamp=now_str
        )

    @staticmethod
    def _get_sample_fallback(location_name: str) -> Optional[WeatherData]:
        if SAMPLE_PATH.exists():
            try:
                with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    wind_deg = _safe_float(data.get("wind_direction_deg"), 135.0)
                    wind_speed_ms = _safe_float(data.get("wind_speed_ms"), 5.14)
                    wind_speed_knots = _safe_float(data.get("wind_speed_knots"), 10.0)
                    return WeatherData(
                        location=location_name,
                        temperature_c=_safe_float(data.get("temperature_c"), 31.2),
                        humidity_percent=_safe_float(data.get("humidity_percent"), 76.0),
                        rainfall_mm=_safe_float(data.get("rainfall_mm"), 0.0),
                        condition=data.get("condition", "Partly Cloudy"),
                        wind_speed_ms=wind_speed_ms,
                        wind_speed_knots=wind_speed_knots,
                        wind_direction_deg=wind_deg,
                        wind_direction_cardinal=bearing_to_cardinal(wind_deg),
                        visibility_km=_safe_float(data.get("visibility_km"), 9.0),
                        forecast_hourly=[
                            {"time": "06:00", "temp_c": 28.5, "wind_ms": 4.2},
                            {"time": "09:00", "temp_c": 30.1, "wind_ms": 4.8},
                            {"time": "12:00", "temp_c": 31.5, "wind_ms": 5.4},
                            {"time": "15:00", "temp_c": 32.0, "wind_ms": 5.8},
                            {"time": "18:00", "temp_c": 30.0, "wind_ms": 4.9},
                            {"time": "21:00", "temp_c": 29.0, "wind_ms": 4.1}
                        ],
                        source="IMD Coastal Weather Bulletin (Verified Dataset Snapshot)",
                        data_quality="DEMO SNAPSHOT",
                        timestamp=data.get("timestamp", datetime.now().strftime("%d %b %Y, %H:%M IST"))
                    )
            except Exception as err:
                logger.error(f"Failed to parse sample snapshot from {SAMPLE_PATH}: {err}")
        return None

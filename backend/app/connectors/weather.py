import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import httpx
from ..core.models import WeatherData
from ..core.location import bearing_to_cardinal
from ..database.database import get_cached_data, set_cached_data

SAMPLE_PATH = Path(__file__).resolve().parent.parent / "data" / "sample" / "imd_visakhapatnam.json"

class WeatherProvider:
    """Weather provider supporting live Open-Meteo API with IMD integration and fallback snapshots."""
    
    @staticmethod
    async def get_weather(lat: float, lon: float, location_name: str = "Visakhapatnam") -> WeatherData:
        cache_key = f"weather_{round(lat, 2)}_{round(lon, 2)}"
        cached = get_cached_data(cache_key, max_age_seconds=900)
        if cached:
            return WeatherData(
                location=cached.get("location", location_name),
                temperature_c=cached.get("temperature_c"),
                humidity_percent=cached.get("humidity_percent"),
                rainfall_mm=cached.get("rainfall_mm"),
                condition=cached.get("condition", "Clear"),
                wind_speed_ms=cached.get("wind_speed_ms", 0.0),
                wind_speed_knots=cached.get("wind_speed_knots", 0.0),
                wind_direction_deg=cached.get("wind_direction_deg", 0.0),
                wind_direction_cardinal=cached.get("wind_direction_cardinal", "N"),
                visibility_km=cached.get("visibility_km", 10.0),
                forecast_hourly=cached.get("forecast_hourly", []),
                source=cached.get("source", "Open-Meteo / IMD"),
                data_quality="CACHED",
                timestamp=cached.get("timestamp", datetime.now().strftime("%d %b %Y, %H:%M IST"))
            )

        # Attempt Live Open-Meteo Weather API
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,wind_direction_10m,visibility&hourly=temperature_2m,precipitation_probability,wind_speed_10m,wind_direction_10m&forecast_days=2&timezone=auto"
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    current = data.get("current", {})
                    wind_speed_kmh = current.get("wind_speed_10m", 15.0)
                    wind_speed_ms = round(wind_speed_kmh / 3.6, 2)
                    wind_speed_knots = round(wind_speed_kmh / 1.852, 1)
                    wind_deg = current.get("wind_direction_10m", 140.0)
                    
                    code = current.get("weather_code", 0)
                    condition_map = {
                        0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
                        45: "Foggy", 51: "Light Drizzle", 61: "Slight Rain", 63: "Moderate Rain",
                        65: "Heavy Rain", 80: "Rain Showers", 95: "Thunderstorm"
                    }
                    condition = condition_map.get(code, "Partly Cloudy")
                    
                    # Hourly forecast items
                    hourly_raw = data.get("hourly", {})
                    forecast_hourly = []
                    times = hourly_raw.get("time", [])[:12]
                    temps = hourly_raw.get("temperature_2m", [])[:12]
                    winds = hourly_raw.get("wind_speed_10m", [])[:12]
                    for i in range(len(times)):
                        t_str = times[i].split("T")[-1] if "T" in times[i] else str(times[i])
                        w_ms = round(winds[i] / 3.6, 1) if i < len(winds) else 0.0
                        forecast_hourly.append({
                            "time": t_str,
                            "temp_c": temps[i] if i < len(temps) else 30.0,
                            "wind_ms": w_ms
                        })
                    
                    now_str = datetime.now().strftime("%d %b %Y, %H:%M IST")
                    weather_obj = WeatherData(
                        location=location_name,
                        temperature_c=current.get("temperature_2m", 30.5),
                        humidity_percent=current.get("relative_humidity_2m", 78.0),
                        rainfall_mm=current.get("precipitation", 0.0),
                        condition=condition,
                        wind_speed_ms=wind_speed_ms,
                        wind_speed_knots=wind_speed_knots,
                        wind_direction_deg=wind_deg,
                        wind_direction_cardinal=bearing_to_cardinal(wind_deg),
                        visibility_km=round(current.get("visibility", 10000) / 1000, 1),
                        forecast_hourly=forecast_hourly,
                        source="Live Open-Meteo Weather API",
                        data_quality="LIVE",
                        timestamp=now_str
                    )
                    set_cached_data(cache_key, weather_obj.model_dump(), quality="LIVE")
                    return weather_obj
        except Exception:
            pass

        # Fallback to Sample Snapshot
        return WeatherProvider._get_sample_fallback(location_name)

    @staticmethod
    def _get_sample_fallback(location_name: str) -> WeatherData:
        if SAMPLE_PATH.exists():
            try:
                with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return WeatherData(
                        location=location_name,
                        temperature_c=data.get("temperature_c", 31.2),
                        humidity_percent=data.get("humidity_percent", 76),
                        rainfall_mm=data.get("rainfall_mm", 0.0),
                        condition=data.get("condition", "Partly Cloudy"),
                        wind_speed_ms=data.get("wind_speed_ms", 5.14),
                        wind_speed_knots=data.get("wind_speed_knots", 10.0),
                        wind_direction_deg=data.get("wind_direction_deg", 135),
                        wind_direction_cardinal=bearing_to_cardinal(data.get("wind_direction_deg", 135)),
                        visibility_km=data.get("visibility_km", 9.0),
                        forecast_hourly=[
                            {"time": "06:00", "temp_c": 28.5, "wind_ms": 4.2},
                            {"time": "09:00", "temp_c": 30.1, "wind_ms": 4.8},
                            {"time": "12:00", "temp_c": 31.5, "wind_ms": 5.4},
                            {"time": "15:00", "temp_c": 32.0, "wind_ms": 5.8},
                            {"time": "18:00", "temp_c": 30.0, "wind_ms": 4.9},
                            {"time": "21:00", "temp_c": 29.0, "wind_ms": 4.1}
                        ],
                        source="IMD Coastal Weather Bulletin (Snapshot)",
                        data_quality="DEMO SNAPSHOT",
                        timestamp=data.get("timestamp", datetime.now().strftime("%d %b %Y, %H:%M IST"))
                    )
            except Exception:
                pass
        return WeatherData(
            location=location_name,
            temperature_c=30.0,
            humidity_percent=75,
            rainfall_mm=0.0,
            condition="Partly Cloudy",
            wind_speed_ms=5.0,
            wind_speed_knots=9.7,
            wind_direction_deg=140,
            wind_direction_cardinal="SE",
            visibility_km=10.0,
            source="IMD / Weather Fallback",
            data_quality="DEMO SNAPSHOT",
            timestamp=datetime.now().strftime("%d %b %Y, %H:%M IST")
        )

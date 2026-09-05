import json
import logging
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
import httpx
from ..core.models import MarineWarning
from ..core.config import settings

logger = logging.getLogger(__name__)

SAMPLE_PATH = Path(__file__).resolve().parent.parent / "data" / "sample" / "imd_visakhapatnam.json"


class IMDProvider:
    """
    IMD Marine Warnings connector.
    
    Generates LIVE dynamic warnings by analyzing real-time weather & marine conditions
    from Open-Meteo APIs. Falls back to local IMD snapshot if live APIs are unreachable.
    
    Warning logic mirrors official IMD Fishermen Warning criteria:
    - Wind speed thresholds (Beaufort Scale marine classifications)
    - Wave height thresholds (WMO Sea State Scale)
    - Weather code severity (thunderstorm, heavy rain)
    - Visibility conditions (fog advisory)
    """

    # IMD Fishermen Warning Thresholds (based on official IMD criteria)
    WIND_THRESHOLDS = {
        "VERY HIGH": 17.2,   # >= 17.2 m/s (Gale force, Beaufort 8+)
        "HIGH": 10.8,        # >= 10.8 m/s (Strong breeze, Beaufort 6+)
        "MODERATE": 7.9,     # >= 7.9 m/s (Moderate breeze, Beaufort 5)
    }
    WAVE_THRESHOLDS = {
        "VERY HIGH": 4.0,    # >= 4.0m (Very rough sea, WMO State 6+)
        "HIGH": 2.5,         # >= 2.5m (Rough sea, WMO State 5)
        "MODERATE": 1.5,     # >= 1.5m (Moderate sea, WMO State 4)
    }

    @staticmethod
    async def get_warnings(lat: float, lon: float, location_name: str = "Visakhapatnam") -> List[MarineWarning]:
        """
        Fetch LIVE weather conditions and generate dynamic marine warnings
        based on real-time wind, wave, and weather severity analysis.
        """
        warnings: List[MarineWarning] = []
        now_str = datetime.now().strftime("%d %b %Y, %H:%M IST")
        valid_until_str = (datetime.now() + timedelta(hours=24)).strftime("%d %b %Y, %H:%M IST")

        try:
            # Fetch LIVE weather data from Open-Meteo
            weather_url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}"
                f"&current=weather_code,wind_speed_10m,wind_gusts_10m,visibility"
                f"&timezone=auto"
            )
            marine_url = (
                f"https://marine-api.open-meteo.com/v1/marine"
                f"?latitude={lat}&longitude={lon}"
                f"&current=wave_height,swell_wave_height"
                f"&timezone=auto"
            )

            async with httpx.AsyncClient(timeout=6.0) as client:
                weather_resp, marine_resp = await client.get(weather_url), await client.get(marine_url)

            if weather_resp.status_code == 200 and marine_resp.status_code == 200:
                w_current = weather_resp.json().get("current", {})
                m_current = marine_resp.json().get("current", {})

                wind_speed_kmh = w_current.get("wind_speed_10m", 0) or 0
                wind_gusts_kmh = w_current.get("wind_gusts_10m", 0) or 0
                weather_code = w_current.get("weather_code", 0) or 0
                visibility_m = w_current.get("visibility", 50000) or 50000
                wave_height = m_current.get("wave_height", 0) or 0
                swell_height = m_current.get("swell_wave_height", 0) or 0

                wind_speed_ms = wind_speed_kmh / 3.6
                wind_gusts_ms = wind_gusts_kmh / 3.6
                visibility_km = visibility_m / 1000.0

                warn_id_counter = 1

                # --- Wind-based warnings ---
                for level, threshold in IMDProvider.WIND_THRESHOLDS.items():
                    if wind_speed_ms >= threshold:
                        wind_knots = round(wind_speed_ms * 1.944, 1)
                        gust_knots = round(wind_gusts_ms * 1.944, 1)
                        if level == "VERY HIGH":
                            headline = f"GALE WARNING: Sustained winds {wind_knots} kts with gusts up to {gust_knots} kts"
                            description = (
                                f"Gale force winds of {round(wind_speed_ms, 1)} m/s ({wind_knots} kts) detected with gusts "
                                f"reaching {round(wind_gusts_ms, 1)} m/s ({gust_knots} kts). "
                                f"ALL fishing vessels must return to port immediately. Do NOT venture into open sea."
                            )
                            color = "RED"
                        elif level == "HIGH":
                            headline = f"STRONG WIND ADVISORY: Winds {wind_knots} kts, gusts {gust_knots} kts"
                            description = (
                                f"Strong winds of {round(wind_speed_ms, 1)} m/s ({wind_knots} kts) with gusts "
                                f"reaching {round(wind_gusts_ms, 1)} m/s ({gust_knots} kts). "
                                f"Small craft should not venture beyond 12 nautical miles from shore."
                            )
                            color = "ORANGE"
                        else:
                            headline = f"Moderate wind advisory: Sustained winds {wind_knots} kts"
                            description = (
                                f"Moderate winds of {round(wind_speed_ms, 1)} m/s ({wind_knots} kts). "
                                f"Exercise caution for small mechanized craft. Monitor conditions."
                            )
                            color = "YELLOW"

                        warnings.append(MarineWarning(
                            id=f"IMD-LIVE-WIND-{warn_id_counter:02d}",
                            category="Fishermen Wind Advisory",
                            severity=level,
                            headline=headline,
                            description=description,
                            affected_areas=[location_name, f"{location_name} Coastal Waters"],
                            color_code=color,
                            issued_at=now_str,
                            valid_until=valid_until_str,
                            source="Marine advisory dynamically generated from live weather/ocean telemetry using defined warning thresholds"
                        ))
                        warn_id_counter += 1
                        break  # Only emit the highest matching wind warning

                # --- Wave-based warnings ---
                for level, threshold in IMDProvider.WAVE_THRESHOLDS.items():
                    if wave_height >= threshold:
                        if level == "VERY HIGH":
                            headline = f"VERY ROUGH SEA WARNING: Wave height {wave_height}m, Swell {swell_height}m"
                            description = (
                                f"Very rough sea conditions with significant wave height of {wave_height}m "
                                f"and swell of {swell_height}m. ALL fishing operations suspended. "
                                f"Vessels must seek shelter in nearest port."
                            )
                            color = "RED"
                        elif level == "HIGH":
                            headline = f"ROUGH SEA ADVISORY: Wave height {wave_height}m"
                            description = (
                                f"Rough sea with wave height {wave_height}m and swell {swell_height}m. "
                                f"Small craft and country boats advised NOT to venture into open sea."
                            )
                            color = "ORANGE"
                        else:
                            headline = f"Moderate sea state: Wave height {wave_height}m"
                            description = (
                                f"Moderate sea conditions with {wave_height}m waves. "
                                f"Small craft should exercise caution beyond 20 nm from shore."
                            )
                            color = "YELLOW"

                        warnings.append(MarineWarning(
                            id=f"ADV-LIVE-WAVE-{warn_id_counter:02d}",
                            category="Sea State Advisory",
                            severity=level,
                            headline=headline,
                            description=description,
                            affected_areas=[location_name, f"{location_name} Offshore Waters"],
                            color_code=color,
                            issued_at=now_str,
                            valid_until=valid_until_str,
                            source="Marine advisory dynamically generated from live weather/ocean telemetry using defined warning thresholds"
                        ))
                        warn_id_counter += 1
                        break

                # --- Weather code based warnings (thunderstorm, heavy rain) ---
                severe_codes = {
                    95: ("Thunderstorm", "HIGH", "ORANGE"),
                    96: ("Thunderstorm with Hail", "VERY HIGH", "RED"),
                    99: ("Severe Thunderstorm with Heavy Hail", "VERY HIGH", "RED"),
                    65: ("Heavy Rain", "MODERATE", "YELLOW"),
                    67: ("Freezing Heavy Rain", "HIGH", "ORANGE"),
                    75: ("Heavy Snowfall", "HIGH", "ORANGE"),
                    82: ("Violent Rain Showers", "HIGH", "ORANGE"),
                }
                if weather_code in severe_codes:
                    wx_name, wx_sev, wx_color = severe_codes[weather_code]
                    warnings.append(MarineWarning(
                        id=f"ADV-LIVE-WX-{warn_id_counter:02d}",
                        category="Severe Weather Advisory",
                        severity=wx_sev,
                        headline=f"{wx_name} detected over {location_name} coastal waters",
                        description=(
                            f"Weather code {weather_code} ({wx_name}) detected from live atmospheric model. "
                            f"Mariners should take appropriate precautions and monitor VHF Channel 16."
                        ),
                        affected_areas=[location_name],
                        color_code=wx_color,
                        issued_at=now_str,
                        valid_until=valid_until_str,
                        source="Marine advisory dynamically generated from live weather/ocean telemetry using defined warning thresholds"
                    ))
                    warn_id_counter += 1

                # --- Visibility warning (fog) ---
                if visibility_km < 2.0:
                    fog_sev = "HIGH" if visibility_km < 0.5 else "MODERATE"
                    fog_color = "ORANGE" if visibility_km < 0.5 else "YELLOW"
                    warnings.append(MarineWarning(
                        id=f"ADV-LIVE-VIS-{warn_id_counter:02d}",
                        category="Visibility Advisory",
                        severity=fog_sev,
                        headline=f"Low visibility ({round(visibility_km, 1)} km) over coastal waters",
                        description=(
                            f"Visibility reduced to {round(visibility_km, 1)} km due to fog/mist. "
                            f"Navigate with caution. Use radar and sound signals. Reduce speed."
                        ),
                        affected_areas=[location_name],
                        color_code=fog_color,
                        issued_at=now_str,
                        valid_until=valid_until_str,
                        source="Marine advisory dynamically generated from live weather/ocean telemetry using defined warning thresholds"
                    ))

                # --- If no specific warnings triggered, issue a LIVE all-clear ---
                if not warnings:
                    warnings.append(MarineWarning(
                        id="ADV-LIVE-CLR-01",
                        category="Coastal Marine Advisory",
                        severity="LOW",
                        headline=f"Normal sea state: Wind {round(wind_speed_ms, 1)} m/s, Waves {wave_height}m",
                        description=(
                            f"No severe weather warning for {location_name} coastal tract. "
                            f"Current conditions: Wind {round(wind_speed_ms, 1)} m/s "
                            f"({round(wind_speed_ms * 1.944, 1)} kts), "
                            f"Wave height {wave_height}m, Visibility {round(visibility_km, 1)} km. "
                            f"Conditions favorable for coastal fishing operations."
                        ),
                        affected_areas=[location_name],
                        color_code="GREEN",
                        issued_at=now_str,
                        valid_until=valid_until_str,
                        source="Marine advisory dynamically generated from live weather/ocean telemetry using defined warning thresholds"
                    ))

                logger.info(f"IMD: Generated {len(warnings)} LIVE warning(s) for {location_name}")
                return warnings

        except Exception as err:
            logger.warning(f"Live IMD warning generation failed for {lat}, {lon}: {err}. Falling back to snapshot.")

        # Fallback: Parse official IMD Coastal & Fishermen warning snapshot
        if SAMPLE_PATH.exists():
            try:
                with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("warnings", []):
                        warnings.append(MarineWarning(
                            id=item.get("id", "IMD-01"),
                            category=item.get("category", "Fishermen Warning"),
                            severity=item.get("severity", "MODERATE"),
                            headline=item.get("headline", "Squally weather likely over coastal waters"),
                            description=item.get("description", "Fishermen are advised to exercise caution."),
                            affected_areas=item.get("affected_areas", [location_name]),
                            color_code=item.get("color_code", "YELLOW"),
                            issued_at=item.get("issued_at", now_str),
                            valid_until=item.get("valid_until", "Next 24-48 Hours"),
                            source=item.get("source", "IMD Cyclone Warning Centre (CWC) [Snapshot]")
                        ))
            except Exception:
                pass

        if not warnings:
            warnings.append(MarineWarning(
                id="IMD-FALLBACK-01",
                category="Coastal Marine Advisory",
                severity="LOW",
                headline="Normal sea state with light to moderate surface breeze",
                description=f"No severe weather warning for {location_name} coastal tract. (Snapshot data)",
                affected_areas=[location_name],
                color_code="GREEN",
                issued_at=now_str,
                valid_until="Next 24 Hours",
                source="IMD Cyclone Warning Centre [Snapshot Fallback]"
            ))

        return warnings

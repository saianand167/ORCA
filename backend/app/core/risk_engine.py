from pathlib import Path
from typing import List, Optional
import yaml
from .models import WeatherData, OceanData, MarineWarning, RiskAssessment, RiskLevel, UserType

def load_risk_config():
    config_path = Path(__file__).resolve().parent.parent / "config" / "risk_thresholds.yaml"
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception:
            pass
    # Built-in default thresholds
    return {
        "wind_speed_ms": {"low_max": 5.5, "moderate_max": 9.0, "high_max": 13.5},
        "wave_height_m": {"low_max": 1.25, "moderate_max": 2.0, "high_max": 3.5},
        "swell_height_m": {"low_max": 1.0, "moderate_max": 1.8, "high_max": 2.8},
        "current_speed_ms": {"low_max": 0.5, "moderate_max": 1.0, "high_max": 1.8},
        "user_type_modifiers": {
            "fisherman": {"wave_weight": 0.35, "wind_weight": 0.30, "warning_weight": 0.25, "current_weight": 0.10},
            "ocean_researcher": {"wave_weight": 0.30, "wind_weight": 0.25, "warning_weight": 0.30, "current_weight": 0.15},
            "ship_operator": {"wave_weight": 0.30, "wind_weight": 0.35, "warning_weight": 0.25, "current_weight": 0.10}
        }
    }

RISK_CONFIG = load_risk_config()

def evaluate_marine_risk(
    weather: Optional[WeatherData],
    ocean: Optional[OceanData],
    warnings: Optional[List[MarineWarning]] = None,
    user_type: UserType = "fisherman"
) -> RiskAssessment:
    reasons: List[str] = []
    
    # 1. Wave risk score (0 - 100)
    wave_h = ocean.significant_wave_height_m if ocean else 1.2
    wave_limits = RISK_CONFIG.get("wave_height_m", {})
    if wave_h <= wave_limits.get("low_max", 1.25):
        wave_score = (wave_h / 1.25) * 25
    elif wave_h <= wave_limits.get("moderate_max", 2.0):
        wave_score = 25 + ((wave_h - 1.25) / 0.75) * 35
        reasons.append(f"Moderate wave height ({wave_h:.1f} m)")
    elif wave_h <= wave_limits.get("high_max", 3.5):
        wave_score = 60 + ((wave_h - 2.0) / 1.5) * 25
        reasons.append(f"Elevated rough waves ({wave_h:.1f} m)")
    else:
        wave_score = 90 + min(10, (wave_h - 3.5) * 5)
        reasons.append(f"Hazardous high wave conditions ({wave_h:.1f} m)")

    # 2. Wind risk score (0 - 100)
    wind_ms = weather.wind_speed_ms if weather else 4.0
    wind_limits = RISK_CONFIG.get("wind_speed_ms", {})
    if wind_ms <= wind_limits.get("low_max", 5.5):
        wind_score = (wind_ms / 5.5) * 25
    elif wind_ms <= wind_limits.get("moderate_max", 9.0):
        wind_score = 25 + ((wind_ms - 5.5) / 3.5) * 35
        reasons.append(f"Moderate surface breeze ({wind_ms:.1f} m/s / {wind_ms*1.944:.1f} kts)")
    elif wind_ms <= wind_limits.get("high_max", 13.5):
        wind_score = 60 + ((wind_ms - 9.0) / 4.5) * 25
        reasons.append(f"Strong squally winds ({wind_ms:.1f} m/s / {wind_ms*1.944:.1f} kts)")
    else:
        wind_score = 90 + min(10, (wind_ms - 13.5) * 3)
        reasons.append(f"Gale/storm force winds ({wind_ms:.1f} m/s / {wind_ms*1.944:.1f} kts)")

    # 3. Swell & Current score (0 - 100)
    current_ms = ocean.surface_current_speed_ms if ocean else 0.3
    if current_ms > 1.2:
        reasons.append(f"Strong surface current ({current_ms:.2f} m/s)")
        current_score = 75
    elif current_ms > 0.7:
        current_score = 45
    else:
        current_score = 15

    # 4. Warnings score
    warning_score = 0
    active_warnings = warnings or []
    if active_warnings:
        for w in active_warnings:
            reasons.append(f"Active advisory: {w.headline}")
            if w.severity == "VERY HIGH" or "cyclone" in w.category.lower():
                warning_score = max(warning_score, 95)
            elif w.severity == "HIGH":
                warning_score = max(warning_score, 80)
            elif w.severity == "MODERATE":
                warning_score = max(warning_score, 55)
            else:
                warning_score = max(warning_score, 30)

    # Weights by user type
    weights = RISK_CONFIG.get("user_type_modifiers", {}).get(user_type, {
        "wave_weight": 0.35, "wind_weight": 0.30, "warning_weight": 0.25, "current_weight": 0.10
    })

    composite_score = (
        wave_score * weights.get("wave_weight", 0.35) +
        wind_score * weights.get("wind_weight", 0.30) +
        warning_score * weights.get("warning_weight", 0.25) +
        current_score * weights.get("current_weight", 0.10)
    )
    
    # If a severe cyclone/gale warning is present, ensure score is at least 75
    if warning_score >= 80:
        composite_score = max(composite_score, warning_score * 0.9)

    final_score = int(round(min(100, max(5, composite_score))))

    if final_score <= 30:
        risk_level: RiskLevel = "LOW"
        safe_for_ops = True
        if not reasons:
            reasons.append("Calm sea state and gentle wind parameters")
        summary = "Favorable marine conditions for operations."
    elif final_score <= 60:
        risk_level = "MODERATE"
        safe_for_ops = True
        summary = "Moderate conditions; exercise standard coastal caution."
    elif final_score <= 80:
        risk_level = "HIGH"
        safe_for_ops = False
        summary = "Unfavorable rough conditions; small craft advisories apply."
    else:
        risk_level = "VERY HIGH"
        safe_for_ops = False
        summary = "Hazardous severe marine state; avoid operations."

    return RiskAssessment(
        risk_level=risk_level,
        score=final_score,
        reasons=reasons,
        safe_for_operations=safe_for_ops,
        summary=summary,
        model_name="ORCA Prototype Risk Model v1.0",
        disclaimer="Prototype decision-support result. Always verify official marine advisories before operating."
    )
